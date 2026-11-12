---
type: debug
status: open
opened: 2026-11-05
by: Barney (Claude)
subsystems: [cart-arduino, swing-up]
---
# Cart jolts with UIM344 red LED during double swing-up

## Symptoms
2026-11-04 rig runs (V2/V2b swing-up, several plans): the cart jolts during the swing, unlike the twin, and the motor's red LED is on meanwhile [HW, Barney]. Most attempts failed; re-greasing the rails helped a little. Bench supply limit 2 A, drew at most about 1 A [HW]. Belt tension unknown.

## Best explanation so far (2026-11-05) [HYP]
UIM344 position-error lockout: the motor falls behind its step pulses by more than Max. Pos. Error, stops and locks, red LED (vendor CFG344 tooltip). Cause: torque below what the swing-up asks (16-17.5 m/s² at up to 0.83 m/s in every 2026-11-04 attempt). Suspects: low I_work setting, supply voltage, the 10 ms speed staircase from ArduinoSlave, arm reaction loads. Belt skip cannot light the LED (encoder on the motor shaft). The supply reading does not rule out a low current setting (chopper drive). Details: [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md).

**Update 2026-11-11 (all 30 runs, [doc](https://claude.ai/artifact/YAj8iBivoMQSxVneBDnZv9)):** the logs now show the stalls directly. The cart follows commands up to about 12 m/s²; at the 16-18 m/s² reversals (0.83-0.96 m/s) it stops being pushed for 0.1-0.5 s in 15 runs, and in run 162911 it stayed dead from 4.9 s to the end (latched lockout) [HW log]. ~~Demand there is about 0.65-0.8 N m at 310-360 rpm: at or above what this motor gives, so no margin [HYP].~~ Superseded 2026-11-12 by [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md): CFG344 read Micro-Stepping 4, so the pulley is 1 in (r 12.7 mm): torque is half, rpm double (about 590 rpm at 0.78 m/s, 720 at 0.96). Demand is about 0.33-0.4 N m at 620-720 rpm, where torque is set by supply voltage [HYP].

## Tests
Plan doc: https://claude.ai/artifact/7YmvrJBDnQpgkRZXUc57fp. Tools: ChatGPT-Pendulum-Project `claude/project-thread-wk3tn6` `CartJolt/`.
1. Read the UIM344 config with CFG344 (Windows + USB-TTL, motor powered, driver off).
2. Supply: 24-48 V, limit 3 A+, CC lamp, 1000-2200 µF bulk cap.
3. Mechanical (power off): push force along the track, belt tension, paint-pen witness marks on pulley/idler/clamps, mount bolts.
4. `motor_stress_test.py` arms off (18 trials, asks red LED / jolt / mark offset).
5. `replay_run_motor.py` a jolting attempt, arms off then on.
6. One change at a time, rerun 4-5.
7. Code: lower CART_ACCEL_MAX_M_S2 in a copy; `ArduinoSlaveRamp` (ramped step rate).
8. 2026-11-11: `two_load_stall_test.py` (arms off, bare cart then a weighed item): measures the cart's effective mass and the motor's force at 0.8 m/s.
9. 2026-11-11: `two_load_reversal_test.py` (same, 3 back-to-back reversals), `command_style_test.py` (same move sent 7 ways, blind scoring), `reversal_method_test.py` (the reversal stall search with the command method chosen on the command line: `--method A..G` or `--period/--smooth/--hyst/--send`; one stall acceleration per method).

| Result | Points to |
| --- | --- |
| Red LED, stays on | lockout: torque vs demand (config/supply/code) |
| Off the tape mark, no red LED | belt skip or pulley slip (mechanical) |
| Jolts only with arms on in replay | arm reaction load |
| Never in replay, only live | controller/radio |

## Results
- 2026-11-05, log-analysis thread ("Analyze yesterday's double swing-up runs"), run `swingup_double_20261104_153309_280984` [HW log, HYP]: 200 ms windows fitting an extra constant cart accel dA on top of the commanded speed (V2 ratios). Below 3 m/s² commanded the cart follows (dA about 0). ~~At 3 m/s² or more, 78 % of 54 windows come up short, mean 1.1 m/s²; the clear cases are short by about 3 m/s²~~ (Superseded 2026-11-11 by [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md): over all 30 runs, with radio timing in the noise model, the cart follows up to about 12 m/s²; only the 16-18 m/s² reversals fail) (attempt 4, t 33.6-33.7 s: a_cmd +8, cart gave about half; attempt 5, t 43.7-43.9 s at the 0.83 m/s cap). No frozen cart: attempts 2-5 track fine at first, so any lockout cleared between attempts. Supports "motor cannot deliver the accel at speed", not belt skip specifically. 200 ms windows smear short jolts.
- 2026-11-06 torque budget ([doc](https://claude.ai/artifact/3zyNMAfTcsA97iVPe8zss6), [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md)): ~~at full current the swing needs at most about half of the 1.26 N m holding torque (r 25.4 mm assumed).~~ (r is 12.7 mm, 2026-11-12: halve these torques; motor rpm is double.) ~~The 3-8 m/s² shortfalls need only 0.15-0.35 N m, so the motor is delivering far below rating: low I_work, 24 V corner speed, friction or a different r [HYP].~~ Superseded 2026-11-11 by [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md): those shortfalls were fit noise; the motor fails at about 0.65-0.8 N m. Braking torque at speed is at least driving torque (back-EMF helps), so the hard moment of a reversal is speeding up at its end.
- 2026-11-11, all 2026-11-04 runs ([doc](https://claude.ai/artifact/YAj8iBivoMQSxVneBDnZv9), [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md), scripts ChatGPT-Pendulum-Project `claude/project-thread-wk3tn6` `CartJolt/analysis/` 7c93da6) [HW log]:
  - Below about 12 m/s² the cart follows: scale on commanded speed changes median 1.00, middle half 0.9-1.1 (about 2,800 windows with slow arms).
  - Stalls (fit with no cart acceleration beats the commanded one 2x) in 15 runs, each SWING one right after 6-28 commands of 12 m/s² or more. 20 of 206 decidable high-demand windows vs 3 of 602 at lower demand. By path: same_4.0s 4 %, same_3.0s 0 %, folded_4.5s 36 %, whip_4.5s 24 %; whip/folded 0 catches.
  - Latched: 162911 dead 4.9-20.8 s while the Mega sent pulses; 163044 next run moved, so the Mega reset cleared it. Fits "stop and locked" + red LED.
  - Lag on the 10 ms staircase: 5 mm if the motor can do 18 m/s², 34 mm at 16, 84-100 mm at 12-14 [SIM]. A cliff, not a gradual shortfall.
  - Mega no-reply stops: all 11 in RECOVER, 7 within 0.9-3.6 s after a stall. Stop button pressed, or the jolt getting into the switch wiring [?].
  - Not usable: 151934, 152746 (arm 1 reading frozen), 161145 (cart never moved [?]).

## 2026-11-11 (evening): reversal method test on the rig
Barney ran `reversal_method_test.py` (3 reversals +/-0.78 m/s, arms off, bare cart). He answered "b" at the first slight stutter, so these are stutter-onset accelerations, not hard stalls [HW]:
- E (2 ms stream): clean to about 19-20, stutters 20-21 m/s² (answers flipped at 20 and 21). D (5 ms stream): about 19 (19 clean once, stuttered once). F (10 ms + hysteresis): about 18.5 (one early stutter at 16, then 16-18 clean, 19 stuttered; search not finished). G (10 ms + 30 ms S-curve): 13.37 +/- 0.38 (finished; 6 stutters at 14-16).
- D/E/F within about 2 m/s², the same as the answer scatter: the command rate is not the main limit; the motor runs out around 19-20 m/s² at 0.78 m/s [HW].
- G clearly worse. Its commands were checked: same top speed (0.779 m/s), no overshoot; it stays at top speed about 20 ms longer per corner. It ran last, so motor warming is possible [HYP]. A (current method) was not in the paste.
- Mega round trip median 4.1 ms (fake Mega 0.3 ms): USB-serial latency [HYP]; harmless at 10 ms.
- Near top speed the Mega timer (/64, 125000/(N+1)) only gives 0.779, 0.733, 0.692 m/s (5-6 % steps), so even 2 ms commands still jump 0.046 m/s at a time [SIM].
- Next: `--summary` (A and the first G run), then `--method A,G --accel 15 --repeats 4` after a cool-down.

## 2026-11-11: plan vs commanded vs stall accelerations (double swing-up)
- Plans (7 V2 JSONs, DoubleSwingUp_V2): limit 8 m/s² (x(1-v/1.0) when speeding up), 0.75 m/s; peak 4.7 (same_4.0s) to 7.7 m/s² (whip_3.0s); median |a| 0.9-1.8, 90th percentile 3.3-4.9 [SIM].
- Commanded during SWING (plan + feedback, `force_command_n`, 33 runs 2026-11-04): median 2.7, p90 11.3, p99 16.2 m/s²; 9 % of swing time >= 12, 4 % at the 16 cap (CART_ACCEL_MAX_M_S2 16; logged peaks 16-18 after timer rounding); speed commands up to 0.86 m/s (1.0 in whip runs) [HW log].
- Stall onsets in SWING (excluding the frozen-sensor runs 151934, 152746, 161145): 12 in 11 runs, all after commands of 16.2-18.0 m/s² at 0.83-0.96 m/s [HW log].
- So the feedback, not the plan, drives the motor past its limit. Candidate fix: CART_ACCEL_MAX_M_S2 about 12 in a copy [HYP, untested].

## 2026-11-12: full 11-11 bench results (results.zip) and UIM344 settings
Doc: [Cart motor: 11-11 test results and UIM344 settings](https://claude.ai/artifact/EkGfVu5qQuAdt5p4UewPay). Barney uploaded `~/Desktop/CartJolt/results` (36 runs, 2026-11-11 15:49-17:13); he pressed b at the first slight stutter; Ctrl+C read as severe on the running trial [HW]:
- Highest clean reversal accel per run (+/-0.78 m/s, bare): A 10 ms 22/19/18; B 20 ms 14/13; C 40 ms 8/6; D 5 ms 18-22 (6 runs); E 2 ms 18-28 (5); F 18-22 (5); G 22/13. Only B and C clearly worse; the rest overlap (same method varies 4-10 m/s^2). Style test (+/-0.7 m/s, 12 m/s^2 default): B, C scored 2,2; D 0,0; others mostly 0. Cruise: all 0 except C.
- Two-load: with a 0.387 kg battery the reversal test went clean to 25-28 (bare clean to 25); only the first loaded run stuttered at 16. No mass estimate. A torque limit would drop ~25 %: the stutter onset is not a plain torque limit [HYP]. Labels say "30V" on the battery runs: meaning unknown (supply voltage?) [?].
- Later runs (after 17:00) a little lower (18-22) than 16:30-16:45 (20-28): motor warming? [HYP]
- CFG344 v5.70 tooltips (read from CFG344.exe): LPR = encoder pulses/rev, read only; I_work = run current; I_idle = % of I_work when stopped; Max. Pos. Error = max missing steps before lockout + red light (unit "pulse"); Ultra-quiet Speed (rpm) = below it the motor runs "ultra-quiet and smooth"; also Resonance Suppress 1st/2nd (rpm). UIM5756PM rated 2.8 A, 1.2 N m.
- Recommended (not yet applied): I_work 2.8 A; Ultra-quiet Speed minimum (mode switch inside the 0-293 rpm range on every reversal [HYP]); I_idle 50 %; Max. Pos. Error about 20 mm of cart (0.12 rev); leave Micro-Stepping (its value tells the pulley: 8 = 2 in, 4 = 1 in pitch diameter). One change at a time, rerun method A.
- Config wires (signal cable black pin 7 GND, white pin 8 TX, green pin 9 RX): not to stay on the Mega during runs. Pin 7 is tied to the motor supply 0 V and would bypass the opto-isolated step inputs (ground noise into Mega/Pi) [HYP]; Serial2 (pins 16/17) would be the free pins (not 0/1, not 18 = step counter); logic level unknown (measure white-black); Mega needs a pass-through sketch and the undocumented baud. Advised a USB-TTL adapter.
- 2026-11-12 Barney: D (5 ms stream), E and F felt very similar at the rig, D smoothest and most consistent [HW, by eye]; matches the style test (D 0, 0). Option offered: V2b copy keeping the 10 ms loop but sending two interpolated speed commands per cycle.
- 2026-11-12 config wiring advice: motor supply ON, driver OFF (Mega USB unplugged; check the cart slides freely), step/dir/ena wires can stay. Barney plans to use an iRobot Create 2 mini-DIN serial cable (5 V TTL) as the adapter: its pin 1 is battery voltage, not ground; use pin 3 (Create TX) to motor white, pin 4 (Create RX) to motor green, pin 5/6 GND to motor black; verify with a meter (Tensility numbering is reversed). Measure motor white-black idle level first; 3.3 V means a 1k/2k divider on the green line [?].

## 2026-11-12: UIM344 settings read with CFG344 [HW]
Barney read the motor with CFG344 v5.70 (iRobot Create 2 serial cable as the USB-TTL adapter): S/N 4294967295 (blank), LPR 1000, I_work 3.0 A, I_idle 100 %, Micro-Stepping 4, Max. Pos. Error 1000 pulse, Ultra-quiet Speed 4 rpm.
- Micro-Stepping 4 = 800 pulses per turn; with 0.638175 m per 6400 pulses the pulley is 79.8 mm per turn = 25.4 mm (1 in) pitch diameter, r 12.7 mm. All earlier torque numbers (r 25.4 mm) halve and motor rpm doubles: about 590 rpm at 0.78 m/s, 720 at 0.96. Rotor inertia seen at the belt: 3e-5/0.0127^2 = 0.19 kg (not 0.047). CartJolt constants fixed (ChatGPT-Pendulum-Project `claude/project-thread-wk3tn6` c6b5935).
- I_work already above rated (2.8 A) and Ultra-quiet already minimal: neither is the cause. Max. Pos. Error 1000 = about 1 turn = 80 mm of cart lag (if encoder pulses) before lockout: the motor can fall far behind and then race to catch up, which fits the "correcting itself" stutter [HYP]. My 11-12 advice of 2.8 A / minimal ultra-quiet / 20 mm is superseded by this read.
- Advice now: I_idle 50 % (3 A at standstill heats the motor; later 11-11 runs were weaker [HYP]); leave the rest. ~~At 590-720 rpm torque is limited by back-EMF, so supply voltage is the main lever: try 36 V (UIM344 24-48 V, keep margin for braking regen, bulk capacitor) [HYP].~~ Superseded 2026-11-12 (evening) by [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md): bare D runs at 18, 24 and 30 V reached the same 20-26 m/s²; voltage is not the limit above about 18 V at 0.78 m/s. Asked Barney the normal supply voltage and whether "30V" in the battery run labels was a voltage change (would explain open question 21).
- 2026-11-12 Barney: supply is 30 V (limit 2 A; supply current never above 0.8 A, 0.018 A with the driver disabled). Supply current is not coil current: 0.8 A at 30 V fits full 3 A coil current [HYP]. ~~Voltage budget at 590-720 rpm (Kt about 0.30 N m/A from 1.2 N m at 2.8 A; L about 3 mH assumed, 50 pole pairs): back-EMF 19-23 V plus coil reactance about 28-34 V at 3 A needs roughly 35-42 V, so at 30 V the coil current and torque fade at 0.8-0.96 m/s, where every swing stall happened [HYP]. Next: try 36-40 V (stay under about 42 V for braking regen; driver max 48 V; bulk capacitor).~~ Superseded 2026-11-12 (evening) by [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md): bare D runs at 18, 24 and 30 V reached the same 20-26 m/s²; voltage is not the limit above about 18 V at 0.78 m/s. The Kt / L estimate overstated the voltage needed (18 V would have had no headroom at 590 rpm). "30V" in the battery-run labels = normal supply, so open question 21 is still open.
- Coil resistance cannot be measured with a meter (coils wired inside to the built-in driver). Estimate: enable and hold still 20 s, R per coil = (30 x I_supply - 0.5) / 9.
- 2026-11-12 correction (Barney): only runs labelled "30V" were at 30 V; every unlabelled run was at 24 V. So the loaded reversal runs (clean to 25-28) were at 30 V and the bare run (clean to 25) at 24 V; all method runs (A-G), the bare reversal run and the stall-test runs were at 24 V. ~~The +25 % voltage roughly offset +30 % mass: fits voltage-limited torque at speed [HYP].~~ Superseded 2026-11-12 (evening) by [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md): bare D runs at 18, 24 and 30 V reached the same 20-26 m/s²; voltage is not the limit above about 18 V at 0.78 m/s. Asked for back-to-back bare D runs at 24 V and 30 V, the supply's maximum voltage, and the 11-04 swing-up voltage.
- 2026-11-12 Barney: bench supply max 30 V / 5 A [?]; the 2026-11-04 swing-up runs were at 24 V (he believes). ~~Advised: run everything at 30 V from now on (+25 % voltage at the speeds where the stalls happen), raise the current limit to 4-5 A, confirm with back-to-back bare D runs at 24 V and 30 V; for more, a 36 V switching supply with the bulk capacitor, staying under about 40 V.~~ Superseded 2026-11-12 (evening) by [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md): bare D runs at 18, 24 and 30 V reached the same 20-26 m/s²; voltage is not the limit above about 18 V at 0.78 m/s. Stay at 24 V.

## 2026-11-12 (evening): supply voltage sweep, and the swing-up with method D
Barney ran `reversal_method_test.py --method D` (bare cart, 3 reversals at ±0.78 m/s, about 590 rpm) at several supply voltages (`CartJolt_Selected.zip`, runs `revm_p5-stream_20261112_172747` to `_173625`) [HW]:

| Supply | Runs | Highest clean (m/s²) | First stutter (b) at |
| --- | --- | --- | --- |
| 24 V | 4 (one after an Arduino reset and supply power cycle) | 23, 25.5, 22, 21 | 20 and 24; 26.5-28; none; 22 |
| 30 V | 1 | 20 | 21-22 |
| 18 V | 1 | 20 (stopped there) | none |
| 12 V | 1 | 14 | 14 (once) |

- Barney: little difference between 18 V and 36 V (no 36 V run in the zip) [HW, by eye; 36 V ?].
- From 18 V up, supply voltage does not set the limit at 0.78 m/s; only 12 V is clearly lower. The 2026-11-12 voltage-limit hypothesis is withdrawn (struck above). Not tested: 0.83-0.96 m/s, where the swing stalls happened. Stay at 24 V.
- Neither 0.387 kg of added mass (2026-11-11, clean to 25-28) nor 18-30 V moves the stutter point, which scatters 20-28 m/s² run to run. A plain torque limit would move with both, so the limit is more likely the UIM344's own closed loop (Max. Pos. Error 1000, catch-up), a resonance, or judging scatter [HYP]. [Open question 22](../open-questions.md).
- Swing-up with method D (Barney asked): `PythonMaster2_swingup_V2b_D.py`, ChatGPT-Pendulum-Project `claude/project-thread-wk3tn6` `DoubleSwingUp_V2D/` (commit 4ae6037; copy in project files `DoubleSwingUp_V2D/`). Made from V2b by `tools/make_v2b_d.py`; V2b unchanged.
  - Each 10 ms cycle sends its speed change in 2 halves, 5 ms apart, without waiting for the Mega's reply. Replies are read as they arrive; 150 ms without one stops the run as before.
  - The model, the swing TVLQR and the balance gains include the split; the plan's speed changes are timed to the halves' average (+2.5 ms). The stop brake is streamed too.
  - Options `--sends 1|2|5` (every 10/5/2 ms) and `--accel-max` (default 16). Installs to a new Pi folder `~/Desktop/DoubleSwingUpV2D`.
  - Twin check, `same_4.0s`, paired runs with the same radio and noise (`tools/twin_v2bd_check.py`) [SIM]: clean radio 12/12 caught first try for both V2b and V2b_D; rig-like radio 42/142 (30 %) vs 41/137 (30 %) attempts caught; with `--accel-max 12` 27/144 (19 %). The twin's motor never stalls, so only the rig can show whether the 5 ms steps reduce the jolt.
- First rig run of V2b_D, 2026-11-12 18:29 local (`swingup_double_20261112_182942_358826.csv`, same_4.0s) [HW]: attempt 1 followed the twin almost exactly (cart -46 mm / -0.57 m/s at 0.5 s vs twin -41 / -0.54; -286 mm at 1.0 s vs -289; arms within about 5°). At 1.34 s TX1 went silent for more than 150 ms (wireless_timeout, radio_age 154-174 ms): the attempt aborted and the run stopped at 13 missing frames in RECOVER (MAX_SETTLE_MISSES 12). Pi pacing fine: 3 of 476 timed sends more than 2 ms late (worst 5 ms). AngleSensorDiagnostic right after (motor off, arms swung by hand, 9 s): no missing frames, ages 1-3 ms (a few 6-17). TX1 is powered from the Mega 5 V on the cart PCB, so a 5 V sag or the moving cable during the run is a candidate [HYP]. Asked Barney for the CSV and whether the cart jolted near 1.2-1.3 s; offered a ride-through of gaps up to 1 s while recovering.
- V2b_D updated (commit 7cc647f): radio gaps while waiting or settling now hold the cart still for up to 1 s (MAX_SETTLE_MISSES 100) instead of stopping after 12 frames; a gap while balancing ends that catch and recovers instead of stopping the run. Twin [SIM]: rig-like radio 41/139 attempts caught (same as before), no gap stops; 300 ms stalls 10/min no longer stop the run.
- Rig runs 2026-11-12 18:37-18:41 local (V2b_D, same_4.0s) [HW, console]: 183735 (pre-ride-through): attempt 1 36° off at 1.09 s, then stopped on a TX1 gap. 183837 (ride-through): 4 attempts, each ended by a TX1 gap of 40-42 frames (about 0.4 s) at 1.75-1.82 s (attempts 1-3) and 3.69 s (attempt 4, arms at +6/+4° from upright); repeated 40-41-frame gaps while recovering. Fixed-length 0.4 s gaps look like TX1 rebooting [HYP]. Barney then 'may have fixed the sensor issue' (what he changed: asked). 184140: no dropouts; 7 attempts, none caught: attempt 1 within about 30 mm and 4° of the twin to 2.0 s, then all drifted 35-40° off the plan at 2.3-3.6 s (one hit the cart abort at -362 mm); best reached about 30° from upright. Asked for a `--sends 1` A/B run, the CSVs, and whether the cart jolted.
