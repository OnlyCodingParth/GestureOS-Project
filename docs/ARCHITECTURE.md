# Architecture

## Approved design

GestureOS uses a separate Python 3.12 engine and an Electron shell with a React + TypeScript renderer. The Electron application is intentionally deferred until M6. The fallback is PySide6 using the same engine core if the packaged M6 skeleton cannot run on a clean Windows account after two focused weeks.

## Engine responsibilities

The engine owns camera capture, MediaPipe Tasks API tracking, rule-based gesture evaluation, safety state, allowed Windows actions, configuration, hotkey, watchdog, logging, and the local server. Capture keeps only the newest frame. Pure gesture, safety, configuration, and protocol logic must remain hardware-independent and testable.

## Safety boundary

Every recognized gesture must pass through the state machine before it can reach an action executor:

`camera -> landmarks -> gesture rules -> safety validation -> allow-listed action -> UI feedback`

The states are Off, Idle, Candidate, Active, and Cooldown. Emergency stop, camera loss, engine error, or UI-heartbeat loss put the engine in Off and release held buttons and keys.

## Process and communication

Electron creates a session token, starts the engine, and manages its lifecycle. The engine binds only to `127.0.0.1` on a random port and serves one token-authenticated WebSocket with validated messages, commands, settings, heartbeat, status, landmarks, and optional visible-window preview. The UI does not own the camera or Windows automation.

Configuration belongs in `%APPDATA%\\GestureOS`, not in the repository. It is schema-versioned, backed up on save, and written only by the engine.
