import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.gestures import Gesture
from gestureos_engine.activation import ActivationState
from gestureos_engine.pipeline import GestureSafetyPipeline


class TestGestureSafetyPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = GestureSafetyPipeline(
            hold_duration=0.8,
            cooldown_duration=1.0,
        )

    def test_initially_disabled(self):
        self.assertEqual(
            self.pipeline.activation.state,
            ActivationState.DISABLED,
        )

    def test_disabled_blocks_gesture(self):
        result = self.pipeline.process(
            Gesture.PINCH,
            current_time=1.0,
        )

        self.assertEqual(result["status"], "BLOCKED")

    def test_enable(self):
        self.assertTrue(self.pipeline.enable())

        self.assertTrue(
            self.pipeline.activation.can_execute()
        )

    def test_waiting_for_hold(self):
        self.pipeline.enable()

        result = self.pipeline.process(
            Gesture.PINCH,
            current_time=1.0,
        )

        self.assertEqual(result["status"], "WAITING")

    def test_completed_hold_simulates_action(self):
        self.pipeline.enable()

        self.pipeline.process(
            Gesture.PINCH,
            current_time=1.0,
        )

        result = self.pipeline.process(
            Gesture.PINCH,
            current_time=1.8,
        )

        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(result["action"], "MOUSE_CLICK")

    def test_unknown_gesture_ignored(self):
        self.pipeline.enable()

        result = self.pipeline.process(
            Gesture.UNKNOWN,
            current_time=1.0,
        )

        self.assertEqual(result["status"], "IGNORED")

    def test_unknown_resets_hold(self):
        self.pipeline.enable()

        self.pipeline.process(
            Gesture.PINCH,
            current_time=1.0,
        )

        self.pipeline.process(
            Gesture.UNKNOWN,
            current_time=1.5,
        )

        result = self.pipeline.process(
            Gesture.PINCH,
            current_time=2.0,
        )

        self.assertEqual(result["status"], "WAITING")

    def test_disable_blocks_actions(self):
        self.pipeline.enable()
        self.pipeline.disable()

        result = self.pipeline.process(
            Gesture.PINCH,
            current_time=1.0,
        )

        self.assertEqual(result["status"], "BLOCKED")

    def test_emergency_stop_blocks_actions(self):
        self.pipeline.enable()
        self.pipeline.emergency_stop()

        result = self.pipeline.process(
            Gesture.PINCH,
            current_time=1.0,
        )

        self.assertEqual(result["status"], "BLOCKED")

    def test_cannot_enable_during_emergency(self):
        self.pipeline.emergency_stop()

        self.assertFalse(self.pipeline.enable())

    def test_emergency_reset_stays_disabled(self):
        self.pipeline.emergency_stop()
        self.pipeline.reset_emergency()

        self.assertEqual(
            self.pipeline.activation.state,
            ActivationState.DISABLED,
        )

    def test_reenable_after_emergency_reset(self):
        self.pipeline.emergency_stop()
        self.pipeline.reset_emergency()

        self.assertTrue(self.pipeline.enable())

    def test_no_repeated_action_during_same_hold(self):
        self.pipeline.enable()

        self.pipeline.process(
            Gesture.PINCH,
            current_time=1.0,
        )

        self.pipeline.process(
            Gesture.PINCH,
            current_time=1.8,
        )

        result = self.pipeline.process(
            Gesture.PINCH,
            current_time=2.0,
        )

        self.assertEqual(result["status"], "WAITING")

        self.assertEqual(
            len(self.pipeline.executor.history),
            1,
        )

    def test_invalid_gesture(self):
        with self.assertRaises(TypeError):
            self.pipeline.process("PINCH")


if __name__ == "__main__":
    unittest.main(verbosity=2)