---
updated: 2026-10-29
updated_by: Ryan (Claude, math-folder session)
---
# 6. Balance vs swing-up: what differs and why

[Back to Double](README.md) · Prev: [5. Swing-up](05_swing_up.md) · Next: [7. Results](07_results.md)

## 6.1 Side by side

| | Balance (`PythonMasterDouble-Claude.py`) | Swing-up (`PythonMaster2_swingup.py`, SWING phase) |
| --- | --- | --- |
| Region of motion | within a few degrees of upright | full turns, every angle |
| Model used | linear, at upright | full nonlinear (`f`), linearised along the plan every step |
| Arm values | SYSID ratios (P2 2.013, J2r 0.414) | swing-fit ratios (P2 1.802, J2r 0.391) [HYP] |
| Joint friction B2 | 0.03 | 0.114 (fitted to big swings; the balance part of the same script uses 0.03) |
| Actuator model | ramp, send the average speed | staircase, send the new speed |
| Delay assumed | 9 ms | 8 ms |
| Reference | zero (upright, cart centred) | the plan $`\mathbf z_{\text{ref}}[k]`$, $`a_{\text{ref}}[k]`$ |
| Feedforward | none | $`a_{\text{ref}}[k]`$ does almost all the work |
| Feedback gain | constant $`K`$ (7 numbers) | $`K_k`$, a different 7-number gain each of the 250 steps |
| LQR weights | 2°, 60°/s, 5 cm, 0.3 m/s; $`R`$ = 1/1.3² | 5°, 120°/s, 25 cm, 0.3 m/s; $`R`$ = 1/5² |
| Horizon | infinite (one Riccati fixed point) | 2.5 s, backward recursion ending in the balance $`P`$ |
| Estimator | linear steady Kalman filter, all states coupled | nonlinear prediction + per-arm constant gain, sensor-age compensation |
| Limits | 15 m/s², 0.8 m/s | 16 m/s² with the torque-speed limit, 1.0 m/s |
| Gives up | 30° | 35° from the plan, or cart 0.36 m |
| Tolerance to model error [SIM] | about 5 % in the worst direction, 15 % or more in others ([4.10](04_balance.md#410-how-sensitive-is-the-balance-to-the-arm-values-sim)) | about 2-4 % in every direction ([7.2](07_results.md#72-which-model-errors-the-swing-up-survives-sim)) |
| Rig result | 12.8 min [HW] | 0 catches in 35 attempts [HW] |

## 6.2 Why the swing-up is so much more sensitive

**Balance is a regulator; swing-up is mostly open loop.** The balance controller only has to keep small errors small, and it sees them immediately. The swing-up's motion comes from the plan: about 2.5 s of feedforward chosen for a model, with feedback trimming the difference. Every error in the model makes the real arms drift from the plan, and the drift is amplified by the unstable dynamics (up to 12.7 % per cycle near upright, [3.5](03_linear_model.md#35-discretisation)) until the feedback is out of authority.

**The feedback has little room.** The plan already uses the whole track (±0.25 m) and nearly the whole speed range (0.75 of the 0.831 m/s really available, [7.4](07_results.md#74-why-every-rig-attempt-tops-out-at-0831-ms)). Any correction that needs more speed is clipped. In the balance, the cart normally moves a few millimetres at a few cm/s, so the limits are far away.

**The swing passes through regions where the cart barely reaches the arms.** The cart acts on each arm through $`p_i\cos\theta_i`$ ([2.3](02_equations_of_motion.md#23-lagranges-equations)). When an arm is horizontal, $`\cos\theta \approx 0`$ and no cart acceleration can turn it. Errors that build up there cannot be corrected until the arm moves on.

**Chaos.** Away from upright and hanging, nearby motions of a double pendulum separate quickly. A balance never goes there.

## 6.3 Why different arm values and friction

The balance needs the model near upright, where small differences in P2 or J2r shift the gains a little and the loop absorbs them ([4.10](04_balance.md#410-how-sensitive-is-the-balance-to-the-arm-values-sim)). The swing-up needs the model over the whole motion, so it was given ratios fitted to the rig's own swing-up attempts (swing-fit, [params.md](../../params.md)) [HYP], including a joint friction B2 = 0.114, about 20x the SysID value. For the balance part the script keeps `BALANCE_B2` = 0.03 because "The rig balances best with 0.03". Friction measured in big swings and friction that matters for 1° wobbles need not be the same number: real joint friction is partly Coulomb (constant torque), which looks like a big viscous coefficient at low speeds and a small one at high speeds [HYP].

## 6.4 Why different actuator models

The balance script was written first, with the ramp model and the "send the average speed" trick, and it works. The swing-up needs the stepper's real behaviour to predict 2.5 s ahead, including the instantaneous speed jumps and the arm kicks they cause ([2.7](02_equations_of_motion.md#27-when-the-stepper-jumps-speed-the-kick)): at 0.75 m/s and 7 m/s², each 10 ms jump is 0.07 m/s, which kicks arm 1 by 0.39 rad/s near upright. Over a period both models move the cart the same distance; they differ in when within the period the arms feel it.

## 6.5 Compared with the single

| | Single ([Single 8](../Single/08_balance_vs_swingup.md)) | Double |
| --- | --- | --- |
| Swing-up method | feedback only: energy pumping, works from any start | plan + TV-LQR: needs a still, hanging start |
| What the swing-up needs from the model | almost nothing (IDENTIFY measures $`\omega_0`$ on the rig) | 4 ratios within 2-4 % |
| Hand-over | catch window (17°, 3.5 rad/s, energy, cart) | the plan ends exactly at upright; balance takes over at a fixed step |
| Balance gains | LQR ×2 on a force model | LQR on the acceleration model with delay, no extra factor |

[Back to Double](README.md) · Prev: [5. Swing-up](05_swing_up.md) · Next: [7. Results](07_results.md)
