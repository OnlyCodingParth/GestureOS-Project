# GestureOS Development Rules

## Required rules

1. Follow the approved research and architecture.
2. Implement one milestone at a time.
3. Do not modify unrelated files.
4. Do not add dependencies without justification.
5. Never invent library APIs.
6. Preserve previously tested functionality.
7. Prioritize Windows 11 compatibility.
8. Implement safety mechanisms before real Windows automation.
9. Run relevant tests after modifications.
10. Update `PROGRESS.md` after every completed task.
11. Do not start another milestone without user approval.
12. Keep all code and documentation professionally organized.

## Project-specific guardrails

- Use Python 3.12 and the MediaPipe Tasks API; do not use legacy `mp.solutions` examples.
- The engine owns camera access, Windows actions, configuration, and safety. The UI only displays state and sends validated commands.
- Keep the engine transport-agnostic. Electron + React/TypeScript begins at M6; PySide6 is the fallback only if the M6 packaging trigger is met.
- Route every Windows action through the safety layer. Start in dry-run mode; release all held input on any transition to Off.
- Keep control local-only: loopback binding, session token, origin checks, schema validation, and no frame persistence by default.
- Make changes in small named-file tasks. Add tests first for pure logic where practical and review the diff before committing.
- Record dependency decisions in `docs/DECISIONS.md` and project state in `PROGRESS.md`.
