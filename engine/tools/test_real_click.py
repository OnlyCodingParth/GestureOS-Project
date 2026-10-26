import sys
import time
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.activation import GestureActivation
from gestureos_engine.automation import WindowsAutomation
from gestureos_engine.emergency import EmergencyStopController


def main():
    print("=" * 55)
    print("GestureOS | M5.2 Real Mouse Click Test")
    print("=" * 55)

    print("\nSAFETY INFORMATION:")
    print("- GestureOS starts DISABLED.")
    print("- Only one mouse click will be executed.")
    print("- You must explicitly confirm the action.")
    print("- Move the cursor to a screen corner for PyAutoGUI fail-safe.")
    print("- Press Ctrl+C in the terminal to cancel.")

    activation = GestureActivation()
    emergency = EmergencyStopController(activation=activation)

    if not emergency.start_hotkey():
        print("\n[CANCELLED] Global emergency stop unavailable.")
        return

    automation = WindowsAutomation(
        activation=activation,
        dry_run=False,
        emergency_stop_available=True,
    )

    print("\nCurrent state:", activation.state.value)

    confirmation = input(
        "\nType YES to enable one real mouse click: "
    )

    if confirmation != "YES":
        print("\n[CANCELLED] No mouse action executed.")
        return

    activation.enable()

    print("\nGestureOS ENABLED.")
    print("Position your mouse over a safe, empty area.")
    print("The click will happen after 5 seconds.")

    try:
        for seconds in range(5, 0, -1):
            print(f"Click in {seconds} seconds...")
            time.sleep(1)

        result = automation.left_click()

        print("\nResult:", result)

    except KeyboardInterrupt:
        print("\n[CANCELLED] Test interrupted.")

    finally:
        emergency.stop_hotkey()
        activation.disable()
        print("[SYSTEM] GestureOS DISABLED.")
        print("[SYSTEM] Test completed.")


if __name__ == "__main__":
    main()