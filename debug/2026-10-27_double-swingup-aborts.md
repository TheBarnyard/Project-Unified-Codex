---
type: debug
status: open
opened: 2026-10-27
by: Barney (Claude)
subsystems: [swing-up, cart-arduino, arms-and-model]
---
# Double swing-up aborts on the rig

## Symptoms
Every rig attempt aborts at step 108 to 198 of 250, mostly cart aborts near the track limit, some on angle. Same on the old arm (2026-10-21) and the new arm 1.

## Runs
| Run | Plan | Result |
| --- | --- | --- |
| `swingup_double_20261027_173146_753180` | old ratios | 2 of 3 cart aborts at -0.256 m; feedback hits CART_ACCEL_MAX at step about 115 |
| `swingup_double_20261027_182845_619344` | SysID ratios, PLAN_TRACK 0.30 | 5/5 failed: 4 cart aborts at -360 mm (k 127 to 146), 1 angle |
| `swingup_double_20261028_085228` | swingfit, PLAN_TRACK 0.25 | failed at k=135 |

## Tests and dead ends
- Model mismatch with the new arm: ruled out. Existing ratios fit the new arm within about 7 deg [HW].
- More track margin alone: did not help (twin) [SIM].
- Ratio refit from swing windows: B2 about 20x the SysID value [HYP]; a closed-loop twin with that model reproduces the abort at k about 141 [SIM].

## Current best explanation (2026-10-28)
In all runs the cart sticks at v = -0.831 m/s (commanded -0.858, a = 0) for about 25 cycles from k about 112. The torque limit, 16 x (1 - |v| / 1.0) = 2.7 m/s^2 at 0.83 m/s, is smaller than one stepper timer step (0.831 to 0.890 m/s needs 5.9 m/s^2 in 10 ms), so the speed rounds back: a hard cap near 0.83 m/s [HW]. Plans peaking at 0.75 m/s have no headroom.

## Findings 2026-10-29 (Ryan/Claude, [math-folder session](../sessions/2026/10/2026-10-29_1448_Barney_math-folder.md))
- All 35 attempts in the logs branch (15 runs, 2026-10-21 to 2026-10-28): 0 caught, aborted at k = 107 to 237, 24 angle and 11 cart aborts, every one reached exactly 0.831 m/s [HW]. Confirms the cap above on all of them.
- But the cap is not the first thing that goes wrong: in all five attempts of `swingup_double_20261027_184605` the largest error from the plan is 1-4° at k = 100, then 8-10° at k = 110, before the first step at 0.831 m/s (k = 113) [HW]. The jump happens the same way every attempt, so it is a model error, not noise [HYP]. [Math/Double 7.3](../Math/Double/07_results.md#73-what-the-rig-did-hw)
- Simulation of the script's loop (independent of the twin): the stored plan needs every ratio within about 2-3 % and B2 within well under ±50 % [SIM]. The v060 plan: 13 vs 11 of 28 single-error cases [SIM].
- **A 3.5 s plan with the same limits survives 25 of 36 single model errors instead of 11, including B2 x0.5 to x2** [SIM]. File: `Math/Double/data/double_swingup_trajectory_3.5s.json` (script format; checked with the script's `plan_problem` and `load_trajectory`). [Math/Double 7.2](../Math/Double/07_results.md#72-which-model-errors-the-swing-up-survives-sim)
- The fitted ratio sets break H = L1·P2 (swing-fit implies L1 = 0.218 m, real 0.200 m). The swing-up tolerates physical errors much better than ratio errors [SIM]; fitting with H fixed to 0.2·P2 is untested [HYP].

## Next
- 2026-10-29: try `Math/Double/data/double_swingup_trajectory_3.5s.json` (back up the stored plan, copy it over `double_swingup_trajectory.json`) [SIM says 2x more tolerant].
- Try plan `double_swingup_trajectory_v060.json` (PLAN_SPEED 0.60); best in the twin [SIM].
- Or round the timer toward the requested speed, or raise MOTOR_TOP_SPEED (stall risk).

Plans: branch `claude/project-thread-orcdoj` of `TheBarnyard/ChatGPT-Pendulum-Project`, `DoubleSwingUp_NewArm/`.
