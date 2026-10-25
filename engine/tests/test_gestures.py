import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.gestures import Gesture, GestureRecognizer


class TestGestureRecognizer(unittest.TestCase):

    def setUp(self):
        self.recognizer = GestureRecognizer()

        self.landmarks = [
            SimpleNamespace(x=0.5, y=0.5)
            for _ in range(21)
        ]

        # Set palm width to 0.4.
        self.landmarks[5].x = 0.3
        self.landmarks[17].x = 0.7

        # Keep thumb away from index by default.
        self.landmarks[4].x = 0.1
        self.landmarks[4].y = 0.1

    def test_open_palm(self):
        for tip, pip in self.recognizer.FINGER_JOINTS:
            self.landmarks[tip].y = 0.2
            self.landmarks[pip].y = 0.4

        self.assertEqual(
            self.recognizer.recognize(self.landmarks),
            Gesture.OPEN_PALM,
        )

    def test_fist(self):
        for tip, pip in self.recognizer.FINGER_JOINTS:
            self.landmarks[tip].y = 0.6
            self.landmarks[pip].y = 0.4

        self.assertEqual(
            self.recognizer.recognize(self.landmarks),
            Gesture.FIST,
        )

    def test_pinch(self):
        self.landmarks[4].x = 0.5
        self.landmarks[4].y = 0.5

        self.landmarks[8].x = 0.52
        self.landmarks[8].y = 0.51

        self.assertEqual(
            self.recognizer.recognize(self.landmarks),
            Gesture.PINCH,
        )

    def test_unknown(self):
        self.assertEqual(
            self.recognizer.recognize([]),
            Gesture.UNKNOWN,
        )

    def test_none(self):
        self.assertEqual(
            self.recognizer.recognize(None),
            Gesture.UNKNOWN,
        )

    def test_zero_palm_width(self):
        self.landmarks[5].x = 0.5
        self.landmarks[17].x = 0.5

        self.assertEqual(
            self.recognizer.recognize(self.landmarks),
            Gesture.UNKNOWN,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)