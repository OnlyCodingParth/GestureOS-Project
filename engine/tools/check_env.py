"""Verify the M0 Python runtime and its essential GestureOS dependencies."""

from __future__ import annotations

import platform
import struct
import sys


def main() -> int:
    """Print verification details and return nonzero when a requirement is unmet."""
    failures: list[str] = []

    print(f"Python: {platform.python_version()} ({struct.calcsize('P') * 8}-bit)")
    print(f"Executable: {sys.executable}")
    if sys.version_info[:2] != (3, 12):
        failures.append("Python 3.12 is required.")
    if struct.calcsize("P") * 8 != 64:
        failures.append("A 64-bit Python runtime is required.")

    try:
        import mediapipe as mp
        import cv2
        import numpy as np
        from mediapipe.tasks import python as mp_tasks_python
        from mediapipe.tasks.python import vision
    except ImportError as error:
        failures.append(f"Required import failed: {error}")
    else:
        print(f"MediaPipe: {mp.__version__}")
        print(f"OpenCV: {cv2.__version__}")
        print(f"NumPy: {np.__version__}")
        tasks_available = all(
            (
                hasattr(mp_tasks_python, "BaseOptions"),
                hasattr(vision, "HandLandmarker"),
            )
        )
        print(f"MediaPipe Tasks API: {'available' if tasks_available else 'unavailable'}")
        if not tasks_available:
            failures.append("MediaPipe Tasks API HandLandmarker is unavailable.")

    if failures:
        print("\nEnvironment verification failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nEnvironment verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
