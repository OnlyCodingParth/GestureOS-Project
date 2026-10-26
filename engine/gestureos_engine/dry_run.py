from datetime import datetime, timezone

from gestureos_engine.gestures import Gesture
from gestureos_engine.activation import GestureActivation


class DryRunExecutor:
    """Simulate gesture actions without controlling Windows."""

    ACTION_MAP = {
        Gesture.PINCH: "MOUSE_CLICK",
        Gesture.OPEN_PALM: "OPEN_PALM_ACTION",
        Gesture.FIST: "FIST_ACTION",
    }

    def __init__(self, activation=None):
        self.activation = (
            activation
            if activation is not None
            else GestureActivation()
        )

        self.history = []

    def execute(self, gesture):
        """
        Simulate an action if gesture control is enabled.

        This method never performs real Windows automation.
        """

        if not isinstance(gesture, Gesture):
            raise TypeError("gesture must be a Gesture enum value.")

        # Block actions when GestureOS is disabled.
        if not self.activation.can_execute():
            return {
                "status": "BLOCKED",
                "reason": "GestureOS is not enabled.",
                "action": None,
            }

        # Find the action mapped to this gesture.
        action = self.ACTION_MAP.get(gesture)

        if action is None:
            return {
                "status": "IGNORED",
                "reason": "No action mapped to this gesture.",
                "action": None,
            }

        # Create a simulated action record.
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gesture": gesture.value,
            "action": action,
            "mode": "DRY_RUN",
            "status": "SIMULATED",
        }

        self.history.append(record)

        print(
            f"[DRY RUN] {gesture.value} -> {action}"
        )

        return record

    def clear_history(self):
        """Remove all simulated action records."""

        self.history.clear()