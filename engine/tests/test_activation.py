import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.activation import (
    ActivationState,
    GestureActivation,
)


class TestGestureActivation(unittest.TestCase):

    def setUp(self):
        self.activation = GestureActivation()

    def test_initial_state_disabled(self):
        self.assertEqual(
            self.activation.state,
            ActivationState.DISABLED,
        )

        self.assertFalse(self.activation.can_execute())

    def test_enable(self):
        self.assertTrue(self.activation.enable())

        self.assertEqual(
            self.activation.state,
            ActivationState.ENABLED,
        )

        self.assertTrue(self.activation.can_execute())

    def test_disable(self):
        self.activation.enable()

        self.assertTrue(self.activation.disable())

        self.assertEqual(
            self.activation.state,
            ActivationState.DISABLED,
        )

        self.assertFalse(self.activation.can_execute())

    def test_emergency_stop(self):
        self.activation.enable()
        self.activation.emergency_stop()

        self.assertEqual(
            self.activation.state,
            ActivationState.EMERGENCY_STOPPED,
        )

        self.assertFalse(self.activation.can_execute())

    def test_cannot_enable_after_emergency(self):
        self.activation.emergency_stop()

        self.assertFalse(self.activation.enable())
        self.assertFalse(self.activation.can_execute())

    def test_cannot_disable_after_emergency(self):
        self.activation.emergency_stop()

        self.assertFalse(self.activation.disable())

        self.assertEqual(
            self.activation.state,
            ActivationState.EMERGENCY_STOPPED,
        )

    def test_reset_emergency(self):
        self.activation.emergency_stop()

        self.assertTrue(self.activation.reset_emergency())

        self.assertEqual(
            self.activation.state,
            ActivationState.DISABLED,
        )

        self.assertFalse(self.activation.can_execute())

    def test_reset_without_emergency(self):
        self.assertFalse(self.activation.reset_emergency())

    def test_enable_after_emergency_reset(self):
        self.activation.emergency_stop()
        self.activation.reset_emergency()

        self.assertTrue(self.activation.enable())
        self.assertTrue(self.activation.can_execute())

    def test_repeated_emergency_stop(self):
        self.activation.emergency_stop()
        self.activation.emergency_stop()

        self.assertEqual(
            self.activation.state,
            ActivationState.EMERGENCY_STOPPED,
        )

        self.assertFalse(self.activation.can_execute())


if __name__ == "__main__":
    unittest.main(verbosity=2)