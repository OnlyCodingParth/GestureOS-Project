import sys
import time
from pathlib import Path

import cv2
import pyautogui

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.async_capture import AsyncCameraCapture
from gestureos_engine.tracker import HandTracker
from gestureos_engine.mouse_controller import MouseController
from gestureos_engine.activation import GestureActivation
from gestureos_engine.emergency import EmergencyStopController


WINDOW_NAME = "GestureOS | M5.6.6 Async Cursor"

MAX_FRAME_AGE = 0.15
MAX_STEP = 80
SAFE_MARGIN = 0.08


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
    print("GestureOS | M5.6.6 Async Real Cursor Control")
    print("=" * 60)

    print("Cursor control starts DISABLED.")
    print("E = Enable | D = Disable | S = Emergency")
    print("R = Reset emergency | Q = Quit")
    print("No clicking or scrolling.\n")

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0

    screen_width, screen_height = pyautogui.size()

    controller = MouseController(
        screen_width=screen_width,
        screen_height=screen_height,
        smoothing=0.3,
        margin=0.08,
        dead_zone=3,
        max_step=80,
        jump_threshold=240,
    )

    activation = GestureActivation()
    emergency = EmergencyStopController(activation=activation)
    camera = AsyncCameraCapture()
    tracker = None

    min_x = round(screen_width * SAFE_MARGIN)
    max_x = round((screen_width - 1) * (1 - SAFE_MARGIN))
    min_y = round(screen_height * SAFE_MARGIN)
    max_y = round((screen_height - 1) * (1 - SAFE_MARGIN))

    last_frame_id = 0
    processed_frames = 0
    movement_count = 0
    stale_frames = 0

    start_time = time.monotonic()

    try:
        if not emergency.start_hotkey():
            print("[ERROR] Global emergency stop unavailable; refusing automation.")
            return
        camera.start()
        tracker = HandTracker(max_hands=1)

        while True:
            try:
                frame, frame_id, captured_at = camera.read_new(
                    last_frame_id, max_age=MAX_FRAME_AGE
                )
            except RuntimeError as exc:
                activation.camera_failure()
                print(f"[ERROR] Camera stopped: {exc}")
                break

            if frame is None or frame_id == last_frame_id:
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break

                time.sleep(0.002)
                continue

            last_frame_id = frame_id

            age = time.monotonic() - captured_at
            if age > MAX_FRAME_AGE:
                stale_frames += 1
                controller.reset()
                continue

            frame = cv2.flip(frame, 1)
            result = tracker.detect(frame)

            processed_frames += 1

            if result.hand_landmarks:
                landmarks = result.hand_landmarks[0]
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

                if activation.can_execute():
                    try:
                        current_x, current_y = pyautogui.position()

                        move_x, move_y = limit_step(
                            current_x,
                            current_y,
                            target_x,
                            target_y,
                        )

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

                        print("[EMERGENCY] PyAutoGUI fail-safe triggered.")

            else:
                controller.reset()

            elapsed = time.monotonic() - start_time
            fps = processed_frames / elapsed if elapsed > 0 else 0

            draw_text(
                frame,
                "GestureOS | Async Cursor",
                35,
                (255, 255, 0),
            )

            draw_text(
                frame,
                f"State: {activation.state.value}",
                75,
            )

            draw_text(
                frame,
                f"FPS: {fps:.2f}",
                115,
            )

            draw_text(
                frame,
                f"Frame Age: {age * 1000:.1f} ms",
                155,
            )

            draw_text(
                frame,
                "E:ON D:OFF S:STOP R:RESET Q:QUIT",
                195,
            )

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("e"):
                if activation.enable():
                    controller.reset()
                    print("[SYSTEM] Cursor ENABLED.")

            elif key == ord("d"):
                activation.disable()
                controller.reset()
                print("[SYSTEM] Cursor DISABLED.")

            elif key == ord("s"):
                activation.emergency_stop()
                emergency.stop_hotkey()
                controller.reset()
                print("[EMERGENCY] Cursor STOPPED.")

            elif key == ord("r"):
                activation.reset_emergency()
                controller.reset()
                print("[SYSTEM] Emergency reset. Cursor DISABLED.")

            elif key == ord("q"):
                break

    except KeyboardInterrupt:
        print("\n[SYSTEM] Interrupted.")

    except Exception as exc:
        activation.emergency_stop()
        print(f"\n[ERROR] {exc}")

    finally:
        activation.emergency_stop()

        if tracker is not None:
            tracker.close()

        camera.stop()
        cv2.destroyAllWindows()

        elapsed = time.monotonic() - start_time
        fps = processed_frames / elapsed if elapsed > 0 else 0

        print("\n" + "=" * 60)
        print("GestureOS | Async Cursor Test Summary")
        print("=" * 60)
        print(f"Frames processed: {processed_frames}")
        print(f"Cursor movements: {movement_count}")
        print(f"Stale frames skipped: {stale_frames}")
        print(f"Average FPS: {fps:.2f}")
        print("System stopped safely.")


if __name__ == "__main__":
    main()