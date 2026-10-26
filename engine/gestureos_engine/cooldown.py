import math
import time


class ActionCooldown:
    """Prevent an action from triggering too frequently."""

    def __init__(self, cooldown_duration=1.0):
        if not math.isfinite(cooldown_duration) or cooldown_duration <= 0:
            raise ValueError(
                "cooldown_duration must be a positive finite number."
            )

        self.cooldown_duration = cooldown_duration
        self.last_action_times = {}

    def allow(self, action_name, current_time=None):
        """
        Return True if the action is allowed.

        An allowed action immediately starts its cooldown.
        """

        if not isinstance(action_name, str) or not action_name.strip():
            raise ValueError("action_name must be a non-empty string.")

        if current_time is None:
            current_time = time.monotonic()

        if not math.isfinite(current_time):
            raise ValueError("current_time must be finite.")

        last_time = self.last_action_times.get(action_name)

        # First occurrence of an action is allowed.
        if last_time is None:
            self.last_action_times[action_name] = current_time
            return True

        elapsed = current_time - last_time

        # Reject invalid backwards time values.
        if elapsed < 0:
            return False

        # Block the action while cooldown is active.
        if elapsed < self.cooldown_duration and not math.isclose(
            elapsed,
            self.cooldown_duration,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            return False

        # Cooldown completed.
        self.last_action_times[action_name] = current_time
        return True

    def reset(self, action_name=None):
        """Reset one action or all cooldowns."""

        if action_name is None:
            self.last_action_times.clear()
        else:
            self.last_action_times.pop(action_name, None)