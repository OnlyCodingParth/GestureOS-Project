import math


class MouseController:
    """Convert normalized hand coordinates into screen coordinates."""

    def __init__(
        self,
        screen_width,
        screen_height,
        smoothing=0.25,
        margin=0.05,
        dead_zone=0.0,
        max_step=None,
        jump_threshold=None,
        sensitivity=1.0,
    ):
        if screen_width <= 0 or screen_height <= 0:
            raise ValueError("Screen dimensions must be positive.")

        if not 0 < smoothing <= 1:
            raise ValueError("Smoothing must be between 0 and 1.")

        if not 0 <= margin < 0.5:
            raise ValueError("Margin must be between 0 and 0.5.")
        if dead_zone < 0:
            raise ValueError("dead_zone must not be negative.")
        if max_step is not None and max_step <= 0:
            raise ValueError("max_step must be positive.")
        if jump_threshold is not None and jump_threshold <= 0:
            raise ValueError("jump_threshold must be positive.")
        if sensitivity <= 0:
            raise ValueError("sensitivity must be positive.")

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.smoothing = smoothing
        self.margin = margin
        self.dead_zone = dead_zone
        self.max_step = max_step
        self.jump_threshold = jump_threshold
        self.sensitivity = sensitivity

        self.previous_x = None
        self.previous_y = None

    def map_coordinates(self, x, y):
        """Map normalized hand coordinates to screen coordinates."""

        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError("Coordinates must be finite.")

        usable_area = 1.0 - (2.0 * self.margin)

        normalized_x = (x - self.margin) / usable_area
        normalized_y = (y - self.margin) / usable_area

        normalized_x = max(0.0, min(1.0, normalized_x))
        normalized_y = max(0.0, min(1.0, normalized_y))

        screen_x = normalized_x * (self.screen_width - 1)
        screen_y = normalized_y * (self.screen_height - 1)

        return screen_x, screen_y

    def smooth_coordinates(self, x, y):
        """Apply exponential smoothing to cursor movement."""

        if self.previous_x is None:
            self.previous_x = x
            self.previous_y = y

            return round(x), round(y)

        target_x = self.previous_x + (x - self.previous_x) * self.sensitivity
        target_y = self.previous_y + (y - self.previous_y) * self.sensitivity
        dx = target_x - self.previous_x
        dy = target_y - self.previous_y
        distance = math.hypot(dx, dy)
        if distance <= self.dead_zone:
            return round(self.previous_x), round(self.previous_y)
        if self.jump_threshold is not None and distance > self.jump_threshold:
            scale = self.jump_threshold / distance
            target_x = self.previous_x + dx * scale
            target_y = self.previous_y + dy * scale
        if self.max_step is not None and distance > self.max_step:
            scale = self.max_step / distance
            target_x = self.previous_x + dx * scale
            target_y = self.previous_y + dy * scale

        smooth_x = (
            self.previous_x
            + self.smoothing * (target_x - self.previous_x)
        )

        smooth_y = (
            self.previous_y
            + self.smoothing * (target_y - self.previous_y)
        )

        self.previous_x = smooth_x
        self.previous_y = smooth_y

        return round(smooth_x), round(smooth_y)

    def update(self, x, y):
        """Convert hand position into smoothed screen coordinates."""

        mapped_x, mapped_y = self.map_coordinates(x, y)

        return self.smooth_coordinates(mapped_x, mapped_y)

    def reset(self):
        """Reset smoothing history."""

        self.previous_x = None
        self.previous_y = None