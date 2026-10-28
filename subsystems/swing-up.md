---
updated: 2026-10-28
updated_by: Barney (Claude, PUC setup session)
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
- `Code/SinglePendulum/PythonMasterSwingUpExp.py`, `swingup_control.py` in ENGT480. [?] status on the rig.
