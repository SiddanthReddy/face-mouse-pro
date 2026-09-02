"""
Gesture recognition engine for Face Mouse Pro.
Detects Left Click, Right Click, Double Click, Drag & Drop (long blink), and Mouth Open (Scroll Mode).
Includes dual-eye natural blink rejection to prevent false clicks during normal involuntary blinking.
"""

import time
from collections.abc import Sequence
from enum import Enum, auto
from typing import Any

from src.utils.helpers import calculate_ear, calculate_mar
from src.utils.logger import setup_logger

logger = setup_logger("GestureDetector")


class GestureAction(Enum):
    NONE = auto()
    LEFT_CLICK = auto()
    RIGHT_CLICK = auto()
    DOUBLE_CLICK = auto()
    DRAG_TOGGLE = auto()
    SCROLL_UP = auto()
    SCROLL_DOWN = auto()


class EyeState:
    """
    Tracks state machine for a single eye (left or right).
    """

    def __init__(self):
        self.is_closed = False
        self.close_start_time: float | None = None
        self.closed_frame_count = 0
        self.last_blink_release_time: float = 0.0
        self.consecutive_blink_count = 0


class GestureDetector:
    """
    Stateful detector analyzing facial landmarks across video frames.
    """

    def __init__(
        self,
        blink_ear_threshold: float = 0.21,
        blink_min_frames: int = 2,
        blink_max_frames: int = 14,
        double_click_window_sec: float = 0.40,
        long_blink_duration_sec: float = 0.80,
        both_eyes_natural_blink_ratio_diff: float = 0.05,
        mouth_mar_threshold: float = 0.45,
        mouth_open_min_frames: int = 3,
        click_cooldown_sec: float = 0.35,
    ):
        self.blink_ear_threshold = blink_ear_threshold
        self.blink_min_frames = blink_min_frames
        self.blink_max_frames = blink_max_frames
        self.double_click_window_sec = double_click_window_sec
        self.long_blink_duration_sec = long_blink_duration_sec
        self.both_eyes_natural_blink_ratio_diff = both_eyes_natural_blink_ratio_diff
        self.mouth_mar_threshold = mouth_mar_threshold
        self.mouth_open_min_frames = mouth_open_min_frames
        self.click_cooldown_sec = click_cooldown_sec

        self.left_eye_state = EyeState()
        self.right_eye_state = EyeState()

        # Mouth state
        self.mouth_open_frames = 0
        self.is_mouth_open = False

        # Global cooldown tracker
        self.last_action_time = 0.0

        # Pending click state for double-click disambiguation
        self.pending_left_click = False
        self.pending_left_click_time = 0.0

        # Current metrics for HUD rendering
        self.current_left_ear = 0.0
        self.current_right_ear = 0.0
        self.current_mar = 0.0

    def update_parameters(self, config_gestures: dict[str, Any]) -> None:
        """
        Updates detection thresholds from configuration.
        """
        self.blink_ear_threshold = config_gestures.get("blink_ear_threshold", self.blink_ear_threshold)
        self.blink_min_frames = config_gestures.get("blink_min_frames", self.blink_min_frames)
        self.blink_max_frames = config_gestures.get("blink_max_frames", self.blink_max_frames)
        self.double_click_window_sec = config_gestures.get("double_click_window_sec", self.double_click_window_sec)
        self.long_blink_duration_sec = config_gestures.get("long_blink_duration_sec", self.long_blink_duration_sec)
        self.mouth_mar_threshold = config_gestures.get("mouth_mar_threshold", self.mouth_mar_threshold)
        self.click_cooldown_sec = config_gestures.get("click_cooldown_sec", self.click_cooldown_sec)

    def process(
        self,
        left_eye_landmarks: Sequence[Sequence[float]],
        right_eye_landmarks: Sequence[Sequence[float]],
        mouth_landmarks: Sequence[Sequence[float]],
        current_time: float | None = None,
    ) -> GestureAction:
        """
        Processes facial landmarks for the current frame and returns any triggered action.
        """
        if current_time is None:
            current_time = time.perf_counter()

        # Calculate EAR & MAR
        self.current_left_ear = calculate_ear(left_eye_landmarks)
        self.current_right_ear = calculate_ear(right_eye_landmarks)
        self.current_mar = calculate_mar(mouth_landmarks)

        left_closed = self.current_left_ear < self.blink_ear_threshold
        right_closed = self.current_right_ear < self.blink_ear_threshold
        mouth_open = self.current_mar > self.mouth_mar_threshold

        # Update mouth open state
        if mouth_open:
            self.mouth_open_frames += 1
            if self.mouth_open_frames >= self.mouth_open_min_frames:
                self.is_mouth_open = True
        else:
            self.mouth_open_frames = 0
            self.is_mouth_open = False

        # Involuntary natural blink check: both eyes closed simultaneously
        is_natural_both_eye_blink = left_closed and right_closed

        # Check pending left click timeout (if waiting for second click to form double-click)
        triggered_action = GestureAction.NONE
        if self.pending_left_click and (current_time - self.pending_left_click_time > self.double_click_window_sec):
            self.pending_left_click = False
            triggered_action = GestureAction.LEFT_CLICK
            self.last_action_time = current_time
            logger.debug("Dispatched confirmed Left Click after double-click window expired.")

        # If currently in cooldown, track state but do not fire new clicks
        in_cooldown = (current_time - self.last_action_time) < self.click_cooldown_sec

        # --- LEFT EYE PROCESSING ---
        if left_closed and not is_natural_both_eye_blink:
            if not self.left_eye_state.is_closed:
                self.left_eye_state.is_closed = True
                self.left_eye_state.close_start_time = current_time
                self.left_eye_state.closed_frame_count = 1
            else:
                self.left_eye_state.closed_frame_count += 1

                # Check for Long Blink (Drag Toggle) while holding eye closed
                duration = current_time - (self.left_eye_state.close_start_time or current_time)
                if duration >= self.long_blink_duration_sec and not in_cooldown:
                    self.left_eye_state.is_closed = False
                    self.left_eye_state.closed_frame_count = 0
                    self.last_action_time = current_time
                    self.pending_left_click = False
                    logger.info("Long blink triggered -> DRAG_TOGGLE")
                    return GestureAction.DRAG_TOGGLE
        else:
            # Eye released / opened
            if self.left_eye_state.is_closed:
                duration = current_time - (self.left_eye_state.close_start_time or current_time)
                frames = self.left_eye_state.closed_frame_count
                self.left_eye_state.is_closed = False
                self.left_eye_state.closed_frame_count = 0

                # Check if this release constitutes a valid single blink
                if (
                    (not is_natural_both_eye_blink)
                    and (not in_cooldown)
                    and (self.blink_min_frames <= frames <= self.blink_max_frames)
                ):
                    time_since_last = current_time - self.left_eye_state.last_blink_release_time
                    self.left_eye_state.last_blink_release_time = current_time

                    if self.pending_left_click and (time_since_last <= self.double_click_window_sec):
                        # Second blink within double-click window -> DOUBLE CLICK!
                        self.pending_left_click = False
                        self.last_action_time = current_time
                        logger.info("Rapid 2nd blink triggered -> DOUBLE_CLICK")
                        return GestureAction.DOUBLE_CLICK
                    else:
                        # First blink -> buffer as pending left click
                        self.pending_left_click = True
                        self.pending_left_click_time = current_time

        # --- RIGHT EYE PROCESSING ---
        if right_closed and not is_natural_both_eye_blink:
            if not self.right_eye_state.is_closed:
                self.right_eye_state.is_closed = True
                self.right_eye_state.close_start_time = current_time
                self.right_eye_state.closed_frame_count = 1
            else:
                self.right_eye_state.closed_frame_count += 1
        else:
            if self.right_eye_state.is_closed:
                duration = current_time - (self.right_eye_state.close_start_time or current_time)
                frames = self.right_eye_state.closed_frame_count
                self.right_eye_state.is_closed = False
                self.right_eye_state.closed_frame_count = 0

                if (
                    (not is_natural_both_eye_blink)
                    and (not in_cooldown)
                    and (self.blink_min_frames <= frames <= self.blink_max_frames)
                ):
                    self.last_action_time = current_time
                    self.pending_left_click = False
                    logger.info("Right eye blink triggered -> RIGHT_CLICK")
                    return GestureAction.RIGHT_CLICK

        # If natural blink occurred, reset both eye open states without firing
        if is_natural_both_eye_blink:
            self.left_eye_state.is_closed = False
            self.left_eye_state.closed_frame_count = 0
            self.right_eye_state.is_closed = False
            self.right_eye_state.closed_frame_count = 0

        return triggered_action
