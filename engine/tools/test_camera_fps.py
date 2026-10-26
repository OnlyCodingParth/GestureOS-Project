import cv2
import time


def test_camera(name, width, height, fps, use_mjpg=False):
    print(f"\n{'=' * 50}")
    print(f"Testing: {name}")
    print(f"{'=' * 50}")

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("[ERROR] Camera unavailable.")
        camera.release()
        return

    try:
        if use_mjpg:
            camera.set(
                cv2.CAP_PROP_FOURCC,
                cv2.VideoWriter_fourcc(*"MJPG")
            )

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        camera.set(cv2.CAP_PROP_FPS, fps)

        actual_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = camera.get(cv2.CAP_PROP_FPS)

        fourcc = int(camera.get(cv2.CAP_PROP_FOURCC))

        actual_format = "".join(
            chr((fourcc >> (8 * i)) & 255)
            for i in range(4)
        )

        print(f"Requested FPS: {fps}")
        print(f"Reported FPS: {actual_fps:.2f}")
        print(
            f"Resolution: {int(actual_width)} x "
            f"{int(actual_height)}"
        )
        print(f"Format: {actual_format}")

        # Warm-up frames
        for _ in range(15):
            success, _ = camera.read()

            if not success:
                print("[ERROR] Camera warm-up failed.")
                return

        frames = 100
        start = time.perf_counter()

        for _ in range(frames):
            success, frame = camera.read()

            if not success or frame is None:
                print("[ERROR] Frame capture failed.")
                return

        elapsed = time.perf_counter() - start

        measured_fps = frames / elapsed

        print(f"Measured Capture FPS: {measured_fps:.2f}")

    finally:
        camera.release()


def main():
    print("GestureOS | Camera FPS Configuration Test")
    print("No mouse automation will occur.")

    configurations = [
        ("YUY2 640x480 @ 30 FPS", 640, 480, 30, False),
        ("MJPG 640x480 @ 30 FPS", 640, 480, 30, True),
        ("MJPG 320x240 @ 30 FPS", 320, 240, 30, True),
    ]

    for name, width, height, fps, mjpg in configurations:
        test_camera(name, width, height, fps, mjpg)
        time.sleep(1)


if __name__ == "__main__":
    main()