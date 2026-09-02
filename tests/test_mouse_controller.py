"""
Unit tests for MouseController bounds and safety logic.
"""

from src.core.mouse_controller import MouseController


def test_mouse_controller_initialization():
    mc = MouseController(sensitivity_x=2.0, sensitivity_y=2.0)
    assert mc.screen_width > 0
    assert mc.screen_height > 0
    assert not mc.is_dragging
    assert not mc.is_paused


def test_mouse_controller_pause_toggle():
    mc = MouseController()
    paused = mc.toggle_pause()
    assert paused
    assert mc.is_paused

    resumed = not mc.toggle_pause()
    assert resumed
    assert not mc.is_paused


def test_mouse_controller_relative_clamping():
    mc = MouseController()
    # Large movement to corner
    tx, ty = mc.move_cursor_relative(10.0, 10.0)
    assert 0 <= tx < mc.screen_width
    assert 0 <= ty < mc.screen_height

    # Large negative movement
    tx, ty = mc.move_cursor_relative(-20.0, -20.0)
    assert 0 <= tx < mc.screen_width
    assert 0 <= ty < mc.screen_height
