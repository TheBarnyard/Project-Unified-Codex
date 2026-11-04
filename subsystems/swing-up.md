---
updated: 2026-11-04
updated_by: Ryan (Claude, V2 arms fit session)
---
# Swing-up

## Double swing-up
- Trajectory designed offline by optimal control (`swingup_design.py`, IPOPT), tracked with time-varying LQR, then handed to balance. Exports to MuJoCo.
- Rig script: `PythonMaster2_swingup.py` with `double_swingup_trajectory.json`. Both live only on the Pi in the legacy ENGT481 checkout [?].
- Status: catches in the digital twin [SIM]; every rig attempt so far aborts. Current lead and plans: [debug record](../debug/2026-10-27_double-swingup-aborts.md). Limits: [params.md](../params.md).
- The twin shows the TV-LQR swing is fragile: about 3% model ratio error, or B2 x1.5 or x0.5, makes it fail [SIM].
- 2026-10-29 ([twin v3 session](../sessions/2026/10/2026-10-29_2133_Barney_twin-new-arms-math.md)): plan re-made for the new arms (`double_swingup_trajectory_newarms.json`, 2.5 s; ~~peak 0.280 m~~ Superseded 2026-10-30 by the same session: re-made from the Pi's 2026-10-27 script (PLAN_TRACK 0.25 m), peak 0.250 m / 0.751 m/s / 8.0 m/s²) with copy `PythonMaster2_swingup_newarms.py`; catches in the twin [SIM], not tried on the rig. Files in project files `TwinV3/ctl3/DoublePendulum/`.
- 2026-10-29 (Ryan/Claude, [math-folder session](../sessions/2026/10/2026-10-29_1448_Barney_math-folder.md)): full math and an independent simulator in [Math/Double](../Math/Double/README.md); every gain of the double scripts reproduced exactly. Findings:
  - Independent re-implementation agrees with the twin: one ratio off by 2-3 % or B2 x0.5/x1.5 breaks the stored 2.5 s plan [SIM].
  - All 35 rig attempts 2026-10-21 to 2026-10-28: the error from the plan jumps from about 3° to about 9° between k = 100 and 110 in every attempt, before the 0.831 m/s cap at k ≈ 113 [HW]. Model error is the likely cause, the cap the symptom [HYP]. [Math/Double 7.3](../Math/Double/07_results.md#73-what-the-rig-did-hw)
  - **A longer plan with the same limits is far more tolerant:** 3.5 s survives 25 of 36 single model errors (incl. B2 x0.5 to x2) vs 11 of 36 for the stored 2.5 s plan [SIM]. Ready in the script's file format: `Math/Double/data/double_swingup_trajectory_3.5s.json`, checked with the script's own `plan_problem` and `load_trajectory`. Untested on the rig. [Math/Double 7.2](../Math/Double/07_results.md#72-which-model-errors-the-swing-up-survives-sim)
  - The fitted ratio sets break the identity H = L1·P2 (L1 = 0.200 m): the swing-fit set implies L1 = 0.218 m. In simulation the swing-up tolerates real physical errors (CoM ±10 mm, arm 1 mass -15/+20 %) far better than such ratio errors; arm 2's mass and inertia (about ±5 %) are the sensitive values [SIM]. [Math/Double 1.5](../Math/Double/01_variables.md#15-the-ratios-what-the-scripts-and-system-id-really-use)
- **2026-11-04: V2-arm swing-up package (Barney picked 7 plans from the [style gallery](https://claude.ai/artifact/WJcTh1yAmw7quvpkzteU65)), [V2 arms fit session](../sessions/2026/11/2026-11-04_1555_Barney_v2-arms-model-fit.md).** `PythonMaster2_swingup_V2.py` is a copy of the Pi's script (ba019f9), with the V2 fit in `SYSID_RATIOS`, `--path`/`--list` plan picker, `ARM2_CHANNEL = "auto"` (slot 2 or 3), `PLAN_TRACK_M 0.30`, and `--plan` keeping the plan's start branch. Plans `double_swingup_V2_<name>.json`: same_3.0s / same_3.5s / same_4.0s, whip_3.0s / whip_3.5s / whip_4.5s (arm 2 makes 1.5 turns), folded_4.5s. Code: `TheBarnyard/ChatGPT-Pendulum-Project` branch `claude/project-thread-74rdr9`, `DoubleSwingUp_V2/` (commit 9949265). Pi folder suggested: `~/Desktop/DoubleSwingUpV2`.
  - Exact script on the digital twin (11 cases × 3 seeds: nominal, arm-2 mass ±4 %, arm-2 I ±10 %, arm-1 I +10 %, arm-2 CoM +3 %, friction ×3, TX2 on slot 3, radio loss), first-try catches [SIM]: same_4.0s 33/33, same_3.5s 33/33, same_3.0s 30/33, whip_4.5s 28/33, whip_3.5s 27/33, folded_4.5s 24/33, whip_3.0s 23/33. All catch in the nominal case. Whip and folded are sensitive to arm 2's mass and inertia. Untested on the rig.
  - Visuals (2026-11-04 18:40): [V2 Swing-Up Simulations](https://claude.ai/artifact/ALjwSAhuB8Vr3RKMJCCFU5), twin vs plan per path at nominal, arm-2 I +10 % and mass -4 %; GIFs in Claude project files `DoubleSwingUp_V2/visuals/`. Only same_3.5s and same_4.0s catch in all three [SIM].
- Triple (no rig): the same method with n = 3 needs a 4.0 s plan to stay inside the rig's limits [SIM][HYP]. [Math/Triple](../Math/Triple/README.md)

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
