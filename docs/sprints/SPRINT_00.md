# SPRINT_00.md — Repo Scaffold & Configuration

## Objective

Stand up the full repository skeleton, dependency management, and configuration loading — with **zero computer-vision logic**. By the end of this sprint, the app should be able to boot, load config, log a message, and exit cleanly. No camera, no MediaPipe, no portal.

This sprint exists precisely so that every later sprint can assume "config loads, logging works, the package layout exists" rather than re-deriving it.

## Prerequisite Reading

- `SDD.md` §4 (Architecture), §6 (Folder Structure)
- `API_SPEC.md` — `core/config.py`, `core/logger.py`, `core/frame_context.py`
- `CONFIG_SPEC.md` — full file
- `CODING_STANDARDS.md`, `CODEX_GUIDELINES.md` — full files (first sprint, read in full; later sprints can skim)

## Architecture Changes

None — this sprint *creates* the architecture skeleton, it doesn't change anything (there's nothing yet to change).

## Files Created

```
requirements.txt
requirements-dev.txt
.gitignore
README.md                      # placeholder: project name, one-paragraph description, "under construction"
config/config.yaml              # all keys from CONFIG_SPEC.md, defaults from that table
config/logging.yaml
src/__init__.py
src/core/__init__.py
src/core/config.py
src/core/logger.py
src/core/frame_context.py
src/app/__init__.py
src/app/main.py                 # boots config + logger, logs "Startup OK", exits
src/utils.py                    # distance(), ema(), unwrap_angle_delta() per API_SPEC.md — implemented and tested even though nothing calls them yet
tests/__init__.py
tests/unit/__init__.py
tests/unit/test_utils.py
tests/data/__init__.py
```

## Files Modified

None (nothing exists yet).

## Acceptance Criteria

- [ ] `pip install -r requirements-dev.txt` succeeds in a clean virtualenv.
- [ ] Every key in `CONFIG_SPEC.md`'s tables exists in `config/config.yaml` with the documented default.
- [ ] `src/core/config.py` loads `config/config.yaml` once and exposes typed values (per `API_SPEC.md`); no other file reads YAML directly.
- [ ] `src/core/logger.py`'s `get_logger(__name__)` produces correctly formatted, correctly leveled log output per `config/logging.yaml`.
- [ ] `python -m src.app.main` runs, logs `"Startup OK"` at `INFO` level, and exits with code 0.
- [ ] `utils.py`'s three functions (`distance`, `ema`, `unwrap_angle_delta`) are implemented and unit-tested — these are the only pieces of "real" logic in this sprint, and every later sprint depends on them being correct now.
- [ ] No file exceeds 300 lines (`CODING_STANDARDS.md` §1).

## Prototype (Expected Output)

```
$ python -m src.app.main
2026-07-07 10:00:00 [INFO] src.app.main: Startup OK
```

No visual/webcam output yet — this sprint is infrastructure only.

## Testing

- `tests/unit/test_utils.py`: known input/output pairs for `distance()` (e.g. (0,0)→(3,4) = 5.0), `ema()` (verify the exact formula, α=0 returns previous, α=1 returns new), `unwrap_angle_delta()` (verify correct handling of the −π/π wraparound case explicitly, since this is the one non-obvious case − SDD §9.4(c)).
- No integration tests yet (nothing to integrate).

## Git Commit

```
Sprint 00: scaffold repo, config loading, logging, core utils
```

## Review Checklist

- [ ] `MASTER_PLAN.md` Current Status table updated (Sprint 00 complete, Sprint 01 next).
- [ ] `CHANGELOG.md` `[Unreleased]` → new `[v0.0] — Sprint 00` entry.
- [ ] No `ARCHITECTURE_DECISIONS.md` entry expected this sprint (no new design decisions — pure scaffolding of already-decided architecture). If any config default was changed from `CONFIG_SPEC.md`'s table during implementation, that change must be reflected back into `CONFIG_SPEC.md` in this same commit.
- [ ] Confirm `requirements.txt` pins versions (not just bare package names) for reproducibility.
