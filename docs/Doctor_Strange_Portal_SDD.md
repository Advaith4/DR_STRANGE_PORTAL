# Doctor Strange Portal — Software Design Document (SDD)

**Project Codename:** Sling Ring
**Document Type:** Engineering Specification / Software Design Document
**Version:** 1.0
**Status:** Draft for Implementation
**Author:** Advaith
**Target Audience:** Implementation agents (human or AI, e.g. Codex/Claude Code), future contributors, portfolio reviewers

---

## Document Control

| Field | Value |
|---|---|
| Document Owner | Advaith |
| Reviewers | — |
| Related Documents | `Doctor_Strange_Portal_Scope.md` (superseded by this document) |
| Repository | `doctor-strange-portal/` |
| Primary Language | Python 3.10+ |

---

## Table of Contents

1. Product Vision
2. Target Users & Use Cases
3. User Journey
4. System Architecture
5. Module Responsibilities
6. Folder Structure
7. Data Flow Diagrams
8. MediaPipe Landmark Details
9. Gesture Recognition Algorithm
10. Rendering & Overlay Pipeline
11. Portal Animation Pipeline
12. Disappearance Algorithm
13. State Machine Design
14. Performance Targets
15. Testing Strategy
16. Edge Cases
17. Future Improvements
18. Development Milestones
19. Task Checklist
20. References

---

# 1. Product Vision

## 1.1 Elevator Pitch

A webcam-only, real-time application that lets a person open a glowing, swirling "Sling Ring" portal in mid-air with a circular hand gesture, step through it, and visually vanish from the frame — reproducing the signature Doctor Strange VFX beat using nothing but classical and ML-based computer vision, with no green screen and no external compositing software.

## 1.2 Why This Project Exists

This is a **learning-first** project disguised as a **demo-first** project. The dual goals are:

- **Learning goal:** build fluency across the full CV stack a real vision engineer touches daily — camera I/O, landmark-based tracking, temporal signal processing (gesture recognition), image compositing (alpha blending), segmentation, and animation/state management.
- **Demo goal:** produce something visually impressive enough to anchor a portfolio, resume line, or interview conversation, because it is instantly legible to a non-technical audience ("the app makes me disappear through a magic portal") while resting on real technical depth underneath.

## 1.3 Design Philosophy

The project is deliberately architected **like a small real-time game engine**, not a single monolithic script. That means:

- A fixed **frame loop** (update → render) exactly like a game engine's main loop.
- A **finite state machine (FSM)** driving high-level behavior, not nested conditionals.
- **Systems** (hand tracking, gesture recognition, portal, disappearance, overlay) that own their own data and expose narrow interfaces, similar to Entity-Component-System-adjacent design without the full ECS overhead (that would be over-engineering for this scope).
- A **single source of truth per frame**: one `FrameContext` object passed through the pipeline, rather than global mutable state scattered across modules.

This philosophy is what separates a "hackathon script" from an "engineering artifact" — and it's the primary thing this SDD is designed to make legible to a reviewer or an AI code-generation agent.

## 1.4 Non-Goals

To keep scope honest, this document explicitly states what the project is **not** trying to do:

