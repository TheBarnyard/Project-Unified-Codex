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

**Update 2026-11-11 (all 30 runs, [doc](https://claude.ai/artifact/YAj8iBivoMQSxVneBDnZv9)):** the logs now show the stalls directly. The cart follows commands up to about 12 m/s²; at the 16-18 m/s² reversals (0.83-0.96 m/s) it stops being pushed for 0.1-0.5 s in 15 runs, and in run 162911 it stayed dead from 4.9 s to the end (latched lockout) [HW log]. Demand there is about 0.65-0.8 N m at 310-360 rpm: at or above what this motor gives, so no margin [HYP].

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
- 2026-11-06 torque budget ([doc](https://claude.ai/artifact/3zyNMAfTcsA97iVPe8zss6), [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md)): at full current the swing needs at most about half of the 1.26 N m holding torque (r 25.4 mm assumed). ~~The 3-8 m/s² shortfalls need only 0.15-0.35 N m, so the motor is delivering far below rating: low I_work, 24 V corner speed, friction or a different r [HYP].~~ Superseded 2026-11-11 by [session](../sessions/2026/11/2026-11-05_1943_Barney_cart-jolt-debug-plan.md): those shortfalls were fit noise; the motor fails at about 0.65-0.8 N m. Braking torque at speed is at least driving torque (back-EMF helps), so the hard moment of a reversal is speeding up at its end.
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
