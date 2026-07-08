from __future__ import annotations

from collections import deque
from time import perf_counter


class FpsCounter:
    def __init__(self, window_size: int = 30) -> None:
        self.window_size = max(1, window_size)
        self._frame_deltas: deque[float] = deque(maxlen=self.window_size)
        self._last_time: float | None = None

    def update(self) -> None:
        now = perf_counter()
        if self._last_time is not None:
            elapsed = now - self._last_time
            if elapsed > 0:
                self._frame_deltas.append(elapsed)
        self._last_time = now

    def get_fps(self) -> float:
        if not self._frame_deltas:
            return 0.0
        average_delta = sum(self._frame_deltas) / len(self._frame_deltas)
        if average_delta <= 0:
            return 0.0
        return 1.0 / average_delta
