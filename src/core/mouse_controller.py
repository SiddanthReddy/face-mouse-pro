"""
Mouse controller module for Face Mouse Pro.
Executes cursor moves, clicks, drag-and-drop, and scrolling via PyAutoGUI.
Includes screen boundary clamping and safety features.
"""

from __future__ import annotations

import time

import pyautogui
from face_mouse_core.config import CursorMappingConfig, SmoothingConfig
from face_mouse_core.cursor import CursorMapper, OneEuroFilter2D
from face_mouse_core.gestures import GestureType
from face_mouse_core.models import Vector2D

from src.core.gesture_detector import GestureAction
from src.utils.logger import setup_logger

logger = setup_logger("MouseController")

# PyAutoGUI configuration
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.001


class MouseController:
    """
    Translates facial tracking vectors and gestures into OS mouse events.
    """

    def __init__(
        self,
        sensitivity_x: float = 2.2,
        sensitivity_y: float = 2.0,
        deadzone_x: float = 0.008,
        deadzone_y: float = 0.008,
        acceleration_curve: float = 1.2,
        invert_x: bool = False,
        invert_y: bool = False,
        scroll_speed: int = 30,
        scroll_deadzone_y: float = 0.02,
        scroll_cooldown_sec: float = 0.08,
    ):
        self.sensitivity_x = sensitivity_x
        self.sensitivity_y = sensitivity_y
        self.deadzone_x = deadzone_x
        self.deadzone_y = deadzone_y
        self.acceleration_curve = acceleration_curve
        self.invert_x = invert_x
        self.invert_y = invert_y
        self.scroll_speed = scroll_speed
        self.scroll_deadzone_y = scroll_deadzone_y
        self.scroll_cooldown_sec = scroll_cooldown_sec

        # Screen dimensions
        try:
            self.screen_width, self.screen_height = pyautogui.size()
        except Exception:
            self.screen_width, self.screen_height = 1920, 1080

        # State flags
        self.is_dragging = False
        self.is_paused = False
        self.last_scroll_time = 0.0

        # Adaptive filter for smooth cursor movement
        self._cursor_mapper = CursorMapper(
            CursorMappingConfig(
                sensitivity_x=self.sensitivity_x,
                sensitivity_y=self.sensitivity_y,
                acceleration_curve=self.acceleration_curve,
                invert_x=self.invert_x,
                invert_y=self.invert_y,
            )
        )
        self.filter = OneEuroFilter2D(SmoothingConfig(min_cutoff=1.2, beta=0.04, derivative_cutoff=1.0))

        # Virtual cursor position tracker
        self.current_cursor_x = float(self.screen_width // 2)
        self.current_cursor_y = float(self.screen_height // 2)

        logger.info(f"MouseController initialized. Screen bounds: {self.screen_width}x{self.screen_height}")

    def update_settings(self, cursor_cfg: dict, scroll_cfg: dict) -> None:
        """
        Updates controller runtime settings.
        """
        self.sensitivity_x = cursor_cfg.get("sensitivity_x", self.sensitivity_x)
        self.sensitivity_y = cursor_cfg.get("sensitivity_y", self.sensitivity_y)
        self.deadzone_x = cursor_cfg.get("deadzone_x", self.deadzone_x)
        self.deadzone_y = cursor_cfg.get("deadzone_y", self.deadzone_y)
        self.acceleration_curve = cursor_cfg.get("acceleration_curve", self.acceleration_curve)
        self.invert_x = cursor_cfg.get("invert_x", self.invert_x)
        self.invert_y = cursor_cfg.get("invert_y", self.invert_y)
        self.scroll_speed = scroll_cfg.get("scroll_speed", self.scroll_speed)
        self.scroll_deadzone_y = scroll_cfg.get("scroll_deadzone_y", self.scroll_deadzone_y)
        self.scroll_cooldown_sec = scroll_cfg.get("scroll_cooldown_sec", self.scroll_cooldown_sec)
        self._cursor_mapper = CursorMapper(
            CursorMappingConfig(
                sensitivity_x=self.sensitivity_x,
                sensitivity_y=self.sensitivity_y,
                acceleration_curve=self.acceleration_curve,
                invert_x=self.invert_x,
                invert_y=self.invert_y,
            )
        )

    def move_cursor_relative(self, dx: float, dy: float, current_time: float | None = None) -> tuple[int, int]:
        """
        Calculates screen cursor delta from relative normalized face vector and moves the cursor.
        """
        if self.is_paused:
            return int(self.current_cursor_x), int(self.current_cursor_y)

        # Core maps the relative vector without knowing display dimensions.
        mapped = self._cursor_mapper.map_offset(Vector2D(dx, dy))
        scaled_dx = mapped.x * self.screen_width
        scaled_dy = mapped.y * self.screen_height

        # Preserve pixel-domain smoothing and the existing filter parameters.
        timestamp = time.perf_counter() if current_time is None else current_time
        smoothed = self.filter.filter(Vector2D(scaled_dx, scaled_dy), timestamp)
        smooth_dx, smooth_dy = smoothed.x, smoothed.y

        # Target coordinates clamped to safe screen boundaries (avoiding exact corner fail-safe triggers)
        margin = 4
        target_x = max(margin, min(self.screen_width - margin, self.current_cursor_x + smooth_dx))
        target_y = max(margin, min(self.screen_height - margin, self.current_cursor_y + smooth_dy))

        self.current_cursor_x = target_x
        self.current_cursor_y = target_y

        try:
            pyautogui.moveTo(int(target_x), int(target_y))
        except pyautogui.FailSafeException:
            logger.warning("PyAutoGUI FailSafe triggered. Resetting cursor position to center.")
            self.current_cursor_x = float(self.screen_width // 2)
            self.current_cursor_y = float(self.screen_height // 2)
            try:
                pyautogui.moveTo(int(self.current_cursor_x), int(self.current_cursor_y))
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Error moving mouse cursor: {e}")

        return int(target_x), int(target_y)

    def execute_gesture(self, action: GestureAction) -> None:
        """
        Executes the corresponding mouse click or drag event for a recognized gesture.
        """
        if self.is_paused or action == GestureAction.NONE:
            return

        try:
            if action == GestureType.LEFT_CLICK:
                logger.info("Executing Left Click")
                pyautogui.click(button="left")

            elif action == GestureType.RIGHT_CLICK:
                logger.info("Executing Right Click")
                pyautogui.click(button="right")

            elif action == GestureType.DOUBLE_CLICK:
                logger.info("Executing Double Click")
                pyautogui.doubleClick(button="left")

            elif action == GestureType.DRAG_TOGGLE:
                self.is_dragging = not self.is_dragging
                if self.is_dragging:
                    logger.info("Drag Started: Mouse Down")
                    pyautogui.mouseDown(button="left")
                else:
                    logger.info("Drag Released: Mouse Up")
                    pyautogui.mouseUp(button="left")

        except Exception as e:
            logger.error(f"Error executing mouse gesture {action}: {e}")

    def handle_scroll(self, dy: float) -> None:
        """
        Scrolls up or down based on vertical head offset during mouth-open mode.
        """
        if self.is_paused:
            return

        now = time.perf_counter()
        if now - self.last_scroll_time < self.scroll_cooldown_sec:
            return

        if abs(dy) < self.scroll_deadzone_y:
            return

        # Upwards head movement (negative dy in image coords) -> scroll UP (positive clicks)
        # Downwards head movement (positive dy in image coords) -> scroll DOWN (negative clicks)
        scroll_amount = int(-1 * (dy / max(abs(dy), 1e-4)) * self.scroll_speed)

        try:
            pyautogui.scroll(scroll_amount)
            self.last_scroll_time = now
            logger.debug(f"Executed scroll: {scroll_amount}")
        except Exception as e:
            logger.error(f"Error executing scroll: {e}")

    def toggle_pause(self) -> bool:
        """
        Toggles pause mode on/off.
        """
        self.is_paused = not self.is_paused
        if self.is_paused and self.is_dragging:
            pyautogui.mouseUp(button="left")
            self.is_dragging = False
        logger.info(f"Mouse control {'PAUSED' if self.is_paused else 'RESUMED'}")
        return self.is_paused

    def cleanup(self) -> None:
        """
        Releases any held mouse buttons on application exit.
        """
        if self.is_dragging:
            try:
                pyautogui.mouseUp(button="left")
            except Exception:
                pass
            self.is_dragging = False
