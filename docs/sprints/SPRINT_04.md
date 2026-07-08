# SPRINT_04.md — Portal Animation

## Objective

Bring the portal to life: scale-in on spawn (ease-out), a looping idle animation from the full PNG sequence, and scale-out on close (ease-in). This is Prototype v0.4 — the portal now has a believable lifecycle instead of just appearing/staying static.

## Prerequisite Reading

- `SDD.md` §11 (Portal Animation Pipeline) — full section, including §11.2 sub-states and §11.3 easing math
- `API_SPEC.md` — `effects/portal_engine.py` (full `PortalPhase` state machine), `animation/portal_animator.py`
- `CONFIG_SPEC.md` — `PORTAL_OPEN_DURATION_S`, `PORTAL_CLOSE_DURATION_S`, `PORTAL_LOOP_FPS`

## Architecture Changes

None — this sprint completes the `PortalEngine`/`PortalAnimator` contracts that Sprint 03 only partially implemented (static-only).

## Files Created

```
src/animation/__init__.py
src/animation/portal_animator.py   # ease_out_cubic, ease_in_cubic, interpolate_radius
tests/unit/test_portal_animator.py  # pure math, fully unit-testable — no camera/rendering needed
```

## Files Modified

```
src/effects/portal_engine.py        # full PortalPhase state machine: SCALE_IN → IDLE_LOOP → SCALE_OUT → DESPAWN
src/app/main.py                     # call PortalEngine.update(dt) every frame; call request_close() based on a trigger (temporary: e.g. a debug keypress, since real close-on-body-overlap is Sprint 06)
```

## Acceptance Criteria

- [ ] `PortalAnimator.ease_out_cubic` / `ease_in_cubic` match their documented formulas exactly, unit-tested at t=0, 0.5, 1.0 against hand-computed expected values.
- [ ] Portal visibly scales in smoothly (fast start, gentle settle) over `PORTAL_OPEN_DURATION_S`, not instantaneously and not linearly.
- [ ] Portal PNG sequence loops continuously and smoothly during `IDLE_LOOP` at `PORTAL_LOOP_FPS`, with no visible frame-skip stutter or abrupt loop-seam.
- [ ] Requesting close (temporary debug trigger for this sprint) shrinks the portal over `PORTAL_CLOSE_DURATION_S` with the mirrored ease-in curve, then fully despawns (removed from the overlay, not just invisible).
- [ ] `request_close()` is a documented no-op if called while not in `IDLE_LOOP` (e.g., calling it during `SCALE_IN`), per `API_SPEC.md`.

## Prototype (Expected Output)

Drawing a valid circle now produces a portal that visibly grows open with an organic ease, loops its animated interior, and — on the temporary debug close trigger — shrinks shut and disappears entirely.

## Testing

- `tests/unit/test_portal_animator.py`: exact-value assertions on both easing functions at known `t`, and on `interpolate_radius` at t=0 (should be 0 or target depending on opening/closing direction) and t=1 (should be the opposite bound).
- Manual: verify no visual popping/snapping at phase transitions (`SCALE_IN → IDLE_LOOP` and `SCALE_OUT → DESPAWN` should be seamless, not a visible jump).

## Git Commit

```
Sprint 04: portal lifecycle state machine, easing curves, looping animation — Prototype v0.4
```

## Review Checklist

- [ ] `MASTER_PLAN.md` Current Status → Sprint 04 complete, Prototype v0.4, Sprint 05 next.
- [ ] `CHANGELOG.md` → `[v0.4] — Sprint 04` entry.
- [ ] Note in the changelog that portal-close is currently triggered by a temporary debug mechanism, not real body-overlap detection — that's Sprint 06's job, and this should be explicit so it's not mistaken for a bug later.
