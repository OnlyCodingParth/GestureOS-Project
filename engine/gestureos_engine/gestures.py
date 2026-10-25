from enum import Enum
import math


class Gesture(Enum):
    """Supported hand gestures."""

    OPEN_PALM = "OPEN_PALM"
    FIST = "FIST"
    PINCH = "PINCH"
    UNKNOWN = "UNKNOWN"


class GestureRecognizer:
    """Recognize basic gestures from 21 hand landmarks."""

    FINGER_JOINTS = [
        (8, 6),    # Index fingertip and PIP joint
        (12, 10),  # Middle fingertip and PIP joint
        (16, 14),  # Ring fingertip and PIP joint
        (20, 18),  # Pinky fingertip and PIP joint
    ]

    PINCH_THRESHOLD = 0.35

    @staticmethod
    def distance(point1, point2):
        """Calculate 2D Euclidean distance between two landmarks."""

        return math.hypot(
            point1.x - point2.x,
            point1.y - point2.y,
        )

    def recognize(self, landmarks):
        """Return the detected gesture."""

        # Step 1: Validate the landmarks.
        if landmarks is None or len(landmarks) != 21:
            return Gesture.UNKNOWN

        # Step 2: Get thumb and index fingertips.
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]

        # Step 3: Calculate palm width.
        palm_width = self.distance(
            landmarks[5],
            landmarks[17],
        )

        # FIX: Avoid invalid or zero palm width.
        if palm_width <= 1e-6:
            return Gesture.UNKNOWN

        # Step 4: Calculate pinch distance.
        pinch_distance = self.distance(
            thumb_tip,
            index_tip,
        )

        # Step 5: Normalize pinch distance.
        normalized_distance = pinch_distance / palm_width

        # Step 6: Detect pinch gesture.
        if normalized_distance < self.PINCH_THRESHOLD:
            return Gesture.PINCH

        # Step 7: Detect Open Palm and Fist.
        extended_fingers = 0

        for tip_id, pip_id in self.FINGER_JOINTS:
            tip = landmarks[tip_id]
            pip = landmarks[pip_id]

            # Smaller Y means the fingertip is higher.
            if tip.y < pip.y:
                extended_fingers += 1

        # All four fingers are extended.
        if extended_fingers == 4:
            return Gesture.OPEN_PALM

        # All four fingers are folded.
        if extended_fingers == 0:
            return Gesture.FIST

        # Gesture not recognized.
        return Gesture.UNKNOWN