import pyautogui
import time


class WindowsAutomation:
    """Execute Windows mouse actions with explicit safety checks."""

    def __init__(
        self,
        activation,
        dry_run=True,
        emergency_stop_available=None,
    ):
        if activation is None:
            raise ValueError("An activation controller is required.")

        self.activation = activation
        self.dry_run = dry_run
        self.emergency_stop_available = (
            dry_run
            if emergency_stop_available is None
            else emergency_stop_available
        )

        # PyAutoGUI emergency fail-safe.
        pyautogui.FAILSAFE = True

        # Small pause between automation operations.
        pyautogui.PAUSE = 0.1

    def left_click(self):
        """Perform or simulate a left mouse click."""

        if not self.activation.can_execute():
            return {
                "status": "BLOCKED",
                "reason": "GestureOS is disabled.",
            }

        if not self.dry_run and not self.emergency_stop_available:
            return {
                "status": "BLOCKED",
                "reason": "Emergency stop is unavailable.",
            }

        if self.dry_run:
            return {
                "status": "SIMULATED",
                "action": "LEFT_CLICK",
            }

        try:
            pyautogui.click(button="left")

            return {
                "status": "EXECUTED",
                "action": "LEFT_CLICK",
            }

        except pyautogui.FailSafeException:
            self.activation.emergency_stop()

            return {
                "status": "EMERGENCY_STOPPED",
                "reason": "PyAutoGUI fail-safe triggered.",
            }
        except Exception as exc:
            self.activation.emergency_stop()
            return {"status": "ERROR", "reason": str(exc)}

    def right_click(self):
        """Perform or simulate a right mouse click."""

        if not self.activation.can_execute():
            return {
                "status": "BLOCKED",
                "reason": "GestureOS is disabled.",
            }

        if not self.dry_run and not self.emergency_stop_available:
            return {
                "status": "BLOCKED",
                "reason": "Emergency stop is unavailable.",
            }

        if self.dry_run:
            return {
                "status": "SIMULATED",
                "action": "RIGHT_CLICK",
            }

        try:
            pyautogui.click(button="right")

            return {
                "status": "EXECUTED",
                "action": "RIGHT_CLICK",
            }

        except pyautogui.FailSafeException:
            self.activation.emergency_stop()

            return {
                "status": "EMERGENCY_STOPPED",
                "reason": "PyAutoGUI fail-safe triggered.",
            }
        except Exception as exc:
            self.activation.emergency_stop()
            return {"status": "ERROR", "reason": str(exc)}

    def scroll(self, amount, cooldown, current_time=None):
        """Perform one bounded, rate-limited vertical scroll operation."""

        if not isinstance(amount, int) or amount == 0:
            raise ValueError("amount must be a non-zero integer.")
        if abs(amount) > 5:
            raise ValueError("scroll amount must be between -5 and 5.")
        if not self.activation.can_execute():
            return {"status": "BLOCKED", "reason": "GestureOS is disabled."}
        if not cooldown.allow("MOUSE_SCROLL", current_time):
            return {"status": "COOLDOWN", "action": "MOUSE_SCROLL"}
        if not self.dry_run and not self.emergency_stop_available:
            return {
                "status": "BLOCKED",
                "reason": "Emergency stop is unavailable.",
            }
        if self.dry_run:
            return {"status": "SIMULATED", "action": "MOUSE_SCROLL", "amount": amount}
        try:
            pyautogui.scroll(amount)
            return {"status": "EXECUTED", "action": "MOUSE_SCROLL", "amount": amount}
        except Exception as exc:
            self.activation.emergency_stop()
            return {"status": "ERROR", "reason": str(exc)}