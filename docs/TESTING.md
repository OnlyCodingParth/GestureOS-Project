# Testing Strategy

## Test layers

- Unit tests: gesture rules, state transitions, configuration, and protocol using recorded landmark data; no camera required.
- Hardware tests: camera availability, tracking quality, cursor feel, display scaling, media keys, and global hotkey behavior.
- Recovery tests: camera loss, engine loss, UI loss, corrupt configuration, and emergency stop during drag.
- Packaging tests: engine spike at M2b; Electron chain at M6; clean-account install at M11.

## Core acceptance targets

These are research targets to measure and tune locally, not guarantees:

- Capture: 60 seconds without a backlog; disconnect recovers or explains within five seconds.
- Tracking: visible hand yields 21 landmarks; no-hand state never crashes.
- Recognition: replay tests pass; each v1 pose succeeds at least 8/10 live trials for the developer and then two other people.
- Mouse: reaches four corners; at least 18/20 intended clicks; tracking loss releases drag within 300 ms.
- Emergency stop: stops within 200 ms, releasing buttons and keys; elevated-app behavior is documented.
- Integration: engine goes Off within five seconds after UI loss; one-hour run has no crash or stuck input.

Record measured FPS, delay, CPU, memory, failures, and tuning decisions in `PROGRESS.md` and `DECISIONS.md`.

## M5 controlled Windows tests

Run unit tests from PowerShell without touching the real mouse:

```powershell
Set-Location 'C:\Users\ADMIN\OneDrive\Desktop\My_Personal\My Project\GestureOS-Project\engine'
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Safe dry-run tools:

```powershell
& .\.venv\Scripts\python.exe tools\test_gesture_click_dry_run.py
& .\.venv\Scripts\python.exe tools\test_scroll_dry_run.py
& .\.venv\Scripts\python.exe tools\verify_emergency_stop.py
```

The cursor-only tool is `tools\test_async_cursor.py`. It starts disabled, requires the
global emergency stop to register, and performs no clicking or scrolling. Press `E`
only after confirming the preview, press `S` or Ctrl+Alt+Shift+X to stop, `R` to reset,
and `Q` to quit. Camera failure and tracking loss reset cursor smoothing and block actions.

The controlled real-click tool is `tools\test_real_click.py`. It starts disabled and
requires typing `YES`, but it is still a physical click test: position the cursor over
a safe target and keep the PyAutoGUI corner fail-safe available. Run it only on a
non-production desktop. No test tool automatically enables real automation.

Known limitations: global hotkeys can be blocked by Windows policy, another registered
owner, secure desktop transitions, or privilege boundaries. A successful registration
does not guarantee availability on the secure desktop, so manual verification must
include the preview unfocused. The async worker reduces processing backlog by selecting
the newest frame; it does not increase the webcam's physical FPS.

## M0 environment record

Verified on 2026-10-25 with the project-local `engine/.venv/`:

- Python 3.12.10, 64-bit
- MediaPipe 1.1.1
- OpenCV 5.0.0 from `opencv-contrib-python` 5.0.0.93 (installed through MediaPipe; no second OpenCV package)
- NumPy 2.5.4
- MediaPipe Tasks API import: passed
- `pip check`: passed with no broken requirements
- Node.js v24.18.0; npm 11.16.0; Git 2.55.0.windows.3

Manual camera acceptance test: passed. The default-camera preview captured 651 frames at an average 28.5 FPS; Q-key exit succeeded and the camera closed cleanly.
