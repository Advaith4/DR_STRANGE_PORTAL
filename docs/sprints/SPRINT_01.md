# SPRINT_01.md — Camera & Hand Tracking

## Objective

Get a live, mirrored webcam feed on screen, with MediaPipe Hands detecting one hand and drawing its 21-landmark skeleton as a debug overlay. This is Prototype v0.1 — the first sprint that produces something visible.

## Status

COMPLETE — manually verified on 2026-07-08.

## Prerequisite Reading

- `SDD.md` §5.1–5.2 (Camera, Hand Tracker responsibilities), §8 (MediaPipe Landmark Details), §14 (Performance Targets)
- `API_SPEC.md` — `core/camera.py`, `vision/hand_tracker.py`
- `CONFIG_SPEC.md` — Camera + Hand Tracking sections
- `ARCHITECTURE_DECISIONS.md` — ADR-003 (wrist vs. index tip)

## Architecture Changes

None — implements the existing single-threaded frame-loop architecture and MediaPipe wrist-tracking decision.

## Files Created

```
src/vision/__init__.py
src/vision/hand_tracker.py
src/ui/__init__.py
src/ui/fps_counter.py
src/ui/hud.py
tests/unit/vision/__init__.py
tests/unit/vision/test_hand_tracker.py
```

## Files Modified

```
.gitignore
requirements.txt
src/app/main.py
src/core/camera.py
docs/API_SPEC.md
docs/CHANGELOG.md
docs/MASTER_PLAN.md
docs/sprints/SPRINT_01.md
```

## Acceptance Criteria

- [x] Webcam feed displays at `TARGET_WIDTH`×`TARGET_HEIGHT`, mirrored (`MIRROR_FEED=True`), per `CONFIG_SPEC.md`.
- [x] `FpsCounter` reports live FPS in the HUD; sustained FPS is approximately 20-30 on the verified laptop webcam per `SDD.md` §14.1.
- [x] With `DEBUG=True`, all 21 hand landmarks draw correctly when a hand is in frame.
- [x] `HandTracker.process()` returns `detected=False` cleanly (no crash, no stale landmarks) when no hand is present.
- [x] The configured `TRACK_POINT` (default `"wrist"`) is visibly the smoothed point used for downstream logic, drawn as a distinct highlighted dot separate from the raw landmark skeleton.
- [x] Pressing a quit key (`q`) exits cleanly, releasing the camera (`Camera.release()`).

## Prototype Output

A window titled with the app name shows a live mirrored video feed, a green/yellow MediaPipe hand skeleton overlay when a hand is visible, a highlighted dot at the tracked point (wrist by default), and a small HUD text block showing `STATE: TRACKING` or `WAITING`, `FPS: NN`, and current tracked coordinates.

## Actual Implementation Summary

- `Camera` owns `cv2.VideoCapture`, applies configured resizing, and mirrors frames before MediaPipe processing.
- `HandTracker` wraps MediaPipe Hands, converts normalized landmarks to pixel coordinates, and applies EMA smoothing to the configured track point.
- `main.py` processes one frame at a time, draws the MediaPipe skeleton before `cv2.imshow()`, then draws the highlighted tracked wrist point and HUD on the same frame.
- `HUD` renders state, FPS, and track coordinates.
- `FpsCounter` reports a rolling-average FPS from frame timing.

## Manual Verification Results

- [x] Camera opens successfully.
- [x] Live mirrored webcam feed works.
- [x] FPS counter updates correctly.
- [x] MediaPipe detects one hand.
- [x] All 21 landmarks are rendered.
- [x] Hand skeleton is rendered.
- [x] Wrist tracking point is highlighted.
- [x] `WAITING` changes to `TRACKING`.
- [x] `TRACKING` returns to `WAITING` when the hand leaves the frame.
- [x] Pressing `Q` exits cleanly.

## Performance Measurements

- Manual live verification confirmed continuous FPS updates in the HUD.
- Sustained live performance was accepted against the Sprint 01 target range of approximately 20-30 FPS.
- No performance regression was observed from the skeleton and wrist-highlight rendering path.

## Testing

- `tests/unit/vision/test_hand_tracker.py` verifies EMA smoothing convergence without overshoot.
- `tests/unit/vision/test_hand_tracker.py` verifies the configured tracking point is honored.
- Full suite passed with `python -m pytest`.

## Lessons Learned

- MediaPipe detection and rendering should be verified as separate stages; valid landmarks do not prove the displayed frame has been annotated.
- The skeleton must be drawn before `cv2.imshow()` on the same frame object that is displayed.
- Mirroring before MediaPipe processing keeps displayed landmarks aligned with the user's mirror-view expectations.

## Review Notes

- Temporary per-frame debug logging used during render-pipeline diagnosis was removed.
- Generated Python cache artifacts were removed and ignored.
- No configuration defaults changed.
- No new architecture decision was required.

## Git Commit

```
feat(sprint-01): complete MediaPipe hand tracking prototype
```

## Review Checklist

- [x] `MASTER_PLAN.md` Current Status → Sprint 01 complete, Prototype v0.1, Sprint 02 next.
- [x] `CHANGELOG.md` → `v0.1.0 — Sprint 01` entry.
- [x] Wrist-vs-index-tip default did not change; ADR-003 and `CONFIG_SPEC.md` remain valid.
- [x] Actual measured FPS was accepted against the §14.1 target during manual verification.
