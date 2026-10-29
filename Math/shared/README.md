# Shared model and controller code (any number of links)

Python used by [Double](../Double/README.md) and [Triple](../Triple/README.md). The single has its own self-contained scripts in [`../Single/sims/`](../Single/sims/README.md), because they copy `PythonMasterUpExpClaudeImproved.py` line for line.

Conventions (the same as the team's double scripts): absolute angles $`\theta_i`$ from upright, positive = centre of mass toward +x (opposite to the single script); state $`\mathbf z = [\theta_1, \omega_1, \dots, \theta_n, \omega_n, x, v]`$; joint friction on the relative rate $`\omega_i - \omega_{i-1}`$. The equations are derived in [Double 2](../Double/02_equations_of_motion.md).

## `nlink_cart.py`: model, linearisation, design

| Function | What it does | Explained in |
| --- | --- | --- |
| `Link`, `Rig` | arm masses, CoM distances, lengths, inertias; `Rig.p()`, `Rig.h()` give $`p_j`$ and $`h_{ij}`$; `Rig.from_team_ratios()` builds a rig from the scripts' P1, P2, J2r, H, B1, B2 | [Double 1](../Double/01_variables.md) |
| `accel_dynamics(rig, z, a)` | $`\dot{\mathbf z}`$ with the cart acceleration as input (the stepper's model) | [Double 2.5](../Double/02_equations_of_motion.md#25-two-ways-to-drive-the-model) |
| `speed_jump(rig, z, dv)` | the instant arm "kick" when the stepper jumps speed by `dv` | [Double 2.7](../Double/02_equations_of_motion.md#27-when-the-stepper-jumps-speed-the-kick) |
| `linear_accel(rig)`, `linear_force(rig)` | A and B at upright for acceleration or force input | [Double 3.1](../Double/03_linear_model.md#31-linearising-at-upright) |
| `c2d`, `delay_discretize(A, B, T, tau)` | zero-order hold, and the delayed version with the previous command as an extra state | [Double 3.5-3.6](../Double/03_linear_model.md#35-discretisation) |
| `stair_step`, `linearize_stair` | one 10 ms period of the stepper's staircase (speed jumps `tau` after the sample) and its Jacobians | [Double 3.7](../Double/03_linear_model.md#37-the-staircase-model-swing-up-script) |
| `dlqr`, `dlqe`, `bryson_Q` | discrete LQR, the scripts' Kalman predictor gain, Bryson's rule | [Double 4.4](../Double/04_balance.md#44-the-weights-brysons-rule) |
| `kalman_physical(...)` | steady Kalman gain from physical noise (arm disturbance, encoder counts, cart steps) | [Double 4.6](../Double/04_balance.md#46-the-kalman-filter-hardware-noise-filter-form) |
| `balance_design_ramp`, `balance_design_stair` | the full balance design of `PythonMasterDouble-Claude.py` / `PythonMaster2_swingup.py` | [Double 4.3](../Double/04_balance.md#43-generation-2-acceleration-model-with-delay-pythonmasterdouble-claudepy) |
| `plan_team(rig, T, X, V, A, Vtop, ...)` | swing-up plan by multiple shooting: knots every 0.05 s, minimise $`\int a^2 dt`$, track, speed and torque-speed limits (CasADi + IPOPT) | [Double 5.3-5.4](../Double/05_swing_up.md#53-the-plan-as-an-optimisation-problem) |
| `plan_team_homotopy(...)` | the same, starting from loose limits and tightening them step by step (continuation) | [Triple 4](../Triple/04_swing_up.md) |
| `stair_reference`, `tvlqr_stair` | the staircase reference $`a_{\text{ref}}`$ and the time-varying LQR gains along a plan | [Double 5.5-5.6](../Double/05_swing_up.md#55-from-the-plan-to-motor-commands) |
| `swing_observer_gain(...)` | the swing-up observer's per-arm gain [0.512, 18.21] | [Double 5.7](../Double/05_swing_up.md#57-estimating-the-state-during-the-swing) |
| `timer_speed(v)` | the Mega's step rate after `round(125000/f) - 1` | [Double 7.4](../Double/07_results.md#74-why-every-rig-attempt-tops-out-at-0831-ms) |
| `plan_swingup`, `tvlqr`, `simulate` | an earlier, simpler planner, TV-LQR and simulator (kept because they are short and easy to read) | |

## `swing_sim.py`: the scripts' control loops in simulation

| Name | What it is |
| --- | --- |
| `build(rig_model, plan_Z)` | everything `PythonMaster2_swingup.py` computes at start-up: balance gain, $`a_{\text{ref}}`$, 250 TV-LQR gains, observer gain |
| `TeamSwingController` | the script's SWING → BALANCE loop: observer, $`a = a_{\text{ref}}[k] - K_k(\hat{\mathbf z} - \mathbf z_{\text{ref}}[k])`$, abort, limits, torque-speed limit, timer rounding |
| `TeamBalanceController` | `PythonMasterDouble-Claude.py`'s loop: Kalman filter, $`a = -K[\hat{\mathbf z}; a_{\text{prev}}]`$, limits, auto-trim |
| `run(rig_true, ctrl, T_total, ...)` | the plant: nonlinear arms integrated every 0.5 ms, stepper speed jumps `tau_true` after each sample (with the kick), encoders rounded to counts plus noise, cart rounded to steps |

What the simulation leaves out: [Double 7.1](../Double/07_results.md#71-what-was-simulated-sim).

Needs numpy and scipy; `casadi` (`pip install casadi`) only for `plan_team` and `plan_team_homotopy`.
