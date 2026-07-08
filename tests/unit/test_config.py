import importlib
from pathlib import Path

import pytest

from src.core.config import AppConfig, ConfigError, load_config


def test_load_config_returns_expected_defaults() -> None:
    config = load_config()

    assert isinstance(config, AppConfig)
    assert config.target_width == 960
    assert config.target_height == 540
    assert config.camera_device_index == 0
    assert config.mirror_feed is True
    assert config.debug is False


def test_invalid_config_raises_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_module = importlib.import_module("src.core.config")
    invalid_path = tmp_path / "config.yaml"
    invalid_path.write_text("TARGET_WIDTH: 2000\n", encoding="utf-8")

    monkeypatch.setattr(config_module, "CONFIG_PATH", invalid_path)
    config_module.load_config.cache_clear()

    with pytest.raises(ConfigError):
        config_module.load_config()
