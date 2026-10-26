"""Verify emergency state transitions without registering a live hotkey."""

import sys
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.emergency import EmergencyStopController


controller = EmergencyStopController()
print("Initial:", controller.activation.state.value)
controller.trigger()
print("Stopped:", controller.activation.state.value)
print("Enable while stopped:", controller.activation.enable())
controller.reset()
print("After reset:", controller.activation.state.value)
print("Manual enable:", controller.activation.enable())
