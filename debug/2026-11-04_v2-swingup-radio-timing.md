---
type: debug
status: likely-fixed
opened: 2026-11-04
by: Ryan (Claude, V2 arms fit session)
subsystems: [swing-up, wireless]
---
# V2 double swing-up drifts off the plan after ~1.5 s (radio timing noise)

## Symptoms
- First rig run of `PythonMaster2_swingup_V2.py --path same_4.0s`, 2026-11-04, CSV `swingup_double_20261104_153309_280984.csv` (Pi `~/Desktop/DoubleSwingUpV2/run_logs/`) [HW].
- 5 attempts, no catch. Aborts at k = 162, 289, 248, 342 (36-40 deg off the plan) and 208 (cart -362 mm). Attempt 4 got to arm 1 50 deg, arm 2 -4 deg from upright at 3.4 s.
- Every attempt tracks the plan within about 2 deg and 5 mm until k ≈ 100-140. Then the feedback asks for ±16 m/s² (CART_ACCEL_MAX) and sits on the 0.83 m/s speed cap (13-28 cycles per attempt), and the error grows.
- Run stopped after attempt 5: `6 unusable angle frames in a row`, angle3 (TX2) wireless_timeout, 102 ms, while settling.

## Tests and results
All on the logged CSV, session [2026-11-04 V2 arms fit](../sessions/2026/11/2026-11-04_1555_Barney_v2-arms-model-fit.md).
- **Model:** 0.3 s windows of the swing data, start state fitted per window, each reading placed at its time (cycle − radio age − 1.5 ms), cart speed changes 8 ms after the cycle. With the V2 ratios the RMS error is 0.3-0.6 deg before k = 100 and 1.5-2 deg after. Refitting P1, P2, J2r, H, B1 and B2 on the swing data moves them by less than 4 % and does not lower the error (1.81 → 1.78 deg). Extra cart delay (8-25 ms) or a first-order cart lag (10-30 ms) does not lower it either. So the V2 model is not the cause [HW].
- **Timing:** the loop timestamps alternate 8.2 / 12.3 ms, but the Mega's step count per cycle stays constant and esp32_sequence goes up by exactly 1 every cycle. So commands go out on a steady 10 ms beat and only the timestamp jitters (Arduino reply latency). This is not a cause.
- **Radio:** 11 % of TX1 frames and 5 % of TX2 frames are 10-70 ms old. TX1 has 7.7 gaps per second, 1-7 frames long. The excite run of the same morning has the same numbers (TX1 10 %, TX2 5 % at 10 ms or more), so the link has been this way all along [HW].
- **Observer innovations** (reading minus the model's 10 ms prediction): 0.6 deg before k = 100 and 2-3 deg after on the rig, against 0.06 / 0.2 deg on the twin with a clean radio. The first reading after a gap is 4.6 / 7.8 deg off in the fast part. With a smooth curve through the neighbouring readings (no model), the rig's readings scatter about 1.1 deg against 0.6 deg on the twin, which means about 2-3 ms of hidden spread in a reading's true age. On an arm moving at 5-15 rad/s that is 1-3 deg. The swing observer assumed 3 counts (0.07 deg).
- **Twin with a radio fitted to this log** (ESP-NOW FIFO with retries, attempt time 0.3 + Exp(1.8) ms, 30 % attempt failure, 8 / 3 blackouts per second for TX1 / TX2 of 4 + Exp(10) ms). Its age histogram matches the rig. The exact V2 script then catches 4 of 54 attempts, against 12 of 12 with a clean radio [SIM]. The failure looks like the rig: feedback at 16-20 m/s² from k ≈ 150.

## Ruled out (dead ends)
- Model error: ruled out by the refit above.
- Cart lag or extra delay: ruled out, no better fit with either.
- Loop timing: ruled out, the commands are regular (see Timing).
- Settings alone (SWING_DISTURBANCE 0.5-3, SWING_ACCEL 2-5) on the V2 observer: 2-10 % → at best 40-57 % of attempts on the rig-like twin, 4 seeds each, not reliable [SIM].

## Cause and fix
- Cause [SIM, consistent with HW log]: the swing observer treats every reading as nearly exact. Radio timing noise on fast arms (1-3 deg) and readings that repeat during gaps make it chase noise. The TV-LQR then saturates the cart (16 m/s², 0.83 m/s) and the arms drift off the plan.
- Fix: `PythonMaster2_swingup_V2b.py` (V2 unchanged), `TheBarnyard/ChatGPT-Pendulum-Project` branch `claude/project-thread-74rdr9`, `DoubleSwingUp_V2/`, commit fd49fd7, sha256 20457d6f…
  - Per-arm (angle, rate) covariance. Each reading counts as encoder noise plus `SWING_TIMING_NOISE_MS` (3.0) × arm speed. Readings already used are skipped. Gain for slow arms is about the same as V2 (0.74), for fast arms about 65× smaller.
  - `SWING_DISTURBANCE_RAD_S2` 3 → 10 (with 3 the observer leans on the model and fails at arm-2 inertia +10 % even with a clean radio), `SWING_ACCEL_M_S2` 5 → 4.
  - More than 5 missing frames during a swing ends only that attempt. While waiting or settling, up to `MAX_SETTLE_MISSES = 12` are allowed. Balance keeps 5.
- Twin, `same_4.0s` [SIM]: rig-like radio V2 4/54 (7 %), V2b 14/40 (35 %) of attempts caught, 18 runs. Other seed sets gave V2b 21-75 % against 2-6 % for V2. Clean radio, nominal / arm-2 I +10 % / arm-2 m -4 %: both 12/12. A 150 ms TX1 gap mid-swing: V2 stops the run, V2b retries and catches.

## Next
- Run V2b on the rig: `--path same_4.0s`, then `same_3.5s`. Send the CSV.
- Improve the radio, the bigger lever [HYP]: check that the XIAO antennas are attached, the LiPo is charged, and the receiver has line of sight. TX1 (on the cart, Mega 5 V since 2026-10-27) loses twice as much as TX2. A weak supply caused dropouts before (see gotchas, 335 mA bursts). ESP-NOW channel 6 is usually the busiest Wi-Fi channel, and changing it means reflashing TX1, TX2 and the receiver.
- Firmware idea: add a TX sample counter to the 3-byte packet so the receiver can report the true age. Needs a protocol change.

## Files
- Script and tools: branch above, `DoubleSwingUp_V2/PythonMaster2_swingup_V2b.py`, `tools/make_v2b.py` (builds V2b from V2), `tools/twin_rig.py` (twin radio models), `tools/twin_v2b_check.py` + `.json` (results).
- Analysis scripts: Claude project files `DoubleSwingUp_V2/run_20261104_analysis/`.
