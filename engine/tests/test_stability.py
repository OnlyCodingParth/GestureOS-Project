import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.gestures import Gesture
from gestureos_engine.stability import GestureStabilizer


class TestGestureStabilizer(unittest.TestCase):

    def test_initial_state(self):
        stabilizer = GestureStabilizer()

        self.assertEqual(
            stabilizer.stable_gesture,
            Gesture.UNKNOWN,
        )

    def test_stable_open_palm(self):
        stabilizer = GestureStabilizer()

        stabilizer.update(Gesture.OPEN_PALM)
        stabilizer.update(Gesture.OPEN_PALM)

        result = stabilizer.update(Gesture.OPEN_PALM)

        self.assertEqual(result, Gesture.OPEN_PALM)

    def test_single_frame_noise(self):
        stabilizer = GestureStabilizer()

        for _ in range(3):
            stabilizer.update(Gesture.OPEN_PALM)

        result = stabilizer.update(Gesture.UNKNOWN)

        self.assertEqual(result, Gesture.OPEN_PALM)

    def test_switch_to_fist(self):
        stabilizer = GestureStabilizer()

        for _ in range(3):
            stabilizer.update(Gesture.OPEN_PALM)

        for _ in range(5):
            result = stabilizer.update(Gesture.FIST)

        self.assertEqual(result, Gesture.FIST)

    def test_reset(self):
        stabilizer = GestureStabilizer()

        for _ in range(3):
            stabilizer.update(Gesture.PINCH)

        stabilizer.reset()

        self.assertEqual(
            stabilizer.stable_gesture,
            Gesture.UNKNOWN,
        )

        self.assertEqual(len(stabilizer.history), 0)

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            GestureStabilizer(window_size=0)

        with self.assertRaises(ValueError):
            GestureStabilizer(window_size=5, minimum_votes=6)

    def test_invalid_gesture(self):
        stabilizer = GestureStabilizer()

        with self.assertRaises(TypeError):
            stabilizer.update("OPEN_PALM")


if __name__ == "__main__":
    unittest.main(verbosity=2)