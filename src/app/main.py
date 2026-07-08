from __future__ import annotations

import importlib

import cv2

try:
    landmark_pb2 = importlib.import_module("mediapipe.framework.formats.landmark_pb2")
    mp_drawing = importlib.import_module("mediapipe.python.solutions.drawing_utils")
    mp_hands = importlib.import_module("mediapipe.python.solutions.hands")
except (
    ImportError
):  # pragma: no cover - unavailable dependency mirrors HandTracker fallback
    landmark_pb2 = None
    mp_drawing = None
    mp_hands = None

from src.core.camera import Camera, CameraError
from src.core.config import load_config
from src.core.logger import get_logger, initialize_logging
from src.ui.fps_counter import FpsCounter
from src.ui.hud import HUD
from src.vision.hand_tracker import HandTracker


def main() -> int:
    """Run the Sprint 01 webcam and hand-tracking loop."""
    config = load_config()
    initialize_logging()
    logger = get_logger("src.app.main")

    camera: Camera | None = None
    fps_counter: FpsCounter | None = None
    hud: HUD | None = None
    hand_tracker: HandTracker | None = None

    try:
        camera = Camera(
            device_index=config.camera_device_index,
            target_width=config.target_width,
            target_height=config.target_height,
            mirror_feed=config.mirror_feed,
        )
        fps_counter = FpsCounter(window_size=config.fps_window_size)
        hud = HUD()
        hand_tracker = HandTracker(
            max_num_hands=config.max_num_hands,
            track_point=config.track_point,
            smoothing_alpha=config.smoothing_alpha,
        )

        cv2.namedWindow("Doctor Strange Portal", cv2.WINDOW_NORMAL)
        logger.info("Camera ready; starting frame loop")

        while True:
            frame = camera.read()
            if fps_counter is not None:
                fps_counter.update()
            fps = fps_counter.get_fps() if fps_counter is not None else 0.0

            if hand_tracker is not None:
                hand_result = hand_tracker.process(frame)
                state = "TRACKING" if hand_result.detected else "WAITING"
                if hand_result.raw_landmarks:
                    _draw_landmarks(frame, hand_result.raw_landmarks)
                    if hand_result.track_point is not None:
                        x, y = map(int, hand_result.track_point)
                        cv2.circle(frame, (x, y), 7, (0, 0, 255), -1)
                        cv2.circle(frame, (x, y), 3, (255, 255, 255), -1)
            else:
                state = "WAITING"
                hand_result = None

            if hud is not None:
                hud.draw(
                    frame,
                    state,
                    fps,
                    hand_result.track_point if hand_result is not None else None,
                )

            cv2.imshow("Doctor Strange Portal", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in {ord("q"), ord("Q")}:
                break
    except CameraError as exc:
        logger.error("Camera error: %s", exc)
        return 1
    except Exception as exc:  # pragma: no cover - defensive branch
        logger.exception("Unexpected runtime error: %s", exc)
        return 1
    finally:
        if camera is not None:
            camera.release()
        cv2.destroyAllWindows()

    logger.info("Application shutdown complete")
    return 0


def _draw_landmarks(frame: cv2.Mat, landmarks: list[tuple[float, float]]) -> None:
    if landmark_pb2 is None or mp_drawing is None or mp_hands is None:
        return

    height, width = frame.shape[:2]
    normalized_landmarks = landmark_pb2.NormalizedLandmarkList(
        landmark=[
            landmark_pb2.NormalizedLandmark(x=x / width, y=y / height)
            for x, y in landmarks
        ]
    )
    mp_drawing.draw_landmarks(
        frame,
        normalized_landmarks,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
        mp_drawing.DrawingSpec(color=(0, 200, 255), thickness=2, circle_radius=2),
    )


if __name__ == "__main__":
    raise SystemExit(main())
