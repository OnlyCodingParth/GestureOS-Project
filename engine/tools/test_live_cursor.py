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
from gestureos_engine.activation import GestureActivation


WINDOW_NAME = "GestureOS | M5.5 Real Cursor Control"

# Start with a limited movement area for safer testing.
# This prevents the test from moving the cursor to screen edges.
SAFE_MARGIN = 0.08

# Maximum cursor movement allowed in one frame.
MAX_STEP = 80


def draw_text(frame, text, y, color=(255, 255, 255)):
    cv2.putText(
        frame,
        text,
        (20, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2,
        cv2.LINE_AA,
    )


def limit_step(current_x, current_y, target_x, target_y):
    """Limit sudden cursor jumps."""

    dx = target_x - current_x
    dy = target_y - current_y

    distance = (dx * dx + dy * dy) ** 0.5

    if distance <= MAX_STEP:
        return target_x, target_y

    scale = MAX_STEP / distance

    return (
        round(current_x + dx * scale),
        round(current_y + dy * scale),
    )


def main():
    print("=" * 60)
    print("GestureOS | M5.5 Real Cursor Movement")
    print("=" * 60)

    print("\nSAFETY:")
    print("- Cursor control starts DISABLED.")
    print("- Only mouse movement is enabled.")
    print("- No clicking, scrolling, or typing.")
    print("- Press E to enable.")
    print("- Press D to disable.")
    print("- Press S for emergency stop.")
    print("- Press R to reset emergency.")
    print("- Press Q to quit.")
    print("- PyAutoGUI corner fail-safe remains enabled.\n")

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0

    screen_width, screen_height = pyautogui.size()

    print(f"Screen: {screen_width} x {screen_height}")

    controller = MouseController(
        screen_width=screen_width,
        screen_height=screen_height,
        smoothing=0.20,
        margin=0.08,
    )

    activation = GestureActivation()

    camera = CameraCapture()
    tracker = None

    frame_count = 0
    movement_count = 0

    start_time = time.monotonic()

    # Safe area inside screen boundaries.
    min_x = round(screen_width * SAFE_MARGIN)
    max_x = round(screen_width * (1 - SAFE_MARGIN))

    min_y = round(screen_height * SAFE_MARGIN)
    max_y = round(screen_height * (1 - SAFE_MARGIN))

    try:
        camera.start()
        tracker = HandTracker(max_hands=1)

        while True:
            frame = camera.read()
            frame = cv2.flip(frame, 1)

            frame_count += 1

            detection = tracker.detect(frame)

            hand_detected = bool(detection.hand_landmarks)

            if hand_detected:
                landmarks = detection.hand_landmarks[0]
                index_tip = landmarks[8]

                target_x, target_y = controller.update(
                    index_tip.x,
                    index_tip.y,
                )

                height, width = frame.shape[:2]

                finger_x = int(index_tip.x * width)
                finger_y = int(index_tip.y * height)

                cv2.circle(
                    frame,
                    (finger_x, finger_y),
                    12,
                    (0, 255, 0),
                    -1,
                )

                draw_text(
                    frame,
                    f"Target: ({target_x}, {target_y})",
                    75,
                    (0, 255, 255),
                )

                if activation.can_execute():
                    try:
                        current_x, current_y = pyautogui.position()

                        move_x, move_y = limit_step(
                            current_x,
                            current_y,
                            target_x,
                            target_y,
                        )

                        # Keep cursor away from screen corners.
                        move_x = max(min_x, min(max_x, move_x))
                        move_y = max(min_y, min(max_y, move_y))

                        pyautogui.moveTo(
                            move_x,
                            move_y,
                            duration=0,
                        )

                        movement_count += 1

                    except pyautogui.FailSafeException:
                        activation.emergency_stop()
                        controller.reset()

                        print(
                            "[EMERGENCY] PyAutoGUI fail-safe triggered."
                        )

            else:
                controller.reset()

                draw_text(
                    frame,
                    "Tracking: NO HAND",
                    75,
                    (0, 0, 255),
                )

            state = activation.state.value

            state_color = (
                (0, 255, 0)
                if activation.can_execute()
                else (0, 0, 255)
            )

            draw_text(
                frame,
                "GestureOS | Real Cursor Control",
                35,
                (255, 255, 0),
            )

            draw_text(
                frame,
                f"State: {state}",
                110,
                state_color,
            )

            elapsed = time.monotonic() - start_time

            fps = frame_count / elapsed if elapsed > 0 else 0

            draw_text(
                frame,
                f"FPS: {fps:.1f}",
                145,
            )

            draw_text(
                frame,
                "E: Enable | D: Disable | S: STOP",
                180,
            )

            draw_text(
                frame,
                "R: Reset | Q: Quit",
                215,
            )

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("e"):
                if activation.enable():
                    controller.reset()
                    print("[SYSTEM] Cursor control ENABLED.")
                else:
                    print("[SYSTEM] Cannot enable during emergency stop.")

            elif key == ord("d"):
                activation.disable()
                controller.reset()
                print("[SYSTEM] Cursor control DISABLED.")

            elif key == ord("s"):
                activation.emergency_stop()
                controller.reset()
                print("[EMERGENCY] Cursor control STOPPED.")

            elif key == ord("r"):
                activation.reset_emergency()
                controller.reset()
                print("[SYSTEM] Emergency reset. System DISABLED.")

            elif key == ord("q"):
                print("[SYSTEM] Quit requested.")
                break

    except KeyboardInterrupt:
        print("\n[SYSTEM] Interrupted by user.")

    finally:
        activation.emergency_stop()

        if tracker is not None:
            tracker.close()

        camera.stop()
        cv2.destroyAllWindows()

        elapsed = time.monotonic() - start_time

        average_fps = frame_count / elapsed if elapsed > 0 else 0

        print("\n" + "=" * 60)
        print("GestureOS | M5.5 Test Summary")
        print("=" * 60)

        print(f"Frames processed: {frame_count}")
        print(f"Cursor movements: {movement_count}")
        print(f"Average FPS: {average_fps:.2f}")
        print("System safely stopped.")


if __name__ == "__main__":
    main()