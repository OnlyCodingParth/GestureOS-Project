import sys
import time
from pathlib import Path

import cv2

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.capture import CameraCapture
from gestureos_engine.tracker import HandTracker
from gestureos_engine.gestures import Gesture, GestureRecognizer
from gestureos_engine.stability import GestureStabilizer


def main():
    camera = CameraCapture()
    tracker = None

    recognizer = GestureRecognizer()
    stabilizer = GestureStabilizer(
        window_size=5,
        minimum_votes=3,
    )

    frames = 0
    start_time = None
    previous_hand_count = 0

    try:
        camera.start()
        tracker = HandTracker(max_hands=1)

        print("GestureOS | M3.4 Live Gesture Recognition")
        print("Supported: OPEN_PALM, FIST, PINCH")
        print("Press Q to exit.")

        start_time = time.perf_counter()

        while time.perf_counter() - start_time < 60:
            frame = camera.read()
            frame = cv2.flip(frame, 1)

            result = tracker.detect(frame)

            hand_count = len(result.hand_landmarks)

            if hand_count > 0:
                landmarks = result.hand_landmarks[0]

                raw_gesture = recognizer.recognize(landmarks)
                stable_gesture = stabilizer.update(raw_gesture)

            else:
                raw_gesture = Gesture.UNKNOWN

                # Clear previous gesture when the hand disappears.
                if previous_hand_count > 0:
                    stabilizer.reset()

                stable_gesture = Gesture.UNKNOWN

            previous_hand_count = hand_count

            frames += 1

            elapsed = time.perf_counter() - start_time
            fps = frames / elapsed if elapsed > 0 else 0

            # Display raw gesture.
            cv2.putText(
                frame,
                f"Raw: {raw_gesture.value}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            # Display stable gesture.
            cv2.putText(
                frame,
                f"Stable: {stable_gesture.value}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            # Display hand count.
            cv2.putText(
                frame,
                f"Hands: {hand_count}",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            # Display FPS.
            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

            cv2.imshow("GestureOS | Live Gestures", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Test stopped by user.")
                break

    except (RuntimeError, ValueError, FileNotFoundError) as error:
        print(f"Gesture recognition error: {error}")

    finally:
        camera.stop()

        if tracker is not None:
            tracker.close()

        cv2.destroyAllWindows()

        if start_time is not None:
            elapsed = time.perf_counter() - start_time
            fps = frames / elapsed if elapsed > 0 else 0

            print(f"Frames processed: {frames}")
            print(f"Average FPS: {fps:.2f}")

        print("Gesture recognition cleanup completed.")


if __name__ == "__main__":
    main()