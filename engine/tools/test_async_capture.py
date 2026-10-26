import sys
import time
from pathlib import Path
from statistics import mean

import cv2

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.async_capture import AsyncCameraCapture
from gestureos_engine.tracker import HandTracker


MAX_TEST_SECONDS = 30
MAX_FRAME_AGE = 0.20


def main():
    print("=" * 55)
    print("GestureOS | M5.6.5 Async Camera Test")
    print("=" * 55)

    print("MODE: PERFORMANCE TEST ONLY")
    print("No mouse movement or clicks.")
    print("Press Q to quit.\n")

    camera = AsyncCameraCapture()
    tracker = None

    processed_frames = 0
    detected_frames = 0
    last_frame_id = 0

    detection_times = []
    frame_ages = []

    start_time = time.monotonic()

    try:
        camera.start()
        tracker = HandTracker(max_hands=1)

        while time.monotonic() - start_time < MAX_TEST_SECONDS:
            frame, frame_id, captured_at = camera.read()

            if frame is None or frame_id == last_frame_id:
                time.sleep(0.002)
                continue

            last_frame_id = frame_id

            age = time.monotonic() - captured_at

            if age > MAX_FRAME_AGE:
                continue

            frame_ages.append(age * 1000)

            frame = cv2.flip(frame, 1)

            detection_start = time.perf_counter()
            result = tracker.detect(frame)
            detection_end = time.perf_counter()

            detection_times.append(
                (detection_end - detection_start) * 1000
            )

            processed_frames += 1

            if result.hand_landmarks:
                detected_frames += 1

                index_tip = result.hand_landmarks[0][8]

                height, width = frame.shape[:2]

                x = int(index_tip.x * width)
                y = int(index_tip.y * height)

                cv2.circle(
                    frame,
                    (x, y),
                    12,
                    (0, 255, 0),
                    -1,
                )

            elapsed = time.monotonic() - start_time
            fps = processed_frames / elapsed if elapsed > 0 else 0

            cv2.putText(
                frame,
                f"FPS: {fps:.2f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Frame Age: {age * 1000:.1f} ms",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                "ASYNC TEST - NO MOUSE CONTROL",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2,
            )

            cv2.imshow(
                "GestureOS | Async Camera Test",
                frame,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[SYSTEM] Quit requested.")
                break

    except KeyboardInterrupt:
        print("\n[SYSTEM] Interrupted.")

    finally:
        if tracker is not None:
            tracker.close()

        camera.stop()
        cv2.destroyAllWindows()

        elapsed = time.monotonic() - start_time
        fps = processed_frames / elapsed if elapsed > 0 else 0

        print("\n" + "=" * 55)
        print("GestureOS | Async Performance Report")
        print("=" * 55)

        print(f"Frames processed: {processed_frames}")
        print(f"Frames with hand: {detected_frames}")
        print(f"Average FPS: {fps:.2f}")

        if detection_times:
            print(
                f"Average MediaPipe detection: "
                f"{mean(detection_times):.2f} ms"
            )

        if frame_ages:
            print(
                f"Average frame age before detection: "
                f"{mean(frame_ages):.2f} ms"
            )

        print("Async capture test completed.")


if __name__ == "__main__":
    main()