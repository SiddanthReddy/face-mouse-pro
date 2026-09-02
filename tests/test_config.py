"""
Unit tests for ConfigManager.
"""

import os
import tempfile

from src.config.config_manager import ConfigManager


def test_config_load_defaults():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_cfg = os.path.join(tmpdir, "settings.json")
        cfg = ConfigManager(config_path=tmp_cfg)

        assert os.path.exists(tmp_cfg)
        assert cfg.get("camera", "fps") == 30
        assert cfg.get("cursor", "sensitivity_x") == 2.2
        assert cfg.get("gestures", "blink_ear_threshold") == 0.21


def test_config_modify_and_persist():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_cfg = os.path.join(tmpdir, "settings.json")
        cfg = ConfigManager(config_path=tmp_cfg)

        cfg.set("cursor", "sensitivity_x", 3.5, auto_save=True)
        assert cfg.get("cursor", "sensitivity_x") == 3.5

        # Reload from disk
        cfg2 = ConfigManager(config_path=tmp_cfg)
        assert cfg2.get("cursor", "sensitivity_x") == 3.5


def test_config_corrupted_json_recovery():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_cfg = os.path.join(tmpdir, "settings.json")
        with open(tmp_cfg, "w", encoding="utf-8") as f:
            f.write("{invalid_json: true,")

        cfg = ConfigManager(config_path=tmp_cfg)
        assert cfg.get("camera", "width") == 640
