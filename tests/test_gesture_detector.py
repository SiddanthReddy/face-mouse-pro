"""
Unit tests for GestureDetector state machine.
"""

from src.core.gesture_detector import GestureAction, GestureDetector


def get_mock_eye(open_state: bool):
    if open_state:
        return [(0.0, 0.0), (0.2, 0.15), (0.4, 0.15), (0.6, 0.0), (0.4, -0.15), (0.2, -0.15)]
    else:
        return [(0.0, 0.0), (0.2, 0.01), (0.4, 0.01), (0.6, 0.0), (0.4, -0.01), (0.2, -0.01)]


def get_mock_mouth(open_state: bool):
    if open_state:
        return [(0.0, 0.0), (0.3, 0.25), (0.5, 0.25), (0.8, 0.0), (0.5, -0.25), (0.3, -0.25)]
    else:
        return [(0.0, 0.0), (0.3, 0.02), (0.5, 0.02), (0.8, 0.0), (0.5, -0.02), (0.3, -0.02)]


def test_natural_both_eye_blink_suppression():
    """
    Involuntary blinking of both eyes simultaneously must NOT trigger Left or Right clicks.
    """
    detector = GestureDetector(blink_ear_threshold=0.21, blink_min_frames=2, click_cooldown_sec=0.1)

    # 3 frames both eyes closed
    t = 1.0
    for _ in range(3):
        action = detector.process(
            left_eye_landmarks=get_mock_eye(False),
            right_eye_landmarks=get_mock_eye(False),
            mouth_landmarks=get_mock_mouth(False),
            current_time=t,
        )
        assert action == GestureAction.NONE
        t += 0.033

    # Release both eyes
    action = detector.process(
        left_eye_landmarks=get_mock_eye(True),
        right_eye_landmarks=get_mock_eye(True),
        mouth_landmarks=get_mock_mouth(False),
        current_time=t,
    )
    assert action == GestureAction.NONE
    assert not detector.pending_left_click


def test_left_click_gesture():
    """
    Closing left eye for 3 frames, then opening and waiting double_click window triggers Left Click.
    """
    detector = GestureDetector(
        blink_ear_threshold=0.21, blink_min_frames=2, double_click_window_sec=0.20, click_cooldown_sec=0.05
    )

    t = 1.0
    # Left eye closed 3 frames, right eye open
    for _ in range(3):
        action = detector.process(
            left_eye_landmarks=get_mock_eye(False),
            right_eye_landmarks=get_mock_eye(True),
            mouth_landmarks=get_mock_mouth(False),
            current_time=t,
        )
        assert action == GestureAction.NONE
        t += 0.033

    # Left eye opened -> sets pending left click
    action = detector.process(
        left_eye_landmarks=get_mock_eye(True),
        right_eye_landmarks=get_mock_eye(True),
        mouth_landmarks=get_mock_mouth(False),
        current_time=t,
    )
    assert action == GestureAction.NONE
    assert detector.pending_left_click

    # Advance time beyond double_click_window_sec
    t += 0.25
    action = detector.process(
        left_eye_landmarks=get_mock_eye(True),
        right_eye_landmarks=get_mock_eye(True),
        mouth_landmarks=get_mock_mouth(False),
        current_time=t,
    )
    assert action == GestureAction.LEFT_CLICK


def test_double_click_gesture():
    """
    Two rapid blinks of left eye triggers DOUBLE_CLICK.
    """
    detector = GestureDetector(
        blink_ear_threshold=0.21, blink_min_frames=2, double_click_window_sec=0.35, click_cooldown_sec=0.05
    )

    t = 1.0
    # First blink
    for _ in range(3):
        detector.process(get_mock_eye(False), get_mock_eye(True), get_mock_mouth(False), current_time=t)
        t += 0.033
    detector.process(get_mock_eye(True), get_mock_eye(True), get_mock_mouth(False), current_time=t)
    t += 0.05

    # Second blink
    for _ in range(3):
        detector.process(get_mock_eye(False), get_mock_eye(True), get_mock_mouth(False), current_time=t)
        t += 0.033
    action = detector.process(get_mock_eye(True), get_mock_eye(True), get_mock_mouth(False), current_time=t)

    assert action == GestureAction.DOUBLE_CLICK


def test_right_click_gesture():
    """
    Single right eye blink triggers RIGHT_CLICK immediately upon release.
    """
    detector = GestureDetector(blink_ear_threshold=0.21, blink_min_frames=2, click_cooldown_sec=0.05)

    t = 1.0
    for _ in range(3):
        detector.process(get_mock_eye(True), get_mock_eye(False), get_mock_mouth(False), current_time=t)
        t += 0.033
    action = detector.process(get_mock_eye(True), get_mock_eye(True), get_mock_mouth(False), current_time=t)

    assert action == GestureAction.RIGHT_CLICK


def test_long_blink_drag_toggle():
    """
    Holding left eye closed for >= long_blink_duration triggers DRAG_TOGGLE.
    """
    detector = GestureDetector(blink_ear_threshold=0.21, long_blink_duration_sec=0.50, click_cooldown_sec=0.05)

    t = 1.0
    action = GestureAction.NONE
    for _ in range(20):  # 20 * 0.033 = 0.66s > 0.50s
        action = detector.process(get_mock_eye(False), get_mock_eye(True), get_mock_mouth(False), current_time=t)
        if action == GestureAction.DRAG_TOGGLE:
            break
        t += 0.033

    assert action == GestureAction.DRAG_TOGGLE
