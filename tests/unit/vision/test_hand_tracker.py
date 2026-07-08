from __future__ import annotations

from src.vision.hand_tracker import HandTracker


def test_ema_smoothing_converges_without_overshoot() -> None:
    tracker = HandTracker(max_num_hands=1, track_point="wrist", smoothing_alpha=0.5)
    raw_points = [(0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 0.0)]

    smoothed = tracker._smooth_point(raw_points[0], None)
    for point in raw_points[1:]:
        smoothed = tracker._smooth_point(point, smoothed)

    assert smoothed[0] > 20.0
    assert smoothed[1] == 0.0


def test_track_point_uses_configured_point() -> None:
    tracker = HandTracker(max_num_hands=1, track_point="index_tip")

    assert tracker.track_point_name == "index_tip"
