"""Safe bounded scroll backend test; dry-run is always enabled."""

import sys
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.activation import GestureActivation
from gestureos_engine.automation import WindowsAutomation
from gestureos_engine.cooldown import ActionCooldown


activation = GestureActivation()
activation.enable()
automation = WindowsAutomation(activation, dry_run=True)
cooldown = ActionCooldown(cooldown_duration=0.5)
print(automation.scroll(3, cooldown, current_time=1.0))
print(automation.scroll(3, cooldown, current_time=1.1))
print(automation.scroll(-3, cooldown, current_time=1.5))
activation.emergency_stop()
print(automation.scroll(1, cooldown, current_time=2.0))
