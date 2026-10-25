"""Run a manual M0 webcam preview test without hand tracking."""

from __future__ import annotations

import time

import cv2


CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
MAX_DURATION_SECONDS = 60.0
WINDOW_NAME = "GestureOS M0 Camera Test - press Q to quit"


def main() -> int:
    """Preview the default camera, report average FPS, and always release it."""
    capture = cv2.VideoCapture(CAMERA_INDEX)
    if not capture.isOpened():
        print("Unable to open the default camera (index 0).")
        return 1

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    start_time = time.perf_counter()
    frame_count = 0
    exit_reason = "60-second limit reached"
    print("Camera preview started. Press Q in the preview window to exit early.")

    try:
        while time.perf_counter() - start_time < MAX_DURATION_SECONDS:
            ok, frame = capture.read()
            if not ok or frame is None:
                print("Camera frame read failed.")
                return 1

            frame_count += 1
            elapsed = time.perf_counter() - start_time
            average_fps = frame_count / elapsed if elapsed else 0.0
            cv2.putText(
                frame,
                f"Average FPS: {average_fps:.1f}",
                (16, 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow(WINDOW_NAME, frame)

            if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                exit_reason = "Q pressed"
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()

    elapsed = time.perf_counter() - start_time
    average_fps = frame_count / elapsed if elapsed else 0.0
    print(
        f"Camera test completed: {exit_reason}. "
        f"Frames: {frame_count}. Average FPS: {average_fps:.1f}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
