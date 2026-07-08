from __future__ import annotations

import time
from collections import deque
from typing import Deque

import cv2
import numpy as np


class CameraError(RuntimeError):
    """Raised when the camera cannot be opened or read."""


class Camera:
    def __init__(
        self,
        device_index: int = 0,
        target_width: int = 960,
        target_height: int = 540,
        mirror_feed: bool = True,
    ) -> None:
        self.device_index = device_index
        self.target_width = target_width
        self.target_height = target_height
        self.mirror_feed = mirror_feed
        self._capture = cv2.VideoCapture(device_index)
        if not self._capture.isOpened():
            raise CameraError(f"Unable to open camera device {device_index}")

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, float(target_width))
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, float(target_height))
        self._fps_samples: Deque[float] = deque(maxlen=30)
        self._last_timestamp: float | None = None

    def read(self) -> np.ndarray:
        """Return the next BGR frame, resized, and optionally mirrored."""
        if self._capture is None or not self._capture.isOpened():
            raise CameraError("Camera is not available")

        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise CameraError("Failed to read frame from camera")

        resized = cv2.resize(
            frame,
            (self.target_width, self.target_height),
            interpolation=cv2.INTER_AREA,
        )
        if self.mirror_feed:
            resized = cv2.flip(resized, 1)

        now = time.perf_counter()
        if self._last_timestamp is not None:
            elapsed = now - self._last_timestamp
            if elapsed > 0:
                self._fps_samples.append(1.0 / elapsed)
        self._last_timestamp = now
        return resized

    def get_fps(self) -> float:
        """Return a rolling-average FPS estimate based on frame timing."""
        if not self._fps_samples:
            return 0.0
        return sum(self._fps_samples) / len(self._fps_samples)

    def release(self) -> None:
        """Release the underlying camera capture."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
