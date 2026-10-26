import time
import math

from gestureos_engine.gestures import Gesture


class GestureHoldDetector:
    """Confirm a gesture only after it is held continuously."""

    def __init__(self, hold_duration=0.8):
        if hold_duration <= 0:
            raise ValueError("hold_duration must be greater than zero.")

        self.hold_duration = hold_duration
        self.current_gesture = Gesture.UNKNOWN
        self.start_time = None
        self.confirmed = False

    def update(self, gesture, current_time=None):
        """Return True once a gesture has been held long enough."""

        if not isinstance(gesture, Gesture):
            raise TypeError("gesture must be a Gesture enum value.")

        if current_time is None:
            current_time = time.monotonic()

        # UNKNOWN must never trigger an action.
        if gesture == Gesture.UNKNOWN:
            self.reset()
            return False

        # Start a new timer when the gesture changes.
        if gesture != self.current_gesture:
            self.current_gesture = gesture
            self.start_time = current_time
            self.confirmed = False
            return False

        # Do not confirm the same continuous hold twice.
        if self.confirmed:
            return False

        elapsed = current_time - self.start_time

        # Handle small floating-point precision differences.
        if elapsed >= self.hold_duration or math.isclose(
            elapsed,
            self.hold_duration,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            self.confirmed = True
            return True

        return False

    def reset(self):
        """Clear the current gesture and its hold timer."""

        self.current_gesture = Gesture.UNKNOWN
        self.start_time = None
        self.confirmed = False