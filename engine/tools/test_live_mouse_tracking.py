import sys
import time
from pathlib import Path

import cv2
import pyautogui

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.capture import CameraCapture
from gestureos_engine.tracker import HandTracker
from gestureos_engine.mouse_controller import MouseController


def draw_text(frame, text, position, color=(255, 255, 255)):
    """Display text on the webcam preview."""

    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2,
        cv2.LINE_AA,
    )


def main():
    print("=" * 55)
    print("GestureOS | M5.4 Live Finger Tracking")
    print("=" * 55)

    print("MODE: DRY RUN")
    print("No real mouse movement will occur.")
    print("Press Q to quit.\n")

    screen_width, screen_height = pyautogui.size()

    print(f"Screen Resolution: {screen_width} x {screen_height}")

    mouse_controller = MouseController(
        screen_width=screen_width,
        screen_height=screen_height,
        smoothing=0.25,
        margin=0.05,
    )

    camera = CameraCapture()
    tracker = None

    frame_count = 0
    detected_frames = 0
    start_time = time.monotonic()

    try:
        camera.start()
        tracker = HandTracker(max_hands=1)

        while True:
            frame = camera.read()

            frame_count += 1

            # Mirror the webcam image.
            frame = cv2.flip(frame, 1)

            detection = tracker.detect(frame)

            if detection.hand_landmarks:
                landmarks = detection.hand_landmarks[0]

                # MediaPipe index finger tip = landmark 8.
                index_tip = landmarks[8]

                screen_x, screen_y = mouse_controller.update(
                    index_tip.x,
                    index_tip.y,
                )

                detected_frames += 1

                height, width = frame.shape[:2]

                finger_x = int(index_tip.x * width)
                finger_y = int(index_tip.y * height)

                # Highlight index fingertip.
                cv2.circle(
                    frame,
                    (finger_x, finger_y),
                    12,
                    (0, 255, 0),
                    -1,
                )

                draw_text(
                    frame,
                    f"Finger: ({index_tip.x:.2f}, {index_tip.y:.2f})",
                    (20, 70),
                )

                draw_text(
                    frame,
                    f"Cursor Target: ({screen_x}, {screen_y})",
                    (20, 105),
                    (0, 255, 255),
                )

                draw_text(
                    frame,
                    "Tracking: ACTIVE",
                    (20, 140),
                    (0, 255, 0),
                )

            else:
                mouse_controller.reset()

                draw_text(
                    frame,
                    "Tracking: NO HAND",
                    (20, 140),
                    (0, 0, 255),
                )

            elapsed = time.monotonic() - start_time

            fps = frame_count / elapsed if elapsed > 0 else 0

            draw_text(
                frame,
                "GestureOS | M5.4",
                (20, 35),
                (255, 255, 0),
            )

            draw_text(
                frame,
                f"FPS: {fps:.1f}",
                (20, 175),
            )

            draw_text(
                frame,
                "DRY RUN - Press Q to Quit",
                (20, 210),
                (255, 255, 0),
            )

            cv2.imshow(
                "GestureOS | Live Finger Tracking",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print("[SYSTEM] Quit requested.")
                break

    except KeyboardInterrupt:
        print("\n[SYSTEM] Interrupted by user.")

    finally:
        if tracker is not None:
            tracker.close()

        camera.stop()
        cv2.destroyAllWindows()

        elapsed = time.monotonic() - start_time

        average_fps = frame_count / elapsed if elapsed > 0 else 0

        print("\n" + "=" * 55)
        print("GestureOS | M5.4 Test Summary")
        print("=" * 55)

        print(f"Frames processed: {frame_count}")
        print(f"Frames with hand detected: {detected_frames}")
        print(f"Average FPS: {average_fps:.2f}")
        print("Live tracking cleanup completed.")


if __name__ == "__main__":
    main()