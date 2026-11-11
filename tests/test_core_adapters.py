"""Regression tests for the Windows compatibility adapters."""

import pytest

from src.core.calibration import CalibrationManager
from src.core.gesture_detector import GestureAction, GestureDetector
from src.utils.helpers import OneEuroFilter2D, calculate_ear, calculate_mar


def eye(open_state):
    h = 0.15 if open_state else 0.01
    return [(0.0, 0.0), (0.2, h), (0.4, h), (0.6, 0.0), (0.4, -h), (0.2, -h)]


def mouth(open_state):
    h = 0.25 if open_state else 0.02
    return [(0.0, 0.0), (0.3, h), (0.5, h), (0.8, 0.0), (0.5, -h), (0.3, -h)]


def test_windows_gesture_adapter_preserves_delayed_left_click_and_event_enum():
    detector = GestureDetector(blink_min_frames=2, double_click_window_sec=0.2, click_cooldown_sec=0.05)
    for now in (1.0, 1.033, 1.066):
        assert detector.process(eye(False), eye(True), mouth(False), current_time=now) is GestureAction.NONE
    assert detector.process(eye(True), eye(True), mouth(False), current_time=1.099) is GestureAction.NONE
    assert detector.pending_left_click
    assert detector.process(eye(True), eye(True), mouth(False), current_time=1.30) is GestureAction.LEFT_CLICK


def test_windows_gesture_adapter_maps_json_cap_and_live_parameters():
    detector = GestureDetector(blink_max_frames=12)
    assert detector.config.blink_max_frames == 12
    detector.update_parameters({"blink_max_frames": 14, "mouth_open_min_frames": 8})
    assert detector.config.blink_max_frames == 14
    # Legacy update_parameters did not update this value; keep that behavior.
    assert detector.config.mouth_open_min_frames == 3


def test_windows_gesture_settings_update_other_runtime_fields_without_resetting_state():
    detector = GestureDetector(blink_min_frames=2)
    detector.process(eye(False), eye(True), mouth(False), current_time=2.0)
    assert detector.left_eye_state.is_closed

    detector.update_parameters(
        {
            "blink_min_frames": 3,
            "double_click_window_sec": 0.4,
            "long_blink_duration_sec": 0.8,
            "click_cooldown_sec": 0.2,
        }
    )

    assert detector.config.blink_min_frames == 3
    assert detector.config.double_click_window_seconds == 0.4
    assert detector.config.long_blink_duration_seconds == 0.8
    assert detector.config.click_cooldown_seconds == 0.2
    assert detector.left_eye_state.is_closed


def test_windows_gesture_adapter_ignores_malformed_landmarks_without_state_change():
    detector = GestureDetector()
    assert detector.process(eye(False), eye(True), mouth(False), current_time=1.0) is GestureAction.NONE
    closed_frames = detector.left_eye_state.closed_frame_count

    assert detector.process([(0.1, 0.2)], eye(True), mouth(False), current_time=1.033) is GestureAction.NONE
    assert detector._detector.last_input_valid is False
    assert detector.left_eye_state.is_closed
    assert detector.left_eye_state.closed_frame_count == closed_frames


def test_windows_gesture_adapter_rejects_backward_timestamps():
    detector = GestureDetector()
    detector.process(eye(True), eye(True), mouth(False), current_time=2.0)

    with pytest.raises(ValueError, match="monotonic"):
        detector.process(eye(True), eye(True), mouth(False), current_time=1.9)


def test_gesture_threshold_comparisons_remain_strict_at_boundary():
    detector = GestureDetector(blink_ear_threshold=0.5, mouth_mar_threshold=0.625)

    detector.process(eye(True), eye(True), mouth(True), current_time=1.0)

    assert detector.current_left_ear == pytest.approx(0.5)
    assert detector.current_mar == pytest.approx(0.625)
    assert not detector.left_eye_state.is_closed
    assert detector.mouth_open_frames == 0
    assert not detector.is_mouth_open


def test_windows_calibration_adapter_delegates_mean_and_deadzone():
    calibration = CalibrationManager(is_calibrated=False)
    for i in range(9):
        assert not calibration.add_sample_and_calibrate(0.50, 0.50 + i * 0.01)
    assert calibration.add_sample_and_calibrate(0.50, 0.59)
    assert calibration.is_calibrated
    assert calibration.neutral_y == pytest.approx(0.545)
    dx, dy = calibration.get_relative_offset(0.56, 0.60, deadzone_x=0.01, deadzone_y=0.01)
    assert dx == pytest.approx(0.05)
    assert dy == pytest.approx(0.045)
    calibration.reset_calibration()
    assert calibration.calibration_samples == []


def test_windows_geometry_wrappers_delegate_to_core_metrics():
    assert calculate_ear(eye(True)) == pytest.approx(0.5)
    assert calculate_mar(mouth(True)) == pytest.approx(0.625)


def test_windows_filter_wrapper_retains_tuple_api_with_explicit_time():
    filter_2d = OneEuroFilter2D(min_cutoff=1.0, beta=0.01)
    assert filter_2d.filter((10.0, 20.0), timestamp=3.0) == (10.0, 20.0)
    x, y = filter_2d.filter((15.0, 25.0), timestamp=3.033)
    assert 10.0 < x < 15.0
    assert 20.0 < y < 25.0
