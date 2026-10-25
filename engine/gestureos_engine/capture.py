import cv2


class CameraCapture:
    """Manage webcam initialization, frame capture, and cleanup."""

    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.camera = None

    def start(self):
        """Open and configure the webcam."""

        if self.camera is not None:
            raise RuntimeError("Camera is already started.")

        camera = cv2.VideoCapture(
            self.camera_index,
            cv2.CAP_DSHOW
        )

        if not camera.isOpened():
            camera.release()
            raise RuntimeError("Unable to open webcam.")

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        self.camera = camera
        return self

    def read(self):
        """Read a frame from the webcam."""

        if self.camera is None:
            raise RuntimeError("Camera has not been started.")

        success, frame = self.camera.read()

        if not success or frame is None:
            raise RuntimeError("Unable to read webcam frame.")

        return frame

    def stop(self):
        """Release the webcam safely."""

        if self.camera is not None:
            self.camera.release()
            self.camera = None