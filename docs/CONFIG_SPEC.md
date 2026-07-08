# CONFIG_SPEC.md — Configuration Reference

All tunable values live in `config/config.yaml` at the repo root, loaded once at startup by `src/core/config.py` into a typed, importable object — logic files never read the YAML directly. Logging setup (levels, handlers, format) is configured separately in `config/logging.yaml`, loaded by `src/core/logger.py`; it is deliberately kept out of `config.yaml` since logging setup is infrastructure, not a gameplay/behavior tunable. This document is the reference for every value, its default, its valid range, and which module owns it.

---

## Camera / Capture

| Key | Default | Range | Owner Module |
|---|---|---|---|
| `TARGET_WIDTH` | `960` | 480–1280 | `core/camera.py` |
| `TARGET_HEIGHT` | `540` | 270–720 | `core/camera.py` |
| `CAMERA_DEVICE_INDEX` | `0` | ≥0 | `core/camera.py` |
| `MIRROR_FEED` | `True` | bool | `core/camera.py` |

## Hand Tracking

| Key | Default | Range | Owner Module |
|---|---|---|---|
| `MAX_NUM_HANDS` | `1` | 1–2 | `vision/hand_tracker.py` |
| `TRACK_POINT` | `"wrist"` | `"wrist"` \| `"index_tip"` | `vision/hand_tracker.py` |
| `SMOOTHING_ALPHA` | `0.5` | 0.0–1.0 | `vision/hand_tracker.py` (EMA, see `SDD.md` §9.2) |
| `HAND_LOST_FRAME_THRESHOLD` | `5` | 1–30 | `app/state_machine.py` (frames before `TRACKING → WAITING`) |

## Gesture Detection

| Key | Default | Range | Owner Module |
|---|---|---|---|
| `GESTURE_BUFFER_SIZE` | `25` | 10–60 | `vision/gesture_detector.py` |
| `RADIUS_TOLERANCE` | `0.35` | 0.1–0.6 (coefficient of variation) | `vision/gesture_detector.py` |
| `ANGULAR_COVERAGE_THRESHOLD_DEG` | `300.0` | 180–360 | `vision/gesture_detector.py` |
| `MIN_GESTURE_RADIUS_PX` | `30.0` | 10–100 | `vision/gesture_detector.py` |
| `GESTURE_COOLDOWN_SECONDS` | `4.0` | 1.0–10.0 | `vision/gesture_detector.py` |

## Portal

| Key | Default | Range | Owner Module |
|---|---|---|---|
| `PORTAL_OPEN_DURATION_S` | `0.6` | 0.2–2.0 | `effects/portal_engine.py` |
| `PORTAL_CLOSE_DURATION_S` | `0.5` | 0.2–2.0 | `effects/portal_engine.py` |
| `PORTAL_FRAMES_DIR` | `"assets/portal_frames/"` | valid path | `effects/portal_engine.py` |
| `PORTAL_LOOP_FPS` | `24` | 12–60 | `effects/portal_engine.py` |

## Disappearance

| Key | Default | Range | Owner Module |
|---|---|---|---|
| `FADE_DURATION_S` | `1.2` | 0.5–3.0 | `effects/disappear_engine.py` |
| `ENTER_DEBOUNCE_FRAMES` | `8` | 3–30 | `app/state_machine.py` (§13.4 debounce) |
| `BACKGROUND_CAPTURE_COUNTDOWN_S` | `3` | 0–10 | `app/main.py` (calibration countdown) |

## Performance / Debug

| Key | Default | Range | Owner Module |
|---|---|---|---|
| `DEBUG` | `False` | bool | `ui/hud.py`, `effects/overlay_engine.py` |
| `FPS_WARNING_FLOOR` | `15` | 5–30 | `ui/fps_counter.py` |
| `FPS_WINDOW_SIZE` | `30` | 10–60 | `ui/fps_counter.py` |

---

## Logging (`config/logging.yaml`, separate from the table above)

| Key | Default | Notes |
|---|---|---|
| `root_level` | `"INFO"` | Overridden to `"DEBUG"` when `config.yaml`'s `DEBUG` is `True` |
| `format` | `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"` | Standard, includes module name for traceability |
| `handlers` | `["console"]` | A `"file"` handler writing to `logs/` is a fair v1.1 addition, not required for v1 |

## Rules for Adding a New Config Value

1. It goes in `config/config.yaml` (behavior/tuning) or `config/logging.yaml` (logging infra) — never inline in a logic file (`CODING_STANDARDS.md` §3).
2. It gets a row in the relevant table in this file, in the same change that introduces it (`CODEX_GUIDELINES.md` §9).
3. Give it a valid range even if informally derived — future tuning sessions need to know the boundaries of sane values, not just the default.
4. `src/core/config.py` is the only module that reads `config.yaml` off disk — every other module receives values through it, never opens the YAML itself.
