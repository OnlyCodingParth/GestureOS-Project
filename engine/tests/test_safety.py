import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.gestures import Gesture
from gestureos_engine.safety import GestureHoldDetector


class TestGestureHoldDetector(unittest.TestCase):

    def test_initial_state(self):
        detector = GestureHoldDetector()

        self.assertEqual(
            detector.current_gesture,
            Gesture.UNKNOWN,
        )

        self.assertFalse(detector.confirmed)

    def test_hold_not_completed(self):
        detector = GestureHoldDetector(hold_duration=0.8)

        self.assertFalse(
            detector.update(Gesture.PINCH, current_time=1.0)
        )

        self.assertFalse(
            detector.update(Gesture.PINCH, current_time=1.5)
        )

    def test_hold_completed(self):
        detector = GestureHoldDetector(hold_duration=0.8)

        detector.update(Gesture.PINCH, current_time=1.0)

        self.assertTrue(
            detector.update(Gesture.PINCH, current_time=1.8)
        )

    def test_no_repeated_confirmation(self):
        detector = GestureHoldDetector(hold_duration=0.8)

        detector.update(Gesture.PINCH, current_time=1.0)
        detector.update(Gesture.PINCH, current_time=1.8)

        self.assertFalse(
            detector.update(Gesture.PINCH, current_time=2.0)
        )

    def test_gesture_change_resets_timer(self):
        detector = GestureHoldDetector(hold_duration=0.8)

        detector.update(Gesture.PINCH, current_time=1.0)

        self.assertFalse(
            detector.update(Gesture.FIST, current_time=1.5)
        )

        self.assertFalse(
            detector.update(Gesture.FIST, current_time=2.0)
        )

        self.assertTrue(
            detector.update(Gesture.FIST, current_time=2.3)
        )

    def test_unknown_resets_timer(self):
        detector = GestureHoldDetector(hold_duration=0.8)

        detector.update(Gesture.PINCH, current_time=1.0)
        detector.update(Gesture.UNKNOWN, current_time=1.5)

        self.assertFalse(
            detector.update(Gesture.PINCH, current_time=2.0)
        )

        self.assertFalse(
            detector.update(Gesture.PINCH, current_time=2.5)
        )

    def test_invalid_duration(self):
        with self.assertRaises(ValueError):
            GestureHoldDetector(hold_duration=0)

        with self.assertRaises(ValueError):
            GestureHoldDetector(hold_duration=-1)

    def test_invalid_gesture(self):
        detector = GestureHoldDetector()

        with self.assertRaises(TypeError):
            detector.update("PINCH")

    def test_manual_reset(self):
        detector = GestureHoldDetector(hold_duration=0.8)

        detector.update(Gesture.PINCH, current_time=1.0)
        detector.reset()

        self.assertEqual(
            detector.current_gesture,
            Gesture.UNKNOWN,
        )

        self.assertIsNone(detector.start_time)
        self.assertFalse(detector.confirmed)


if __name__ == "__main__":
    unittest.main(verbosity=2)