# SPRINT_06.md — Disappearance Effect

## Objective

Wire up the actual "vanish" payoff: capture a clean background at startup, debounce sustained body/portal overlap, fade the user's body region into the stored background, and trigger the real (non-debug) portal close once the fade completes. This is Prototype v0.6 — the full effect works end-to-end for the first time.

## Prerequisite Reading

- `SDD.md` §12 (Disappearance Algorithm, full section including §12.5 known limitation), §13.4 (debounce rationale)
- `API_SPEC.md` — `effects/disappear_engine.py`
- `CONFIG_SPEC.md` — `FADE_DURATION_S`, `ENTER_DEBOUNCE_FRAMES`, `BACKGROUND_CAPTURE_COUNTDOWN_S`

## Architecture Changes

None.

## Files Created

```
src/effects/disappear_engine.py
tests/unit/test_disappear_engine.py    # fade-progress math and overlap-check logic, isolated from actual pixel blending
```

## Files Modified

```
src/app/main.py                          # startup countdown + capture_background(); debounce logic gating overlap → fade start; call PortalEngine.request_close() (replacing Sprint 04's temporary debug trigger) once fade_progress reaches 1.0
src/app/state_machine.py                  # first real use of the full transition table: WAITING → TRACKING → PORTAL_OPENING → PORTAL_ACTIVE → USER_ENTERING → DISAPPEARING → PORTAL_CLOSING → RESET, all wired to real events instead of stubs
```

## Acceptance Criteria

- [ ] Startup countdown (`BACKGROUND_CAPTURE_COUNTDOWN_S`) clearly signals "clear the frame" before capturing background, per `SDD.md` §12.1.
- [ ] `USER_ENTERING → DISAPPEARING` only fires after sustained overlap across `ENTER_DEBOUNCE_FRAMES` frames, not a single-frame incidental overlap (`SDD.md` §13.4, §16 edge case table) — verify explicitly by briefly waving a hand through the portal without the body following, and confirming this does NOT trigger disappearance.
- [ ] Fade-out visibly blends only the estimated body region into the background over `FADE_DURATION_S`, using the same easing utilities as the portal (§12.4) — not an abrupt cut, not a whole-frame freeze.
- [ ] On fade completion, the state machine transitions to `PORTAL_CLOSING` and the portal's **real** `request_close()` fires (Sprint 04's debug trigger is now removed, not just unused).
- [ ] Full state machine cycle completes at least once, end-to-end, in a single continuous live run without any manual state reset: `WAITING → ... → RESET → WAITING` again, ready for a second gesture.
- [ ] The known v1 limitation (soft elliptical fade boundary, not pixel-accurate silhouette — `SDD.md` §12.5) is visually present but not catastrophically distracting; if it's bad enough to undermine the demo, flag it now rather than pushing it silently into polish.

## Prototype (Expected Output)

The complete core loop for the first time: user draws a circle → portal opens with animation → user walks in → after a brief sustained overlap, their body region fades into the background → portal closes → app resets and is ready again.

## Testing

- `tests/unit/test_disappear_engine.py`: unit-test `check_overlap()` (circle-circle math, reuse `utils.distance()`) and the `update()` fade-progress ramp (given a sequence of `overlapping=True` calls, `fade_progress` should monotonically increase toward 1.0 at a rate consistent with `FADE_DURATION_S` and the configured frame rate).
- Manual: the full state-machine cycle test above, run at least 3 times consecutively to confirm `RESET → WAITING` genuinely re-arms the system rather than leaving it in a stuck state.

## Git Commit

```
Sprint 06: background capture, debounced overlap, disappearance fade, full state-machine wiring — Prototype v0.6
```

## Review Checklist

- [ ] `MASTER_PLAN.md` Current Status → Sprint 06 complete, Prototype v0.6, Sprint 07 next.
- [ ] `CHANGELOG.md` → `[v0.6] — Sprint 06` entry — explicitly note this is the first sprint where the full end-to-end demo loop works.
- [ ] Update `ARCHITECTURE_DECISIONS.md` ADR-002 with a real note on whether the v1 fade-boundary limitation held up acceptably in practice, or whether it should be escalated in priority within `SDD.md` §17.1's future-improvements ranking.
