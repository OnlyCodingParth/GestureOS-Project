import sys
import time
from pathlib import Path

import cv2

# Allow this test script to import the GestureOS engine package.
ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.capture import CameraCapture


def main():
    camera = CameraCapture()
    frames = 0
    start_time = None

    try:
        camera.start()

        print("GestureOS | M1.2 Webcam Test")
        print("Camera started successfully.")
        print("Press Q in the preview window to exit.")

        start_time = time.perf_counter()

        while time.perf_counter() - start_time < 60:
            frame = camera.read()
            frames += 1

            elapsed = time.perf_counter() - start_time
            fps = frames / elapsed if elapsed > 0 else 0

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )

            cv2.imshow("GestureOS | M1.2", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Test stopped by user.")
                break

    except RuntimeError as error:
        print(f"Camera error: {error}")

    finally:
        camera.stop()
        cv2.destroyAllWindows()

        if start_time is not None:
            elapsed = time.perf_counter() - start_time
            fps = frames / elapsed if elapsed > 0 else 0

            print(f"Frames captured: {frames}")
            print(f"Average FPS: {fps:.2f}")

        print("Camera cleanup completed.")


if __name__ == "__main__":
    main()