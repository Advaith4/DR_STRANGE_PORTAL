# SPRINT_07.md — Integration & Polish

## Objective

No new features. This sprint hardens what already exists: strip/toggle debug visuals for a clean demo build, run the full manual test matrix from `SDD.md` §15.3 and the edge-case table from §16, perform an extended soak test, and produce the demo artifacts (video, screenshots, README). This is the sprint that turns "it works" into "it's a release."

## Prerequisite Reading

- `SDD.md` §15 (Testing Strategy — full), §16 (Edge Cases — full), §18 Phase 8 acceptance criteria
- `CODING_STANDARDS.md`, `CODEX_GUIDELINES.md` — re-read in full; this sprint is the point to audit accumulated drift (magic numbers that crept in, files that grew past 300 lines, TODOs left behind)

## Architecture Changes

None expected. If auditing turns up a real architectural issue (e.g. a file that's silently grown past the 300-line limit and genuinely needs splitting), that's an explicit, flagged task within this sprint — not a silent fix (`CODEX_GUIDELINES.md` §5), and it gets its own `ARCHITECTURE_DECISIONS.md` entry if it changes a prior decision.

## Files Created

```
output/screenshots/                # final demo screenshots
output/recordings/                  # final demo video
README.md                            # replaces the Sprint 00 placeholder: full setup instructions, gesture demo GIF, feature list, credits
tests/integration/test_pipeline.py    # first real integration test: constructs a full FrameContext pipeline run over recorded sample data (tests/data/), asserts no exceptions and expected state transitions occur
tests/integration/test_state_flow.py   # exercises the full AppState transition table against a scripted sequence of synthetic events
```

## Files Modified

```
src/ui/hud.py                        # confirm DEBUG=False produces a genuinely clean, no-skeleton, no-debug-dots demo view
config/config.yaml                    # DEBUG default confirmed False for the release build
(any files flagged during the audit — see Architecture Changes above)
```

## Acceptance Criteria

- [ ] Full manual interactive checklist from `SDD.md` §15.3 passes:
  - Portal reliably spawns on a natural circular gesture across several attempts.
  - Portal does not spontaneously spawn during idle hand movement.
  - Disappearance activates only on meaningful overlap, not incidental hand-through.
  - App recovers to `WAITING` if the hand leaves frame mid-gesture.
  - No crash when the portal spawns near a frame edge.
- [ ] Every edge case in `SDD.md` §16's table has been manually exercised at least once, with results noted (even "confirmed as documented limitation, not a bug" counts as a result).
- [ ] Extended soak test completed: app left running in `WAITING` for an extended period (e.g. 30+ minutes) with no crash, no memory growth, no FPS degradation.
- [ ] `DEBUG=False` produces a clean demo-ready view (no skeleton, no debug dots, minimal/no HUD clutter) suitable for recording.
- [ ] Demo video and screenshots captured and saved to `output/`.
- [ ] README is complete: setup instructions someone unfamiliar with the project could follow from scratch, plus the demo GIF/screenshots.
- [ ] `tests/integration/test_pipeline.py` and `test_state_flow.py` pass.
- [ ] A full audit pass against `CODING_STANDARDS.md` confirms no file exceeds 300 lines, no hardcoded magic numbers remain outside `config.yaml`, and no bare `except:` clauses exist anywhere in `src/`.

## Prototype (Expected Output)

**Release v1.0.** The complete, polished, demo-ready application: clean UI, reliable gesture-to-disappearance loop, no debug clutter, accompanied by a recorded demo video and a complete README.

## Testing

- Full regression pass across every unit test written in Sprints 00–06 — confirm nothing regressed during the polish pass.
- New integration tests (`tests/integration/`) exercise the full pipeline and full state machine end-to-end against recorded/synthetic data, not just individual modules in isolation.
- Soak test as described above.

## Git Commit

```
Sprint 07: integration testing, edge-case audit, debug cleanup, demo artifacts — Release v1.0
```

## Review Checklist

- [ ] `MASTER_PLAN.md` Current Status → Sprint 07 complete, **Release v1.0**, no next sprint (future work now lives entirely in `SDD.md` §17 as v1.x candidates, each getting its own sprint file created on demand when actually started).
- [ ] `CHANGELOG.md` → final `[v1.0] — Sprint 07` entry, summarizing the full feature set shipped.
- [ ] Tag the git release `v1.0`.
- [ ] Do a final read-through of `ARCHITECTURE_DECISIONS.md` — confirm every entry still reflects what was actually built, and add any decisions made during this polish pass that aren't yet captured.
