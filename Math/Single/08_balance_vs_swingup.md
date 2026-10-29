---
updated: 2026-10-29
updated_by: Ryan (Claude, math-folder session)
---
# 8. Balancing vs swing-up: what is different and why

[Back to Single](README.md) · Prev: [7. Swing-up](07_swing_up.md) · Next: [9. Code walkthrough](09_code_walkthrough.md)

Two very different controllers share one loop. Balance is **linear state feedback around one point** (upright). Swing-up is **nonlinear energy control over the whole circle**. Neither can do the other's job: the linear model is wrong 20° from upright, and energy control has no way to hold an unstable point.

## 8.1 Side by side (inside PythonMasterUpExpClaudeImproved.py)

| | Balance (LQG) | Swing-up (energy) |
| --- | --- | --- |
| Valid where | $`\lvert\theta\rvert`$ < 0.3 rad to enter, gives up at 0.8 rad | anywhere on the circle |
| Model | linearised $`A, B`$ about upright ([3](03_linear_model.md)) | only $`\omega_0`$ and $`\dot e = \ddot x\dot\theta\cos\theta/g`$ ([7.2](07_swing_up.md#72-normalised-energy)) |
| Goal | drive $`[\theta, \dot\theta, x, \dot x]`$ to 0 | drive the energy $`e`$ to $`e^* \approx 1`$ |
| Angle rate | Kalman estimate $`\hat{\dot\theta}`$ | filtered finite difference $`\hat{\dot\theta}_{\text{fd}}`$ |
| Cart speed used | estimator state $`\hat{\dot x}`$ | the speed it commanded itself, $`v_{\text{swing}}`$ |
| Law | $`u = -2K\hat{\mathbf y}`$, a force; speed = $`\hat{\dot x}`$ integrated through the model ([5.5](05_kalman_lqg.md#55-the-virtual-cart)) | acceleration $`6\,\text{sat}(4(e^*-e))\,\text{sign}(\dot\theta\cos\theta)`$ + centering; speed = integral |
| Gains | $`K`$ from $`Q`$ = diag(40,5,150,60), $`R`$ = 1, ×2 | gain 4, accel 6 m/s², spring 12/s², damper 6/s |
| Effective strength | 1.55 m/s² per degree of tilt ([4.5](04_lqr.md#45-what-the-law-means-for-a-stepper)) | always full 6 m/s² until 0.25 from target |
| Speed / accel limits | 0.8 m/s, 15 m/s² | 0.6 m/s, 6 m/s² |
| Cart centering | built into $`K`$ ($`K_x`$, $`K_{\dot x}`$) + auto-trim | shaped spring-damper |
| Depends on | $`m, l, I`$ (via IDENTIFY), $`M`$, $`b_c`$, $`Q`$, $`R`$, $`Q_N`$, $`R_N`$ | $`\omega_0`$ only |
| Sensitive to angle offset | yes, 1° parks the cart 8.3 cm off ([5.9](05_kalman_lqg.md#59-auto-trim-lines-758-768-slow-integral-action-on-the-upright-reference)) | barely ($`\cos\theta`$ changes by 0.015 % for 1° near upright) |
| Typical cart speed [HW] | about 1 cm/s once settled (95th percentile 7.7 mm/s) | ±0.6 m/s (mostly at the clip) |
| Failure | hands back to swing-up | soft limit → motor stop |

## 8.2 Why the balance gains differ between scripts

| Script | Q | $`I`$ used | Start | Speed clip | Force ramp |
| --- | --- | --- | --- | --- | --- |
| `PythonMaster.py`, `PythonMaster_auto.py` (balance only) | (5, 5, 5, 5) | 0.003 fixed | arm held upright by hand, cart still and centred | none | 200 cycles (2 s) |
| `PythonMasterSwingUpExp.py` (earlier swing-up, `swingup_control.py`) | (5, 5, 5, 5) | 0.003 fixed, no IDENTIFY | swung up | none in LQG | restarted at every catch (`loop = 0`, line 579): 2 s of reduced force right when the arm needs the most |
| **`PythonMasterUpExpClaudeImproved.py`** | **(40, 5, 150, 60)** | **identified each run** | swung up, caught at 15-17° and moving | 0.8 m/s, 15 m/s² | off (loop = 250 at catch) |

A balance-only start is gentle: $`\theta \approx 0`$, everything at rest, and the 2 s force ramp hides start-up transients. A catch is violent: the arm is 15-17° off and moving 1-3 rad/s, the cart may be moving at up to 0.6 m/s and be up to 12 cm off centre. The bigger $`Q_\theta`$ catches harder and the much bigger $`Q_x`$, $`Q_{\dot x}`$ bring the cart home before the 0.22 m limit. Simulated comparison: [fig04](images/fig04_balanceQ_vs_swingupQ.png) in [4.6](04_lqr.md#46-balance-script-q-vs-swing-up-script-q).

The price: with $`Q_x`$ = 150 the arm is held less still in steady balance, because the controller keeps tilting it to steer the cart. Rig numbers for comparison: this script balanced with θ std 0.79° and cart std 2.3 cm (run balance_20261016_160234 [HW]).

## 8.3 Why IDENTIFY matters more for swing-up than for balance

- Balance: LQR is robust. With the wrong inertia (0.003 instead of 0.00175) the gains are 15 % different but the closed loop is still stable. The balance-only scripts never identified and still balanced for minutes (22.8 min record, 2026-10-14 [HW]).
- Swing-up: $`e`$ uses $`\omega_0^2`$ directly. With the model's 5.91 instead of the real 7.29 rad/s, $`(\dot\theta/\omega_0)^2`$ is overestimated by 52 %: the energy reads too high, so pumping stops early and the catch test passes at the wrong time. The one rig run where IDENTIFY failed never caught [HW].

## 8.4 The hand-over is the hard part

The two controllers must agree at the switch:
1. **Same state.** The estimator is seeded with the measured state (lines 732-734), so the LQG does not start from zero.
2. **Same cart speed.** The LQG's speed command is $`\hat{\dot x}`$, seeded with the swing speed, so there is no speed jump; the 15 m/s² limit smooths the rest.
3. **Model valid.** The catch window keeps the LQG inside the region where the linear model holds.
4. **Room to work.** The catch is only allowed with the cart within 12 cm, because the catch itself moves the cart 10-15 cm.
5. **No ramp.** A force ramp would let the arm fall during the first 2 s.

And back: when LQG gives up, the swing speed starts from the estimator's speed, again avoiding a jump.

## 8.5 What changes for the double and triple pendulum

(Details in [../Double](../Double/README.md) and [../Triple](../Triple/README.md).)

- Balance stays LQR/LQG, just with a bigger state (6 or 8 states), and is much more sensitive to model errors.
- Energy pumping alone does not work: with two or more links the energy can be right while the links are in the wrong configuration. The team's double swing-up uses an offline-optimised trajectory tracked by a time-varying LQR instead ([swing-up subsystem page](../../subsystems/swing-up.md)).

[Back to Single](README.md) · Prev: [7. Swing-up](07_swing_up.md) · Next: [9. Code walkthrough](09_code_walkthrough.md)
