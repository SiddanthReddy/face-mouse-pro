"""Windows calibration state adapter backed by shared pure calculations."""

from typing import Any

from face_mouse_core.calibration import CalibrationAccumulator, relative_offset
from face_mouse_core.models import NormalizedPoint

from src.utils.logger import setup_logger

logger = setup_logger("Calibration")


class CalibrationManager:
    """Preserve the Windows calibration API while delegating its calculations."""

    def __init__(self, neutral_x: float = 0.5, neutral_y: float = 0.5, is_calibrated: bool = False):
        neutral = NormalizedPoint(float(neutral_x), float(neutral_y))
        self.neutral_x = neutral.x
        self.neutral_y = neutral.y
        self.is_calibrated = is_calibrated
        self.sample_target = 10
        self._accumulator = CalibrationAccumulator(self.sample_target)

    @property
    def calibration_samples(self) -> list[tuple[float, float]]:
        return [(point.x, point.y) for point in self._accumulator.samples]

    def calibrate_immediate(self, nose_x: float, nose_y: float) -> tuple[float, float]:
        neutral = NormalizedPoint(float(nose_x), float(nose_y))
        self.neutral_x, self.neutral_y = neutral.x, neutral.y
        self.is_calibrated = True
        logger.info(f"Calibrated immediate neutral position: ({neutral.x:.4f}, {neutral.y:.4f})")
        return (neutral.x, neutral.y)

    def add_sample_and_calibrate(self, nose_x: float, nose_y: float) -> bool:
        point = NormalizedPoint(float(nose_x), float(nose_y))
        result = self._accumulator.add_sample(point)
        if result is None:
            return False
        self.neutral_x, self.neutral_y = result.x, result.y
        self.is_calibrated = True
        logger.info(f"Calibrated averaged neutral position: ({result.x:.4f}, {result.y:.4f})")
        return True

    def reset_calibration(self) -> None:
        self.is_calibrated = False
        self._accumulator.reset()
        logger.info("Calibration reset.")

    def get_relative_offset(
        self, nose_x: float, nose_y: float, deadzone_x: float = 0.008, deadzone_y: float = 0.008
    ) -> tuple[float, float]:
        point = NormalizedPoint(float(nose_x), float(nose_y))
        neutral = NormalizedPoint(self.neutral_x, self.neutral_y) if self.is_calibrated else None
        offset = relative_offset(point, neutral, deadzone_x=deadzone_x, deadzone_y=deadzone_y)
        return (offset.x, offset.y)

    def to_dict(self) -> dict[str, Any]:
        return {"calibrated": self.is_calibrated, "neutral_x": self.neutral_x, "neutral_y": self.neutral_y}
