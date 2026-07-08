# API_SPEC.md — Module Interface Contracts

This document defines the exact public interface of every module, per the updated folder structure (see `SDD.md` §6, revised below). Codex/Claude Code implementing any module should treat these signatures as fixed contracts — see `CODEX_GUIDELINES.md` §3 before changing any of them.

Types referenced throughout: `np.ndarray` (OpenCV BGR frame), plain tuples for coordinates, dataclasses for structured results.

---

## Folder Structure (see `SDD.md` §6 for full rationale)

```
src/
├── core/
│   ├── camera.py
│   ├── frame_context.py
│   ├── config.py               # loads config/config.yaml
│   └── logger.py                # shared logging.getLogger(__name__) setup
├── vision/
│   ├── hand_tracker.py
│   ├── gesture_detector.py
│   └── pose_tracker.py
├── effects/
│   ├── portal_engine.py
│   ├── overlay_engine.py
│   └── disappear_engine.py
├── animation/
│   └── portal_animator.py
├── ui/
│   ├── hud.py
│   └── fps_counter.py
├── app/
│   ├── state_machine.py
│   └── main.py
└── utils.py                     # cross-cutting math (distance, easing, EMA)
```

`effects/particles/`, `vision/segmentation.py`, and `rendering/shaders.py` are intentionally absent — they're future work (`SDD.md` §17), not v1 scope, and get their own package + API contract added on demand when actually built.

---

## `core/logger.py`

```python
import logging

def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger configured from config/logging.yaml
    (levels, handlers, format). Call once per module as:
    logger = get_logger(__name__)
    Never call logging.basicConfig() ad hoc elsewhere in the codebase —
    this function is the single place logging is configured."""
```

---

## `core/frame_context.py`

```python
from dataclasses import dataclass, field
import numpy as np

@dataclass
class FrameContext:
    frame: np.ndarray
    timestamp: float
    wrist_pos: tuple[float, float] | None = None
    hand_landmarks: list | None = None
    portal_triggered: bool = False
    portal_centroid: tuple[float, float] | None = None
    portal_radius: float | None = None
    body_center: tuple[float, float] | None = None
    body_radius_estimate: float | None = None
    state: str = "WAITING"
    debug_info: dict = field(default_factory=dict)
```

No methods — pure data carrier. Never add logic here (`CODING_STANDARDS.md` §1).

---

## `core/camera.py`

```python
class Camera:
    def __init__(
        self,
        device_index: int = 0,
        target_width: int = 960,
        target_height: int = 540,
        mirror_feed: bool = True,
    ): ...

    def read(self) -> np.ndarray:
        """Return the next BGR frame, resized to (target_width, target_height),
        and optionally horizontally mirrored. Raises CameraError if capture fails."""

    def get_fps(self) -> float:
        """Return a rolling-average FPS computed from internal timestamps,
        not cv2.CAP_PROP_FPS."""

    def release(self) -> None: ...
```

---

## `vision/hand_tracker.py`

```python
from dataclasses import dataclass

@dataclass
class HandResult:
    detected: bool
    wrist_pos: tuple[float, float] | None      # pixel coords, smoothed
    raw_landmarks: list | None                  # all 21 landmarks, pixel coords
    track_point: tuple[float, float] | None      # whichever point is configured as primary

class HandTracker:
    def __init__(
        self,
        max_num_hands: int = 1,
        track_point: str = "wrist",
        smoothing_alpha: float = 0.5,
    ): ...

    def process(self, frame: np.ndarray) -> HandResult:
        """Run MediaPipe Hands on the frame, apply EMA smoothing to the
        configured track_point, return a HandResult."""
```

---

## `vision/gesture_detector.py`

```python
from dataclasses import dataclass

@dataclass
class GestureResult:
    triggered: bool
    centroid: tuple[float, float] | None
    radius: float | None

class GestureDetector:
    def __init__(self, buffer_size: int = 25, radius_tolerance: float = 0.35,
                 angular_coverage_threshold_deg: float = 300.0,
                 min_gesture_radius_px: float = 30.0,
                 cooldown_seconds: float = 4.0): ...

    def update(self, point: tuple[float, float] | None) -> GestureResult:
        """Feed one new tracked point (or None if hand lost, which clears
        the buffer). Returns whether a circular gesture completed this call."""

    def reset(self) -> None:
        """Clear buffer and cooldown state (called on hand-lost or after
        a state-machine reset)."""
```

---

## `vision/pose_tracker.py`

```python
@dataclass
class BodyResult:
    detected: bool
    center: tuple[float, float] | None
    radius_estimate: float | None   # derived from shoulder/hip landmarks

class PoseTracker:
    def __init__(self): ...

    def process(self, frame: np.ndarray) -> BodyResult:
        """Run MediaPipe Pose, return an approximate body center + radius
        estimate (bounding ellipse/circle heuristic, not per-pixel mask)."""
```