- Not a production SaaS product; no auth, no cloud deployment, no multi-user support.
- Not attempting full 3D scene understanding — all effects are 2D compositing tricks with a 2D depth heuristic at most.
- Not attempting robust segmentation-grade rotoscoping in v1 (that's a stretch goal, see §17).
- Not targeting mobile in v1; desktop webcam only.

---

# 2. Target Users & Use Cases

## 2.1 Primary User Persona

**"Advaith-as-demoer"** — a CS student showing this at a hackathon booth, in a portfolio video, or in a technical interview. Needs: fast setup, reliable triggering in front of an audience, visually "wow" output, and a codebase clean enough to walk through live if asked "how does this work?"

## 2.2 Secondary Persona

**A future contributor / reviewer** reading the GitHub repo — possibly a recruiter, possibly another student forking it. Needs: a README and SDD that explain the system without needing to run it.

## 2.3 Use Cases

| ID | Use Case | Actor | Outcome |
|---|---|---|---|
| UC-1 | Open a portal with a hand circle gesture | End user | Portal spawns and animates open at gesture location |
| UC-2 | Walk through the open portal | End user | User's pixels are replaced by background, appears to vanish |
| UC-3 | Portal auto-closes after use | System | Portal shrinks and disappears, state resets to `WAITING` |
| UC-4 | Developer swaps portal art asset | Developer | New PNG sequence dropped into `assets/portal_frames/`, no code change needed |
| UC-5 | Developer tunes gesture sensitivity | Developer | Adjusts constants in `gesture_detector.py` config, no logic rewrite |

---

# 3. User Journey

```
┌────────────────────────────────────────────────────────────────────┐
│  1. User launches app → webcam feed appears, HUD shows "WAITING"   │
│  2. User raises hand into frame → hand skeleton overlay (debug)    │
│  3. User draws a circle in the air with wrist/index finger         │
│  4. System recognizes circular path → HUD flashes "Portal Opening" │
│  5. A shimmering portal animates open at the gesture's centroid    │
│  6. User walks toward and through the portal boundary               │
│  7. As user's body region overlaps portal, their pixels fade into  │
│     the pre-captured clean background — user appears to vanish     │
│  8. Portal shrinks, closes, sound cue (optional) plays               │
│  9. System resets to WAITING, ready for the next gesture             │
└────────────────────────────────────────────────────────────────────┘
```

### Journey Design Notes

- The journey must feel **magical but legible** — the user should always have visible feedback (HUD text, portal glow intensity, cooldown indicator) so they understand *why* nothing happened if a gesture fails.
- The "disappearing" beat is the emotional payoff and must be prioritized in polish time (Phase 8) even if it means trimming stretch goals.

---

# 4. System Architecture

## 4.1 Architectural Style

**Layered pipeline with a central state machine**, similar in shape to a simplified game engine tick:

```
 ┌───────────────────────────────────────────────────────────────┐
 │                         main.py (Game Loop)                   │
 │                                                                 │
 │   while running:                                               │
 │       frame = camera.read()                                    │
 │       ctx   = FrameContext(frame)                              │
 │       ctx   = hand_tracker.process(ctx)                        │
 │       ctx   = gesture_detector.process(ctx)                    │
 │       ctx   = state_machine.update(ctx)     # drives behavior  │
 │       ctx   = portal.update(ctx)                                │
 │       ctx   = disappear.update(ctx)                             │
 │       frame = overlay.render(ctx)                               │
 │       display(frame)                                            │
 └───────────────────────────────────────────────────────────────┘
```

## 4.2 Layers

| Layer | Modules | Responsibility |
|---|---|---|
| **Input** | `camera.py` | Acquire raw frames, manage FPS |
| **Perception** | `hand_tracker.py`, body detection (in `disappear.py` or a future `pose_tracker.py`) | Convert pixels into structured landmark data |
| **Interpretation** | `gesture_detector.py` | Convert landmark time-series into semantic events (`portal_triggered`) |
| **Control** | `state_machine.py` | Own the app's behavioral state; the only module allowed to decide "what happens now" |
| **Simulation** | `portal.py`, `disappear.py` | Own animatable state (portal radius, opacity, fade progress) |
| **Presentation** | `overlay.py` | Composite everything back onto the frame; the only module allowed to draw pixels |
| **Utility** | `utils.py` | Shared math (distance, smoothing, easing functions) |

## 4.3 The FrameContext Object

A single dataclass threaded through every stage of the pipeline per frame. This is the architectural backbone that prevents the "large nested if-statement" anti-pattern the original scope doc already correctly flagged as a risk.

```python
from dataclasses import dataclass, field
import numpy as np

@dataclass
class FrameContext:
    frame: np.ndarray                 # current BGR frame
    timestamp: float                  # time.time() at capture
    wrist_pos: tuple | None = None    # (x, y) or None if no hand
    hand_landmarks: list | None = None
    portal_triggered: bool = False
    body_mask: np.ndarray | None = None
    state: str = "WAITING"
    debug_info: dict = field(default_factory=dict)
```

Every module receives a `FrameContext`, mutates or reads only the fields relevant to it, and returns it. This keeps module boundaries strict and makes unit testing trivial (construct a fake `FrameContext`, call `.process()`, assert on the output).

## 4.4 Why Not a Full ECS or Multi-threaded Pipeline?

Explicitly rejected alternatives, and why:

- **Full Entity-Component-System:** Overkill for a single-entity (one hand, one portal, one user) real-time app. Adds indirection without paying for itself at this scale.
- **Multi-threaded capture/processing:** Tempting for FPS gains, but introduces race conditions on `FrameContext` mutation that would materially increase debugging cost for a project explicitly scoped as "beginner-friendly, modular, learning-first." A single-threaded loop with frame-skipping (see §14) is the correct tradeoff here.
- **Multi-agent orchestration (e.g. CrewAI-style):** Not applicable — this is a real-time perception loop, not an LLM reasoning task. Mentioned only to explicitly rule it out, since it appears elsewhere in Advaith's project portfolio (HRMS copilot) for a different class of problem.

---

# 5. Module Responsibilities

## 5.1 `camera.py` — Capture System

- Owns the `cv2.VideoCapture` handle.
- Responsible for resolution normalization (downscale to a fixed working resolution, e.g. 960×540, regardless of native webcam resolution — this is the single highest-leverage performance decision in the whole app).
- Exposes `read() -> np.ndarray` and `get_fps() -> float`.
- Owns FPS monitoring via a rolling timestamp buffer, not `cv2.CAP_PROP_FPS` (which is frequently inaccurate on consumer webcams).

## 5.2 `hand_tracker.py` — Perception System

- Wraps `mediapipe.solutions.hands`.
- Configured for `max_num_hands=1` (single-hand tracking is sufficient and materially faster).
- Extracts wrist landmark (`landmark[0]`) as the primary tracked point, with index fingertip (`landmark[8]`) available as an alternate/secondary tracking point for more precise circle drawing (see §8 for why wrist vs. fingertip is a real design decision, not an arbitrary choice).
- Applies **exponential smoothing** to the raw landmark position before it ever reaches the gesture detector, to reduce jitter (see §9.2).

## 5.3 `gesture_detector.py` — Interpretation System

- Maintains a fixed-length ring buffer (`collections.deque(maxlen=N)`) of smoothed wrist positions.
- Runs the circular-motion heuristic (§9) every frame once the buffer is full.
- Owns gesture **cooldown** logic (prevents re-triggering immediately after a successful trigger).
- Emits a boolean event (`portal_triggered`) plus the **centroid** and **estimated radius** of the detected circle, which become the portal's spawn parameters.

## 5.4 `portal.py` — Portal Engine

- Owns portal lifecycle state independent of the app-level FSM: `SCALE_IN`, `IDLE_LOOP`, `SCALE_OUT`.
- Loads the PNG sequence once at startup into memory (never re-read from disk per frame).
- Exposes `.update(dt)` for animation timestep advancement and `.get_current_frame_and_mask()` for the overlay engine.
- Owns the portal's center and current radius, which `disappear.py` needs to determine body/portal overlap.

## 5.5 `overlay.py` — Presentation System

- The **only** module permitted to call `cv2.imshow`-bound drawing operations on the final frame.
- Owns alpha-blending math (§10) and boundary clipping (portal partially off-screen must not crash the app).
- Owns HUD rendering (state name, debug skeleton, FPS counter) — all debug visuals are toggled by a single `DEBUG` flag so they can be stripped for the demo-recording build.

## 5.6 `disappear.py` — Disappearance Engine

- Captures and stores a clean background frame at startup (before the user enters frame, or via a short calibration countdown).
- Computes an overlap test between the user's body region and the portal's current bounding circle.
- Owns the fade-out progress value (0.0 → 1.0) and blends the live frame with the stored background accordingly.

## 5.7 `state_machine.py` — Control System

- The single authority for "what state are we in and what triggers a transition."
- Implemented as an explicit `Enum` + transition table, **not** nested `if/elif` chains (this was already correctly identified as a risk in the original scope document and is preserved as a hard architectural rule here — see §13).

## 5.8 `utils.py` — Shared Utilities

- Distance/angle math, exponential moving average smoothing, easing functions (ease-in/out for animation curves), and a small `Timer` helper for cooldowns.

---

# 6. Folder Structure

```
doctor-strange-portal/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
│
├── config/
│   ├── config.yaml              # tunable values, see CONFIG_SPEC.md
│   └── logging.yaml              # logging levels/handlers, see core/logger.py
│
├── assets/
│   ├── portal_frames/          # PNG sequence, e.g. portal_000.png ... portal_059.png
│   ├── sounds/                 # optional .wav/.mp3 cues
│   └── background/             # optional pre-captured background fallback
│
├── src/
│   ├── core/
│   │   ├── camera.py
│   │   ├── frame_context.py
│   │   ├── config.py           # loads config/config.yaml into typed constants
│   │   └── logger.py           # one-line logging.getLogger(__name__) setup helper
│   ├── vision/
│   │   ├── hand_tracker.py
│   │   ├── gesture_detector.py
│   │   └── pose_tracker.py
│   ├── effects/
│   │   ├── portal_engine.py
│   │   ├── overlay_engine.py
│   │   └── disappear_engine.py
│   ├── animation/
│   │   └── portal_animator.py
│   ├── ui/
│   │   ├── hud.py
│   │   └── fps_counter.py
│   ├── app/
│   │   ├── state_machine.py
│   │   └── main.py
│   └── utils.py                 # cross-cutting math (distance, easing, EMA)
│
├── tests/
│   ├── unit/
│   │   ├── vision/test_gesture_detector.py
│   │   ├── app/test_state_machine.py
│   │   └── test_utils.py
│   ├── integration/
│   │   └── test_pipeline.py     # exercises the full FrameContext pipeline end-to-end on synthetic input
│   └── data/
│       └── sample_landmarks/    # recorded landmark sequences used as fixtures (real circle, scribble, etc.)
│
├── docs/
│   ├── MASTER_PLAN.md
│   ├── Doctor_Strange_Portal_SDD.md   # this document
│   ├── API_SPEC.md
│   ├── CONFIG_SPEC.md
│   ├── CODING_STANDARDS.md
│   ├── CODEX_GUIDELINES.md
│   ├── ASSET_GUIDE.md
│   ├── ARCHITECTURE_DECISIONS.md
│   ├── CHANGELOG.md
│   ├── architecture_diagram.png
│   └── sprints/
│       └── SPRINT_00.md … SPRINT_07.md
│
└── output/
    ├── screenshots/
    └── recordings/
```

### Rationale for This Revision (Right-Sizing Pass)

A later review proposed a considerably larger structure — per-package DI container, an event bus, `rendering/shaders.py`, a `particles/` package, `vision/segmentation.py`, and a `notebooks/` folder. Four ideas from that proposal were genuinely worth adopting and are reflected above: the `config/` split (values vs. logging setup), an ADR log (`ARCHITECTURE_DECISIONS.md`), a `CHANGELOG.md`, and a `tests/unit` + `tests/integration` + `tests/data` split with real fixture data.

The rest was deliberately **not** adopted, because it conflicts with this project's own stated non-functional requirement (§Objectives: "beginner-friendly," "modular," "easily extensible" — not "production-scale"):

- **No DI container / event bus** (`core/events.py`, `dependency_container.py`, `bootstrap.py`): this app has one runtime loop and a handful of singleton systems instantiated once in `main.py`. A dependency-injection framework and an event bus are solutions to multi-team, multi-environment complexity this project doesn't have — and an event bus would directly compete with the state-machine-as-transition-table pattern already committed to in §13, creating two control-flow mechanisms where one suffices.
- **No `effects/particles/`, no `vision/segmentation.py`, no `rendering/shaders.py`**: particles and Selfie Segmentation are explicitly *future* work (§17.1), not v1 scope, and there is no shader pipeline in an OpenCV/NumPy project. Building package scaffolding for features that don't exist yet means empty stub files sitting in the repo for the length of the whole build — which reads to a reviewer as "designed but abandoned," undermining the portfolio goal rather than helping it. When segmentation or particles actually get built (v1.1+), they get their own package at that point, per §17's existing rule that stretch goals get their own sprint file created on demand.
- **No `notebooks/`**: gesture detection and portal animation are real-time interactive systems, not offline data-analysis tasks — a Jupyter notebook can't meaningfully answer "does my live circular gesture trigger," so this would end up as unopened dead weight.
- **`effects/portal_engine.py` and `effects/disappear_engine.py` stay single files, not sub-packages** (e.g. not split into `portal_renderer.py` / `portal_assets.py` / `portal_math.py`): per `CODING_STANDARDS.md`'s own 300-line rule, a module gets split when it actually grows past that limit, not preemptively on day one. Sprint 4–6 is when this gets revisited if either file earns a split.

### Additions vs. the Original Scope Document

- **`core/config.py`** (loading `config/config.yaml`, see `CONFIG_SPEC.md`): centralizes every tunable constant so no module hardcodes magic numbers.
- **`core/logger.py`**: one shared setup for `logging.getLogger(__name__)`-style module loggers, configured from `config/logging.yaml`, per `CODING_STANDARDS.md` §8.
- **`tests/unit/`, `tests/integration/`, `tests/data/`**: the original document listed "Modular testing" only as a risk-mitigation bullet; this SDD promotes it to a proper test package with real fixture data (recorded landmark sequences), not just inline synthetic points.
- **`ARCHITECTURE_DECISIONS.md`, `CHANGELOG.md`**: a running log of *why* a design choice was made (e.g. wrist vs. index tip, geometric heuristic vs. ML classifier) and a plain record of what shipped in each sprint.
- **`API_SPEC.md`, `CODING_STANDARDS.md`, `CODEX_GUIDELINES.md`, `MASTER_PLAN.md`, sprint files**: companion documents that turn this SDD from a design narrative into an AI-codeable specification — see `docs/MASTER_PLAN.md` for how they all relate.

---

# 7. Data Flow Diagrams

## 7.1 Per-Frame Data Flow

```
   Camera Frame (BGR ndarray)
          │
          ▼
   ┌─────────────────┐
   │  Hand Tracker    │──► hand_landmarks (21 points) ──► wrist_pos (smoothed)
   └─────────────────┘
          │
          ▼
   ┌─────────────────┐
   │ Gesture Detector │──► ring buffer of wrist_pos ──► portal_triggered (bool)
   └─────────────────┘                                   + centroid, radius
          │
          ▼
   ┌─────────────────┐
   │  State Machine   │──► current_state (Enum)
   └─────────────────┘
          │
          ├──────────────┬─────────────────┐
          ▼              ▼                 ▼
   ┌───────────┐  ┌──────────────┐  ┌───────────────┐
   │  Portal   │  │  Disappear   │  │   (future)     │
   │  Engine   │  │   Engine     │  │  Pose Tracker  │
   └───────────┘  └──────────────┘  └───────────────┘
          │              │
          └──────┬───────┘
                 ▼
          ┌─────────────┐
          │  Overlay     │──► Final composited frame ──► cv2.imshow
          │  Engine      │
          └─────────────┘
```

## 7.2 Cross-Frame (Temporal) Data Flow

The gesture detector is the only module that carries state **across** frames in a way that matters architecturally — it accumulates history. This is deliberately isolated:

```
Frame 1 wrist_pos ─┐
Frame 2 wrist_pos ─┼─► deque(maxlen=20) ─► circularity_score() ─► trigger?
Frame 3 wrist_pos ─┘
      ...
Frame N wrist_pos ─┘
```

This isolation matters: if gesture recognition needs to be swapped later (e.g., for an ML classifier instead of a geometric heuristic — see §17), only `gesture_detector.py` and its buffer need to change. Every other module is stateless per-frame or owns its own independent lifecycle state (portal, disappearance).

---

# 8. MediaPipe Landmark Details

MediaPipe Hands returns **21 normalized landmarks** per detected hand, each with `(x, y, z)` in image-relative coordinates (`x, y ∈ [0, 1]`, `z` relative depth, smaller = closer to camera). Understanding all 21 is necessary even though this project only actively uses 1–2 of them, because future stretch goals (multi-finger gestures, pinch-to-resize portal) depend on this map.

```
        8   12  16   20
        │   │   │    │
        7   11  15   19
        │   │   │    │
        6   10  14   18
        │   │   │    │
    4   5   9   13   17
    │   │   │   │    │
    3   │   │   │    │
    │   │   │   │    │
    2   │   │   │    │
     \  │   │   │   /
      \ │   │   │  /
        \│   │  │ /
          \  │  │/
            \│ 0│  ← WRIST
```

| Index | Landmark Name | Notes |
|---|---|---|
| 0 | WRIST | **Primary tracked point** for gesture recognition. Chosen over fingertip because wrist motion is more stable/less jittery — the wrist moves as a rigid extension of the forearm, while fingertips wobble with small finger-joint flexion even during an intended "smooth circle" gesture. |
| 1–4 | THUMB_CMC → THUMB_TIP | Reserved for future pinch-gesture (portal resize) |
| 5–8 | INDEX_FINGER_MCP → TIP | Index tip (8) is the **secondary** candidate tracked point — more precise for deliberate "drawing" gestures, at the cost of more jitter. Kept as a config toggle (`TRACK_POINT = "wrist"` or `"index_tip"` in `config.py`) rather than a hardcoded choice, since this is a legitimate open design decision that benefits from live A/B testing during Phase 2. |
| 9–12 | MIDDLE_FINGER_MCP → TIP | Unused in v1 |
| 13–16 | RING_FINGER_MCP → TIP | Unused in v1 |
| 17–20 | PINKY_MCP → TIP | Unused in v1 |

### Design Decision: Wrist vs. Index Tip

This is called out explicitly because it's a real, non-obvious tradeoff a reviewer might ask about:

| Criterion | Wrist (landmark 0) | Index Tip (landmark 8) |
|---|---|---|
| Jitter | Low | Higher |
| Gesture "feel" | Less precise, more "whole-hand wave" | Feels like actually drawing a circle |
| Occlusion robustness | Higher (wrist rarely self-occludes) | Lower (fingertip can bend out of frame) |
| Recommended for | v1 default, robustness-first demo | Stretch goal precision mode |

**Decision:** default to wrist for v1, expose the choice as a config constant, revisit after Phase 2 playtesting.

### Coordinate System Notes

- MediaPipe landmarks are normalized `[0, 1]` relative to frame width/height — they must be multiplied by `(frame_width, frame_height)` to get pixel coordinates, and this conversion should live in exactly one place (`hand_tracker.py`) to avoid inconsistent scaling bugs elsewhere in the pipeline.
- MediaPipe's coordinate origin is top-left, same as OpenCV — no flip needed for `x, y`, but the webcam feed itself should be horizontally mirrored (`cv2.flip(frame, 1)`) at capture time for an intuitive "mirror" UX, and this flip must happen **before** MediaPipe processes the frame, not after, or landmark coordinates will map to the wrong side of a mirrored display.

---

# 9. Gesture Recognition Algorithm

## 9.1 Problem Framing

Input: a time-ordered sequence of `(x, y)` wrist positions, one per frame, arriving continuously.
Output: a boolean "the user just drew an approximate circle" event, fired **at most once** per gesture, robust to noisy/imperfect circles, robust to varying gesture speed, and robust to the user's hand leaving frame mid-gesture.

This is a real algorithm design problem, not a trivial one — a naive "did the path return near its start" check fires on lots of non-circular motion too. The approach below layers three independent heuristics that must **all** pass, which is what makes it robust to false positives without needing a trained classifier.

## 9.2 Step 1: Smoothing (Preprocessing)

Raw landmark positions are noisy frame-to-frame. Apply an **exponential moving average (EMA)**:

```
smoothed_x(t) = α · raw_x(t) + (1 − α) · smoothed_x(t−1)
smoothed_y(t) = α · raw_y(t) + (1 − α) · smoothed_y(t−1)
```

With `α ≈ 0.4–0.6` — high enough to stay responsive (a portal-opening gesture is intentionally fast), low enough to kill single-frame jitter. This constant belongs in `config.py` as `SMOOTHING_ALPHA`.

## 9.3 Step 2: History Buffer

Maintain `deque(maxlen=N)` of smoothed positions, `N ≈ 20–30` frames (≈0.7–1s at 25–30 FPS — tuned to roughly match a natural, deliberate circle-drawing speed).

## 9.4 Step 3: Three-Part Circularity Test

Given the buffer of points `P = {p_1, ..., p_N}`:

**(a) Centroid computation**

```
centroid = ( mean(x_i), mean(y_i) )  for all p_i in P
```

**(b) Radius consistency check**

Compute distance from each point to the centroid:

```
r_i = distance(p_i, centroid)
mean_r = mean(r_i)
std_r  = stddev(r_i)
```

A true circle has low variance in radius. Accept only if:

```
std_r / mean_r  <  RADIUS_TOLERANCE     (e.g. 0.35)
```

This is a **coefficient of variation** threshold — using the ratio rather than a raw stddev threshold makes it scale-invariant, so the gesture works whether the user draws a small tight circle or a big sweeping one.

**(c) Angular coverage check**

This is the step that actually distinguishes "a circle" from "a back-and-forth scribble that happens to have consistent radius." For each point, compute its angle relative to the centroid:

```
θ_i = atan2(p_i.y − centroid.y, p_i.x − centroid.x)
```

Unwrap the angle sequence (handle the −π/π wraparound), then sum the **signed angular deltas** between consecutive points:

```
total_rotation = Σ (θ_{i+1} − θ_i)   [unwrapped]
```

Accept only if:

```
| total_rotation |  ≥  ANGULAR_COVERAGE_THRESHOLD   (e.g. 300° ≈ 5.2 rad)
```

This requires the path to have swept most of the way around the centroid in a **consistent rotational direction** — a scribble that reverses direction repeatedly will partially cancel out in this signed sum, correctly rejecting it. A minimum-rotation threshold below 360° (rather than requiring an exact full turn) is intentional: it tolerates a slightly incomplete circle without feeling unresponsive to the user.

**(d) Minimum radius check (sanity gate)**

Reject gestures where `mean_r` is smaller than a `MIN_GESTURE_RADIUS_PX` — otherwise natural hand tremor while holding the hand still could, in rare cases, pass the coefficient-of-variation test at a tiny scale.

## 9.5 Trigger & Cooldown

```python
if radius_consistent and angular_coverage_sufficient and radius_large_enough:
    if cooldown_timer.expired():
        emit(portal_triggered=True, centroid=centroid, radius=mean_r)
        cooldown_timer.reset(COOLDOWN_SECONDS)   # e.g. 3–5s
        buffer.clear()
```

The cooldown prevents the same completed circle from re-triggering across multiple consecutive frames before the user's hand has moved on, and gives a clean UX window before the next gesture is accepted.

## 9.6 Why Not Just Use an ML Classifier?

Explicitly considered and deferred: a small trained gesture classifier (e.g., on landmark sequences) would generalize better to varied circle styles, but (a) requires a labeled dataset the project doesn't have, (b) adds a training/inference dependency for a gesture simple enough that geometric heuristics solve it well, and (c) contradicts the "beginner-friendly, understandable code" non-functional requirement — a reviewer can read and verify the geometric approach in one sitting. Listed as a stretch goal (§17) if the classical approach proves too fragile in practice.

---

# 10. Rendering & Overlay Pipeline

## 10.1 Alpha Blending Fundamentals

Portal PNG assets are RGBA. For each pixel where the portal overlaps the frame:

```
output = foreground · alpha + background · (1 − alpha)
```

Applied per-channel (B, G, R), with `alpha` normalized to `[0, 1]` from the PNG's alpha channel (`[0, 255]`).

## 10.2 Region-of-Interest (ROI) Compositing

Rather than blending the full frame every call, extract only the bounding-box ROI where the portal currently overlaps the frame, blend within that ROI, and write it back. This is the single biggest performance win available in the overlay stage — blending a full 960×540 frame every call when the portal only occupies a 200×200 region wastes >90% of the compute.

## 10.3 Boundary Clipping

The portal's bounding box must be clamped to the frame's dimensions before slicing, and the corresponding sub-region of the PNG asset must be clipped identically — a portal spawned near a frame edge must not crash on an out-of-bounds slice. This is called out explicitly because it's a common, easy-to-miss bug class in overlay code (an off-by-one or unclamped negative index here silently either crashes or corrupts adjacent memory views in NumPy).

## 10.4 Layer Order (Z-Order)

Rendering order per frame, back to front:

```
1. Live camera frame (or disappearance-blended frame, see §12)
2. Portal PNG (alpha blended)
3. Debug skeleton / landmarks (if DEBUG flag on)
4. HUD text (state, FPS)
```

---

# 11. Portal Animation Pipeline

## 11.1 Asset Format

A PNG sequence (`portal_000.png … portal_NNN.png`), pre-rendered externally (e.g., via a looping VFX asset or generated procedurally) and loaded once at startup into an in-memory list of NumPy arrays — never re-decoded from disk per frame.

## 11.2 Portal Lifecycle Sub-States

Independent of the app-level FSM (§13), the portal owns its own micro-state:

```
SPAWN → SCALE_IN → IDLE_LOOP → SCALE_OUT → DESPAWN
```

- **SCALE_IN:** radius interpolates from 0 to target radius over `T_open` seconds using an ease-out curve (fast start, gentle settle) — a linear scale reads as mechanical, not magical.
- **IDLE_LOOP:** the PNG sequence loops continuously (looking animated/alive) while radius holds steady; this is the longest-duration sub-state, active for as long as the app-level state is `PORTAL_ACTIVE`.
- **SCALE_OUT:** mirrors SCALE_IN, ease-in curve (accelerating shrink) for a satisfying "snap closed" feel.

## 11.3 Easing Function

```python
def ease_out_cubic(t):
    return 1 - (1 - t) ** 3
```

Used for `SCALE_IN`; `ease_in_cubic` (t³) used for `SCALE_OUT`. These live in `utils.py` as pure functions taking normalized time `t ∈ [0, 1]` and returning a normalized progress value — kept generic so future animations (fade curves, camera shake in stretch goals) reuse the same utilities.

## 11.4 Scale & Position Binding

The portal's center and target radius are set **once**, at trigger time, from the gesture detector's output (§9.5), and held fixed for the portal's lifetime — the portal does not follow the user's hand after opening. This is a deliberate simplicity decision: a portal that tracks the hand post-spawn would require continuous gesture-to-portal binding logic that adds complexity without adding to the core demo beat (user walks through a fixed portal).

---

# 12. Disappearance Algorithm

## 12.1 Precondition: Clean Background Capture

At app startup (or on a manual "recalibrate background" keypress), capture and store one frame with no user present. This is the ground truth the disappearance effect blends toward. A short on-screen countdown ("Clear the frame in 3... 2... 1...") should gate this capture so it isn't accidentally taken with the user still in view.

## 12.2 Body Region Estimation (v1: MediaPipe Pose)

Per the original scope document's Option A: use MediaPipe Pose to get a body-center landmark (e.g., midpoint of shoulders/hips) and approximate the user's silhouette as a bounding ellipse or box scaled from a couple of pose landmarks (shoulders width, hip-to-shoulder height) — not full per-pixel segmentation in v1. This is a deliberate fidelity/complexity tradeoff: an approximate bounding region is enough to detect "user overlaps portal" and to gate a **region-limited** background replacement, without needing per-pixel segmentation accuracy in the first working version.

## 12.3 Overlap Detection

```
overlap = distance(body_center, portal_center) < (portal_radius + body_radius_estimate)
```

A simple circle-circle overlap test, reusing the same distance utility as the gesture detector (`utils.py`).

## 12.4 Disappearance Blend

Once overlap is detected and the app-level state transitions to `DISAPPEARING`:

```
frame_output = live_frame · (1 − fade_progress) + background · fade_progress
```

Applied **only within the estimated body region**, not the whole frame — the rest of the scene stays live so the effect reads as "the person is vanishing," not "the whole camera froze." `fade_progress` ramps 0 → 1 over `T_fade` seconds (e.g., 1–1.5s) using the same easing utilities as the portal (§11.3), so the vanish feels intentional rather than an abrupt cut.

## 12.5 Known v1 Limitation

Because the body region is an approximate ellipse/box rather than a pixel-accurate mask, edges of the disappearance effect will show a soft rectangular/elliptical fade boundary rather than a perfectly rotoscoped silhouette. This is accepted as a v1 tradeoff and explicitly tracked as the top stretch goal (§17, Selfie Segmentation) rather than something to over-engineer for in the first working build.

---

# 13. State Machine Design

## 13.1 Explicit States

```python
from enum import Enum, auto

class AppState(Enum):
    WAITING = auto()
    TRACKING = auto()
    PORTAL_OPENING = auto()
    PORTAL_ACTIVE = auto()
    USER_ENTERING = auto()
    DISAPPEARING = auto()
    PORTAL_CLOSING = auto()
    RESET = auto()
```

## 13.2 Transition Table

| From | Trigger | To |
|---|---|---|
| `WAITING` | hand detected | `TRACKING` |
| `TRACKING` | hand lost for > N frames | `WAITING` |
| `TRACKING` | `portal_triggered == True` | `PORTAL_OPENING` |
| `PORTAL_OPENING` | portal SCALE_IN complete | `PORTAL_ACTIVE` |
| `PORTAL_ACTIVE` | body enters overlap zone | `USER_ENTERING` |
| `USER_ENTERING` | overlap sustained > N frames (debounce) | `DISAPPEARING` |
| `USER_ENTERING` | overlap lost before debounce | `PORTAL_ACTIVE` |
| `DISAPPEARING` | fade_progress reaches 1.0 | `PORTAL_CLOSING` |
| `PORTAL_CLOSING` | portal SCALE_OUT complete | `RESET` |
| `RESET` | one frame delay (cleanup) | `WAITING` |

## 13.3 Implementation Rule (Non-Negotiable)

`state_machine.py` implements the transition table as **data** (a dict keyed by `(state, event) -> new_state`), not as a chain of `if current_state == X and event == Y`. This was flagged as a risk in the original scope document ("Never chain large nested if-statements") and is elevated here to an explicit architectural constraint: any pull request that reintroduces nested conditionals for state transitions should be treated as a design regression, not a style nitpick.

```python
TRANSITIONS = {
    (AppState.WAITING, "hand_detected"): AppState.TRACKING,
    (AppState.TRACKING, "hand_lost"): AppState.WAITING,
    (AppState.TRACKING, "portal_triggered"): AppState.PORTAL_OPENING,
    # ...
}

def update(state, event):
    return TRANSITIONS.get((state, event), state)  # no-op if unmatched
```

## 13.4 Debounce Note (USER_ENTERING)

The `USER_ENTERING → DISAPPEARING` transition is intentionally debounced (requires sustained overlap across several frames, not a single frame) to prevent a brief, incidental hand-through-portal moment from triggering a full-body disappearance prematurely — this was not called out in the original document and is a real edge case worth guarding against explicitly (see §16).

---

# 14. Performance Targets

## 14.1 Target Metrics

| Metric | Target | Rationale |
|---|---|---|
| Frame rate | 20–30 FPS | Below ~15 FPS, gesture tracking and the "magic" feel both degrade noticeably |
| Hand detection latency | < 1 frame | MediaPipe Hands on CPU is fast enough at reduced resolution |
| End-to-end input-to-portal-spawn latency | < 150 ms after gesture completes | Keeps the interaction feeling responsive, not laggy |
| Startup time | < 3 s | Model load + camera warm-up |

## 14.2 Performance Levers, in Priority Order

1. **Resolution downscaling** — process at a fixed reduced resolution (e.g., 960×540 or lower) regardless of native webcam resolution; this affects every downstream stage's cost.
2. **ROI-limited compositing** (§10.2) — never blend a full frame when a bounding box suffices.
3. **MediaPipe model complexity setting** — use the lighter hand-landmark model variant if available, trading a small accuracy cost for latency.
4. **Avoid redundant recomputation** — smoothing state, portal frame cache, and background capture must each be computed once and reused, never recomputed per-frame.
5. **Frame skipping under load** — if FPS drops below a floor (e.g., 15), skip gesture-detector computation (not rendering) on alternating frames as a graceful-degradation fallback, documented as a v1.1 enhancement if v1 profiling shows it's needed.

## 14.3 Profiling Approach

Before optimizing, instrument each pipeline stage's per-call duration (simple `time.perf_counter()` deltas around each module's `.process()`/`.update()` call, aggregated into a rolling average) and log/display it behind the `DEBUG` flag. Optimize the stage that's actually the bottleneck — almost certainly hand detection or overlay compositing, not the gesture math, which is O(N) over a small fixed buffer.

