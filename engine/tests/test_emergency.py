import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.gestures import Gesture
from gestureos_engine.activation import (
    GestureActivation,
    ActivationState,
)
from gestureos_engine.safety import GestureHoldDetector
from gestureos_engine.cooldown import ActionCooldown
from gestureos_engine.emergency import EmergencyStopController


class TestEmergencyStopController(unittest.TestCase):

    def setUp(self):
        self.activation = GestureActivation()
        self.hold_detector = GestureHoldDetector()
        self.cooldown = ActionCooldown()

        self.controller = EmergencyStopController(
            activation=self.activation,
            hold_detector=self.hold_detector,
            cooldown=self.cooldown,
        )

    def test_initial_state(self):
        self.assertFalse(self.controller.is_stopped())

    def test_trigger_emergency(self):
        self.activation.enable()

        state = self.controller.trigger()

        self.assertEqual(
            state,
            ActivationState.EMERGENCY_STOPPED,
        )

        self.assertTrue(self.controller.is_stopped())

    def test_emergency_blocks_actions(self):
        self.activation.enable()

        self.controller.trigger()

        self.assertFalse(
            self.controller.can_execute()
        )

    def test_hold_detector_resets(self):
        self.hold_detector.update(
            Gesture.PINCH,
            current_time=1.0,
        )

        self.controller.trigger()

        self.assertEqual(
            self.hold_detector.current_gesture,
            Gesture.UNKNOWN,
        )

        self.assertIsNone(
            self.hold_detector.start_time
        )

    def test_cooldown_resets(self):
        self.cooldown.allow(
            "MOUSE_CLICK",
            current_time=1.0,
        )

        self.controller.trigger()

        self.assertEqual(
            self.cooldown.last_action_times,
            {},
        )

    def test_cannot_enable_during_emergency(self):
        self.controller.trigger()

        self.assertFalse(
            self.activation.enable()
        )

    def test_reset_returns_disabled(self):
        self.controller.trigger()

        self.assertTrue(
            self.controller.reset()
        )

        self.assertEqual(
            self.activation.state,
            ActivationState.DISABLED,
        )

    def test_reset_does_not_auto_enable(self):
        self.controller.trigger()
        self.controller.reset()

        self.assertFalse(
            self.controller.can_execute()
        )

    def test_manual_enable_after_reset(self):
        self.controller.trigger()
        self.controller.reset()

        self.assertTrue(
            self.activation.enable()
        )

        self.assertTrue(
            self.controller.can_execute()
        )

    def test_repeated_emergency_trigger(self):
        self.controller.trigger()
        self.controller.trigger()

        self.assertTrue(
            self.controller.is_stopped()
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)