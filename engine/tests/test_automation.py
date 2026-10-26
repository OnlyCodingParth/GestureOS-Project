import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.activation import GestureActivation
from gestureos_engine.automation import WindowsAutomation


class TestWindowsAutomation(unittest.TestCase):

    def setUp(self):
        self.activation = GestureActivation()

        self.automation = WindowsAutomation(
            activation=self.activation,
            dry_run=True,
        )

    def test_initially_disabled(self):
        result = self.automation.left_click()

        self.assertEqual(result["status"], "BLOCKED")

    def test_enabled_dry_run_left_click(self):
        self.activation.enable()

        result = self.automation.left_click()

        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(result["action"], "LEFT_CLICK")

    def test_enabled_dry_run_right_click(self):
        self.activation.enable()

        result = self.automation.right_click()

        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(result["action"], "RIGHT_CLICK")

    def test_disable_blocks_click(self):
        self.activation.enable()
        self.activation.disable()

        result = self.automation.left_click()

        self.assertEqual(result["status"], "BLOCKED")

    def test_emergency_blocks_click(self):
        self.activation.enable()
        self.activation.emergency_stop()

        result = self.automation.left_click()

        self.assertEqual(result["status"], "BLOCKED")

    def test_missing_activation_rejected(self):
        with self.assertRaises(ValueError):
            WindowsAutomation(activation=None)

    @patch("gestureos_engine.automation.pyautogui.click")
    def test_real_left_click_backend(self, mock_click):
        self.activation.enable()

        automation = WindowsAutomation(
            activation=self.activation,
            dry_run=False,
            emergency_stop_available=True,
        )

        result = automation.left_click()

        mock_click.assert_called_once_with(button="left")
        self.assertEqual(result["status"], "EXECUTED")

    @patch("gestureos_engine.automation.pyautogui.click")
    def test_real_right_click_backend(self, mock_click):
        self.activation.enable()

        automation = WindowsAutomation(
            activation=self.activation,
            dry_run=False,
            emergency_stop_available=True,
        )

        result = automation.right_click()

        mock_click.assert_called_once_with(button="right")
        self.assertEqual(result["status"], "EXECUTED")


if __name__ == "__main__":
    unittest.main(verbosity=2)