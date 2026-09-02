"""
Configuration Manager for Face Mouse Pro.
Loads, validates, and persists user settings in JSON format.
"""

import json
import os
from typing import Any

from src.utils.logger import setup_logger

logger = setup_logger("ConfigManager")

DEFAULT_SETTINGS: dict[str, Any] = {
    "camera": {"device_index": 0, "width": 640, "height": 480, "fps": 30},
    "cursor": {
        "sensitivity_x": 2.2,
        "sensitivity_y": 2.0,
        "smoothing_factor": 0.65,
        "deadzone_x": 0.008,
        "deadzone_y": 0.008,
        "acceleration_curve": 1.2,
        "invert_x": False,
        "invert_y": False,
    },
    "gestures": {
        "blink_ear_threshold": 0.21,
        "blink_min_frames": 2,
        "blink_max_frames": 14,
        "double_click_window_sec": 0.40,
        "long_blink_duration_sec": 0.80,
        "both_eyes_natural_blink_ratio_diff": 0.05,
        "mouth_mar_threshold": 0.45,
        "mouth_open_min_frames": 3,
        "click_cooldown_sec": 0.35,
    },
    "scroll": {"scroll_speed": 30, "scroll_deadzone_y": 0.02, "scroll_cooldown_sec": 0.08},
    "calibration": {"calibrated": False, "neutral_x": 0.5, "neutral_y": 0.5},
    "ui": {"show_landmarks": True, "show_meters": True, "show_fps": True, "theme": "cyan"},
}


class ConfigManager:
    """
    Manages loading, updating, and persisting configuration settings.
    """

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self.config_path = os.path.join(root_dir, "config", "settings.json")
        else:
            self.config_path = config_path

        self.settings: dict[str, Any] = self._deep_copy(DEFAULT_SETTINGS)
        self.load()

    @staticmethod
    def _deep_copy(data: dict[str, Any]) -> dict[str, Any]:
        return json.loads(json.dumps(data))

    def _merge_defaults(self, target: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
        """
        Recursively merges loaded settings with defaults to guarantee all required keys exist.
        """
        for k, v in source.items():
            if k not in target:
                target[k] = v
            elif isinstance(v, dict) and isinstance(target.get(k), dict):
                target[k] = self._merge_defaults(target[k], v)
        return target

    def load(self) -> dict[str, Any]:
        """
        Loads configuration from disk. Falls back to defaults if missing or corrupted.
        """
        if not os.path.exists(self.config_path):
            logger.info(f"Config file not found at {self.config_path}. Creating default configuration.")
            self.settings = self._deep_copy(DEFAULT_SETTINGS)
            self.save()
            return self.settings

        try:
            with open(self.config_path, encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.settings = self._merge_defaults(loaded, DEFAULT_SETTINGS)
                else:
                    logger.warning("Invalid configuration structure in JSON. Reverting to defaults.")
                    self.settings = self._deep_copy(DEFAULT_SETTINGS)
            logger.info("Configuration successfully loaded.")
        except Exception as e:
            logger.error(f"Error loading configuration from {self.config_path}: {e}. Using defaults.")
            self.settings = self._deep_copy(DEFAULT_SETTINGS)
            self.save()

        return self.settings

    def save(self) -> bool:
        """
        Persists current settings to the JSON config file.
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            logger.info(f"Configuration successfully saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration to {self.config_path}: {e}")
            return False

    def get(self, section: str, key: str | None = None, default: Any = None) -> Any:
        """
        Retrieves a section or specific key from settings.
        """
        sec = self.settings.get(section, {})
        if key is None:
            return sec
        if isinstance(sec, dict):
            return sec.get(key, default)
        return default

    def set(self, section: str, key: str, value: Any, auto_save: bool = True) -> None:
        """
        Updates a setting value and optionally saves to disk.
        """
        if section not in self.settings or not isinstance(self.settings[section], dict):
            self.settings[section] = {}
        self.settings[section][key] = value
        if auto_save:
            self.save()

    def reset_to_defaults(self) -> None:
        """
        Resets settings back to original factory defaults and saves.
        """
        self.settings = self._deep_copy(DEFAULT_SETTINGS)
        self.save()
        logger.info("Configuration reset to factory defaults.")