---

# 15. Testing Strategy

## 15.1 Testing Philosophy

Given the project's dependency on live camera input, most of the system cannot be meaningfully tested with pure black-box automation — the strategy therefore splits into **unit-testable pure logic** vs. **manually verified interactive behavior**.

## 15.2 Unit-Testable Modules (Automated, `tests/`)

| Module | What to test |
|---|---|
| `gesture_detector.py` | Feed synthetic point sequences (a perfect circle, a straight line, a scribble, a partial arc) and assert `portal_triggered` fires only for the circle and the sufficiently-complete arc |
| `state_machine.py` | Assert every transition in the table produces the correct next state, and that unmatched `(state, event)` pairs are no-ops |
| `utils.py` | Assert distance, EMA smoothing, and easing functions against known input/output pairs |
| `portal.py` (lifecycle logic only, no rendering) | Assert `SCALE_IN → IDLE_LOOP → SCALE_OUT` timing and radius interpolation values at known `t` |

Example synthetic-circle test sketch:

```python
def test_perfect_circle_triggers():
    points = generate_circle_points(center=(320, 240), radius=80, n=25)
    detector = GestureDetector()
    for p in points:
        detector.update(p)
    assert detector.portal_triggered is True

def test_straight_line_does_not_trigger():
    points = generate_line_points(start=(100, 240), end=(500, 240), n=25)
    detector = GestureDetector()
    for p in points:
        detector.update(p)
    assert detector.portal_triggered is False
```

