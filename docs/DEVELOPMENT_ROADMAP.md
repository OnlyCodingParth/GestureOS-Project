# Development Roadmap

Each milestone requires its predecessor's passing acceptance gate and user approval. Commit only working states and tag passed gates.

| Milestone | Outcome | Gate |
| --- | --- | --- |
| M0 | Verify environment | Required versions/imports and Windows Camera work |
| M1 | Newest-frame-only capture | 60-second run; disconnect does not hang |
| M2 | Tasks API landmarks | 21-point overlay; FPS and delay recorded |
| M2b | Packaging spike | Packaged tracker works on a clean Windows account |
| M3 | Rules and replay tests | Eight v1 poses pass recorded-landmark tests |
| M4 | Dry-run safety layer | State and hotkey tests pass; release-all verified |
| M5 | Real Windows actions | Each action is added and tested independently |
| M6 | Electron walking skeleton | Engine lifecycle, WebSocket, heartbeat, packaging pass |
| M7 | Premium UI with real data | UI has minimal measured impact on engine CPU |
| M8 | Settings and calibration | Live application and corrupt-config recovery pass |
| M9 | Failure drills | Every prescribed failure recovers or explains |
| M10 | Integration testing | One-hour run without crashes or stuck input |
| M11 | Final packaging | Clean-account install, run, and uninstall pass |

M6 uses Electron + React + TypeScript, Vite, Tailwind, Lucide, and light Motion. Do not initialize that application before M6.
