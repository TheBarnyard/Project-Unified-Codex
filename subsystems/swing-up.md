---
updated: 2026-10-29
updated_by: Ryan (Claude, math-folder session)
---
# Swing-up

## Double swing-up
- Trajectory designed offline by optimal control (`swingup_design.py`, IPOPT), tracked with time-varying LQR, then handed to balance. Exports to MuJoCo.
- Rig script: `PythonMaster2_swingup.py` with `double_swingup_trajectory.json`. Both live only on the Pi in the legacy ENGT481 checkout [?].
- Status: catches in the digital twin [SIM]; every rig attempt so far aborts. Current lead and plans: [debug record](../debug/2026-10-27_double-swingup-aborts.md). Limits: [params.md](../params.md).
- The twin shows the TV-LQR swing is fragile: about 3% model ratio error, or B2 x1.5 or x0.5, makes it fail [SIM].

Plans sent (branch `claude/project-thread-orcdoj` of `TheBarnyard/ChatGPT-Pendulum-Project`, folder `DoubleSwingUp_NewArm/`):
| File | Notes |
| --- | --- |
| `double_swingup_trajectory.json` | SysID ratios, PLAN_TRACK 0.30. Failed 5/5 on rig 2026-10-27 |
| `double_swingup_trajectory_swingfit.json` | Swing-fit ratios, PLAN_TRACK 0.25. Failed 2026-10-28 at k=135 |
| `double_swingup_trajectory_v060.json` | PLAN_SPEED 0.60. Untested on rig |

## Single swing-up
- ~~`Code/SinglePendulum/PythonMasterSwingUpExp.py`, `swingup_control.py` in ENGT480. [?] status on the rig.~~ Superseded 2026-10-29 by [2026-10-29 math session](../sessions/2026/10/2026-10-29_1448_Barney_math-folder.md): that is the earlier version.
- **Best single swing-up (Barney, 2026-10-29): `PythonMasterUpExpClaudeImproved.py`**, byte-identical to `PythonMasterUpExpClaude.py`. Location: etwan007/ENGT480 branch `experiment/legacy-pi-recovery` (commit ba019f9), `LegacyPi/Code/SinglePendulum/`; on the Pi in the legacy ENGT481 checkout.
- Method: IDENTIFY (wiggle, time free swings, measure w0, redesign LQG with matching inertia) → energy pumping with shaped centering spring and adaptive target → catch window (0.30 rad, 3.5 rad/s, e 0.95-1.15, cart < 0.12 m) → LQG Q = diag(40,5,150,60) ×2 with auto-trim; back to swing-up past 0.8 rad or 0.22 m cart.
- 28 rig runs 2026-10-16 to 2026-10-27 [HW]: w0 7.09-7.47 rad/s (model 5.91), swing-up after identify median 1.75 s, 39 catches, longest balance 114 s; 23 of 24 hand-backs were the 0.22 m cart limit.
- Full math, code walkthrough, simulator and figures: [Math/Single](../Math/Single/README.md).
