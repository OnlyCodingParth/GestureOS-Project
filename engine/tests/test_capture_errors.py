import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the engine directory to Python's import path.
ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.capture import CameraCapture


class TestCameraCapture(unittest.TestCase):

    # TEST 1: Reading frames before starting the camera
    def test_read_before_start(self):
        camera = CameraCapture()

        with self.assertRaises(RuntimeError):
            camera.read()

    # TEST 2: Prevent starting the same camera twice
    @patch("gestureos_engine.capture.cv2.VideoCapture")
    def test_double_start(self, mock_capture):
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = True
        mock_capture.return_value = mock_camera

        camera = CameraCapture()

        try:
            camera.start()

            with self.assertRaises(RuntimeError):
                camera.start()
        finally:
            camera.stop()

        mock_camera.release.assert_called_once()

    # TEST 3: Stopping the camera multiple times safely
    def test_safe_stop(self):
        camera = CameraCapture()

        camera.stop()
        camera.stop()

        self.assertIsNone(camera.camera)

    # TEST 4: Camera fails to open
    @patch("gestureos_engine.capture.cv2.VideoCapture")
    def test_camera_open_failure(self, mock_capture):
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = False
        mock_capture.return_value = mock_camera

        camera = CameraCapture()

        with self.assertRaises(RuntimeError):
            camera.start()

        mock_camera.release.assert_called_once()
        self.assertIsNone(camera.camera)

    # TEST 5: Camera fails to read a frame
    @patch("gestureos_engine.capture.cv2.VideoCapture")
    def test_frame_read_failure(self, mock_capture):
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = True
        mock_camera.read.return_value = (False, None)
        mock_capture.return_value = mock_camera

        camera = CameraCapture()

        try:
            camera.start()

            with self.assertRaises(RuntimeError):
                camera.read()
        finally:
            camera.stop()

        mock_camera.release.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)