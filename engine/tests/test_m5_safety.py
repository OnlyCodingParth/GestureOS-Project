import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.activation import ActivationState, GestureActivation
from gestureos_engine.automation import WindowsAutomation
from gestureos_engine.emergency import EmergencyStopController
from gestureos_engine.gestures import Gesture
from gestureos_engine.mouse_controller import MouseController
from gestureos_engine.pipeline import GestureSafetyPipeline
from gestureos_engine.hotkey import GlobalEmergencyHotkey


class TestEmergencyHotkeyLifecycle(unittest.TestCase):
    def test_windows_registration_and_cleanup_are_called(self):
        user32 = Mock()
        kernel32 = Mock()
        kernel32.GetCurrentThreadId.return_value = 42
        user32.RegisterHotKey.return_value = 1
        user32.PeekMessageW.return_value = 0
        hotkey = GlobalEmergencyHotkey(
            lambda: None, user32=user32, kernel32=kernel32
        )
        hotkey._stop.set()
        hotkey._run()
        user32.RegisterHotKey.assert_called_once()
        user32.UnregisterHotKey.assert_called_once_with(None, 0x4753)

    def test_registration_failure_fails_closed(self):
        hotkey = Mock()
        hotkey.start.return_value = False
        controller = EmergencyStopController(hotkey=hotkey)

        self.assertFalse(controller.start_hotkey())
        self.assertFalse(controller.hotkey_available)
        hotkey.start.assert_called_once_with()

    def test_cleanup_unregisters_hotkey(self):
        hotkey = Mock()
        hotkey.start.return_value = True
        controller = EmergencyStopController(hotkey=hotkey)

        self.assertTrue(controller.start_hotkey())
        controller.stop_hotkey()
        hotkey.stop.assert_called_once_with()

    def test_emergency_state_is_irreversible_until_reset(self):
        controller = EmergencyStopController()
        controller.trigger()
        self.assertEqual(
            controller.activation.state,
            ActivationState.EMERGENCY_STOPPED,
        )
        self.assertFalse(controller.activation.enable())
        self.assertTrue(controller.reset())
        self.assertFalse(controller.can_execute())


class TestSafeAutomation(unittest.TestCase):
    def test_real_automation_requires_emergency_stop(self):
        activation = GestureActivation()
        activation.enable()
        automation = WindowsAutomation(
            activation,
            dry_run=False,
            emergency_stop_available=False,
        )
        self.assertEqual(automation.left_click()["status"], "BLOCKED")

    @patch("gestureos_engine.automation.pyautogui.click")
    def test_emergency_blocks_active_automation(self, click):
        activation = GestureActivation()
        activation.enable()
        automation = WindowsAutomation(
            activation,
            dry_run=False,
            emergency_stop_available=True,
        )
        activation.emergency_stop()
        self.assertEqual(automation.left_click()["status"], "BLOCKED")
        click.assert_not_called()


class TestPinchAndCursorSafety(unittest.TestCase):
    def test_one_click_per_pinch_and_release_rearms(self):
        pipeline = GestureSafetyPipeline(hold_duration=0.1)
        pipeline.enable()
        self.assertEqual(
            pipeline.process(Gesture.PINCH, 1.0)["status"], "WAITING"
        )
        self.assertEqual(
            pipeline.process(Gesture.PINCH, 1.1)["status"], "SIMULATED"
        )
        self.assertEqual(
            pipeline.process(Gesture.PINCH, 1.2)["status"], "WAITING"
        )
        pipeline.process(Gesture.UNKNOWN, 1.3)
        self.assertEqual(
            pipeline.process(Gesture.PINCH, 2.0)["status"], "WAITING"
        )
        self.assertEqual(
            pipeline.process(Gesture.PINCH, 2.1)["status"], "SIMULATED"
        )
        self.assertEqual(len(pipeline.executor.history), 2)

    def test_tracking_loss_clears_pending_action(self):
        pipeline = GestureSafetyPipeline(hold_duration=0.1)
        pipeline.enable()
        pipeline.process(Gesture.PINCH, 1.0)
        pipeline.tracking_lost()
        self.assertEqual(
            pipeline.process(Gesture.PINCH, 1.1)["status"], "WAITING"
        )

    def test_cursor_dead_zone_and_maximum_step(self):
        controller = MouseController(
            1000, 1000, smoothing=1.0, dead_zone=2, max_step=10
        )
        controller.update(0.5, 0.5)
        stable = controller.update(0.501, 0.501)
        self.assertEqual(stable, (500, 500))
        limited = controller.update(1.0, 1.0)
        self.assertLessEqual(limited[0] - 500, 10)
        self.assertLessEqual(limited[1] - 500, 10)


class TestAsyncFrameContract(unittest.TestCase):
    def test_stale_and_duplicate_frames_are_rejected(self):
        from gestureos_engine.async_capture import AsyncCameraCapture

        capture = AsyncCameraCapture()
        capture.latest_frame = Mock(copy=lambda: "frame")
        capture.frame_id = 4
        capture.last_frame_time = time.monotonic() - 1
        self.assertIsNone(capture.read_new(4)[0])
        self.assertIsNone(capture.read_new(0, max_age=0.1)[0])

    def test_camera_failure_disables_pipeline(self):
        pipeline = GestureSafetyPipeline()
        pipeline.enable()
        pipeline.camera_failed()
        self.assertEqual(
            pipeline.activation.state,
            ActivationState.EMERGENCY_STOPPED,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
