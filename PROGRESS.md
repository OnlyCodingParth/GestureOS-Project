# Progress

## Current milestone

M5 - Windows automation, safety, and optimization complete; checkpoint ready.

## Completed

- Read and recorded the four approved research documents in `01_Research/`.
- Created the baseline directory structure, documentation, `.gitignore`, and local Git repository.
- Defined the approved architecture, scope, roadmap, testing approach, and engineering rules.
- Verified the required project folders, Markdown files, root `.gitignore`, and four preserved research PDFs.
- Created `engine/.venv/` with Python 3.12.10 (64-bit).
- Installed and verified MediaPipe 1.1.1, OpenCV 5.0.0 (via `opencv-contrib-python` 5.0.0.93), and NumPy 2.5.4.
- Confirmed the MediaPipe Tasks API imports and `pip check` reports no broken requirements.
- Added reproducible M0 environment and manual camera verification scripts.
- Completed the manual webcam test: 651 frames, 28.5 average FPS, and a successful Q-key exit with a clean camera close.
- M1-M4: webcam capture, MediaPipe Tasks tracking, gesture recognition, stabilization, hold detection, cooldown, activation, emergency state, and dry-run pipeline.
- M5.1-M5.6.6: Windows automation backend, controlled click testing, coordinate mapping/smoothing, live cursor movement, and asynchronous capture integration.
- M5 completion: independent Ctrl+Alt+Shift+X emergency-stop controller, fail-closed real automation, bounded cursor controls, one-click-per-pinch integration, bounded scroll backend, tracking/camera failure handling, and safe dry-run tools.
- Full unit suite: 111 tests passing after M5 changes.
- Manual M5 verification: global Ctrl+Alt+Shift+X emergency stop, asynchronous cursor control, camera tracking, cursor movement, safety controls, and dry-run tools passed.

## Working

- M5 is implemented and manually verified. Physical automation remains opt-in and must still be used only through the controlled test tools.

## Broken / known limitations

- Windows registry reports `Windows 10 Home Single Language`, version `25H2`, build `26200.9711`; this needs user confirmation against the expected Windows 11 installation.
- Camera availability was validated on the default webcam. Performance outside the M0 preview and packaging remain later-milestone validation items.
- `RegisterHotKey` may fail under policy, another owner of the shortcut, secure desktop/UAC prompts, or an elevated application boundary. Real automation refuses to enable unless registration succeeds.
- Scrolling has a bounded dry-run/backend API but no live gesture mapping yet; the current gesture vocabulary does not provide a validated, conflict-free scroll gesture.
- The async worker keeps only the newest frame and does not increase physical webcam FPS. Camera read failure transitions the safety pipeline to emergency stopped.

## Next

- Create the M5 GitHub checkpoint.
- M6 architecture is documented in `docs/M6_ARCHITECTURE.md`; implementation must begin with the engine protocol/lifecycle spike after explicit approval.
