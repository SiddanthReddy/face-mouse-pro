"""Windows tuple-based compatibility wrappers for shared geometry and filters."""

from __future__ import annotations

import time

from face_mouse_core.config import SmoothingConfig
from face_mouse_core.cursor import ExponentialSmoother
from face_mouse_core.cursor import OneEuroFilter1D as CoreOneEuroFilter1D
from face_mouse_core.gestures.metrics import calculate_ear as _calculate_ear
from face_mouse_core.gestures.metrics import calculate_mar as _calculate_mar
from face_mouse_core.gestures.metrics import euclidean_distance as _euclidean_distance
from face_mouse_core.models import Vector2D


def euclidean_distance(pt1, pt2) -> float:
    return _euclidean_distance(pt1, pt2)


def calculate_ear(eye_landmarks) -> float:
    return _calculate_ear(eye_landmarks)


def calculate_mar(mouth_landmarks) -> float:
    return _calculate_mar(mouth_landmarks)


class ExponentialFilter:
    """Tuple adapter retaining the historic clamped-alpha API."""

    def __init__(self, alpha: float = 0.6):
        self.alpha = max(0.01, min(0.99, alpha))
        self._filter = ExponentialSmoother(self.alpha)
        self.prev_val: tuple[float, float] | None = None

    def update(self, val: tuple[float, float]) -> tuple[float, float]:
        value = self._filter.update(Vector2D(*val))
        self.prev_val = (value.x, value.y)
        return self.prev_val

    def reset(self) -> None:
        self._filter.reset()
        self.prev_val = None


class LowPassFilter:
    """Legacy standalone scalar low-pass utility retained for compatibility."""

    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha
        self.hat_x_prev: float | None = None

    def update(self, x: float, alpha: float | None = None) -> float:
        if alpha is not None:
            self.alpha = alpha
        if self.hat_x_prev is None:
            self.hat_x_prev = x
            return x
        self.hat_x_prev = self.alpha * x + (1.0 - self.alpha) * self.hat_x_prev
        return self.hat_x_prev

    def reset(self) -> None:
        self.hat_x_prev = None


class OneEuroFilter1D:
    """Compatibility wrapper; time acquisition remains in the Windows layer."""

    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.007, d_cutoff: float = 1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self._filter = CoreOneEuroFilter1D(SmoothingConfig(min_cutoff, beta, d_cutoff))
        self.last_time: float | None = None

    def filter(self, x: float, timestamp: float | None = None) -> float:
        if timestamp is None:
            timestamp = time.perf_counter()
        self.last_time = timestamp
        return self._filter.filter(x, timestamp)

    def reset(self) -> None:
        self._filter.reset()
        self.last_time = None


class OneEuroFilter2D:
    """Tuple-based wrapper around the shared 2D One Euro filter."""

    def __init__(self, min_cutoff: float = 1.2, beta: float = 0.05, d_cutoff: float = 1.0):
        config = SmoothingConfig(min_cutoff, beta, d_cutoff)
        self.filter_x = CoreOneEuroFilter1D(config)
        self.filter_y = CoreOneEuroFilter1D(config)

    def filter(self, point: tuple[float, float], timestamp: float | None = None) -> tuple[float, float]:
        if timestamp is None:
            timestamp = time.perf_counter()
        return (self.filter_x.filter(point[0], timestamp), self.filter_y.filter(point[1], timestamp))

    def reset(self) -> None:
        self.filter_x.reset()
        self.filter_y.reset()
