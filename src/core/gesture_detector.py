"""Windows compatibility adapter for shared-core gesture detection."""

from __future__ import annotations

import time
from dataclasses import replace
from typing import Any, TypeAlias

from face_mouse_core.config import GestureConfig
from face_mouse_core.gestures import GestureDetector as SharedGestureDetector
from face_mouse_core.gestures import GestureType

# Preserve the application-facing enum import while sharing its action values.
GestureAction: TypeAlias = GestureType


class GestureDetector:
    """Keep the legacy Windows API while delegating all gesture logic to core."""

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
    ) -> None:
        config = GestureConfig(
            blink_ear_threshold=blink_ear_threshold,
            blink_min_frames=blink_min_frames,
            blink_max_frames=blink_max_frames,
            double_click_window_seconds=double_click_window_sec,
            long_blink_duration_seconds=long_blink_duration_sec,
            both_eyes_natural_blink_ratio_diff=both_eyes_natural_blink_ratio_diff,
            mouth_mar_threshold=mouth_mar_threshold,
            mouth_open_min_frames=mouth_open_min_frames,
            click_cooldown_seconds=click_cooldown_sec,
        )
        self._detector = SharedGestureDetector(config)

    def update_parameters(self, config_gestures: dict[str, Any]) -> None:
        """Translate legacy JSON names to core settings without resetting state."""
        fields = {
            "blink_ear_threshold": "blink_ear_threshold",
            "blink_min_frames": "blink_min_frames",
            "blink_max_frames": "blink_max_frames",
            "double_click_window_sec": "double_click_window_seconds",
            "long_blink_duration_sec": "long_blink_duration_seconds",
            "mouth_mar_threshold": "mouth_mar_threshold",
            "click_cooldown_sec": "click_cooldown_seconds",
        }
        changes = {target: config_gestures[source] for source, target in fields.items() if source in config_gestures}
        if changes:
            self._detector.update_config(replace(self._detector.config, **changes))

    def process(
        self,
        left_eye_landmarks,
        right_eye_landmarks,
        mouth_landmarks,
        current_time: float | None = None,
    ) -> GestureAction:
        """Process legacy landmark arguments; time fallback stays in this adapter."""
        timestamp = time.perf_counter() if current_time is None else current_time
        return self._detector.process(
            left_eye_landmarks,
            right_eye_landmarks,
            mouth_landmarks,
            timestamp_seconds=timestamp,
        )

    def reset(self) -> None:
        self._detector.reset()

    @property
    def config(self) -> GestureConfig:
        return self._detector.config

    @property
    def left_eye_state(self):
        return self._detector.left_eye_state

    @property
    def right_eye_state(self):
        return self._detector.right_eye_state

    @property
    def mouth_open_frames(self) -> int:
        return self._detector.mouth_open_frames

    @property
    def is_mouth_open(self) -> bool:
        return self._detector.is_mouth_open

    @property
    def last_action_time(self) -> float:
        return self._detector.last_action_time

    @property
    def pending_left_click(self) -> bool:
        return self._detector.pending_left_click

    @property
    def pending_left_click_time(self) -> float:
        return self._detector.pending_left_click_time

    @property
    def current_left_ear(self) -> float:
        return self._detector.current_left_ear

    @property
    def current_right_ear(self) -> float:
        return self._detector.current_right_ear

    @property
    def current_mar(self) -> float:
        return self._detector.current_mar
