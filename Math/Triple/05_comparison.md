---
updated: 2026-10-29
updated_by: Ryan (Claude, math-folder session)
---
# 5. Single, double, triple: balance vs swing-up

[Back to Triple](README.md) · Prev: [4. Swing-up](04_swing_up.md)

## 5.1 One table

| | Single | Double | Triple [HYP rig] |
| --- | --- | --- | --- |
| Unstable poles (cart acceleration as input) | 1 | 2 | 3 |
| Fastest fall, cart held still | 7.3 /s (doubles in 95 ms) | 11.9 /s (58 ms) | **16.7 /s (42 ms)** |
| Cart's direct effect on the top arm (B) | | +0.62 (arm 2) | **-0.07** (arm 3) |
| Energy to add from hanging | 0.255 J | 1.614 J | 3.905 J |
| **Balance** | | | |
| Controller | LQG, force model, K × 2 ([Single 4](../Single/04_lqr.md)) | LQR + Kalman on the acceleration model with delay ([Double 4.3](../Double/04_balance.md#43-generation-2-acceleration-model-with-delay-pythonmasterdouble-claudepy)) | the double's, n = 3 |
| Gain: m/s² per degree of the top arm | 1.55 | -4.6 (arm 2) | **+15.0** (arm 3), -19.0 (arm 2) |
| Largest start lean caught | | 8° / 4° | 4.0° / 1.5° / 1.75° |
| Real motor delay it survives (designed for 9 ms) | | 21.8 ms | **14.1 ms** |
| Tolerance to real arm errors | IDENTIFY measures $`\omega_0`$ | mass -27 to +34 % or more | about ±10 % |
| Tolerance to one fitted number alone | | about ±5 % | **under 1 %** |
| On the rig | balances [HW] | 12.8 min [HW] | no rig |
| **Swing-up** | | | |
| Method | energy pumping, pure feedback ([Single 7](../Single/07_swing_up.md)) | stored plan + TV-LQR | stored plan + TV-LQR |
| Duration | median 1.75 s after IDENTIFY [HW] | 2.5 s plan | **4.0 s** plan for the same limits |
| Needs from the model | almost nothing | ratios ±2 %; arm 2 mass/inertia about ±5 % [SIM] | 4.0 s plan: ±5 % mass, ±10 % inertia all fine; fitted numbers < 1 % [SIM] |
| On the rig | works [HW] | 0 catches in 35 attempts [HW] | no rig |

Sources: [Single README](../Single/README.md), [Double README](../Double/README.md), pages 2-4 here. The single's 7.3 /s is for the cart acceleration as input (the force model of [Single 3](../Single/03_linear_model.md) gives 7.49 /s).

## 5.2 Balance vs swing-up for the triple

| | Balance | Swing-up |
| --- | --- | --- |
| Region | within about 2° of upright | everything, full turns |
| Model | linear at upright, 9 states | full nonlinear, linearised along the plan at each of 400 steps |
| Friction model | joints 3.36e-4 N m s (`BALANCE_B2`) | 1.28e-3 (swing-fit B2) |
| Motor model | ramp, average speed sent | staircase, new speed sent |
| Gain | one $`\mathbf K`$ (9 numbers) | 400 different $`\mathbf K_k`$ |
| Weights | 2°, 60°/s, 5 cm, 0.3 m/s, 1.3 m/s² | 5°, 120°/s, 25 cm, 0.3 m/s, 5 m/s² |
| Estimator | linear Kalman filter | nonlinear prediction + per-arm gain |
| Limits | 15 m/s², 0.8 m/s | 16 m/s², torque-speed limit, 1.0 m/s, the plan's ±0.25 m |
| Weakest point | motor delay (14 ms) and inconsistent model numbers | arm 2 and 3 values for short plans, joint friction lower than modelled, inconsistent numbers |

As for the double ([Double 6.2](../Double/06_balance_vs_swingup.md#62-why-the-swing-up-is-so-much-more-sensitive)): balance is a regulator that sees every error immediately; the swing-up is mostly feedforward, and every model error grows along the plan. The triple adds two things:
1. **Time is the cheapest robustness.** The 4.0 s plan is gentler (the same effort as the double's 2.5 s plan), keeps speed headroom below the 0.831 m/s timer ceiling, and tolerates every physical error tested; the 3.5 s plan does not ([4.7](04_swing_up.md#47-which-model-errors-it-survives-sim)).
2. **Model structure matters more than model accuracy.** Real errors of 5-10 % are fine, but one number fitted on its own breaks both balance and swing-up at about 1 % ([2.4](02_linear_model.md#24-controllability-one-cart-three-arms), [3.6](03_balance.md#36-what-the-balance-tolerates-sim)).

## 5.3 If the team ever builds it [HYP]

In order of how much they matter in these simulations:
1. Fit the model with its physical structure ($`h_{ij} = L_ip_j`$), from measured masses, CoMs and swing periods.
2. Plan the swing-up long enough to stay inside the motor's limits with headroom (4.0 s or more on this rig).
3. Keep the real motor delay well under 14 ms.
4. Make the third encoder, magnet and transmitter on arm 2's tip as light as possible, and include them in $`m_2`$, $`c_2`$, $`I_2`$.
5. The double's code already handles n = 3 in principle: everything in `PythonMaster2_swingup.py` that is written per arm (ratios, observer, angle building from joint encoders) would need a third entry; [`Math/shared/`](../shared/README.md) shows each piece for any n.

[Back to Triple](README.md) · Prev: [4. Swing-up](04_swing_up.md)
