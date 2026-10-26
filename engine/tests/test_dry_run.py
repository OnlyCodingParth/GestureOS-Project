import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.gestures import Gesture
from gestureos_engine.activation import GestureActivation
from gestureos_engine.dry_run import DryRunExecutor


class TestDryRunExecutor(unittest.TestCase):

    def setUp(self):
        self.activation = GestureActivation()

        self.executor = DryRunExecutor(
            activation=self.activation
        )

    def test_disabled_blocks_action(self):
        result = self.executor.execute(Gesture.PINCH)

        self.assertEqual(
            result["status"],
            "BLOCKED",
        )

        self.assertEqual(len(self.executor.history), 0)

    def test_enabled_simulates_action(self):
        self.activation.enable()

        result = self.executor.execute(Gesture.PINCH)

        self.assertEqual(
            result["status"],
            "SIMULATED",
        )

        self.assertEqual(
            result["action"],
            "MOUSE_CLICK",
        )

        self.assertEqual(
            result["mode"],
            "DRY_RUN",
        )

    def test_open_palm_mapping(self):
        self.activation.enable()

        result = self.executor.execute(Gesture.OPEN_PALM)

        self.assertEqual(
            result["action"],
            "OPEN_PALM_ACTION",
        )

    def test_fist_mapping(self):
        self.activation.enable()

        result = self.executor.execute(Gesture.FIST)

        self.assertEqual(
            result["action"],
            "FIST_ACTION",
        )

    def test_unknown_gesture_ignored(self):
        self.activation.enable()

        result = self.executor.execute(Gesture.UNKNOWN)

        self.assertEqual(
            result["status"],
            "IGNORED",
        )

    def test_emergency_stop_blocks_action(self):
        self.activation.enable()
        self.activation.emergency_stop()

        result = self.executor.execute(Gesture.PINCH)

        self.assertEqual(
            result["status"],
            "BLOCKED",
        )

    def test_history_recorded(self):
        self.activation.enable()

        self.executor.execute(Gesture.PINCH)
        self.executor.execute(Gesture.FIST)

        self.assertEqual(
            len(self.executor.history),
            2,
        )

    def test_clear_history(self):
        self.activation.enable()

        self.executor.execute(Gesture.PINCH)

        self.executor.clear_history()

        self.assertEqual(
            len(self.executor.history),
            0,
        )

    def test_invalid_gesture(self):
        with self.assertRaises(TypeError):
            self.executor.execute("PINCH")

    def test_default_activation_disabled(self):
        executor = DryRunExecutor()

        result = executor.execute(Gesture.PINCH)

        self.assertEqual(
            result["status"],
            "BLOCKED",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)