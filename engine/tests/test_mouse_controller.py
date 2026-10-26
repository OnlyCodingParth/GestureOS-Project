import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.mouse_controller import MouseController


class TestMouseController(unittest.TestCase):

    def setUp(self):
        self.controller = MouseController(
            screen_width=1920,
            screen_height=1080,
            smoothing=0.25,
            margin=0.05,
        )

    def test_center_coordinates(self):
        x, y = self.controller.map_coordinates(0.5, 0.5)

        self.assertAlmostEqual(x, 959.5)
        self.assertAlmostEqual(y, 539.5)

    def test_top_left_boundary(self):
        x, y = self.controller.map_coordinates(0.0, 0.0)

        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

    def test_bottom_right_boundary(self):
        x, y = self.controller.map_coordinates(1.0, 1.0)

        self.assertEqual(x, 1919)
        self.assertEqual(y, 1079)

    def test_clamping(self):
        x, y = self.controller.map_coordinates(-0.5, 1.5)

        self.assertEqual(x, 0)
        self.assertEqual(y, 1079)

    def test_first_update(self):
        x, y = self.controller.update(0.5, 0.5)

        self.assertEqual(x, 960)
        self.assertEqual(y, 540)

    def test_smoothing(self):
        self.controller.update(0.5, 0.5)

        x, y = self.controller.update(0.75, 0.75)

        self.assertGreater(x, 960)
        self.assertLess(x, 1493)

        self.assertGreater(y, 540)
        self.assertLess(y, 839)

    def test_reset(self):
        self.controller.update(0.5, 0.5)

        self.controller.reset()

        self.assertIsNone(self.controller.previous_x)
        self.assertIsNone(self.controller.previous_y)

    def test_invalid_screen_size(self):
        with self.assertRaises(ValueError):
            MouseController(0, 1080)

    def test_invalid_smoothing(self):
        with self.assertRaises(ValueError):
            MouseController(1920, 1080, smoothing=0)

    def test_invalid_margin(self):
        with self.assertRaises(ValueError):
            MouseController(1920, 1080, margin=0.5)

    def test_invalid_coordinates(self):
        with self.assertRaises(ValueError):
            self.controller.update(float("nan"), 0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)