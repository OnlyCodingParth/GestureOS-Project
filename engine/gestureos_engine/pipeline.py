from gestureos_engine.gestures import Gesture
from gestureos_engine.activation import GestureActivation
from gestureos_engine.safety import GestureHoldDetector
from gestureos_engine.cooldown import ActionCooldown
from gestureos_engine.dry_run import DryRunExecutor
from gestureos_engine.emergency import EmergencyStopController
from gestureos_engine.automation import WindowsAutomation


class GestureSafetyPipeline:
    """Coordinate gesture safety checks and dry-run execution."""

    def __init__(
        self,
        hold_duration=0.8,
        cooldown_duration=1.0,
        automation=None,
        emergency_stop_available=True,
    ):
        self.activation = GestureActivation()

        self.hold_detector = GestureHoldDetector(
            hold_duration=hold_duration
        )

        self.cooldown = ActionCooldown(
            cooldown_duration=cooldown_duration
        )

        self.executor = DryRunExecutor(
            activation=self.activation
        )
        self.automation = automation or WindowsAutomation(
            activation=self.activation,
            dry_run=True,
            emergency_stop_available=emergency_stop_available,
        )

        self.emergency = EmergencyStopController(
            activation=self.activation,
            hold_detector=self.hold_detector,
            cooldown=self.cooldown,
        )

    def enable(self):
        """Enable gesture processing after clearing stale hold state."""

        if not self.automation.dry_run and not self.emergency.hotkey_available:
            return False
        self.hold_detector.reset()
        return self.activation.enable()

    def disable(self):
        """Disable actions and clear pending gesture confirmation."""

        self.hold_detector.reset()
        return self.activation.disable()

    def emergency_stop(self):
        """Activate emergency stop and clear safety state."""

        return self.emergency.trigger()

    def reset_emergency(self):
        """Return to DISABLED state after an emergency stop."""

        return self.emergency.reset()

    def process(self, gesture, current_time=None):
        """
        Process a stable gesture through the safety pipeline.

        No real Windows actions are executed.
        """

        if not isinstance(gesture, Gesture):
            raise TypeError("gesture must be a Gesture enum value.")

        if not self.activation.can_execute():
            self.hold_detector.reset()

            return {
                "status": "BLOCKED",
                "reason": "GestureOS is not enabled.",
                "action": None,
            }

        if gesture == Gesture.UNKNOWN:
            self.hold_detector.reset()

            return {
                "status": "IGNORED",
                "reason": "No recognized gesture.",
                "action": None,
            }

        # Step 1: Wait for a continuous gesture hold.
        confirmed = self.hold_detector.update(
            gesture,
            current_time=current_time,
        )

        if not confirmed:
            return {
                "status": "WAITING",
                "reason": "Gesture hold not yet confirmed.",
                "action": None,
            }

        # Step 2: Resolve the gesture's action.
        action = self.executor.ACTION_MAP.get(gesture)

        if action is None:
            return {
                "status": "IGNORED",
                "reason": "No action mapped to this gesture.",
                "action": None,
            }

        # Step 3: Check the action cooldown.
        allowed = self.cooldown.allow(
            action,
            current_time=current_time,
        )

        if not allowed:
            return {
                "status": "COOLDOWN",
                "reason": "Action cooldown is active.",
                "action": action,
            }

        if gesture == Gesture.PINCH:
            result = self.automation.left_click()
            if result.get("action") == "LEFT_CLICK":
                result = {**result, "action": "MOUSE_CLICK"}
            if result["status"] == "SIMULATED":
                self.executor.history.append({
                    "gesture": gesture.value,
                    "action": "MOUSE_CLICK",
                    "mode": "DRY_RUN",
                    "status": "SIMULATED",
                })
            return result
        return self.executor.execute(gesture)

    def tracking_lost(self):
        """Clear gesture confirmation so loss cannot produce an action."""

        self.hold_detector.reset()
        self.cooldown.reset()

    def camera_failed(self):
        """Fail closed when capture cannot provide frames."""

        self.tracking_lost()
        self.activation.camera_failure()

    def start_emergency_stop(self):
        """Register the global stop shortcut before real automation."""

        available = self.emergency.start_hotkey()
        self.automation.emergency_stop_available = available
        return available

    def shutdown(self):
        """Stop the global shortcut and fail closed."""

        self.emergency.trigger()
        self.emergency.stop_hotkey()