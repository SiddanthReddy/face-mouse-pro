"""
Camera capture module for Face Mouse Pro.
Manages OpenCV VideoCapture with frame rate tracking, automatic reconnect recovery,
and configurable resolution backends.
"""

import time

import cv2
import numpy as np

from src.utils.logger import setup_logger

logger = setup_logger("Camera")


class Camera:
    """
    Handles robust video frame capture from webcams with auto-reconnect fallback.
    """

    def __init__(self, device_index: int = 0, width: int = 640, height: int = 480, fps: int = 30):
        self.device_index = device_index
        self.width = width
        self.height = height
        self.target_fps = fps
        self.cap: cv2.VideoCapture | None = None
        self.is_opened = False

        # Reconnect state metrics
        self.consecutive_failures = 0
        self.max_failures_before_reconnect = 10
        self.last_reconnect_attempt = 0.0
        self.reconnect_cooldown = 2.0

        # FPS calculation metrics
        self.prev_frame_time = time.perf_counter()
        self.current_fps = 0.0
        self.frame_count = 0

    def start(self) -> bool:
        """
        Initializes and opens the camera capture device.
        """
        logger.info(f"Opening camera index {self.device_index} ({self.width}x{self.height} @ {self.target_fps}fps)")

        # Try DirectShow backend on Windows, then default
        self.cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
        if not self.cap or not self.cap.isOpened():
            logger.warning(f"Failed with DSHOW, trying default backend for camera index {self.device_index}...")
            self.cap = cv2.VideoCapture(self.device_index)

        if not self.cap or not self.cap.isOpened():
            logger.error(f"Could not open camera device index {self.device_index}.")
            self.is_opened = False
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)

        self.is_opened = True
        self.consecutive_failures = 0
        self.prev_frame_time = time.perf_counter()
        logger.info(f"Camera index {self.device_index} successfully opened.")
        return True

    def read_frame(self) -> tuple[bool, np.ndarray | None]:
        """
        Captures next frame with auto-reconnect fallback and mirror flipping.
        """
        if not self.is_opened or self.cap is None:
            self._attempt_reconnect()
            return False, None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.max_failures_before_reconnect:
                logger.warning("Camera stream interrupted. Triggering auto-reconnect...")
                self.stop()
                self._attempt_reconnect()
            return False, None

        self.consecutive_failures = 0

        # Horizontal mirror flip for natural gaze navigation
        frame = cv2.flip(frame, 1)

        # Compute instant smoothed FPS
        now = time.perf_counter()
        dt = now - self.prev_frame_time
        self.prev_frame_time = now
        if dt > 0:
            instant_fps = 1.0 / dt
            self.current_fps = 0.9 * self.current_fps + 0.1 * instant_fps if self.current_fps > 0 else instant_fps

        self.frame_count += 1
        return True, frame

    def _attempt_reconnect(self) -> None:
        now = time.perf_counter()
        if now - self.last_reconnect_attempt > self.reconnect_cooldown:
            self.last_reconnect_attempt = now
            logger.info("Attempting camera reconnection...")
            self.start()

    def get_fps(self) -> float:
        return self.current_fps

    def stop(self) -> None:
        """
        Releases camera hardware resources.
        """
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            logger.info(f"Camera index {self.device_index} released.")
        self.is_opened = False
        self.cap = None
