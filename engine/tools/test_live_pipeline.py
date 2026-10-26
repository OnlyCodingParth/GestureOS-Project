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
from gestureos_engine.pipeline import GestureSafetyPipeline


def draw_text(frame, text, position, color=(255, 255, 255)):
    """Draw readable text on the webcam preview."""

    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        color,
        2,
        cv2.LINE_AA,
    )


def main():
    print("=" * 55)
    print("GestureOS | M4.7 Live Safety Pipeline")
    print("=" * 55)

    print("E = Enable")
    print("D = Disable")
    print("S = Emergency Stop")
    print("R = Reset Emergency")
    print("Q = Quit")

    print("\nStarting webcam...")
    print("DRY-RUN MODE: No Windows actions will be executed.\n")

    camera = CameraCapture()
    tracker = None

    recognizer = GestureRecognizer()

    stabilizer = GestureStabilizer(
        window_size=5,
        minimum_votes=3,
    )

    pipeline = GestureSafetyPipeline(
        hold_duration=0.8,
        cooldown_duration=1.0,
    )

    frame_count = 0
    start_time = time.monotonic()

    last_result = {
        "status": "BLOCKED",
        "reason": "GestureOS is not enabled.",
        "action": None,
    }

    previous_enabled = False

    try:
        camera.start()

        tracker = HandTracker(max_hands=1)

        while True:
            frame = camera.read()

            frame_count += 1

            # Mirror webcam preview for natural hand movement.
            frame = cv2.flip(frame, 1)

            # Detect hands using MediaPipe.
            detection = tracker.detect(frame)

            raw_gesture = Gesture.UNKNOWN
            stable_gesture = Gesture.UNKNOWN

            if detection.hand_landmarks:
                landmarks = detection.hand_landmarks[0]

                raw_gesture = recognizer.recognize(landmarks)

                stable_gesture = stabilizer.update(raw_gesture)

            else:
                # Never keep a stale gesture when the hand disappears.
                stabilizer.reset()
                pipeline.hold_detector.reset()

            enabled = pipeline.activation.can_execute()

            # Reset stabilization when activation changes.
            if enabled != previous_enabled:
                stabilizer.reset()
                pipeline.hold_detector.reset()
                stable_gesture = Gesture.UNKNOWN

            previous_enabled = enabled

            # Process the stable gesture through safety checks.
            last_result = pipeline.process(
                stable_gesture,
                current_time=time.monotonic(),
            )

            if last_result["status"] == "SIMULATED":
                print(
                    "[ACTION]",
                    last_result["action"],
                    "| Gesture:",
                    stable_gesture.value,
                )

            # Calculate average FPS.
            elapsed = time.monotonic() - start_time

            fps = (
                frame_count / elapsed
                if elapsed > 0
                else 0
            )

            # Display system state.
            state = pipeline.activation.state.value

            draw_text(
                frame,
                f"GestureOS: {state}",
                (20, 35),
                (0, 255, 255),
            )

            draw_text(
                frame,
                f"Raw: {raw_gesture.value}",
                (20, 70),
            )

            draw_text(
                frame,
                f"Stable: {stable_gesture.value}",
                (20, 105),
            )

            draw_text(
                frame,
                f"Status: {last_result['status']}",
                (20, 140),
                (0, 255, 0),
            )

            draw_text(
                frame,
                f"FPS: {fps:.1f}",
                (20, 175),
            )

            draw_text(
                frame,
                "E:Enable D:Disable S:Stop R:Reset Q:Quit",
                (20, 215),
                (255, 255, 0),
            )

            cv2.imshow(
                "GestureOS | M4.7 Safety Pipeline",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("e"):
                if pipeline.enable():
                    stabilizer.reset()
                    print("[SYSTEM] GestureOS ENABLED")
                else:
                    print("[SYSTEM] Cannot enable during emergency stop.")

            elif key == ord("d"):
                pipeline.disable()
                stabilizer.reset()
                print("[SYSTEM] GestureOS DISABLED")

            elif key == ord("s"):
                pipeline.emergency_stop()
                stabilizer.reset()
                print("[EMERGENCY] ALL GESTURE ACTIONS BLOCKED")

            elif key == ord("r"):
                if pipeline.reset_emergency():
                    stabilizer.reset()
                    print("[SYSTEM] Emergency reset. GestureOS DISABLED.")
                else:
                    print("[SYSTEM] No emergency stop to reset.")

            elif key == ord("q"):
                print("[SYSTEM] Quit requested.")
                break

    except KeyboardInterrupt:
        print("\n[SYSTEM] Interrupted by user.")

    except Exception as error:
        print(f"\n[ERROR] {error}")
        raise

    finally:
        # Fail closed before releasing hardware resources.
        pipeline.emergency_stop()

        if tracker is not None:
            tracker.close()

        camera.stop()
        cv2.destroyAllWindows()

        elapsed = time.monotonic() - start_time

        average_fps = (
            frame_count / elapsed
            if elapsed > 0
            else 0
        )

        print("\n" + "=" * 55)
        print("GestureOS | Live Test Summary")
        print("=" * 55)
        print(f"Frames processed: {frame_count}")
        print(f"Average FPS: {average_fps:.2f}")
        print(f"Simulated actions: {len(pipeline.executor.history)}")
        print("Safety pipeline cleanup completed.")


if __name__ == "__main__":
    main()