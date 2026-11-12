"""Mocked checks for the core-to-PyAutoGUI cursor adapter."""

import sys
from types import ModuleType

import pytest


class FakePyAutoGUI(ModuleType):
    class FailSafeException(Exception):
        pass

    def __init__(self):
        super().__init__("pyautogui")
        self.moves = []
        self.FAILSAFE = False
        self.PAUSE = None

    def size(self):
        return (100, 80)

    def moveTo(self, x, y):
        self.moves.append((x, y))

    def click(self, **kwargs):
        pass

    def doubleClick(self, **kwargs):
        pass

    def mouseDown(self, **kwargs):
        pass

    def mouseUp(self, **kwargs):
        pass

    def scroll(self, amount):
        pass


@pytest.fixture
def controller(monkeypatch):
    fake = FakePyAutoGUI()
    monkeypatch.setitem(sys.modules, "pyautogui", fake)
    sys.modules.pop("src.core.mouse_controller", None)
    from src.core.mouse_controller import MouseController

    instance = MouseController()
    yield instance, fake
    sys.modules.pop("src.core.mouse_controller", None)


def test_mapping_then_pixel_scale_and_dispatch_remain_in_host_adapter(controller):
    instance, fake = controller
    x, y = instance.move_cursor_relative(0.1, -0.1, current_time=10.0)
    assert (x, y) == (63, 29)
    assert fake.moves == [(63, 29)]
    assert instance.screen_width == 100
    assert instance.screen_height == 80


def test_pixel_boundary_clamp_remains_in_host_adapter(controller):
    instance, _ = controller
    x, y = instance.move_cursor_relative(100.0, 100.0, current_time=10.0)
    assert x == 96
    assert y == 76
