from pathlib import Path

import cv2
import mediapipe as mp


class HandTracker:
    """Detect hand landmarks using MediaPipe Tasks API."""

    def __init__(self, model_path=None, max_hands=2):
        if model_path is None:
            model_path = (
                Path(__file__).resolve().parent
                / "models"
                / "hand_landmarker.task"
            )

        model_path = Path(model_path)

        if not model_path.is_file():
            raise FileNotFoundError(
                f"Hand Landmarker model not found: {model_path}"
            )

        if max_hands < 1:
            raise ValueError("max_hands must be at least 1.")

        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=str(model_path)
            ),
            running_mode=VisionRunningMode.IMAGE,
            num_hands=max_hands,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.landmarker = HandLandmarker.create_from_options(options)

    def detect(self, frame):
        """Return MediaPipe hand detection results for a BGR frame."""

        if frame is None:
            raise ValueError("Frame cannot be None.")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        return self.landmarker.detect(mp_image)

    def close(self):
        """Release MediaPipe resources."""

        if self.landmarker is not None:
            self.landmarker.close()
            self.landmarker = None