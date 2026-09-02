"""
Unit tests for CalibrationManager.
"""

import pytest

from src.core.calibration import CalibrationManager


def test_calibration_uncalibrated_behavior():
    calib = CalibrationManager(is_calibrated=False)
    assert not calib.is_calibrated
    dx, dy = calib.get_relative_offset(0.6, 0.7)
    assert dx == 0.0
    assert dy == 0.0


def test_calibration_immediate():
    calib = CalibrationManager(is_calibrated=False)
    calib.calibrate_immediate(0.52, 0.48)
    assert calib.is_calibrated
    assert calib.neutral_x == pytest.approx(0.52)
    assert calib.neutral_y == pytest.approx(0.48)

    # Offset within deadzone
    dx, dy = calib.get_relative_offset(0.524, 0.484, deadzone_x=0.01, deadzone_y=0.01)
    assert dx == 0.0
    assert dy == 0.0

    # Offset outside deadzone
    dx, dy = calib.get_relative_offset(0.56, 0.52, deadzone_x=0.01, deadzone_y=0.01)
    assert dx == pytest.approx(0.03)
    assert dy == pytest.approx(0.03)


def test_calibration_multi_sample():
    calib = CalibrationManager(is_calibrated=False)
    for _ in range(9):
        finished = calib.add_sample_and_calibrate(0.50, 0.50)
        assert not finished

    finished = calib.add_sample_and_calibrate(0.50, 0.50)
    assert finished
    assert calib.is_calibrated
    assert calib.neutral_x == pytest.approx(0.50)
