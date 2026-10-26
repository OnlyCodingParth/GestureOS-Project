from enum import Enum


class ActivationState(Enum):
    """Possible GestureOS activation states."""

    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    EMERGENCY_STOPPED = "EMERGENCY_STOPPED"


class GestureActivation:
    """Manage permission to execute gesture-controlled actions."""

    def __init__(self):
        # GestureOS must start in a safe, disabled state.
        self.state = ActivationState.DISABLED

    def enable(self):
        """Enable gesture-controlled actions."""

        # Emergency stop cannot be bypassed by enable().
        if self.state == ActivationState.EMERGENCY_STOPPED:
            return False

        self.state = ActivationState.ENABLED
        return True

    def disable(self):
        """Disable gesture-controlled actions."""

        # Preserve emergency-stop state until explicitly reset.
        if self.state == ActivationState.EMERGENCY_STOPPED:
            return False

        self.state = ActivationState.DISABLED
        return True

    def emergency_stop(self):
        """Immediately block all gesture-controlled actions."""

        self.state = ActivationState.EMERGENCY_STOPPED

    def camera_failure(self):
        """Fail closed when camera input is unavailable."""

        self.emergency_stop()

    def reset_emergency(self):
        """Reset emergency stop to the safe DISABLED state."""

        if self.state != ActivationState.EMERGENCY_STOPPED:
            return False

        self.state = ActivationState.DISABLED
        return True

    def can_execute(self):
        """Return True only when gesture control is enabled."""

        return self.state == ActivationState.ENABLED