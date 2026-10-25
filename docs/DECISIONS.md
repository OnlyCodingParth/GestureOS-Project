# Decisions

| Decision | Status | Rationale |
| --- | --- | --- |
| Separate Python engine plus Electron/React shell | Approved | Isolates camera and automation from UI; supports independent testing. |
| Python 3.12, 64-bit | Approved pending M0 verification | Conservative Windows compatibility target. |
| MediaPipe Hand Landmarker Tasks API | Approved | Pretrained 21-landmark tracking; avoids legacy APIs. |
| Rule-based gestures for v1 | Approved | Small, explainable, testable gesture vocabulary. |
| One local WebSocket | Approved | Carries validated events, commands, settings, and heartbeat without a second HTTP framework. |
| Safety before real actions | Approved | Dry run, global stop, release-all, confirmation, cooldown, rate limits, and allow-list prevent harmful input. |
| Windows media keys for v1 volume/media | Approved | Avoids adding pycaw unless exact-percent volume is later justified. |
| Local privacy defaults | Approved | Loopback-only service, token, no frame persistence, no telemetry, no Administrator rights. |
| PyInstaller onedir and electron-builder | Approved | Packaging is tested early; onedir reduces startup and antivirus risk. |
| PySide6 fallback | Conditional | Use only if M6 packaging cannot pass the clean-account test after two focused weeks. |

Add a row before adding or changing a dependency, architecture boundary, or safety policy.
