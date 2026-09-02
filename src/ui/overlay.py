"""
HUD and Visual Overlay module for Face Mouse Pro.
Renders facial landmark contours, EAR/MAR meters, tracking crosshairs, status badges,
and on-screen interactive controls on the live OpenCV camera view.
"""

from typing import Any

import cv2
import numpy as np


class HUDOverlay:
    """
    Renders high-visibility, modern graphical HUD over camera frames.
    """

    COLOR_PRIMARY_CYAN = (245, 206, 0)  # Electric Cyan (BGR)
    COLOR_ACCENT_MAGENTA = (204, 0, 255)  # Magenta Pink
    COLOR_SUCCESS_GREEN = (50, 220, 50)  # Neon Green
    COLOR_WARN_YELLOW = (0, 215, 255)  # Amber Yellow
    COLOR_ALERT_RED = (40, 40, 255)  # Bright Red
    COLOR_BG_DARK = (15, 15, 22)  # Midnight Slate
    COLOR_WHITE = (255, 255, 255)
    COLOR_GRAY = (150, 150, 150)

    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def render(
        self,
        frame: np.ndarray,
        tracking_data: dict[str, Any] | None,
        fps: float,
        is_calibrated: bool,
        is_paused: bool,
        is_dragging: bool,
        is_mouth_open: bool,
        left_ear: float,
        right_ear: float,
        mar: float,
        ear_thresh: float,
        mar_thresh: float,
        sensitivity: float,
    ) -> np.ndarray:
        """
        Composites HUD elements onto the camera frame.
        """
        overlay_frame = frame.copy()
        h, w, _ = frame.shape

        # 1. Top Header Banner
        self._draw_header_banner(
            overlay_frame, w, fps, is_calibrated, is_paused, is_dragging, is_mouth_open, sensitivity
        )

        # 2. Draw Facial Landmarks & Contours if tracking active
        if tracking_data:
            pixels = tracking_data.get("pixels", {})
            self._draw_mesh_features(overlay_frame, pixels, is_mouth_open)
            self._draw_nose_crosshair(overlay_frame, pixels.get("nose"))
        else:
            # Tracking loss banner
            cv2.putText(
                overlay_frame,
                "SEARCHING FOR FACE...",
                (int(w * 0.28), int(h * 0.50)),
                self.font,
                0.85,
                self.COLOR_WARN_YELLOW,
                2,
                cv2.LINE_AA,
            )

        # 3. Bottom Gauges (EAR & MAR Meters)
        self._draw_metric_meters(overlay_frame, w, h, left_ear, right_ear, mar, ear_thresh, mar_thresh)

        # 4. Bottom Controls Quick Bar
        self._draw_footer_controls(overlay_frame, w, h)

        return overlay_frame

    def _draw_header_banner(
        self,
        img: np.ndarray,
        width: int,
        fps: float,
        is_calibrated: bool,
        is_paused: bool,
        is_dragging: bool,
        is_mouth_open: bool,
        sensitivity: float,
    ) -> None:
        cv2.rectangle(img, (0, 0), (width, 50), self.COLOR_BG_DARK, -1)
        cv2.line(img, (0, 50), (width, 50), self.COLOR_PRIMARY_CYAN, 1)

        # App Title
        cv2.putText(img, "FACE MOUSE PRO", (15, 33), self.font, 0.70, self.COLOR_PRIMARY_CYAN, 2, cv2.LINE_AA)

        x_badge = 225

        # Mode Badge
        if is_paused:
            mode_text = "[ PAUSED ]"
            mode_col = self.COLOR_ALERT_RED
        elif is_dragging:
            mode_text = "[ DRAGGING ]"
            mode_col = self.COLOR_ACCENT_MAGENTA
        elif is_mouth_open:
            mode_text = "[ SCROLL MODE ]"
            mode_col = self.COLOR_WARN_YELLOW
        else:
            mode_text = "[ NORMAL ]"
            mode_col = self.COLOR_SUCCESS_GREEN

        cv2.putText(img, mode_text, (x_badge, 33), self.font, 0.52, mode_col, 2, cv2.LINE_AA)

        # Calibration status
        calib_text = "CALIBRATED" if is_calibrated else "PRESS SPACE"
        calib_col = self.COLOR_SUCCESS_GREEN if is_calibrated else self.COLOR_WARN_YELLOW
        cv2.putText(img, f"CALIB: {calib_text}", (x_badge + 125, 33), self.font, 0.45, calib_col, 1, cv2.LINE_AA)

        # Metrics on right
        fps_text = f"FPS: {fps:.0f}"
        sens_text = f"SENS: {sensitivity:.1f}x"
        cv2.putText(
            img, f"{fps_text} | {sens_text}", (width - 150, 33), self.font, 0.42, self.COLOR_WHITE, 1, cv2.LINE_AA
        )

    def _draw_mesh_features(self, img: np.ndarray, pixels: dict[str, Any], is_mouth_open: bool) -> None:
        left_eye_pts = pixels.get("left_eye", [])
        right_eye_pts = pixels.get("right_eye", [])
        mouth_pts = pixels.get("mouth", [])

        # Eyes contour
        if left_eye_pts:
            pts = np.array(left_eye_pts, np.int32).reshape((-1, 1, 2))
            cv2.polylines(img, [pts], True, self.COLOR_PRIMARY_CYAN, 1, cv2.LINE_AA)

        if right_eye_pts:
            pts = np.array(right_eye_pts, np.int32).reshape((-1, 1, 2))
            cv2.polylines(img, [pts], True, self.COLOR_PRIMARY_CYAN, 1, cv2.LINE_AA)

        # Mouth contour
        if mouth_pts:
            pts = np.array(mouth_pts, np.int32).reshape((-1, 1, 2))
            mouth_col = self.COLOR_WARN_YELLOW if is_mouth_open else self.COLOR_ACCENT_MAGENTA
            cv2.polylines(img, [pts], True, mouth_col, 1, cv2.LINE_AA)

    def _draw_nose_crosshair(self, img: np.ndarray, nose_pt: tuple[int, int] | None) -> None:
        if not nose_pt:
            return
        x, y = nose_pt
        cv2.circle(img, (x, y), 8, self.COLOR_PRIMARY_CYAN, 1, cv2.LINE_AA)
        cv2.circle(img, (x, y), 2, self.COLOR_ACCENT_MAGENTA, -1, cv2.LINE_AA)
        cv2.line(img, (x - 12, y), (x - 4, y), self.COLOR_PRIMARY_CYAN, 1, cv2.LINE_AA)
        cv2.line(img, (x + 4, y), (x + 12, y), self.COLOR_PRIMARY_CYAN, 1, cv2.LINE_AA)
        cv2.line(img, (x, y - 12), (x, y - 4), self.COLOR_PRIMARY_CYAN, 1, cv2.LINE_AA)
        cv2.line(img, (x, y + 4), (x, y + 12), self.COLOR_PRIMARY_CYAN, 1, cv2.LINE_AA)

    def _draw_metric_meters(
        self,
        img: np.ndarray,
        w: int,
        h: int,
        l_ear: float,
        r_ear: float,
        mar: float,
        ear_thresh: float,
        mar_thresh: float,
    ) -> None:
        bar_w = 80
        bar_h = 10
        y_base = h - 60

        def draw_meter(x: int, y: int, label: str, value: float, threshold: float, is_above: bool = False):
            cv2.rectangle(img, (x, y), (x + bar_w, y + bar_h), (40, 40, 45), -1)
            ratio = min(1.0, max(0.0, value / (threshold * 2.0 if threshold > 0 else 1.0)))
            fill_w = int(bar_w * ratio)

            is_active = (value > threshold) if is_above else (value < threshold)
            fill_col = self.COLOR_WARN_YELLOW if is_active else self.COLOR_PRIMARY_CYAN

            if fill_w > 0:
                cv2.rectangle(img, (x, y), (x + fill_w, y + bar_h), fill_col, -1)

            thresh_x = int(x + bar_w * 0.5)
            cv2.line(img, (thresh_x, y - 2), (thresh_x, y + bar_h + 2), self.COLOR_ALERT_RED, 1)
            cv2.putText(img, f"{label}: {value:.2f}", (x, y - 4), self.font, 0.38, self.COLOR_WHITE, 1, cv2.LINE_AA)

        draw_meter(15, y_base, "L-EYE", l_ear, ear_thresh, is_above=False)
        draw_meter(110, y_base, "R-EYE", r_ear, ear_thresh, is_above=False)
        draw_meter(205, y_base, "MOUTH", mar, mar_thresh, is_above=True)

    def _draw_footer_controls(self, img: np.ndarray, width: int, height: int) -> None:
        cv2.rectangle(img, (0, height - 30), (width, height), self.COLOR_BG_DARK, -1)
        help_text = "[SPACE] Calibrate | [O] Settings GUI | [P] Pause | [S/D] Sens | [Q] Quit"
        cv2.putText(img, help_text, (15, height - 10), self.font, 0.38, self.COLOR_GRAY, 1, cv2.LINE_AA)
