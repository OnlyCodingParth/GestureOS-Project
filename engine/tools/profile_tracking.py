import sys
import time
from pathlib import Path
from statistics import mean

import cv2

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.capture import CameraCapture
from gestureos_engine.tracker import HandTracker


def milliseconds(start, end):
    return (end - start) * 1000


def main():
    print("=" * 55)
    print("GestureOS | M5.6.1 Performance Profiling")
    print("=" * 55)
    print("MODE: PROFILING ONLY — NO MOUSE AUTOMATION")
    print("Press Q to quit.\n")

    camera = CameraCapture()
    tracker = None

    capture_times = []
    detection_times = []
    frame_count = 0

    start_time = time.monotonic()

    try:
        camera.start()
        tracker = HandTracker(max_hands=1)

        while True:
            capture_start = time.perf_counter()
            frame = camera.read()
            capture_end = time.perf_counter()

            frame = cv2.flip(frame, 1)

            detection_start = time.perf_counter()
            result = tracker.detect(frame)
            detection_end = time.perf_counter()

            capture_times.append(
                milliseconds(capture_start, capture_end)
            )

            detection_times.append(
                milliseconds(detection_start, detection_end)
            )

            frame_count += 1

            hand_count = len(result.hand_landmarks)

            cv2.putText(
                frame,
                f"Hands: {hand_count}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                "PROFILING - NO MOUSE CONTROL",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2,
            )

            cv2.imshow("GestureOS | Performance Profiling", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\n[SYSTEM] Interrupted.")

    finally:
        if tracker is not None:
            tracker.close()

        camera.stop()
        cv2.destroyAllWindows()

        elapsed = time.monotonic() - start_time

        fps = frame_count / elapsed if elapsed > 0 else 0

        print("\n" + "=" * 55)
        print("GestureOS | Performance Report")
        print("=" * 55)

        print(f"Frames processed: {frame_count}")
        print(f"Average FPS: {fps:.2f}")

        if capture_times:
            print(
                f"Average camera capture: "
                f"{mean(capture_times):.2f} ms"
            )

        if detection_times:
            print(
                f"Average MediaPipe detection: "
                f"{mean(detection_times):.2f} ms"
            )

        print("Profiling completed.")


if __name__ == "__main__":
    main()