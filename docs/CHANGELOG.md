# CHANGELOG.md

All notable changes to this project are documented here, one entry per sprint. Format loosely follows [Keep a Changelog](https://keepachangelog.com/): `Added`, `Changed`, `Fixed`, `Known Limitations`.

---

## [Unreleased]

### Added
- Sprint 02 gesture detection is the next planned increment.

---

## v0.1.0 (Sprint 01)

### Features Implemented
- Live OpenCV webcam capture using the configured camera device, target resolution, and mirrored-feed setting.
- MediaPipe Hands integration for one-hand detection.
- Conversion of all 21 normalized MediaPipe landmarks to frame pixel coordinates.
- MediaPipe hand skeleton rendering with all 21 landmarks visible.
- Smoothed wrist/index-tip tracking point support, defaulting to the wrist.
- Highlighted tracked wrist point over the live feed.
- HUD showing `WAITING`/`TRACKING`, FPS, and current tracked coordinates.
- Clean `Q` key shutdown path that releases the camera and destroys OpenCV windows.

### Files Created
- `src/vision/__init__.py`
- `src/vision/hand_tracker.py`
- `src/ui/__init__.py`
- `src/ui/fps_counter.py`
- `src/ui/hud.py`
- `tests/unit/vision/__init__.py`
- `tests/unit/vision/test_hand_tracker.py`

### Files Modified
- `.gitignore`
- `requirements.txt`
- `src/app/main.py`
- `src/core/camera.py`
- `docs/API_SPEC.md`
- `docs/CHANGELOG.md`
- `docs/MASTER_PLAN.md`
- `docs/sprints/SPRINT_01.md`

### Tests Added
- EMA smoothing convergence test for `HandTracker._smooth_point()`.
- Configured track-point selection test for `HandTracker`.

### Bug Fixes
- Replaced the failing custom landmark-rendering path with `mp_drawing.draw_landmarks(...)` so the 21 landmarks and hand skeleton are visible on the same frame passed to `cv2.imshow()`.
- Removed temporary per-frame debug logging used during render-pipeline diagnosis.
- Removed generated Python cache artifacts from the release tree and ignored future cache files.

### Performance Observations
- Manual live run confirmed the FPS HUD updates continuously.
- Manual verification accepted the Sprint 01 target range of approximately 20-30 FPS on the test machine.
- Rendering remains single-threaded, matching ADR-001.

### Manual Verification Completed
- Camera opens successfully.
- Live mirrored webcam feed works.
- FPS counter updates correctly.
- MediaPipe detects one hand.
- All 21 landmarks render.
- Hand skeleton renders.
- Wrist tracking point is highlighted.
- `WAITING` changes to `TRACKING` when a hand is detected.
- `TRACKING` returns to `WAITING` when the hand leaves the frame.
- Pressing `Q` exits cleanly.

### Known Limitations
- Manual webcam verification requires camera hardware and OS camera permission.
- Sprint 01 only visualizes hand tracking; gesture detection begins in Sprint 02.

---

## v0.0.0 (Sprint 00)

### Added
- Project scaffold
- Configuration management
- Centralized logging
- Application bootstrap
- Unit tests for configuration
- Unit tests for logging
- Development tooling (Black, Ruff, Pytest)

### Changed
- Initialized the repository structure and documented the sprint-based implementation plan.

### Fixed
- Hardened configuration validation and startup behavior for the initial scaffold.

### Known Limitations
- Sprint 01 is the next milestone and introduces camera capture and hand tracking.