## 15.3 Manually Verified Behavior (Interactive Checklist)

Not automatable without a hardware test rig; verified by a human running the live app:

- Portal reliably spawns on a natural circular gesture across several attempts.
- Portal does not spontaneously spawn during idle hand movement (false-positive check).
- Disappearance effect activates only when the user meaningfully overlaps the portal, not on incidental hand-through.
- App recovers gracefully (returns to `WAITING`) if the hand leaves frame mid-gesture.
- App does not crash if the portal spawns near a frame edge (boundary clipping check, §10.3).

## 15.4 Regression Testing on Asset/Config Changes

Any change to `config.py` constants (radius tolerance, cooldown, smoothing alpha) should be re-validated against the synthetic-circle test suite (§15.2) plus at least one manual playtest pass, since these constants are the primary lever for both false positives and false negatives in the field.

---

# 16. Edge Cases

Beyond the original document's risk list (false triggers, lighting, busy backgrounds, low FPS, occlusion), this SDD calls out additional concrete edge cases that need explicit handling:

| Edge Case | Failure Mode if Unhandled | Mitigation |
|---|---|---|
| Hand exits frame mid-gesture | Gesture buffer holds a truncated arc that may or may not falsely pass the circularity test | Clear buffer immediately on hand-lost event, not just on trigger |
| Portal spawned very close to frame edge | Overlay slicing crashes on out-of-bounds index | ROI clamping (§10.3), covered by a dedicated manual test |
| User briefly waves hand through portal without intending to "enter" | Premature `DISAPPEARING` transition | Debounce on `USER_ENTERING → DISAPPEARING` (§13.4) |
| Two hands visible in frame | MediaPipe may track the "wrong" hand across frames, causing gesture buffer discontinuity | `max_num_hands=1` plus a simple "closest to last known position" hand-selection tiebreaker |
| Ambient lighting changes after background capture | Disappearance blend shows a visible seam against the stale background | Manual "recalibrate background" keybind; documented limitation rather than solved in v1 (true fix requires segmentation, §17) |
| User wearing clothing/skin tone poorly lit for MediaPipe's model | Hand detection confidence drops, gesture never registers | Document minimum lighting recommendation in README; not algorithmically fixable within scope |
| App left running in `WAITING` for a long time | No known failure mode, but worth explicitly stating: no memory leak expected since PNG sequence and MediaPipe models are loaded once, not per-frame | Verified via extended manual soak test before demo day |

