# SPRINT_01.md — Camera & Hand Tracking

## Objective

Get a live, mirrored webcam feed on screen, with MediaPipe Hands detecting one hand and drawing its 21-landmark skeleton as a debug overlay. This is Prototype v0.1 — the first sprint that produces something visible.

## Prerequisite Reading

- `SDD.md` §5.1–5.2 (Camera, Hand Tracker responsibilities), §8 (MediaPipe Landmark Details), §14 (Performance Targets)
- `API_SPEC.md` — `core/camera.py`, `vision/hand_tracker.py`
- `CONFIG_SPEC.md` — Camera + Hand Tracking sections
- `ARCHITECTURE_DECISIONS.md` — ADR-003 (wrist vs. index tip)

## Architecture Changes

None — implements existing contracts from `API_SPEC.md` as written.

## Files Created

```
src/core/camera.py
src/vision/__init__.py
src/vision/hand_tracker.py
src/ui/__init__.py
src/ui/fps_counter.py
src/ui/hud.py                   # minimal version: state name + FPS text only, debug skeleton draw
tests/unit/vision/__init__.py
tests/unit/vision/test_hand_tracker.py   # tests EMA smoothing logic in isolation, not live MediaPipe output
```

## Files Modified

```
src/app/main.py                 # now opens Camera, runs HandTracker per frame, shows the window, handles quit-key
```

## Acceptance Criteria

- [ ] Webcam feed displays at `TARGET_WIDTH`×`TARGET_HEIGHT`, mirrored (`MIRROR_FEED=True`), per `CONFIG_SPEC.md`.
- [ ] `FpsCounter` reports live FPS in the HUD; sustained FPS is 20–30 on a standard laptop webcam per `SDD.md` §14.1.
- [ ] With `DEBUG=True`, all 21 hand landmarks draw correctly when a hand is in frame.
- [ ] `HandTracker.process()` returns `detected=False` cleanly (no crash, no stale landmarks) when no hand is present.
- [ ] The configured `TRACK_POINT` (default `"wrist"`) is visibly the smoothed point used for downstream logic — verify by drawing it as a distinct highlighted dot, separate from the raw landmark skeleton, so smoothing is visually confirmable (raw jitter vs. smoothed stability).
- [ ] Pressing a quit key (e.g. `q`) exits cleanly, releasing the camera (`Camera.release()`).

## Prototype (Expected Output)

A window titled with the app name showing: live mirrored video, a green hand skeleton overlay when a hand is visible, a highlighted dot at the tracked point (wrist by default), and a small HUD text block showing `STATE: TRACKING` (or `WAITING` with no hand) and `FPS: NN`.

## Testing

- `tests/unit/vision/test_hand_tracker.py`: cannot unit-test MediaPipe's actual detection (that requires a live camera/real image), but **can and must** unit-test the EMA smoothing step in isolation — feed a synthetic sequence of noisy raw points, assert the smoothed output converges and doesn't overshoot, independent of MediaPipe.
- Manual: verify the hand-lost case (move hand out of frame) doesn't crash and cleanly reports `detected=False`.

## Git Commit

```
Sprint 01: camera capture, MediaPipe hand tracking, debug skeleton HUD — Prototype v0.1
```

## Review Checklist

- [ ] `MASTER_PLAN.md` Current Status → Sprint 01 complete, Prototype v0.1, Sprint 02 next.
- [ ] `CHANGELOG.md` → `[v0.1] — Sprint 01` entry.
- [ ] If the wrist-vs-index-tip default changed based on how it actually felt live, update ADR-003 in `ARCHITECTURE_DECISIONS.md` with the real observation, and update `TRACK_POINT`'s default in `CONFIG_SPEC.md` to match.
- [ ] Confirm actual measured FPS against the §14.1 target; if it's below 20 FPS on a real machine, flag it now — don't silently carry a performance problem forward into sprints that assume this floor.
