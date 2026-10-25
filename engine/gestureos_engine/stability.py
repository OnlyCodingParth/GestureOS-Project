from collections import deque

from gestureos_engine.gestures import Gesture


class GestureStabilizer:
    """Stabilize gesture predictions using a sliding window."""

    def __init__(self, window_size=5, minimum_votes=3):
        if window_size < 1:
            raise ValueError("window_size must be at least 1.")

        if not 1 <= minimum_votes <= window_size:
            raise ValueError(
                "minimum_votes must be between 1 and window_size."
            )

        self.window_size = window_size
        self.minimum_votes = minimum_votes

        self.history = deque(maxlen=window_size)
        self.stable_gesture = Gesture.UNKNOWN

    def update(self, gesture):
        """Update gesture history and return the stable gesture."""

        if not isinstance(gesture, Gesture):
            raise TypeError("gesture must be a Gesture enum value.")

        self.history.append(gesture)

        # Count how many times each gesture appears.
        counts = {}

        for item in self.history:
            counts[item] = counts.get(item, 0) + 1

        # Find the most frequent gesture.
        candidate = max(counts, key=counts.get)

        # Update only when enough frames agree.
        if counts[candidate] >= self.minimum_votes:
            self.stable_gesture = candidate

        return self.stable_gesture

    def reset(self):
        """Clear gesture history and reset the stable gesture."""

        self.history.clear()
        self.stable_gesture = Gesture.UNKNOWN