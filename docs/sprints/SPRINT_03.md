# SPRINT_03.md — Portal Rendering (Static)

## Objective

Render a static (non-animated) portal PNG onto the frame at the gesture's centroid, alpha-blended correctly, with boundary clipping. This is Prototype v0.3 — the first sprint with a visible payoff from the gesture detector's output. Animation (scale-in/loop/scale-out) is explicitly **out of scope** here — that's Sprint 04.

## Prerequisite Reading

- `SDD.md` §10 (Rendering & Overlay Pipeline), §11.1 (Asset Format)
- `API_SPEC.md` — `effects/portal_engine.py` (only the spawn/static-frame parts), `effects/overlay_engine.py`
- `CONFIG_SPEC.md` — Portal section
- `ASSET_GUIDE.md` — portal PNG naming/format requirements (read before sourcing/placing assets)

## Architecture Changes

None.

## Files Created

```
src/effects/__init__.py
src/effects/portal_engine.py     # spawn() + a single static frame only in this sprint; phase machine stubbed to always report IDLE_LOOP
src/effects/overlay_engine.py
tests/unit/test_utils.py          # extend: add any new pure-math helpers introduced for ROI clipping, if not already in utils.py
```

## Files Modified

```
src/app/main.py                   # on portal_triggered, call PortalEngine.spawn(); call OverlayEngine.composite() each frame
assets/portal_frames/              # at least one placeholder PNG asset in place (even a simple circle-glow placeholder is fine for this sprint — final art can come later)
```

## Acceptance Criteria

- [ ] On a successful gesture trigger, a portal PNG appears at the gesture's centroid at (at least roughly) the gesture's estimated radius.
- [ ] Alpha blending is correct — no visible hard rectangular edge around the portal PNG, no color fringing.
- [ ] Boundary clipping verified: manually trigger a gesture very close to a frame edge/corner; app must not crash (`SDD.md` §10.3, and `SDD.md` §16 edge-case table).
- [ ] ROI-limited compositing implemented (§10.2) — not a full-frame blend every call; verify by confirming FPS doesn't measurably drop when a portal is on screen versus when it isn't.
- [ ] Portal remains on screen indefinitely in this sprint (no close/despawn logic yet — that's Sprint 04); a second gesture while one is active is a no-op per `PortalEngine.spawn()`'s documented contract.

## Prototype (Expected Output)

Live feed with hand tracking as before; drawing a valid circle now causes a static, alpha-blended portal image to appear and remain at that location.

## Testing

- Unit-testable pieces here are limited (most of this sprint is genuinely visual/rendering code) — focus unit tests on any new pure functions (ROI bounding-box math, clipping arithmetic) rather than trying to unit-test `cv2` drawing calls directly.
- Manual test matrix: portal spawned center-frame, portal spawned at each of the four edges, portal spawned at each corner — confirm no crash and correct partial-clipping visual in all cases.

## Git Commit

```
Sprint 03: static portal rendering, alpha blending, ROI compositing, boundary clipping — Prototype v0.3
```

## Review Checklist

- [ ] `MASTER_PLAN.md` Current Status → Sprint 03 complete, Prototype v0.3, Sprint 04 next.
- [ ] `CHANGELOG.md` → `[v0.3] — Sprint 03` entry.
- [ ] `ASSET_GUIDE.md` updated if the actual asset naming/folder convention used differs at all from what was documented before real assets existed.
- [ ] No ADR entry expected unless the ROI-clipping approach diverged meaningfully from `SDD.md` §10.2–10.3's description.
