import sys
import time
from pathlib import Path

import cv2

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.capture import CameraCapture
from gestureos_engine.tracker import HandTracker


# MediaPipe's 21 hand landmarks are connected using these pairs.
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]


def draw_hand(frame, landmarks):
    """Draw the 21 landmarks and their connections."""

    height, width = frame.shape[:2]

    points = []

    for landmark in landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)
        points.append((x, y))

    # Draw hand skeleton connections.
    for start, end in HAND_CONNECTIONS:
        cv2.line(
            frame,
            points[start],
            points[end],
            (0, 255, 0),
            2,
        )

    # Draw 21 landmark points.
    for point in points:
        cv2.circle(
            frame,
            point,
            4,
            (0, 0, 255),
            -1,
        )


def main():
    camera = CameraCapture()
    tracker = None

    frames = 0
    detected_frames = 0
    start_time = None

    try:
        camera.start()
        tracker = HandTracker(max_hands=2)

        print("GestureOS | M2.3 Live Hand Tracking")
        print("Show your hand to the webcam.")
        print("Press Q to exit.")

        start_time = time.perf_counter()

        while time.perf_counter() - start_time < 60:
            frame = camera.read()

            # Mirror the preview for natural interaction.
            frame = cv2.flip(frame, 1)

            result = tracker.detect(frame)

            frames += 1

            if result.hand_landmarks:
                detected_frames += 1

                for hand_landmarks in result.hand_landmarks:
                    draw_hand(frame, hand_landmarks)

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

            cv2.putText(
                frame,
                f"Hands: {len(result.hand_landmarks)}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

            cv2.imshow("GestureOS | Hand Tracking", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Test stopped by user.")
                break

    except (RuntimeError, ValueError, FileNotFoundError) as error:
        print(f"Hand tracking error: {error}")

    finally:
        camera.stop()

        if tracker is not None:
            tracker.close()

        cv2.destroyAllWindows()

        if start_time is not None:
            elapsed = time.perf_counter() - start_time
            fps = frames / elapsed if elapsed > 0 else 0

            print(f"Frames processed: {frames}")
            print(f"Frames with detected hands: {detected_frames}")
            print(f"Average FPS: {fps:.2f}")

        print("Camera and tracker cleanup completed.")


if __name__ == "__main__":
    main()