---

# 17. Future Improvements

Organized by effort/impact, extending the original "Stretch Goals" list with reasoning:

## 17.1 High Impact, Moderate Effort

- **MediaPipe Selfie Segmentation** for pixel-accurate disappearance (replaces the bounding-ellipse approximation in §12.2) — the single highest-leverage visual-quality upgrade available.
- **Particle sparks at portal edge** — cheap to implement (simple particle system in `overlay.py` or a new `particles.py`), high visual payoff for demo video.

## 17.2 Moderate Impact, Moderate Effort

- **Portal interior distortion** (a subtle swirl/refraction shader-like effect on the frame content visible "through" the portal before the user enters) via a radial warp on the underlying pixels.
- **Sound effects** on open/close (pygame mixer, already listed as optional tech in the original stack).
- **Camera shake** on portal open, for cinematic punch.

## 17.3 High Effort / Stretch

- **Multiple simultaneous portals** — requires generalizing the portal engine from a singleton to a managed list, and generalizing gesture detection to disambiguate multiple concurrent gestures if two-handed support is added.
- **Video recording / auto-clip export** — wrap the render loop with a `cv2.VideoWriter` toggle, straightforward but adds I/O considerations.
- **ML-based gesture classifier** (§9.6) — revisit only if the geometric heuristic proves fragile across a range of real users/lighting in playtesting.
- **"Teleportation" mode** — user disappears at one portal and reappears at a second portal elsewhere in frame (mentioned in the user's own framing of future ambitions); would require compositing the user's captured silhouette onto the destination portal's background, a meaningfully harder compositing problem than simple disappearance.

## 17.4 Explicitly Deferred, Not Planned

- Mobile/AR port — out of scope per §1.4; would require an entirely different rendering/capture stack (e.g., ARKit/ARCore) rather than an extension of this codebase.

---

# 18. Development Milestones

Retains the original document's phase structure, with acceptance criteria added per phase so "done" is unambiguous:

| Phase | Scope | Acceptance Criteria |
|---|---|---|
| 1 | Camera, hand detection, landmark visualization | Stable webcam feed at target FPS; hand skeleton overlay tracks a real hand with visibly low jitter |
| 2 | Gesture history, circle detection | Synthetic-circle unit tests (§15.2) pass; a real hand-drawn circle reliably triggers, a straight line/scribble does not, across ≥10 manual trials |
| 3 | Portal rendering | Portal PNG renders at the gesture's centroid with correct alpha blending and boundary clipping |
| 4 | Portal animation | SCALE_IN/IDLE_LOOP/SCALE_OUT play with correct easing curves, verified visually |
| 5 | Body detection | MediaPipe Pose body-center estimate tracks a real user; overlap test against a test portal fires correctly |
| 6 | Disappearance effect | Fade blend against captured background reads clearly as "disappearing," debounce (§13.4) verified against incidental hand-through |
| 7 | Integration | Full state machine transition table exercised end-to-end in one continuous live run without manual state resets |
| 8 | Polish | Debug visuals stripped for demo build; HUD clean; at least one full soak test (§16) completed without crash |

---

# 19. Task Checklist

- [ ] Scaffold folder structure (§6) including `config.py` and `tests/`
- [ ] Implement `camera.py` with fixed working resolution + rolling FPS monitor
- [ ] Implement `hand_tracker.py` with configurable track-point (wrist vs. index tip, §8)
- [ ] Implement EMA smoothing (§9.2) as a reusable utility
- [ ] Implement `gesture_detector.py` three-part circularity test (§9.4) + cooldown (§9.5)
- [ ] Write synthetic-circle unit tests (§15.2) before wiring up the live demo
- [ ] Implement `state_machine.py` as a transition-table dict (§13.3), not nested conditionals
- [ ] Implement `portal.py` lifecycle (SCALE_IN/IDLE_LOOP/SCALE_OUT) with easing utilities (§11.3)
- [ ] Implement `overlay.py` ROI-limited alpha blending + boundary clipping (§10)
- [ ] Implement background capture + `disappear.py` overlap and fade logic (§12)
- [ ] Add debounce to `USER_ENTERING → DISAPPEARING` transition (§13.4)
- [ ] Wire full pipeline in `main.py` via `FrameContext` (§4.3)
- [ ] Add `DEBUG` flag toggling skeleton/HUD visuals
- [ ] Run manual interactive checklist (§15.3)
- [ ] Run extended soak test (§16)
- [ ] Record demo video + capture screenshots
- [ ] Write README with setup instructions + gesture demo GIF
- [ ] Tag v1.0 release

---

# 20. References

- MediaPipe Hands documentation — 21-landmark hand tracking model
- MediaPipe Pose documentation — body landmark estimation
- MediaPipe Selfie Segmentation documentation — future segmentation upgrade path (§17.1)
- OpenCV `cv2` documentation — video I/O, image processing primitives
- Classic alpha compositing theory ("Compositing Digital Images," Porter & Duff, 1984) — theoretical basis for §10
- Original project scope document: `Doctor_Strange_Portal_Scope.md` (superseded in structure by this SDD, retained as historical reference in `docs/`)

---

*End of Software Design Document.*
