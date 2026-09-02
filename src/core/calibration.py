"""
Calibration module for Face Mouse Pro.
Stores the user's neutral head position and calculates relative motion vectors.
"""

from typing import Any

from src.utils.logger import setup_logger

logger = setup_logger("Calibration")


class CalibrationManager:
    """
    Manages neutral face calibration and relative vector transformations.
    """

    def __init__(self, neutral_x: float = 0.5, neutral_y: float = 0.5, is_calibrated: bool = False):
        self.neutral_x = neutral_x
        self.neutral_y = neutral_y
        self.is_calibrated = is_calibrated
        self.calibration_samples: list = []
        self.sample_target = 10

    def calibrate_immediate(self, nose_x: float, nose_y: float) -> tuple[float, float]:
        """
        Instantly saves the current nose coordinate as the neutral rest position.
        """
        self.neutral_x = float(nose_x)
        self.neutral_y = float(nose_y)
        self.is_calibrated = True
        logger.info(f"Calibrated immediate neutral position: ({self.neutral_x:.4f}, {self.neutral_y:.4f})")
        return (self.neutral_x, self.neutral_y)

    def add_sample_and_calibrate(self, nose_x: float, nose_y: float) -> bool:
        """
        Collects multiple frame samples for smoothed neutral calibration.
        Returns True once calibration finishes.
        """
        self.calibration_samples.append((nose_x, nose_y))
        if len(self.calibration_samples) >= self.sample_target:
            avg_x = sum(p[0] for p in self.calibration_samples) / len(self.calibration_samples)
            avg_y = sum(p[1] for p in self.calibration_samples) / len(self.calibration_samples)
            self.neutral_x = avg_x
            self.neutral_y = avg_y
            self.is_calibrated = True
            self.calibration_samples.clear()
            logger.info(f"Calibrated averaged neutral position: ({self.neutral_x:.4f}, {self.neutral_y:.4f})")
            return True
        return False

    def reset_calibration(self) -> None:
        """
        Resets calibration state to uncalibrated.
        """
        self.is_calibrated = False
        self.calibration_samples.clear()
        logger.info("Calibration reset.")

    def get_relative_offset(
        self, nose_x: float, nose_y: float, deadzone_x: float = 0.008, deadzone_y: float = 0.008
    ) -> tuple[float, float]:
        """
        Computes relative movement vector (dx, dy) from neutral position with deadzone filtering.
        """
        if not self.is_calibrated:
            return (0.0, 0.0)

        raw_dx = nose_x - self.neutral_x
        raw_dy = nose_y - self.neutral_y

        # Apply deadzone for stability at rest
        if abs(raw_dx) < deadzone_x:
            dx = 0.0
        else:
            dx = raw_dx - (deadzone_x if raw_dx > 0 else -deadzone_x)

        if abs(raw_dy) < deadzone_y:
            dy = 0.0
        else:
            dy = raw_dy - (deadzone_y if raw_dy > 0 else -deadzone_y)

        return (dx, dy)

    def to_dict(self) -> dict[str, Any]:
        return {"calibrated": self.is_calibrated, "neutral_x": self.neutral_x, "neutral_y": self.neutral_y}
