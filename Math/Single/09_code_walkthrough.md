---
updated: 2026-10-29
updated_by: Ryan (Claude, math-folder session)
---
# 9. Code walkthrough: PythonMasterUpExpClaudeImproved.py, line by line

[Back to Single](README.md) · Prev: [8. Balance vs swing-up](08_balance_vs_swingup.md) · Next: [10. Simulations and rig results](10_results.md)

**File:** [`LegacyPi/Code/SinglePendulum/PythonMasterUpExpClaudeImproved.py`](https://github.com/etwan007/ENGT480/blob/ba019f9c07369a59731eefc16b8dfa34f9be00f8/LegacyPi/Code/SinglePendulum/PythonMasterUpExpClaudeImproved.py), etwan007/ENGT480, branch `experiment/legacy-pi-recovery`, commit `ba019f9` (Ethan's recovery of the Pi's legacy ENGT481 checkout as it was on 2026-10-28). 860 lines.

**Same file, two names:** `PythonMasterUpExpClaude.py` in the same folder is byte-for-byte identical (checked with `diff`, 2026-10-29). Rig logs from it carry `"swing_up_control": "identify_then_normalised_energy_pumping"` in their config row; there are 28 such runs on the `logs` branch, 2026-10-16 to 2026-10-27.

Helpers it imports, from the same folder: `run_csv_logger.py` (CSV logging on a background thread), `angle_protocol.py` (framed receiver protocol v1), `live_offset_keys.py` (arrow keys), `angle_packet_fallback.py` (missing-packet handling, [5.6](05_kalman_lqg.md#56-missing-angle-packets)).

## Lines 1-51: imports and settings

| Lines | Code | Meaning |
| --- | --- | --- |
| 1-12 | `numpy`, `sympy`, `control`, `serial`, ... | NumPy for arrays, SymPy to derive the model symbolically, python-control for `c2d`, `dlqr`, `dlqe`, pyserial for the two USB ports |
| 20-21 | `ENCODER_COUNTS = 16384`, `HALF_TURN = 8192` | 14-bit encoder ([6.1](06_sensing_actuation.md#61-angle-counts-to-radians-lines-145-148)) |
| 25 | `UPRIGHT_OFFSET_DEG = 0.0` | manual offset added to the upright reference; the auto-trim changes it later |
| 27 | `LIVE_OFFSET_STEP_DEG = 0.05` | arrow-key step |
| 33-34 | `SAVE_RUN_CSV`, `RUN_LOG_DIRECTORY` | every cycle logged to `run_logs/balance_<date>.csv` (name says balance, also for swing-up runs) |
| 35-51 | globals | state shared with the fault handler, so a crash still logs the stage, cycle, angles, cart and last command |

## Lines 53-118: logging, faults, reading the ESP32

| Lines | Meaning |
| --- | --- |
| 53-58 `log()` | timestamped console lines; FAULT and SENSOR always print |
| 61-74 `report_uncaught` | `sys.excepthook`: any crash writes a `fault` event to the CSV, then `atexit` stops the motor |
| 76-85 `read_exact` | read N bytes or raise after 0.1 s (never hang) |
| 88-118 `read_raw_angle1` | read the newest receiver frame; angle 1 = 0xFFFF or a protocol error → `MissingAnglePacketError` with a detailed SENSOR log (wall clock, sequence, radio age) |

## Lines 121-156: calibration and unit conversion

| Lines | Math | Page |
| --- | --- | --- |
| 121-142 `calibrate_from_hanging` | circular mean of 50 readings, stillness check (80 counts), upright = hanging + 8192 | [6.2](06_sensing_actuation.md#62-calibration-from-hanging-lines-121-142-472-474) |
| 145-148 `angleRead` | $`\theta = \text{wrap}(\text{raw} - c_{up})\cdot 2\pi/16384`$ | [6.1](06_sensing_actuation.md#61-angle-counts-to-radians-lines-145-148) |
| 150-156 `positionRead` | 2 bytes big-endian int16 → $`x = \text{steps}\times0.638175/6400`$; then flush the input buffer | [6.4](06_sensing_actuation.md#64-cart-position-lines-150-156) |

## Lines 158-218: the model, symbolically

| Lines | Code | Math |
| --- | --- | --- |
| 159-162 | symbols `t g l m1 mcart B_cart_drag`, functions `theta(t)`, `x(t)`, symbols `I H V F T_drag` | [1](01_variables.md) |
| 165 | `Ts = 1/100` | 100 Hz design rate |
| 168-177 | values: `length` 0.2 (unused), `lval` 0.05, `Ival` 0.003, `m1val` 0.260, `T_dragVal` 0, `mcartVal` 0.969, `B_cart_dragVal` 0.5, `gval` 9.81 | [1](01_variables.md#physical-parameters) |
| 180 | `T = ...` kinetic energy | [2.3](02_equations_of_motion.md#23-kinetic-energy-t-line-180) |
| 181 | `U = m1*g*l*cos(theta)` | [2.4](02_equations_of_motion.md#24-potential-energy-u-line-181) |
| 183 | `L = T - U` | Lagrangian |
| 185-193 | `EL_x`, `EL_theta` | Euler-Lagrange with $`F - b_c\dot x`$ and $`-\tau_d`$ ([2.6](02_equations_of_motion.md#26-euler-lagrange-equations-lines-185-193)) |
| 195-201 | substitute $`\ddot x, \ddot\theta`$ by symbols, `sp.solve` | solve the 2x2 mass-matrix system ([2.7](02_equations_of_motion.md#27-solve-for-the-accelerations-lines-195-201)) |
| 203-209 | `StateSubs`, `NonLinMod = [Y2, F1, Y4, F2]` | state-space form ([2.8](02_equations_of_motion.md#28-state-space-form-lines-203-209)) |
| 211-212 | `A_sym = jacobian`, `B_sym = diff(F)` | linearisation ([3.2](03_linear_model.md#32-jacobians-lines-211-212-218-225-226)) |
| 213-216 | `C` picks θ and x; `D` = 0 | measurements |
| 218 | `Equilibrium` all zeros | upright |

This symbolic derivation takes a few seconds on the Pi every start; it is done once.

## Lines 221-235: design_lqg

| Line | Code | Math |
| --- | --- | --- |
| 223-226 | substitute values (with the given inertia) and the equilibrium | numeric $`A, B`$ |
| 227 | `ctrl.c2d(..., Ts)` | zero-order-hold discretisation ([3.4](03_linear_model.md#34-discretisation-line-227)) |
| 229 | `ctrl.dlqr(ss_disc, diag(40,5,150,60), 1)` | LQR gain $`K`$ ([4](04_lqr.md)) |
| 230 | `ctrl.dlqe(A_d, I4, C, 0.5 I4, 0.01 I2)` | estimator gain $`L`$ ([5.3](05_kalman_lqg.md#53-what-dlqe-computes)) |
| 235 | `ssDisc, Kd, Ld = design_lqg(Ival)` | first design with the nominal inertia; replaced after IDENTIFY (line 677) |

## Lines 238-320: swing-up constants and state

Every constant is in the table in [7.9](07_swing_up.md#79-every-swing-up-constant). The comment block on lines 238-254 is an accurate summary of the method. State variables (lines 291-320): `mode`, `w0_model` (line 298, $`\sqrt{mgl/(I+ml^2)}`$ = 5.911 rad/s), `w0`, `identify_log`, `theta_prev`, `theta_dot_est`, `alpha_td`, `energy_target`, `swing_direction`, `xDiv_swing`, `xDiv_sent`, `catch_count`, `catch_time`, `e_norm`, `swing_energy_peak`.

## Lines 324-391: helper functions

| Lines | Function | Math |
| --- | --- | --- |
| 324-340 | `update_theta_velocity` | filtered finite difference with receiver timestamps ([6.3](06_sensing_actuation.md#63-angle-rate-for-the-swing-up-lines-324-340)) |
| 343-346 | `identify_accel` | +a, -a, -a, +a wiggle ([7.3](07_swing_up.md#73-identify-measure-ω0-on-the-rig)) |
| 349-375 | `measure_natural_frequency` | zero crossings, median period, amplitude correction, decay ([7.3](07_swing_up.md#73-identify-measure-ω0-on-the-rig)) |
| 378-391 | `swing_command` | pumping law + shaped centering, then integrate to a speed ([7.4](07_swing_up.md#74-the-pumping-law-lines-378-391), [7.5](07_swing_up.md#75-centering-spring-lines-383-387)) |

## Lines 394-583: start-up sequence

| Lines | What happens | Why |
| --- | --- | --- |
| 395-408 | zero the loop variables | |
| 411-412 | prompt: motor power OFF, arm hanging | calibration needs a still arm |
| 416-422 | open `/dev/ttyUSB0` (ESP32, 921600 baud) and `/dev/ttyACM0` (Mega, 115200) | |
| 425-451 | `stop_and_close` registered with `atexit` | whatever happens, send 0xFFFFFFFF (stop) and save the CSV |
| 453-459 | toggle DTR, wait 3 s | resets the Mega, so its step counter starts at 0 |
| 465-467 | flush both inputs | avoid the startup junk (see [gotchas](../../gotchas.md)) |
| 471-476 | calibrate, apply manual offset | [6.2](06_sensing_actuation.md#62-calibration-from-hanging-lines-121-142-472-474) |
| 478-511 | start the CSV logger, write a `config` row with every parameter and matrix | reproducibility: every run log carries its own gains |
| 517 | prompt: motor power ON | |
| 524-543 | 10 more angle readings; refuse to start unless the arm is within 20° of hanging | swing-up must start from hanging |
| 546 | enable arrow keys | |
| 550-556 | send -65535 (≈ stopped) | wakes the Arduino (it waits for the first 4 bytes before enabling the driver) and gets the first position |
| 567-572 | seed the estimator and the rate filter with the hanging state | |
| 581 | `identify_started` | IDENTIFY starts now |

## Lines 585-850: the control loop, one cycle

| Lines | Step | Math |
| --- | --- | --- |
| 587-594 | count the cycle; `swing_dt` = real time since last cycle (max 30 ms); `loop` counter up to 250 | |
| 596-610 | arrow keys: shift the upright reference and the stored angle states by the same amount | |
| 612-614 | **predict**: `Yest = A_d @ Ylast + B_d @ u` (with last cycle's force) | [5.4](05_kalman_lqg.md#54-how-the-code-runs-it-every-10-ms) |
| 617-622 | read the angle (or `None` if missing) | |
| 625 | update the finite-difference rate | [6.3](06_sensing_actuation.md#63-angle-rate-for-the-swing-up-lines-324-340) |
| 628-638 | **correct**: `estimate_with_angle` with the measured angle and the cart position from last cycle; store as `Ylast` | [5.4](05_kalman_lqg.md#54-how-the-code-runs-it-every-10-ms), [5.6](05_kalman_lqg.md#56-missing-angle-packets) |
| 640-642 | soft limit 0.30 m → stop | [6.7](06_sensing_actuation.md#67-safety-limits-on-the-cart) |
| 644 | energy $`e`$ | [7.2](07_swing_up.md#72-normalised-energy) |
| 647-691 | **IDENTIFY**: wiggle 0.48 s, settle 0.3 s, log, time swings; then set `w0`, redesign LQG with the identified inertia, switch to SWING | [7.3](07_swing_up.md#73-identify-measure-ω0-on-the-rig) |
| 693-697 | **SWING**: `swing_command` → new speed | [7.4](07_swing_up.md#74-the-pumping-law-lines-378-391) |
| 698-716 | adapt the energy target (short turn-back / too fast over the top) | [7.6](07_swing_up.md#76-adaptive-energy-target-lines-698-716) |
| 717-720 | log the first time above horizontal | |
| 723-742 | **catch** test and hand-over to LQG | [7.7](07_swing_up.md#77-the-catch-lines-723-742) |
| 744-757 | **LQG**: lost balance (θ beyond ±0.8 rad or cart beyond ±0.22 m) → back to SWING | [7.8](07_swing_up.md#78-losing-balance-and-trying-again-lines-746-757) |
| 758-768 | **LQG**: auto-trim of the upright reference | [5.9](05_kalman_lqg.md#59-auto-trim-lines-758-768-slow-integral-action-on-the-upright-reference) |
| 772-780 | **output in LQG**: $`u = -2K\hat{\mathbf y}`$ (only feeds the next prediction); speed = $`\hat{\dot x}`$ clipped to 0.8 m/s and 15 m/s² | [4.4](04_lqr.md#44-the-extra-factor-of-2-line-773), [5.5](05_kalman_lqg.md#55-the-virtual-cart) |
| 781-789 | **output otherwise**: $`u = 0`$, estimator overwritten with the measured state, speed = swing speed | [5.7](05_kalman_lqg.md#57-seeding-the-estimator) |
| 792-802 | speed → step frequency → timer top | [6.5](06_sensing_actuation.md#65-speed-to-step-frequency-to-timer-top-lines-793-807) |
| 805-808 | send the 4-byte command | [6.6](06_sensing_actuation.md#66-serial-protocol) |
| 811-813 | read the cart position (used next cycle) | [6.4](06_sensing_actuation.md#64-cart-position-lines-150-156) |
| 815-850 | CSV sample row (every cycle), status line every 0.5 s with the measured loop rate | |
| 853-860 | Ctrl+C; print the final trim offset so it can be put into `UPRIGHT_OFFSET_DEG` next time | |

## Things worth knowing that the comments do not say

1. **The motor gets a speed, not the LQR force.** The force only drives the estimator, whose speed state is sent. [5.5](05_kalman_lqg.md#55-the-virtual-cart).
2. **`dlqe` returns a predictor gain, used here as a filter gain.** Stable and works; not textbook. [5.4](05_kalman_lqg.md#54-how-the-code-runs-it-every-10-ms).
3. **The ×2 on line 773** doubles the LQR gain; the result is no longer LQR-optimal but is stable with margin. [4.4](04_lqr.md#44-the-extra-factor-of-2-line-773).
4. **The model's inertia is replaced every run.** The CSV `config` row shows the nominal $`K`$; the `identify` event shows the $`K`$ actually used.
5. **`BALANCE_CART_LIMIT_M` is checked during all of LQG**, not only "while catching" as the comment on line 286 says. It caused 23 of 24 hand-backs on the rig. [7.8](07_swing_up.md#78-losing-balance-and-trying-again-lines-746-757).
6. **Auto-trim uses `x`, not `x - x_start`** (line 760). Harmless because the Arduino reset makes them differ by about 2 mm.
7. **Timer "+1"**: real step rate is $`125000/(|N|+1)`$, not $`125000/|N|`$. [6.5](06_sensing_actuation.md#65-speed-to-step-frequency-to-timer-top-lines-793-807).
8. **The force ramp is dead code here** (`loop` is 250 from the first catch). Before the first catch the output is the swing branch anyway.
9. **Unused:** `length`, `H`, `V`, `line`, `angleRaw`, `positionRaw` (global), `T_drag` (zero).

None of these were changed: per [decision 0004](../../decisions/0004_work-in-copies.md) the original files are not edited. If any is worth changing, do it in a copy and compare in [`sims/single_sim.py`](sims/single_sim.py) first.

[Back to Single](README.md) · Prev: [8. Balance vs swing-up](08_balance_vs_swingup.md) · Next: [10. Simulations and rig results](10_results.md)
