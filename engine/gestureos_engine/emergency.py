from gestureos_engine.activation import (
    GestureActivation,
    ActivationState,
)

from gestureos_engine.safety import GestureHoldDetector
from gestureos_engine.cooldown import ActionCooldown
from gestureos_engine.hotkey import GlobalEmergencyHotkey


class EmergencyStopController:
    """Manage emergency stop across GestureOS safety components."""

    def __init__(
        self,
        activation=None,
        hold_detector=None,
        cooldown=None,
        hotkey=None,
    ):
        self.activation = (
            activation
            if activation is not None
            else GestureActivation()
        )

        self.hold_detector = (
            hold_detector
            if hold_detector is not None
            else GestureHoldDetector()
        )

        self.cooldown = (
            cooldown
            if cooldown is not None
            else ActionCooldown()
        )
        self.hotkey = hotkey
        self.hotkey_available = hotkey is not None

    def trigger(self):
        """Activate emergency stop and reset safety components."""

        self.activation.emergency_stop()

        self.hold_detector.reset()

        self.cooldown.reset()

        return self.activation.state

    def start_hotkey(self):
        """Start the independent stop shortcut; return False on failure."""

        if self.hotkey is None:
            self.hotkey = GlobalEmergencyHotkey(self.trigger)
        try:
            self.hotkey_available = self.hotkey.start()
        except (AttributeError, OSError, RuntimeError):
            self.hotkey_available = False
        return self.hotkey_available

    def stop_hotkey(self):
        if self.hotkey is not None:
            self.hotkey.stop()
        self.hotkey_available = False

    def reset(self):
        """Reset emergency stop without automatically enabling GestureOS."""

        self.hold_detector.reset()

        self.cooldown.reset()

        return self.activation.reset_emergency()

    def is_stopped(self):
        """Return True when emergency stop is active."""

        return (
            self.activation.state
            == ActivationState.EMERGENCY_STOPPED
        )

    def can_execute(self):
        """Check whether gesture actions are permitted."""

        return self.activation.can_execute()