---

## `effects/portal_engine.py`

```python
from enum import Enum, auto

class PortalPhase(Enum):
    IDLE = auto()
    SCALE_IN = auto()
    IDLE_LOOP = auto()
    SCALE_OUT = auto()
    DESPAWN = auto()

class PortalEngine:
    def __init__(self, frames_dir: str, open_duration_s: float = 0.6,
                 close_duration_s: float = 0.5): ...

    def spawn(self, center: tuple[float, float], target_radius: float) -> None:
        """Begin SCALE_IN at the given center/radius. No-op if already active."""

    def request_close(self) -> None:
        """Transition IDLE_LOOP -> SCALE_OUT. No-op if not in IDLE_LOOP."""

    def update(self, dt: float) -> None:
        """Advance animation timers/phase by dt seconds."""

    def get_current_frame_and_mask(self) -> tuple[np.ndarray, np.ndarray] | None:
        """Return the current portal RGBA sub-frame and alpha mask for
        compositing, or None if PortalPhase.IDLE/DESPAWN."""

    @property
    def phase(self) -> PortalPhase: ...

    @property
    def center(self) -> tuple[float, float] | None: ...

    @property
    def radius(self) -> float: ...
```

---

## `effects/overlay_engine.py`

```python
class OverlayEngine:
    def __init__(self, debug: bool = False): ...

    def composite(self, base_frame: np.ndarray,
                   portal_rgba: np.ndarray | None,
                   portal_center: tuple[float, float] | None,
                   debug_info: dict) -> np.ndarray:
        """Alpha-blend the portal onto base_frame within a clipped ROI,
        then draw debug skeleton/HUD if self.debug is True. Returns the
        final frame ready for cv2.imshow."""
```

---

## `effects/disappear_engine.py`

```python
class DisappearEngine:
    def __init__(self, fade_duration_s: float = 1.2): ...

    def capture_background(self, frame: np.ndarray) -> None:
        """Store a clean background frame. Called once at startup after
        the calibration countdown."""

    def check_overlap(self, body_center: tuple[float, float] | None,
                        body_radius: float | None,
                        portal_center: tuple[float, float] | None,
                        portal_radius: float | None) -> bool:
        """Circle-circle overlap test. Returns False if any input is None."""

    def update(self, dt: float, overlapping: bool) -> float:
        """Advance fade_progress toward 1.0 while overlapping, hold/reset
        otherwise depending on state-machine debounce rules. Returns
        current fade_progress in [0, 1]."""

    def apply(self, frame: np.ndarray, body_center: tuple[float, float],
               body_radius: float, fade_progress: float) -> np.ndarray:
        """Blend frame toward the stored background within the body
        region only, at the given fade_progress."""
```

---

## `animation/portal_animator.py`

```python
class PortalAnimator:
    """Pure animation-curve helper consumed by PortalEngine; kept separate
    so animation math is independently testable from asset/frame handling."""

    @staticmethod
    def ease_out_cubic(t: float) -> float: ...

    @staticmethod
    def ease_in_cubic(t: float) -> float: ...

    @staticmethod
    def interpolate_radius(t: float, target_radius: float, opening: bool) -> float:
        """Return the current radius given normalized time t in [0, 1]."""
```

---

## `ui/hud.py`

```python
class HUD:
    def __init__(self, font_scale: float = 0.5, thickness: int = 1): ...

    def draw(
        self,
        frame: np.ndarray,
        state: str,
        fps: float,
        track_point: tuple[float, float] | None,
    ) -> None:
        """Draw state name, FPS, and tracked-point coordinates onto frame."""
```

## `ui/fps_counter.py`

```python
class FpsCounter:
    def __init__(self, window_size: int = 30): ...

    def update(self) -> None:
        """Record one frame timestamp."""

    def get_fps(self) -> float:
        """Return rolling-average FPS."""
```

---

## `app/state_machine.py`

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

class StateMachine:
    def __init__(self, initial: AppState = AppState.WAITING): ...

    def handle_event(self, event: str) -> AppState:
        """Look up (current_state, event) in the transition table and
        move to the resulting state. No-op (returns current state
        unchanged) if the pair isn't in the table."""

    @property
    def state(self) -> AppState: ...
```

---

## `utils.py`

```python
def distance(a: tuple[float, float], b: tuple[float, float]) -> float: ...
def ema(previous: float, new: float, alpha: float) -> float: ...
def unwrap_angle_delta(theta_prev: float, theta_curr: float) -> float: ...
```

---

## Contract Change Process

If implementing a sprint reveals that a signature above needs to change (extra parameter, different return type), that is **not** a routine coding decision — flag it per `CODEX_GUIDELINES.md` §3, update this file in the same change, and note the reason inline as a comment above the changed signature.
