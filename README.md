# GestureOS

GestureOS is a Windows 11 desktop hand-gesture controller. It is designed as a safe, local-first companion to the mouse and keyboard for short tasks such as pointing, scrolling, media control, and presentations.

## Status

Project initialization is complete. No implementation or dependencies have been added. The next approved step is **M0 - environment verification**, and it requires user approval before it begins.

## Approved direction

- Python 3.12 gesture engine, kept independent from the desktop UI.
- MediaPipe Hand Landmarker Tasks API for landmarks; rule-based gestures for v1.
- Safety state machine and emergency stop before any real Windows input.
- Electron, React, and TypeScript desktop shell at M6 only.
- Local-only, token-authenticated WebSocket between the engine and shell.

See [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and [PROGRESS.md](PROGRESS.md).

## Research

The approved research remains unchanged in `01_Research/`:

- `01_Technical_Research.pdf`
- `02_Features_Research.pdf`
- `03_Technology_Architecture.pdf`
- `04_UI_UX_Development_Blueprint.pdf`
