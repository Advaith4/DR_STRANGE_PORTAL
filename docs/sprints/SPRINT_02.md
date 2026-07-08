# SPRINT_02.md — Gesture Detection

## Objective

Implement the circular-gesture recognizer: buffer wrist history, run the three-part circularity test, and emit a `portal_triggered` event with the gesture's centroid and radius. This is Prototype v0.2 — the app can now "understand" a gesture, even though nothing visual happens yet in response (that's Sprint 03).

## Prerequisite Reading

- `SDD.md` §9 (Gesture Recognition Algorithm) — read in full, this is the most mathematically dense section in the project
- `API_SPEC.md` — `vision/gesture_detector.py`
- `CONFIG_SPEC.md` — Gesture Detection section
- `ARCHITECTURE_DECISIONS.md` — ADR-004 (geometric heuristic vs. ML)

## Architecture Changes

None — implements the existing `GestureDetector` contract.

## Files Created

```
src/vision/gesture_detector.py
tests/unit/vision/test_gesture_detector.py
tests/data/sample_landmarks/            # recorded or synthetically generated point sequences:
    circle_clean.json                    #   a clean, well-formed circle
    circle_partial.json                  #   an incomplete arc (~250°) — should NOT trigger
    scribble.json                        #   direction-reversing scribble with consistent radius — should NOT trigger
    straight_line.json                   #   should NOT trigger
    circle_small.json                    #   below MIN_GESTURE_RADIUS_PX — should NOT trigger
```

## Files Modified

```
src/app/main.py                          # wires GestureDetector into the per-frame loop, logs trigger events
src/ui/hud.py                            # add: gesture cooldown indicator (e.g. countdown text or dimmed HUD)
```

## Acceptance Criteria

- [ ] All five fixtures in `tests/data/sample_landmarks/` produce the documented pass/fail result via `GestureDetector.update()`.
- [ ] `RADIUS_TOLERANCE`, `ANGULAR_COVERAGE_THRESHOLD_DEG`, `MIN_GESTURE_RADIUS_PX`, `GESTURE_COOLDOWN_SECONDS` are all read from config, not hardcoded (`CODING_STANDARDS.md` §3).
- [ ] Live test: drawing a real circle with your hand (wrist tracked) triggers reliably across ≥10 consecutive manual attempts, per `SDD.md` §18 Phase 2 acceptance criteria.
- [ ] Live test: a straight-line wave and a scribble do **not** trigger, across ≥10 attempts each.
- [ ] Cooldown visibly prevents an immediate re-trigger right after a successful gesture.
- [ ] Hand-lost mid-gesture clears the buffer (`GestureDetector.reset()`), verified by triggering hand-lost partway through a circle and confirming no stale trigger fires afterward.

## Prototype (Expected Output)

Same visual as Sprint 01, plus: when a real circular gesture completes, the console/HUD logs `"Portal triggered at (x, y), radius=r"`. No portal renders yet — this is intentional.

## Testing

- `tests/unit/vision/test_gesture_detector.py`: load each fixture in `tests/data/sample_landmarks/`, feed its points through `GestureDetector.update()` in sequence, assert `.triggered` matches the fixture's expected outcome (see filenames above).
- Explicitly test the angle-unwrapping edge case: a circle crossing the −π/π boundary should still compute correct total rotation (this is the case most likely to have a subtle bug — verify it directly, don't just infer from the clean-circle fixture passing).
- Explicitly test cooldown: two clean circles fed back-to-back with no time gap should only trigger once.

## Git Commit

```
Sprint 02: gesture detector (radius consistency + angular coverage), cooldown, fixtures — Prototype v0.2
```

## Review Checklist

- [ ] `MASTER_PLAN.md` Current Status → Sprint 02 complete, Prototype v0.2, Sprint 03 next.
- [ ] `CHANGELOG.md` → `[v0.2] — Sprint 02` entry.
- [ ] If live playtesting required retuning `RADIUS_TOLERANCE` or `ANGULAR_COVERAGE_THRESHOLD_DEG` away from their documented defaults, update `CONFIG_SPEC.md`'s defaults and add a short ADR entry explaining what real-world behavior forced the change (this is exactly the kind of decision ADR-004's neighbors are for).
- [ ] Confirm no false positives occurred during Sprint 01's incidental hand movement testing — if they did, that's a Sprint 02 regression to fix before moving on, not something to carry into Sprint 03.
