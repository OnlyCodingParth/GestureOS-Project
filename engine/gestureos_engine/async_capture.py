import threading
import time

from gestureos_engine.capture import CameraCapture


class AsyncCameraCapture:
    """Capture webcam frames in a background thread."""

    def __init__(self, camera_index=0, width=640, height=480):
        self.camera = CameraCapture(
            camera_index=camera_index,
            width=width,
            height=height,
        )

        self.thread = None
        self.running = False

        self.lock = threading.Lock()
        self.camera_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.latest_frame = None
        self.frame_id = 0
        self.last_frame_time = None
        self.error = None

    def start(self):
        if self.running:
            raise RuntimeError("Camera is already running.")

        self.camera.start()

        with self.lock:
            self.running = True
            self.latest_frame = None
            self.frame_id = 0
            self.last_frame_time = None
            self.error = None
            self.stop_event.clear()

        self.thread = threading.Thread(
            target=self._capture_loop,
            daemon=True,
        )

        self.thread.start()
        return self

    def _capture_loop(self):
        try:
            while not self.stop_event.is_set():
                with self.camera_lock:
                    if self.stop_event.is_set():
                        break
                    frame = self.camera.read()

                with self.lock:
                    self.latest_frame = frame
                    self.frame_id += 1
                    self.last_frame_time = time.monotonic()

        except Exception as exc:
            with self.lock:
                self.error = exc
                self.running = False

        finally:
            self.running = False

    def read(self):
        """Return latest frame, ID, and capture timestamp."""

        with self.lock:
            if self.error is not None:
                raise RuntimeError(
                    f"Camera capture failed: {self.error}"
                ) from self.error

            if self.latest_frame is None:
                return None, 0, None

            return (
                self.latest_frame.copy(),
                self.frame_id,
                self.last_frame_time,
            )

    def read_new(self, last_frame_id=0, max_age=None):
        """Return a new frame, rejecting duplicates and stale frames."""

        frame, frame_id, captured_at = self.read()
        if frame is None or frame_id <= last_frame_id:
            return None, frame_id, captured_at
        if max_age is not None and captured_at is not None:
            if time.monotonic() - captured_at > max_age:
                return None, frame_id, captured_at
        return frame, frame_id, captured_at

    def stop(self):
        self.stop_event.set()
        with self.lock:
            self.running = False

        # Serialize release with camera.read(); this avoids concurrent
        # access to the OpenCV VideoCapture object.
        with self.camera_lock:
            self.camera.stop()

        if self.thread is not None:
            self.thread.join(timeout=3.0)

            if self.thread.is_alive():
                raise RuntimeError(
                    "Camera thread did not stop safely."
                )

            self.thread = None
