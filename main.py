from typing import Any

"""
Face Mouse Pro — Main Application Entry Point.
Coordinates real-time camera ingestion, MediaPipe face mesh processing,
calibration management, gesture detection, PyAutoGUI mouse execution, UI HUD rendering,
and CustomTkinter GUI Settings Panel.
"""

import argparse
import os
import sys
import time

import cv2

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config.config_manager import ConfigManager
from src.core.calibration import CalibrationManager
from src.core.camera import Camera
from src.core.face_tracker import FaceTracker
from src.core.gesture_detector import GestureAction, GestureDetector
from src.core.mouse_controller import MouseController
from src.ui.overlay import HUDOverlay
from src.ui.settings_window import launch_settings_async
from src.utils.logger import setup_logger

logger = setup_logger("Main")


class FaceMouseProApp:
    """
    Main orchestration class for the Face Mouse Pro application lifecycle.
    """

    def __init__(self, open_settings_on_start: bool = False):
        logger.info("Initializing Face Mouse Pro Application...")

        # 1. Configuration Manager
        self.config_manager = ConfigManager()
        self.settings = self.config_manager.settings

        # 2. Camera Ingestion
        cam_cfg = self.settings.get("camera", {})
        self.camera = Camera(
            device_index=cam_cfg.get("device_index", 0),
            width=cam_cfg.get("width", 640),
            height=cam_cfg.get("height", 480),
            fps=cam_cfg.get("fps", 30),
        )

        # 3. Face Tracker
        self.face_tracker = FaceTracker()

        # 4. Calibration Manager
        calib_cfg = self.settings.get("calibration", {})
        self.calibration = CalibrationManager(
            neutral_x=calib_cfg.get("neutral_x", 0.5),
            neutral_y=calib_cfg.get("neutral_y", 0.5),
            is_calibrated=calib_cfg.get("calibrated", False),
        )

        # 5. Gesture Detector
        gestures_cfg = self.settings.get("gestures", {})
        self.gesture_detector = GestureDetector(
            blink_ear_threshold=gestures_cfg.get("blink_ear_threshold", 0.21),
            blink_min_frames=gestures_cfg.get("blink_min_frames", 2),
            blink_max_frames=gestures_cfg.get("blink_max_frames", 14),
            double_click_window_sec=gestures_cfg.get("double_click_window_sec", 0.40),
            long_blink_duration_sec=gestures_cfg.get("long_blink_duration_sec", 0.80),
            both_eyes_natural_blink_ratio_diff=gestures_cfg.get("both_eyes_natural_blink_ratio_diff", 0.05),
            mouth_mar_threshold=gestures_cfg.get("mouth_mar_threshold", 0.45),
            mouth_open_min_frames=gestures_cfg.get("mouth_open_min_frames", 3),
            click_cooldown_sec=gestures_cfg.get("click_cooldown_sec", 0.35),
        )

        # 6. Mouse Controller
        cursor_cfg = self.settings.get("cursor", {})
        scroll_cfg = self.settings.get("scroll", {})
        self.mouse_controller = MouseController(
            sensitivity_x=cursor_cfg.get("sensitivity_x", 2.2),
            sensitivity_y=cursor_cfg.get("sensitivity_y", 2.0),
            deadzone_x=cursor_cfg.get("deadzone_x", 0.008),
            deadzone_y=cursor_cfg.get("deadzone_y", 0.008),
            acceleration_curve=cursor_cfg.get("acceleration_curve", 1.2),
            invert_x=cursor_cfg.get("invert_x", False),
            invert_y=cursor_cfg.get("invert_y", False),
            scroll_speed=scroll_cfg.get("scroll_speed", 30),
            scroll_deadzone_y=scroll_cfg.get("scroll_deadzone_y", 0.02),
            scroll_cooldown_sec=scroll_cfg.get("scroll_cooldown_sec", 0.08),
        )

        # 7. UI Overlay
        self.hud = HUDOverlay()

        self.running = False

        if open_settings_on_start:
            self.open_settings_panel()

        logger.info("Face Mouse Pro App initialized successfully.")

    def on_settings_changed(self, section: str, key: str, value: Any):
        """
        Callback triggered whenever settings are updated in the GUI.
        """
        logger.info(f"Applying real-time setting change: {section}.{key} = {value}")
        self.mouse_controller.update_settings(self.config_manager.get("cursor"), self.config_manager.get("scroll"))
        self.gesture_detector.update_parameters(self.config_manager.get("gestures"))

    def open_settings_panel(self):
        """
        Spawns the CustomTkinter settings window asynchronously.
        """
        logger.info("Opening Settings Control Panel GUI...")
        launch_settings_async(self.config_manager, self.on_settings_changed)

    def run(self) -> None:
        """
        Executes the main processing loop.
        """
        if not self.camera.start():
            logger.error("Failed to start camera. Please check webcam connection.")
            return

        self.running = True
        window_name = "Face Mouse Pro - Live Control & HUD"
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

        logger.info("Entering main execution loop. Look straight ahead and press SPACE to calibrate.")

        try:
            while self.running:
                ret, frame = self.camera.read_frame()
                if not ret or frame is None:
                    time.sleep(0.01)
                    continue

                now = time.perf_counter()

                # Process face landmarks
                tracking_data = self.face_tracker.process_frame(frame)

                if tracking_data:
                    nose_x, nose_y = tracking_data["nose"]
                    left_eye = tracking_data["left_eye"]
                    right_eye = tracking_data["right_eye"]
                    mouth = tracking_data["mouth"]

                    # 1. Gesture Recognition
                    gesture_action = self.gesture_detector.process(
                        left_eye_landmarks=left_eye,
                        right_eye_landmarks=right_eye,
                        mouth_landmarks=mouth,
                        current_time=now,
                    )

                    # Execute gestures (clicks, drag toggle)
                    if gesture_action != GestureAction.NONE:
                        self.mouse_controller.execute_gesture(gesture_action)

                    # 2. Cursor Motion / Scrolling
                    if self.calibration.is_calibrated:
                        cursor_cfg = self.config_manager.get("cursor")
                        dx, dy = self.calibration.get_relative_offset(
                            nose_x=nose_x,
                            nose_y=nose_y,
                            deadzone_x=cursor_cfg.get("deadzone_x", 0.008),
                            deadzone_y=cursor_cfg.get("deadzone_y", 0.008),
                        )

                        if self.gesture_detector.is_mouth_open:
                            self.mouse_controller.handle_scroll(dy)
                        else:
                            self.mouse_controller.move_cursor_relative(dx, dy)

                # Render HUD Overlay
                gestures_cfg = self.config_manager.get("gestures")
                cursor_cfg = self.config_manager.get("cursor")
                hud_frame = self.hud.render(
                    frame=frame,
                    tracking_data=tracking_data,
                    fps=self.camera.get_fps(),
                    is_calibrated=self.calibration.is_calibrated,
                    is_paused=self.mouse_controller.is_paused,
                    is_dragging=self.mouse_controller.is_dragging,
                    is_mouth_open=self.gesture_detector.is_mouth_open,
                    left_ear=self.gesture_detector.current_left_ear,
                    right_ear=self.gesture_detector.current_right_ear,
                    mar=self.gesture_detector.current_mar,
                    ear_thresh=gestures_cfg.get("blink_ear_threshold", 0.21),
                    mar_thresh=gestures_cfg.get("mouth_mar_threshold", 0.45),
                    sensitivity=cursor_cfg.get("sensitivity_x", 2.2),
                )

                cv2.imshow(window_name, hud_frame)

                # Handle Keyboard Input
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:  # 'q' or ESC
                    logger.info("Exit command received. Shutting down...")
                    break
                elif key == 32:  # SPACE -> Calibrate
                    if tracking_data:
                        nx, ny = tracking_data["nose"]
                        self.calibration.calibrate_immediate(nx, ny)
                        self.config_manager.set("calibration", "calibrated", True, auto_save=False)
                        self.config_manager.set("calibration", "neutral_x", nx, auto_save=False)
                        self.config_manager.set("calibration", "neutral_y", ny, auto_save=True)
                elif key == ord("o") or key == ord("O"):  # Open Settings GUI
                    self.open_settings_panel()
                elif key == ord("p") or key == ord("P"):  # Pause / Resume
                    self.mouse_controller.toggle_pause()
                elif key == ord("s") or key == ord("S"):  # Sensitivity Up
                    curr_sx = self.config_manager.get("cursor", "sensitivity_x", 2.2)
                    curr_sy = self.config_manager.get("cursor", "sensitivity_y", 2.0)
                    new_sx = round(curr_sx + 0.2, 2)
                    new_sy = round(curr_sy + 0.2, 2)
                    self.config_manager.set("cursor", "sensitivity_x", new_sx, auto_save=False)
                    self.config_manager.set("cursor", "sensitivity_y", new_sy, auto_save=True)
                    self.mouse_controller.update_settings(
                        self.config_manager.get("cursor"), self.config_manager.get("scroll")
                    )
                    logger.info(f"Increased sensitivity to {new_sx}")
                elif key == ord("d") or key == ord("D"):  # Sensitivity Down
                    curr_sx = self.config_manager.get("cursor", "sensitivity_x", 2.2)
                    curr_sy = self.config_manager.get("cursor", "sensitivity_y", 2.0)
                    new_sx = max(0.4, round(curr_sx - 0.2, 2))
                    new_sy = max(0.4, round(curr_sy - 0.2, 2))
                    self.config_manager.set("cursor", "sensitivity_x", new_sx, auto_save=False)
                    self.config_manager.set("cursor", "sensitivity_y", new_sy, auto_save=True)
                    self.mouse_controller.update_settings(
                        self.config_manager.get("cursor"), self.config_manager.get("scroll")
                    )
                    logger.info(f"Decreased sensitivity to {new_sx}")
                elif key == ord("r") or key == ord("R"):  # Reset Calibration
                    self.calibration.reset_calibration()
                    self.config_manager.set("calibration", "calibrated", False, auto_save=True)
                    logger.info("Reset calibration.")

        except KeyboardInterrupt:
            logger.info("Interrupted by user.")
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """
        Cleans up all system hardware and window resources.
        """
        logger.info("Performing clean application shutdown...")
        self.running = False
        self.mouse_controller.cleanup()
        self.face_tracker.close()
        self.camera.stop()
        cv2.destroyAllWindows()
        logger.info("Face Mouse Pro shutdown complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Face Mouse Pro — AI Hands-Free Controller")
    parser.add_argument("--settings", action="store_true", help="Launch Settings GUI panel alongside the camera")
    args = parser.parse_args()

    app = FaceMouseProApp(open_settings_on_start=args.settings)
    app.run()
