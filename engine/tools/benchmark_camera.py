import time
import statistics

import cv2


CAMERA_INDEX = 0
WIDTH = 640
HEIGHT = 480
TEST_FRAMES = 150


def benchmark_camera(name, use_mjpg=False):
    print(f"\nTesting: {name}")

    camera = cv2.VideoCapture(
        CAMERA_INDEX,
        cv2.CAP_DSHOW,
    )

    if not camera.isOpened():
        print("[ERROR] Unable to open camera.")
        camera.release()
        return None

    try:
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

        if use_mjpg:
            camera.set(
                cv2.CAP_PROP_FOURCC,
                cv2.VideoWriter_fourcc(*"MJPG"),
            )

        # Warm up camera.
        for _ in range(20):
            success, _ = camera.read()

            if not success:
                print("[ERROR] Camera warm-up failed.")
                return None

        capture_times = []

        start_time = time.perf_counter()

        for _ in range(TEST_FRAMES):
            frame_start = time.perf_counter()

            success, frame = camera.read()

            frame_end = time.perf_counter()

            if not success or frame is None:
                print("[ERROR] Frame capture failed.")
                return None

            capture_times.append(
                (frame_end - frame_start) * 1000
            )

        elapsed = time.perf_counter() - start_time

        average_capture = statistics.mean(capture_times)
        average_fps = TEST_FRAMES / elapsed

        actual_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

        fourcc = int(camera.get(cv2.CAP_PROP_FOURCC))

        actual_format = "".join(
            chr((fourcc >> (8 * i)) & 0xFF)
            for i in range(4)
        )

        print(f"Resolution: {int(actual_width)} x {int(actual_height)}")
        print(f"Camera format: {actual_format}")
        print(f"Average capture: {average_capture:.2f} ms")
        print(f"Capture FPS: {average_fps:.2f}")

        return average_capture

    finally:
        camera.release()


def main():
    print("=" * 55)
    print("GestureOS | Camera Performance Benchmark")
    print("=" * 55)

    print("\nMake sure other webcam applications are closed.")

    normal = benchmark_camera(
        "Default DirectShow",
        use_mjpg=False,
    )

    # Give Windows time to release the camera.
    time.sleep(2)

    mjpg = benchmark_camera(
        "DirectShow + MJPG",
        use_mjpg=True,
    )

    print("\n" + "=" * 55)
    print("Benchmark Summary")
    print("=" * 55)

    if normal is not None:
        print(f"Default capture: {normal:.2f} ms")

    if mjpg is not None:
        print(f"MJPG capture: {mjpg:.2f} ms")

    if normal is not None and mjpg is not None:
        improvement = (
            (normal - mjpg) / normal
        ) * 100

        print(f"Capture time improvement: {improvement:.1f}%")

        if mjpg < normal:
            print("[RESULT] MJPG is faster.")
        else:
            print("[RESULT] Default format is faster or equal.")


if __name__ == "__main__":
    main()