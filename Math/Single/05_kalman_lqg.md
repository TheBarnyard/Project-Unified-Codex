---
updated: 2026-10-29
updated_by: Ryan (Claude, math-folder session)
---
# 5. Kalman filter, LQG, the virtual cart, and auto-trim

[Back to Single](README.md) · Prev: [4. LQR](04_lqr.md) · Next: [6. Sensing and actuation](06_sensing_actuation.md)

Code: line 230 (design), line 614 (predict), lines 629-638 and [`angle_packet_fallback.estimate_with_angle`](https://github.com/etwan007/ENGT480/blob/ba019f9c07369a59731eefc16b8dfa34f9be00f8/LegacyPi/Code/SinglePendulum/angle_packet_fallback.py#L41-L54) (correct), lines 772-780 (output), lines 758-768 (auto-trim) of [the script](https://github.com/etwan007/ENGT480/blob/ba019f9c07369a59731eefc16b8dfa34f9be00f8/LegacyPi/Code/SinglePendulum/PythonMasterUpExpClaudeImproved.py#L230).

## 5.1 Why an estimator

LQR needs all four states. We measure only two: $`\theta`$ (encoder) and $`x`$ (step count). $`\dot\theta`$ and $`\dot x`$ must be inferred. Differencing $`\theta`$ is noisy: one encoder count is 0.022°, and dividing by 0.01 s makes each count a 0.038 rad/s jump. A Kalman filter blends a model prediction with the measurements to get all four, smoothly. LQR + Kalman filter = **LQG** (Linear Quadratic Gaussian).

## 5.2 Noise model

```math
\mathbf y_{k+1} = A_d\mathbf y_k + B_du_k + G\mathbf w_k, \qquad \mathbf z_k = C\mathbf y_k + \mathbf v_k
```

$`\mathbf w \sim \mathcal N(0, Q_N)`$ is "the model is wrong by this much each step"; $`\mathbf v \sim \mathcal N(0, R_N)`$ is sensor noise. The code (line 230):

```python
L_gain, _, _ = ctrl.dlqe(ss_disc.A, sp.diag(1,1,1,1), ss_disc.C, sp.diag(0.5,0.5,0.5,0.5), (0.01)*sp.diag(1,1))
#                         A_d        G = I4                C        Q_N = 0.5 I4                R_N = 0.01 I2
```

$`Q_N/R_N = 50`$: the filter trusts the sensors far more than the model. These are tuning values, not measured noise (a real encoder count is about $`(0.00038)^2`$ rad², much smaller than 0.01).

## 5.3 What dlqe computes

The error covariance $`P`$ of the **prediction** solves the filter DARE:

```math
P = A_dPA_d^T - A_dPC^T(CPC^T + R_N)^{-1}CPA_d^T + GQ_NG^T
```

and python-control returns the **predictor** gain

```math
L = A_d\,P C^T (CPC^T + R_N)^{-1}
```

(It is the LQR DARE with $`A_d \to A_d^T`$, $`B_d \to C^T`$: the duality between control and estimation.) The textbook **filter** gain, the one meant for "correct the prediction with the current measurement", is $`M = PC^T(CPC^T + R_N)^{-1}`$, so $`L = A_dM`$.

Numbers, identified inertia (rows $`\theta, \dot\theta, x, \dot x`$; columns: $`\theta`$ innovation, $`x`$ innovation):

```math
L = \begin{bmatrix}
1.00387 & -0.00477 \\
2.55774 & -0.47482 \\
-0.00457 & 0.98622 \\
-0.44453 & 0.53361
\end{bmatrix}
\qquad
M = \begin{bmatrix}
0.98115 & -0.00009 \\
1.98832 & -0.46097 \\
-0.00009 & 0.98087 \\
-0.45238 & 0.53593
\end{bmatrix}
```

## 5.4 How the code runs it, every 10 ms

```math
\text{predict (line 614):}\quad \hat{\mathbf y}^-_k = A_d\hat{\mathbf y}_{k-1} + B_du_{k-1}
```
```math
\text{correct (estimate\_with\_angle):}\quad \hat{\mathbf y}_k = \hat{\mathbf y}^-_k + L\left(\mathbf z_k - C\hat{\mathbf y}^-_k\right), \qquad \mathbf z_k = [\theta_{\text{meas}},\ x_{\text{meas}}]^T
```

$`\mathbf z - C\hat{\mathbf y}^-`$ is the **innovation**: how far the measurement is from what the model expected.

**Code vs textbook:** the code applies the predictor gain $`L`$ in the filter-form correction (where $`M`$ belongs). It still works: the estimator error evolves as $`\mathbf e_{k+1} = (A_d - A_dLC)\,\mathbf e_k`$, whose eigenvalues are 0.0052, 0.0150, 0.9838 ± 0.0063j, all inside the unit circle. Because $`A_d \approx I`$ at 100 Hz, $`L`$ and $`M`$ differ mostly in the $`\dot\theta`$ row (2.56 vs 1.99). Effect on balance: small [HYP]; the rig balances for minutes with it [HW]. Recorded here so nobody "fixes" one half without the other: switching to $`M`$ would change the effective tuning.

Reading $`L`$:
- Row 1: $`\hat\theta`$ is 100.4 % of the measured angle error: the angle estimate is basically the measured angle.
- Row 3: $`\hat x`$ follows the measured cart position at 98.6 %.
- Row 2: when the angle comes in 0.01 rad higher than predicted, raise $`\hat{\dot\theta}`$ by 0.026 rad/s. This is how the filter "differentiates" $`\theta`$, but smoothed by the model.
- Row 4: $`\hat{\dot x}`$ is pulled by both the angle surprise (-0.44) and the position surprise (+0.53).

The two slow error modes (|z| = 0.984, time constant 0.61 s) are slow only in principle: on the rig the cart speed estimate is also the speed command (next section), so it is right by construction.

## 5.5 The virtual cart

This is the most important thing to understand about how this code drives a stepper:

```python
u = -Kd @ YfinalEst * 2.0                                   # line 773: a FORCE, in newtons
xDiv = float(np.clip(YfinalEst[3].item(), -LQG_SPEED_MAX, LQG_SPEED_MAX))   # line 779: a SPEED
```

The motor is sent **the estimator's own cart-speed state** $`\hat{\dot x}`$, not the force. The force $`u_k`$ only enters the next prediction, through $`B_d`$. Look at the fourth row of the prediction:

```math
\hat{\dot x}^-_{k+1} \approx \hat{\dot x}_k + T_s\left(A_{41}\hat\theta_k + A_{44}\hat{\dot x}_k + B_4u_k\right)
```

That is a numerical integrator: **commanded speed = integral of the model's cart acceleration**. The stepper then really moves at that speed, the encoder count confirms it, and the correction step keeps $`\hat x`$ honest. So:

- The cart mass $`M`$ = 0.969 kg and drag $`b_c`$ = 0.5 N s/m are not "physics of our cart" here; they define how force turns into commanded acceleration ($`B_4 \approx 1/(M+m)`$) and a speed leak ($`A_{44}`$ = -0.43 /s). They are part of the controller.
- Substituting $`u = -2K\hat{\mathbf y}`$, the effective law is $`\ddot x_{\text{cmd}} = -(88.68\theta + 12.49\dot\theta - 18.63x - 20.42\dot x)`$ m/s² (see [4.5](04_lqr.md#45-what-the-law-means-for-a-stepper)).
- There is a one-cycle delay: $`u_k`$ affects the speed sent at cycle $`k+1`$.

History: the balance script [`PythonMaster_auto.py`](https://github.com/etwan007/ENGT480/blob/ba019f9c07369a59731eefc16b8dfa34f9be00f8/LegacyPi/Code/SinglePendulum/PythonMaster_auto.py#L499-L505) still has the older version commented out: `aCart = u.item() / mcartVal; xDiv = xDivLast + aCart * Ts`, replaced by `xDiv = YfinalEst[3].item() #pull velocity from kalman filter estimation`. The Kalman version is the same integrator, plus the arm-reaction and drag terms, plus correction from the measured position.

After the speed is chosen, two clips protect the stepper (lines 778-780):

```math
v = \text{clip}(\hat{\dot x}, \pm 0.8\ \text{m/s}), \qquad v = \text{clip}(v,\ v_{\text{prev}} \pm 15\,\text{m/s}^2 \times \Delta t)
```

The force ramp `if loop < 200` (line 774) is effectively off in this script: `loop` is set to 250 at every catch (line 731), because the arm is already moving and a soft start would drop it.

## 5.6 Missing angle packets

`estimate_with_angle` (helper file, lines 41-54): if the angle for this cycle is missing (radio timeout or the receiver's 0xFFFF marker), it **uses the predicted angle as the measurement**, so the angle innovation is zero and only the cart position corrects the state. After **10 consecutive** missing angles (about 100 ms) it raises `RuntimeError` and the motor is stopped. Rig logs from 2026-10-27 show many runs ending this way; that was the TX1 power problem ([debug page](../../debug/2026-10-27_angle-dropouts.md)). Logs from 2026-10-21 show "Two consecutive" instead of ten, so the helper changed between those dates [HW].

## 5.7 Seeding the estimator

The linear model is only valid near upright. While identifying and swinging, lines 787-788 overwrite the estimator state every cycle with the measured state, $`\hat{\mathbf y} = [\theta,\ \hat{\dot\theta}_{\text{fd}},\ x,\ v_{\text{cmd}}]`$, and set $`u = 0`$. At the catch (lines 732-734) it is seeded the same way, so the first LQG prediction starts from the real state instead of from zero. Without that, the first few LQG outputs would be garbage.

## 5.8 Separation principle

For the ideal linear problem, the closed loop of "LQR on the estimate" has exactly the eigenvalues of $`A_d - B_dK`$ (the controller) together with those of the estimator error dynamics. You can design the two independently. Here the ×2, the velocity-command structure and the non-textbook gain mean it holds only approximately, which is why we check with simulation and the rig.

## 5.9 Auto-trim (lines 758-768): slow integral action on the upright reference

**Problem.** If the upright reference is off by a small angle $`\delta`$ (calibration or encoder error), the arm only stays up when it is *truly* vertical, so the controller always sees $`\theta_{\text{meas}} = \delta`$. Setting $`\ddot x_{\text{cmd}} = 0`$ in the law of 4.5 with $`\dot\theta = \dot x = 0`$:

```math
88.68\,\delta - 18.63\,x = 0 \;\Rightarrow\; x = 4.76\,\delta
```

1° of error parks the cart 8.3 cm off centre, eating into the 22 cm limit.

**Fix.** Integrate the cart offset into the reference:

```math
\frac{d(\text{offset})}{dt} = K_X\,x + K_V\,\hat{\dot x} \quad [\text{deg/s}], \qquad K_X = 4\ \tfrac{\text{deg/s}}{\text{m}},\ K_V = 5\ \tfrac{\text{deg/s}}{\text{m/s}}
```

clamped to ±3° (`AUTO_TRIM_MAX_DEG`), and not during the first 0.5 s after a catch (`AUTO_TRIM_DELAY_S`). The only equilibrium is $`x = 0`$, where the offset equals $`\delta`$. When the offset changes, lines 766-768 shift the stored estimate and the previous angle by the same amount, so the estimator and the rate estimate see no jump.

[HW] In run balance_20261016_160234 the trim settled at +0.35° within 10 s ([fig09](images/fig09_balance_hw.png)): the hanging calibration (next page) was 0.35° off. [SIM] With a 1.0° error injected, the trim ends at 1.001°.

Note: the trim uses absolute `x`, not `x - x_start` (line 760). They differ by the starting step count, about 2 mm, because the Arduino is reset at startup.

[Back to Single](README.md) · Prev: [4. LQR](04_lqr.md) · Next: [6. Sensing and actuation](06_sensing_actuation.md)
