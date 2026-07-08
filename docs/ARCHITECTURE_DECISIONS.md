# ARCHITECTURE_DECISIONS.md — Decision Log (ADRs)

A running log of *why*, not just *what*. Each entry is short: context, decision, alternatives considered, consequence. New entries append at the top. This file exists so that six months from now (or three sprints from now), nobody has to reverse-engineer the reasoning behind a design choice from the code alone.

---

## ADR-006: Right-sized project structure over a full production-service layout

**Date:** 2026-07-07
**Context:** A proposed restructure introduced a dependency-injection container, an event bus, `rendering/shaders.py`, an `effects/particles/` package, `vision/segmentation.py`, and `notebooks/`.
**Decision:** Adopted the genuinely useful parts (config split into `config.yaml`/`logging.yaml`, an ADR log, a changelog, `tests/unit`+`tests/integration`+`tests/data`). Rejected the DI container, event bus, and premature package scaffolding for not-yet-built features.
**Alternatives considered:** Full adoption of the larger structure.
**Consequence:** Keeps the codebase's actual complexity matched to its actual scope (one runtime loop, one user, one camera) per the project's own "beginner-friendly, modular" non-functional requirement. Future features (particles, segmentation) get their package created on demand, at the sprint that actually builds them — see `SDD.md` §17 and §6.

---

## ADR-005: State machine as a transition-table dict, not nested conditionals, and no competing event-bus

**Date:** 2026-07-07 (elevated from `SDD.md` §13.3)
**Context:** The original scope document already flagged "never chain large nested if-statements" as a risk to avoid.
**Decision:** `state_machine.py` implements `(state, event) -> next_state` as a dict lookup. No parallel event-bus/pub-sub system is introduced elsewhere in the app.
**Alternatives considered:** Nested `if/elif` chains (rejected, the exact anti-pattern being avoided); a full event-bus/observer pattern (rejected, see ADR-006 — redundant with the transition table and adds a second, competing control-flow mechanism).
**Consequence:** Any PR reintroducing nested conditionals for state transitions is a design regression, not a style nitpick (`SDD.md` §13.3).

---

## ADR-004: Geometric heuristic for gesture recognition instead of a trained ML classifier

**Date:** 2026-07-07 (elevated from `SDD.md` §9.6)
**Context:** Circular-gesture detection could be solved with a trained classifier over landmark sequences, or with explicit geometry (radius consistency + signed angular coverage).
**Decision:** Geometric heuristic (three-part test: radius consistency, angular coverage, minimum radius sanity check — `SDD.md` §9.4).
**Alternatives considered:** ML classifier — rejected for v1: no labeled dataset exists, adds a training/inference dependency, and is harder for a reviewer to verify by reading the code (contradicts the "beginner-friendly, understandable" requirement).
**Consequence:** Listed as a stretch goal (`SDD.md` §17.3) if the classical approach proves too fragile across real users/lighting during playtesting.

---

## ADR-003: Wrist landmark (index 0) as the default tracked point, not index fingertip (index 8)

**Date:** 2026-07-07 (elevated from `SDD.md` §8)
**Context:** MediaPipe Hands exposes 21 landmarks; either the wrist or the index fingertip could serve as the primary point tracked for the circular gesture.
**Decision:** Default to wrist; expose the choice as `TRACK_POINT` in `config.yaml` rather than hardcoding it.
**Alternatives considered:** Index fingertip — more precise/"feels like drawing," but jitterier and more prone to occlusion (finger bending out of frame).
**Consequence:** Revisit after Phase 2 (`SPRINT_02`) playtesting; if fingertip precision turns out to matter more than wrist stability in practice, flip the default, not the architecture (the config toggle already supports either).

---

## ADR-002: Approximate bounding-ellipse body region (MediaPipe Pose) instead of pixel-accurate segmentation for v1 disappearance

**Date:** 2026-07-07 (elevated from `SDD.md` §12.2, §12.5)
**Context:** The disappearance effect needs *some* estimate of "where is the user's body" to gate background replacement.
**Decision:** MediaPipe Pose body-center + a bounding ellipse/circle derived from shoulder/hip landmarks, not per-pixel Selfie Segmentation.
**Alternatives considered:** MediaPipe Selfie Segmentation — rejected for v1 only on complexity/schedule grounds, not quality; it's the top-ranked future improvement (`SDD.md` §17.1).
**Consequence:** v1's disappearance effect will show a soft elliptical fade boundary rather than a rotoscoped silhouette. Documented as a known, accepted v1 limitation, not a bug.

---

## ADR-001: Single-threaded frame loop instead of multi-threaded capture/processing

**Date:** 2026-07-07 (elevated from `SDD.md` §4.4)
**Context:** Multi-threading capture and processing could improve FPS headroom.
**Decision:** Single-threaded loop with resolution downscaling and ROI-limited compositing as the primary performance levers instead (`SDD.md` §14.2).
**Alternatives considered:** Multi-threaded pipeline — rejected: introduces race conditions on `FrameContext` mutation, raising debugging cost for a project explicitly scoped as learning-first and beginner-friendly.
**Consequence:** If profiling (`SDD.md` §14.3) shows the single-threaded loop can't hit the 20–30 FPS target even after downscaling/ROI optimization, frame-skipping under load (§14.2 item 5) is the next lever, not threading.

---

## Template for New Entries

```
## ADR-0NN: <short decision title>

**Date:** YYYY-MM-DD
**Context:** what problem/question prompted this decision
**Decision:** what was decided
**Alternatives considered:** what else was on the table, and why it lost
**Consequence:** what this implies for future work, or what to revisit and when
```
