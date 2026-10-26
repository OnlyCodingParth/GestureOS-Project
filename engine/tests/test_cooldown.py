import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.cooldown import ActionCooldown


class TestActionCooldown(unittest.TestCase):

    def test_first_action_allowed(self):
        cooldown = ActionCooldown()

        self.assertTrue(
            cooldown.allow("CLICK", current_time=1.0)
        )

    def test_action_blocked_during_cooldown(self):
        cooldown = ActionCooldown(cooldown_duration=1.0)

        cooldown.allow("CLICK", current_time=1.0)

        self.assertFalse(
            cooldown.allow("CLICK", current_time=1.5)
        )

    def test_action_allowed_after_cooldown(self):
        cooldown = ActionCooldown(cooldown_duration=1.0)

        cooldown.allow("CLICK", current_time=1.0)

        self.assertTrue(
            cooldown.allow("CLICK", current_time=2.0)
        )

    def test_independent_action_cooldowns(self):
        cooldown = ActionCooldown(cooldown_duration=1.0)

        self.assertTrue(
            cooldown.allow("CLICK", current_time=1.0)
        )

        self.assertTrue(
            cooldown.allow("SCROLL", current_time=1.2)
        )

        self.assertFalse(
            cooldown.allow("CLICK", current_time=1.3)
        )

    def test_blocked_action_does_not_restart_timer(self):
        cooldown = ActionCooldown(cooldown_duration=1.0)

        cooldown.allow("CLICK", current_time=1.0)
        cooldown.allow("CLICK", current_time=1.5)

        self.assertTrue(
            cooldown.allow("CLICK", current_time=2.0)
        )

    def test_reset_single_action(self):
        cooldown = ActionCooldown()

        cooldown.allow("CLICK", current_time=1.0)
        cooldown.allow("SCROLL", current_time=1.0)

        cooldown.reset("CLICK")

        self.assertTrue(
            cooldown.allow("CLICK", current_time=1.2)
        )

        self.assertFalse(
            cooldown.allow("SCROLL", current_time=1.2)
        )

    def test_reset_all_actions(self):
        cooldown = ActionCooldown()

        cooldown.allow("CLICK", current_time=1.0)
        cooldown.allow("SCROLL", current_time=1.0)

        cooldown.reset()

        self.assertEqual(
            cooldown.last_action_times,
            {},
        )

    def test_invalid_duration(self):
        with self.assertRaises(ValueError):
            ActionCooldown(cooldown_duration=0)

        with self.assertRaises(ValueError):
            ActionCooldown(cooldown_duration=-1)

        with self.assertRaises(ValueError):
            ActionCooldown(cooldown_duration=float("nan"))

    def test_invalid_action_name(self):
        cooldown = ActionCooldown()

        with self.assertRaises(ValueError):
            cooldown.allow("")

        with self.assertRaises(ValueError):
            cooldown.allow("   ")

    def test_backwards_time_blocked(self):
        cooldown = ActionCooldown()

        cooldown.allow("CLICK", current_time=5.0)

        self.assertFalse(
            cooldown.allow("CLICK", current_time=4.0)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)