"""Safe PINCH click integration test; never controls the real mouse."""

import sys
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from gestureos_engine.gestures import Gesture
from gestureos_engine.pipeline import GestureSafetyPipeline


pipeline = GestureSafetyPipeline(hold_duration=0.5)
pipeline.enable()
print(pipeline.process(Gesture.PINCH, 1.0))
print(pipeline.process(Gesture.PINCH, 1.5))
print(pipeline.process(Gesture.PINCH, 1.6))
pipeline.process(Gesture.UNKNOWN, 1.7)
print(pipeline.process(Gesture.PINCH, 2.0))
print(pipeline.process(Gesture.PINCH, 2.5))
pipeline.shutdown()
