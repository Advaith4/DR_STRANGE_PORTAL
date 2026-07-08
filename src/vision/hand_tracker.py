from __future__ import annotations

from dataclasses import dataclass
import importlib

import cv2
import numpy as np

from src.core.logger import get_logger

logger = get_logger("src.vision.hand_tracker")

try:
    mp_hands = importlib.import_module("mediapipe.python.solutions.hands")
except ImportError:  # pragma: no cover - fallback for older packaging
    try:
        mp_hands = importlib.import_module("mediapipe.solutions.hands")
    except ImportError:  # pragma: no cover - fallback for unavailable dependency
        mp_hands = None


@dataclass
class HandResult:
    detected: bool
    wrist_pos: tuple[float, float] | None
    raw_landmarks: list[tuple[float, float]] | None
    track_point: tuple[float, float] | None


class HandTracker:
    def __init__(
        self,
        max_num_hands: int = 1,
        track_point: str = "wrist",
        smoothing_alpha: float = 0.5,
    ) -> None:
        if track_point not in {"wrist", "index_tip"}:
            raise ValueError("track_point must be 'wrist' or 'index_tip'")
        self.max_num_hands = max_num_hands
        self.track_point_name = track_point
        self.smoothing_alpha = smoothing_alpha
        self._smoothed_point: tuple[float, float] | None = None
        if mp_hands is None:
            logger.error("MediaPipe hands module unavailable")
            self._hands = None
        else:
            self._hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=max_num_hands,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            logger.info("MediaPipe Hands initialized successfully")

    def process(self, frame: np.ndarray) -> HandResult:
        """Run MediaPipe Hands on the frame, apply EMA smoothing, and return the result."""
        if self._hands is None:
            self._smoothed_point = None
            return HandResult(False, None, None, None)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            self._smoothed_point = None
            return HandResult(False, None, None, None)

        hand_landmarks = results.multi_hand_landmarks[0].landmark
        raw_landmarks = [
            (landmark.x * frame.shape[1], landmark.y * frame.shape[0])
            for landmark in hand_landmarks
        ]

        track_index = 0 if self.track_point_name == "wrist" else 8
        raw_point = raw_landmarks[track_index]
        smoothed_point = self._smooth_point(raw_point, self._smoothed_point)
        self._smoothed_point = smoothed_point

        return HandResult(
            detected=True,
            wrist_pos=smoothed_point,
            raw_landmarks=raw_landmarks,
            track_point=smoothed_point,
        )

    def _smooth_point(
        self,
        raw_point: tuple[float, float],
        previous_point: tuple[float, float] | None,
    ) -> tuple[float, float]:
        if previous_point is None:
            return raw_point
        return (
            previous_point[0] * self.smoothing_alpha
            + raw_point[0] * (1.0 - self.smoothing_alpha),
            previous_point[1] * self.smoothing_alpha
            + raw_point[1] * (1.0 - self.smoothing_alpha),
        )
