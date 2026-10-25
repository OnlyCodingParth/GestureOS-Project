# Feature Scope

## v1.0 - approved functional foundation

The v1.0 foundation contains the 17 essential feature areas identified in the research:

1. Camera selection, health checks, and clear failure feedback.
2. MediaPipe Tasks API landmark tracking and visible overlay.
3. Arm and pause control.
4. Keyboard emergency stop and release-all behavior.
5. Cursor control with smoothing, dead zone, and a safe box.
6. Left and double click.
7. Drag and drop with safe release on tracking loss.
8. Right click.
9. Vertical scroll.
10. Volume control.
11. Media keys.
12. Calibration.
13. Settings for sensitivity, smoothing, handedness, and reduced movement.
14. Safety state machine, confirmations, cooldowns, rate limits, and danger list.
15. Dashboard and live state.
16. Privacy-first onboarding and JSON settings.
17. Debug status for FPS, latency, gesture, and state.

Only a small, mode-specific pose set is active at a time. Gesture rules use normalized hand-size ratios, confirmation frames, hysteresis, and cooldowns.

## Later releases

- **v1.5:** context profiles, manual modes, remapping, presentation controls, a safe application launcher, window shortcuts, precision/relative cursor modes, activity history, confidence feedback, trainer, and floating status overlay.
- **v2.0:** Gesture Studio, custom gesture training, safe workflows, reading mode, and air annotation after the core is stable.
- **Experimental/deferred:** two-hand zoom, 3D visualization, voice, and hand-driven window drag/resize.

## Excluded from v1

Arbitrary shell commands, default gesture-triggered sleep/lock/shutdown, cloud features, stored camera images, Administrator operation, and frontend work before M6.
