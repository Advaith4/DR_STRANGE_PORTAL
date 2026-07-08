from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from src.core.config import load_config

REPO_ROOT = Path(__file__).resolve().parents[2]
LOGGING_CONFIG_PATH = REPO_ROOT / "config" / "logging.yaml"


def initialize_logging() -> None:
    """Initialize the root logger from config/logging.yaml and the app config."""

    logging_config = _load_logging_config()
    config = load_config()
    level_name = (
        "DEBUG"
        if config.debug
        else str(logging_config.get("root_level", "INFO")).upper()
    )
    level = getattr(logging, level_name, logging.INFO)
    formatter = logging.Formatter(str(logging_config.get("format", "%(message)s")))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.propagate = False

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(level)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger configured from config/logging.yaml."""

    initialize_logging()
    logger = logging.getLogger(name)
    logger.setLevel(logging.getLogger().level)
    logger.propagate = False
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(logging.getLogger().handlers[0].formatter)
    handler.setLevel(logging.getLogger().level)
    logger.addHandler(handler)
    return logger


def _load_logging_config() -> dict[str, Any]:
    if not LOGGING_CONFIG_PATH.exists():
        raise FileNotFoundError(f"Logging config not found: {LOGGING_CONFIG_PATH}")

    values: dict[str, Any] = {}
    for raw_line in LOGGING_CONFIG_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        values[key.strip()] = _parse_scalar(raw_value.strip())
    return values


def _parse_scalar(value: str) -> Any:
    if value.startswith(("'", '"')):
        return value[1:-1]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.startswith("[") and value.endswith("]"):
        return [
            item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()
        ]
    return value
