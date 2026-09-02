"""
Helper functions and mathematical filters for Face Mouse Pro.
Includes Eye Aspect Ratio (EAR), Mouth Aspect Ratio (MAR), Exponential Moving Average (EMA),
and One-Euro Filter for jitter-free cursor tracking.
"""

import math
import time
from collections.abc import Sequence


def euclidean_distance(pt1: Sequence[float], pt2: Sequence[float]) -> float:
    """
    Computes Euclidean distance between two 2D or 3D points.
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(pt1, pt2)))


def calculate_ear(eye_landmarks: Sequence[Sequence[float]]) -> float:
    """
    Calculates Eye Aspect Ratio (EAR) given 6 canonical facial eye landmarks.
    Expected landmark ordering:
    P1 (outer corner), P2 (upper outer), P3 (upper inner),
    P4 (inner corner), P5 (lower inner), P6 (lower outer).

    EAR = (|P2 - P6| + |P3 - P5|) / (2 * |P1 - P4|)
    """
    if len(eye_landmarks) < 6:
        return 0.0

    p1, p2, p3, p4, p5, p6 = eye_landmarks[:6]

    v1 = euclidean_distance(p2, p6)
    v2 = euclidean_distance(p3, p5)
    horiz = euclidean_distance(p1, p4)

    if horiz <= 1e-6:
        return 0.0

    return (v1 + v2) / (2.0 * horiz)


def calculate_mar(mouth_landmarks: Sequence[Sequence[float]]) -> float:
    """
    Calculates Mouth Aspect Ratio (MAR) using key lip landmarks.
    Expected landmark ordering:
    P1 (left corner), P2 (upper lip top), P3 (upper lip inner),
    P4 (right corner), P5 (lower lip inner), P6 (lower lip bottom).

    MAR = (|P2 - P6| + |P3 - P5|) / (2 * |P1 - P4|)
    """
    if len(mouth_landmarks) < 6:
        return 0.0

    p1, p2, p3, p4, p5, p6 = mouth_landmarks[:6]

    v1 = euclidean_distance(p2, p6)
    v2 = euclidean_distance(p3, p5)
    horiz = euclidean_distance(p1, p4)

    if horiz <= 1e-6:
        return 0.0

    return (v1 + v2) / (2.0 * horiz)


class ExponentialFilter:
    """
    Exponential Moving Average (EMA) filter for 2D coordinates.
    """

    def __init__(self, alpha: float = 0.6):
        self.alpha = max(0.01, min(0.99, alpha))
        self.prev_val: tuple[float, float] | None = None

    def update(self, val: tuple[float, float]) -> tuple[float, float]:
        if self.prev_val is None:
            self.prev_val = val
            return val

        filtered_x = self.alpha * val[0] + (1.0 - self.alpha) * self.prev_val[0]
        filtered_y = self.alpha * val[1] + (1.0 - self.alpha) * self.prev_val[1]
        self.prev_val = (filtered_x, filtered_y)
        return self.prev_val

    def reset(self) -> None:
        self.prev_val = None


class LowPassFilter:
    """
    First-order low-pass filter used by OneEuroFilter.
    """

    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha
        self.hat_x_prev: float | None = None

    def update(self, x: float, alpha: float | None = None) -> float:
        if alpha is not None:
            self.alpha = alpha
        if self.hat_x_prev is None:
            self.hat_x_prev = x
            return x
        hat_x = self.alpha * x + (1.0 - self.alpha) * self.hat_x_prev
        self.hat_x_prev = hat_x
        return hat_x

    def reset(self) -> None:
        self.hat_x_prev = None


class OneEuroFilter1D:
    """
    1D One Euro Filter for adaptive smoothing with low latency and jitter reduction.
    """

    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.007, d_cutoff: float = 1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_filter = LowPassFilter()
        self.dx_filter = LowPassFilter()
        self.last_time: float | None = None

    @staticmethod
    def _alpha(rate: float, cutoff: float) -> float:
        tau = 1.0 / (2.0 * math.pi * cutoff)
        te = 1.0 / rate
        return 1.0 / (1.0 + tau / te)

    def filter(self, x: float, timestamp: float | None = None) -> float:
        if timestamp is None:
            timestamp = time.perf_counter()

        if self.last_time is None or self.last_time >= timestamp:
            self.last_time = timestamp
            return self.x_filter.update(x, 1.0)

        dt = timestamp - self.last_time
        self.last_time = timestamp
        rate = 1.0 / max(dt, 1e-5)

        # Estimate derivative
        dx = (x - (self.x_filter.hat_x_prev if self.x_filter.hat_x_prev is not None else x)) * rate
        edx = self.dx_filter.update(dx, self._alpha(rate, self.d_cutoff))

        # Use derivative to compute dynamic cutoff frequency
        cutoff = self.min_cutoff + self.beta * abs(edx)
        return self.x_filter.update(x, self._alpha(rate, cutoff))

    def reset(self) -> None:
        self.x_filter.reset()
        self.dx_filter.reset()
        self.last_time = None


class OneEuroFilter2D:
    """
    2D One Euro Filter for smooth and responsive (x, y) cursor coordinates.
    """

    def __init__(self, min_cutoff: float = 1.2, beta: float = 0.05, d_cutoff: float = 1.0):
        self.filter_x = OneEuroFilter1D(min_cutoff=min_cutoff, beta=beta, d_cutoff=d_cutoff)
        self.filter_y = OneEuroFilter1D(min_cutoff=min_cutoff, beta=beta, d_cutoff=d_cutoff)

    def filter(self, point: tuple[float, float], timestamp: float | None = None) -> tuple[float, float]:
        if timestamp is None:
            timestamp = time.perf_counter()
        fx = self.filter_x.filter(point[0], timestamp)
        fy = self.filter_y.filter(point[1], timestamp)
        return (fx, fy)

    def reset(self) -> None:
        self.filter_x.reset()
        self.filter_y.reset()
