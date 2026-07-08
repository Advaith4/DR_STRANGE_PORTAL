# SPRINT_05.md — Body Detection

## Objective

Add MediaPipe Pose tracking to estimate the user's body center and an approximate radius (bounding ellipse/circle heuristic from shoulder/hip landmarks), and detect overlap against the active portal. This is Prototype v0.5 — the app now "knows" when the user is standing in the portal, even though nothing happens in response yet (that's Sprint 06).

## Prerequisite Reading

- `SDD.md` §12.2–12.3 (Body Region Estimation, Overlap Detection)
- `API_SPEC.md` — `vision/pose_tracker.py`
- `CONFIG_SPEC.md` — `ENTER_DEBOUNCE_FRAMES`
- `ARCHITECTURE_DECISIONS.md` — ADR-002 (why bounding-ellipse, not segmentation, for v1)

## Architecture Changes

None — implements the existing `PoseTracker` contract.

## Files Created

```
src/vision/pose_tracker.py
tests/unit/vision/test_pose_tracker.py    # tests the center/radius derivation math given synthetic landmark inputs, not live MediaPipe Pose output
```

## Files Modified

```
src/app/main.py                             # run PoseTracker per frame; compute overlap against active portal using distance() from utils.py; log overlap events
src/ui/hud.py                                # debug: draw body-center dot + estimated radius circle when DEBUG=True
```

## Acceptance Criteria

- [ ] `PoseTracker.process()` returns a plausible body center and radius estimate for a real person standing in frame, derived from shoulder/hip landmarks per `SDD.md` §12.2.
- [ ] Overlap test correctly reports `True`/`False` based on the circle-circle distance check (`SDD.md` §12.3), reusing `utils.distance()` rather than reimplementing distance math.
- [ ] Debug visualization (body-center dot + radius circle) is visibly reasonable against a real person's actual silhouette — not wildly oversized/undersized.
- [ ] `PoseTracker.process()` returns `detected=False` cleanly when no person/body is in frame (distinct from "hand not detected" — a person can have their body in frame with their hand gesture already completed and hand potentially out of the gesture-tracking view).
- [ ] No FPS regression beyond what's expected from adding a second MediaPipe model — measure and note actual FPS impact (`SDD.md` §14.3 profiling approach).

## Prototype (Expected Output)

Live feed with hand tracking, portal (if triggered), plus (in `DEBUG` mode) a body-center dot and estimated-radius circle on the user. Console/HUD logs an overlap event (`"Body overlapping portal"`) when the user walks into the portal's radius — still no visual disappearance effect yet.

## Testing

- `tests/unit/vision/test_pose_tracker.py`: given synthetic shoulder/hip landmark coordinates, assert the derived center and radius match hand-computed expected values for a couple of concrete test cases (e.g., shoulders at known symmetric coordinates → center should be their midpoint).
- Manual: verify overlap correctly transitions `False → True` as a real person walks toward and into an active portal, and back to `False` if they step away without lingering.

## Git Commit

```
Sprint 05: MediaPipe Pose body tracking, overlap detection — Prototype v0.5
```

## Review Checklist

- [ ] `MASTER_PLAN.md` Current Status → Sprint 05 complete, Prototype v0.5, Sprint 06 next.
- [ ] `CHANGELOG.md` → `[v0.5] — Sprint 05` entry.
- [ ] If real playtesting shows the bounding-ellipse estimate is noticeably too loose/tight against real bodies, note the observation as a candidate update to ADR-002 (the decision itself — deferring segmentation — likely still stands, but the specific radius-derivation formula may need tuning; capture that distinction in the entry rather than conflating "tune a formula" with "change the decision").
