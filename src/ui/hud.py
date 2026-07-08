from __future__ import annotations

import cv2
import numpy as np


class HUD:
    def __init__(self, font_scale: float = 0.5, thickness: int = 1) -> None:
        self.font_scale = font_scale
        self.thickness = thickness

    def draw(
        self,
        frame: np.ndarray,
        state: str,
        fps: float,
        track_point: tuple[float, float] | None,
    ) -> None:
        """Render a minimal HUD with state, FPS, and tracked-point information."""
        y = 20
        for line in self._build_lines(state, fps, track_point):
            cv2.putText(
                frame,
                line,
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                self.font_scale,
                (0, 255, 0),
                self.thickness,
                cv2.LINE_AA,
            )
            y += 24

    def _build_lines(
        self,
        state: str,
        fps: float,
        track_point: tuple[float, float] | None,
    ) -> list[str]:
        lines = [f"STATE: {state.upper()}", f"FPS: {fps:.0f}"]
        if track_point is not None:
            lines.append(f"TRACK: ({track_point[0]:.1f}, {track_point[1]:.1f})")
        return lines
