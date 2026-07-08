from __future__ import annotations

import ast
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "config.yaml"


class ConfigError(ValueError):
    """Raised when configuration is missing, invalid, or out of range."""


@dataclass(frozen=True)
class AppConfig:
    """Typed configuration values loaded from config/config.yaml."""

    target_width: int
    target_height: int
    camera_device_index: int
    mirror_feed: bool
    max_num_hands: int
    track_point: str
    smoothing_alpha: float
    hand_lost_frame_threshold: int
    gesture_buffer_size: int
    radius_tolerance: float
    angular_coverage_threshold_deg: float
    min_gesture_radius_px: float
    gesture_cooldown_seconds: float
    portal_open_duration_s: float
    portal_close_duration_s: float
    portal_frames_dir: str
    portal_loop_fps: int
    fade_duration_s: float
    enter_debounce_frames: int
    background_capture_countdown_s: int
    debug: bool
    fps_warning_floor: int
    fps_window_size: int


@lru_cache(maxsize=1)
def load_config(config_path: Path | None = None) -> AppConfig:
    """Load and validate configuration from config/config.yaml exactly once."""

    path = config_path or CONFIG_PATH
    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path}")

    raw_values = _parse_simple_yaml(path)
    return _build_config(raw_values)


def _build_config(values: dict[str, Any]) -> AppConfig:
    try:
        return AppConfig(
            target_width=_require_int(values, "TARGET_WIDTH", 480, 1280),
            target_height=_require_int(values, "TARGET_HEIGHT", 270, 720),
            camera_device_index=_require_int(values, "CAMERA_DEVICE_INDEX", 0, None),
            mirror_feed=_require_bool(values, "MIRROR_FEED"),
            max_num_hands=_require_int(values, "MAX_NUM_HANDS", 1, 2),
            track_point=_require_choice(values, "TRACK_POINT", {"wrist", "index_tip"}),
            smoothing_alpha=_require_float(values, "SMOOTHING_ALPHA", 0.0, 1.0),
            hand_lost_frame_threshold=_require_int(
                values, "HAND_LOST_FRAME_THRESHOLD", 1, 30
            ),
            gesture_buffer_size=_require_int(values, "GESTURE_BUFFER_SIZE", 10, 60),
            radius_tolerance=_require_float(values, "RADIUS_TOLERANCE", 0.1, 0.6),
            angular_coverage_threshold_deg=_require_float(
                values, "ANGULAR_COVERAGE_THRESHOLD_DEG", 180.0, 360.0
            ),
            min_gesture_radius_px=_require_float(
                values, "MIN_GESTURE_RADIUS_PX", 10.0, 100.0
            ),
            gesture_cooldown_seconds=_require_float(
                values, "GESTURE_COOLDOWN_SECONDS", 1.0, 10.0
            ),
            portal_open_duration_s=_require_float(
                values, "PORTAL_OPEN_DURATION_S", 0.2, 2.0
            ),
            portal_close_duration_s=_require_float(
                values, "PORTAL_CLOSE_DURATION_S", 0.2, 2.0
            ),
            portal_frames_dir=_require_string(values, "PORTAL_FRAMES_DIR"),
            portal_loop_fps=_require_int(values, "PORTAL_LOOP_FPS", 12, 60),
            fade_duration_s=_require_float(values, "FADE_DURATION_S", 0.5, 3.0),
            enter_debounce_frames=_require_int(values, "ENTER_DEBOUNCE_FRAMES", 3, 30),
            background_capture_countdown_s=_require_int(
                values, "BACKGROUND_CAPTURE_COUNTDOWN_S", 0, 10
            ),
            debug=_require_bool(values, "DEBUG"),
            fps_warning_floor=_require_int(values, "FPS_WARNING_FLOOR", 5, 30),
            fps_window_size=_require_int(values, "FPS_WINDOW_SIZE", 10, 60),
        )
    except KeyError as exc:
        raise ConfigError(f"Missing required configuration key: {exc}") from exc


def _require_int(
    values: dict[str, Any], key: str, minimum: int | None, maximum: int | None
) -> int:
    value = _require_value(values, key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ConfigError(f"Configuration key {key} must be an integer")
    if minimum is not None and value < minimum:
        raise ConfigError(f"Configuration key {key} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise ConfigError(f"Configuration key {key} must be <= {maximum}")
    return value


def _require_float(
    values: dict[str, Any], key: str, minimum: float | None, maximum: float | None
) -> float:
    value = _require_value(values, key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ConfigError(f"Configuration key {key} must be numeric")
    numeric_value = float(value)
    if minimum is not None and numeric_value < minimum:
        raise ConfigError(f"Configuration key {key} must be >= {minimum}")
    if maximum is not None and numeric_value > maximum:
        raise ConfigError(f"Configuration key {key} must be <= {maximum}")
    return numeric_value


def _require_bool(values: dict[str, Any], key: str) -> bool:
    value = _require_value(values, key)
    if not isinstance(value, bool):
        raise ConfigError(f"Configuration key {key} must be a boolean")
    return value


def _require_string(values: dict[str, Any], key: str) -> str:
    value = _require_value(values, key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"Configuration key {key} must be a non-empty string")
    return value


def _require_choice(values: dict[str, Any], key: str, choices: set[str]) -> str:
    value = _require_string(values, key)
    if value not in choices:
        raise ConfigError(f"Configuration key {key} must be one of {sorted(choices)}")
    return value


def _require_value(values: dict[str, Any], key: str) -> Any:
    if key not in values:
        raise KeyError(key)
    return values[key]


def _parse_simple_yaml(path: Path) -> dict[str, Any]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Unable to read configuration file: {path}") from exc

    data: dict[str, Any] = {}
    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ConfigError(
                f"Malformed configuration line {line_number}: expected 'key: value'"
            )
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise ConfigError(
                f"Malformed configuration line {line_number}: missing key"
            )
        value = raw_value.strip()
        if not value:
            raise ConfigError(
                f"Malformed configuration line {line_number}: missing value for {key}"
            )
        data[key.upper()] = _parse_scalar(value, line_number)
    return data


def _parse_scalar(value: str, line_number: int) -> Any:
    if value.startswith(("'", '"')):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise ConfigError(
                f"Malformed configuration line {line_number}: invalid string literal"
            ) from exc
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.startswith("[") and value.endswith("]"):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise ConfigError(
                f"Malformed configuration line {line_number}: invalid list literal"
            ) from exc
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)
    try:
        return float(value)
    except ValueError as exc:
        raise ConfigError(
            f"Malformed configuration line {line_number}: unsupported value {value!r}"
        ) from exc
