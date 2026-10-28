---
updated: 2026-10-28
updated_by: Barney (Claude, PUC setup session)
---
# Repos and Pi workflow

## Repositories
| Repo | What | Access |
| --- | --- | --- |
| `etwan007/ENGT480` | Team code and run logs (main repo) | Public; Barney cannot push |
| `ENGT481` | Older code; legacy checkout on the Pi | |
| `TheBarnyard/ChatGPT-Pendulum-Project` | Barney's AI work branches (`claude/project-thread-*`) | Barney |
| `TheBarnyard/Project-Unified-Codex` | This codex (PUC) | Team |

## ENGT480 branches (since 2026-10-21)
- `main`: approved version. Pi checkout `/home/engt481/Desktop/ENGT480`.
- Experiment branches auto-enrolled on the Pi: `*_EXP`, `experiment/*`, plus `Ethan-wirelessTX`. Checkouts at `/home/engt481/Desktop/Experiments/<branch>`. As of 2026-10-23: `Ethan_EXP`, `Jaren_EXP`, `experiment/vecter`. `codex/*` branches are not enrolled.
- Pi automation `Tools/PiAutomation/pi_sync.py`, shared helpers `Code/Global/`, and the log uploader live on `Ethan_EXP`, not `main`. Docs in `GeneralDocumentation/` on `Ethan_EXP`.
- `logs` branch: `<device-id>/Code/...` (legacy ENGT481 checkout) and `<device-id>/checkouts/<main|checkout-id>/Code/<setup>/run_logs/`. Device id `raspberrypi-c8674ffe`.

## On the Pi
- Legacy checkout `~/Desktop/GitHub Repository/ENGT481` is kept untouched; some of Barney's scripts live only there.
- Desktop shortcuts: ENGT480 Run, Sync Status, Pause/Resume Updates. Pause before editing.
- Remote access is through Raspberry Pi Connect (see [gotchas](../gotchas.md)).
