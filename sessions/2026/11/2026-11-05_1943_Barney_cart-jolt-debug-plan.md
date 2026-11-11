---
type: session
date: 2026-11-05
time: 19:43 (UTC)
member: Barney
ai: Claude project thread
topics: [cart-arduino, swing-up]
status: wip
pages_applied: yes
transcript: none
---
# Cart jolt (UIM344 red LED) during double swing-up: causes and debug plan

## Goal
Barney: on the 2026-11-04 swing-up runs the cart jolts (unlike the sim) and the motor shows a red LED meanwhile. The supply never drew more than 1 A even with a 2 A limit. Mechanical, electrical, code or config? Give a debug and test plan. A separate thread analyzes the 2026-11-04 logs.

## What happened
- Read the UIM344 manual, UIM5756PM drawing, CFG344 config tool strings, `ArduinoSlave.ino` (stale ENGT480 clone, main e8f82ea) and `PythonMaster2_swingup_V2b.py`.
- Wrote test tools and a plan. Plan doc: https://claude.ai/artifact/7YmvrJBDnQpgkRZXUc57fp ("Cart jolt debug plan").

## Findings
- Red LED with the driver ON = error (manual p.13). CFG344 tooltip for Max. Pos. Error: "Exceeding this value will result in a lockout and flash a red light. Offline re-enable can clear the error." So red LED = the motor fell behind its pulses by more than Max Pos Error and locked; that stop is the jolt [HYP, from vendor text]. The encoder is on the motor shaft, so belt skipping cannot trip it.
- Driver settings live in the UIM344, readable only by UART + CFG344: I_work (A), I_idle (%), Micro-Stepping, Max. Pos. Error (pulses), Ultra-quiet Speed (rpm), LPR (read only). The manual's example screenshot shows I_work 0.6 A; motor rated 2.8 A, 1.2 N m holding, rotor 300 g cm², 24-48 V (abs max 50 V). Rig values unknown [?].
- Supply current is not phase current (chopper drive): peak about 20 W mech + 7 W copper = about 1.1 A at 24 V, much less on average, so "never over 1 A" does not exclude a low I_work [HYP].
- DISTANCE_PER_6400_STEPS_M 0.638175: at 8 microsteps = 0.16 m/rev = 2.00 in pitch-diameter pulley; at default 32 it would need an 8 in pulley. So the drive is probably set to 8 microsteps [HYP].
- 2026-11-04 V2 log `swingup_double_20261104_153309_280984.csv`: all 5 attempts command 16-17.5 m/s² (CART_ACCEL_MAX 16) and the 0.83 m/s cap repeatedly [HW log]. Estimated 0.65-0.75 N m needed at 16 m/s² (about 1.3 kg assumed, r 25.4 mm): marginal even at full current [HYP].
- ArduinoSlave sets each new step rate instantly (10 ms speed staircase); `position` is commanded pulses, not measured (also found by the log thread). No alarm output on the UIM344 connector (pins: V+, GND, COM, DIR, STP, ENA, GND, TX, RX).
- Lockout clears on a disable/enable: a script start (port open resets the Mega, setup disables then enables) or a motor power cycle.

## Dead ends
- Reading/setting UIM344 parameters from the Pi: the CFG344 serial protocol is not documented; the exe only shows UI strings. Use the Windows tool.

## Changed
- Code: `TheBarnyard/ChatGPT-Pendulum-Project` branch `claude/project-thread-wk3tn6`, `CartJolt/` (commit 1fe4d6a): `motor_stress_test.py`, `replay_run_motor.py`, `cart_link.py`, `ArduinoSlaveRamp/ArduinoSlaveRamp.ino` (copy of ArduinoSlave that ramps the step rate over each 10 ms via Timer1 at 1 kHz; avr-gcc syntax check only, not flashed), `tools/fake_mega.py`. Copy in project files `CartJolt/`. Scripts tested against the fake Mega only [SIM].
- Firmware flashed: none. Wiring: none.

## Open questions and next steps
- Barney: read the UIM344 config (I_work, microstep, Max Pos Error), supply voltage, whether the red LED stays on until restart.
- Then stress test arms off, replay a jolting attempt arms off/on, change one thing at a time. Plan order: config, supply, mechanics, tests, code (lower CART_ACCEL_MAX, ramp sketch).

## 2026-11-06: torque math explainer
- Barney: the motor datasheet says 1.26 N m holding torque (the UIM5756PM drawing in PUC says 1.2). Explainer doc "Cart motor torque math": https://claude.ai/artifact/3zyNMAfTcsA97iVPe8zss6.
- Required torque from the 2026-11-04 V2 log (all SWING cycles, r 25.4 mm, 1.0 kg cart assumed, no friction): 95th pct 0.57 N m near standstill falling to 0.17 at 0.8 m/s when speeding up; braking up to 0.99 max. Arm force beyond (m1+m2)a: median 0.8 N, p90 2.8 N, max 17 N [HW log + HYP].
- ~~Demand at the 3-8 m/s² where the cart fell short is only 0.15-0.35 N m (12-28 % of holding): points to low I_work, voltage limit, friction or a different r [HYP].~~ Superseded 2026-11-11 by the 2026-11-11 section below: over 30 runs the cart follows up to about 12 m/s²; the shortfall was fit noise.
- Low-speed a_max estimate (70 % of T_h(I), M_eff 1.38 kg, 3 N friction, 3 N arm reserve): I_work 2.8 A 21, 2.0 A 14, 1.5 A 9, 1.0 A 5, 0.6 A 1 m/s² [HYP].
- Lag on an unmet acceleration: e = 0.5 (a_cmd - a_m) t^2; a 3 m/s² shortfall reaches 40 mm in 0.16 s. Max Pos Error 1000 pulses = about 40 mm (encoder edges) or 100 mm (step pulses) [?].

## 2026-11-07: Mega not replying at the rig
- Barney ran `PythonMaster2_swingup_V2.py` (V2b was not in ~/Desktop/DoubleSwingUpV2) three times: each failed at the first motor command with "/dev/ttyACM0: received 0/2 bytes"; Mega RESET did not help [HW]. Runs swingup_double_20261107_125303/125337/125446 (no motion).
- AngleSensorDiagnostic: angle2 never_received is expected (TX2 on slot 3; script found it). angle1 missing for 8 s at start, then valid.
- Likely cause [HYP]: ArduinoSlave freezes silently when D22/D27/D23 read LOW (limit switch or stop button), or another process holds the port. Sent fuser/dmesg checks, ~/megacheck.py (3 test commands), V2b install from commit fd49fd7. Waiting on result.

## 2026-11-11: all 2026-11-04 runs analysed for stalls
- Barney uploaded `run_logs.zip`: 36 runs from 2026-11-04 (151934-170648, all `PythonMaster2_swingup_V2.py`, none V2b) plus empty 2026-11-07 / 2026-11-09 files. 60 attempts, 8 catches (all on same_4.0s / same_3.0s). Doc "Cart jolt analysis: 2026-11-04 runs": https://claude.ai/artifact/YAj8iBivoMQSxVneBDnZv9.
- Method: the arms are the only sensor of real cart motion. 0.5 s windows: fit the V2 model with the commanded speed changes vs with no cart acceleration; 0.2 s windows: fit a scale k on the commanded changes. Scripts: ChatGPT-Pendulum-Project `claude/project-thread-wk3tn6` `CartJolt/analysis/` (commit 7c93da6), copy in project files `CartJolt/analysis/`.
- Below about 12 m/s² the cart follows: k median 1.00, middle half 0.9-1.1, about 2,800 windows with arms < 5 rad/s [HW log].
- Transient stalls (cart stops accelerating for 0.1-0.5 s, then follows again) in 15 runs, every SWING one after 6-28 commands of 12 m/s² or more (peaks 16-18 m/s² at 0.83-0.96 m/s). High-demand windows: 20 stalled of 206 decidable; low demand 3 of 602 [HW log, HYP that it is torque].
- Latched stall: run 162911, cart dead from about 4.9 s to the end (20.8 s, Ctrl+C) while the Mega kept sending pulses; next run 163044 moved. Matches the manual: "Maximum Missing Steps: exceed this value, the motor will stop and locked" [HW log; cause HYP].
- By path, stall share of decidable high-demand windows: same_4.0s 4 % (7 catches), same_3.0s 0 % (1 catch), folded_4.5s 36 %, whip_4.5s 24 % (0 catches; these used PLAN_ACCEL 9, MOTOR_TOP_SPEED 1.25, up to 18 m/s² at 0.96 m/s).
- Lag model on the 162911 swing commands (motor with a fixed accel limit following the 10 ms staircase): worst lag 2 mm at 20 m/s² available, 5 mm at 18, 34 mm at 16, 84-100 mm at 12-14. A small shortfall runs away, so failure is a cliff [SIM].
- Torque at the stall points (cart about 1.0 kg [?], arms 0.417 kg, rotor 0.05 kg equivalent, friction 2-5 N [?], r 25.4 mm): 0.65-0.72 N m at 16 m/s², 0.72-0.80 at 18, at 310-360 rpm. Typical 57 mm motor at 2.8 A gives about 0.8-1.0 N m there [HYP, no UIROBOT curve]: the motor is at or somewhat below what it should do; I_work decides.
- Mega no-reply stops: 11 runs, all in RECOVER; 7 came 0.9-3.6 s after a stall. Ask Barney whether the stop button was pressed; else the switch inputs pick up the jolt [HYP].
- Not usable: 151934 and 152746 (arm 1 reading frozen; their k=71 err 35° aborts are sensor faults), 161145 (both readings constant 6 s while 0.27 m commanded: cart likely never moved; motor off, locked or disabled [?]).
- Revises the 2026-11-05 log result and the 2026-11-06 "shortfall at 3-8 m/s²" finding (one run, noise model without radio timing): over 30 runs the cart follows at moderate demand.
- Next: Barney answers (stop button, 162911 red LED, 161145 supply, supply voltage), CFG344 read, supply MIN/MAX, stress test arms off, replay 162911 attempt 1, slow-motion video. Without the rig: cap plans at about 12 m/s² and 0.8 m/s; do not rerun whip/folded.

## 2026-11-11 (later): cart mass from a two-load stall test
- Barney asked whether code can estimate cart mass. Not from run logs: the stepper sets the cart's motion, so the arms never feel a force and cart mass drops out of the equations.
- Built `CartJolt/two_load_stall_test.py` (ChatGPT-Pendulum-Project `claude/project-thread-wk3tn6`, commit b6651ec, copy in project files `CartJolt/`): arms off; each trial is a 60 ms hard speed-up ending at 0.8 m/s (reversal from up to -1.2 m/s at high accel); climbs a ladder 6-40 m/s², then bisects to 1 m/s² and re-checks both ends; operator answers clean / red LED / buzz / off the mark. Run once bare, once with a weighed item; `--compute` gives effective moving mass m = dm*a2/(a1-a2) and motor force beyond friction m*a1 (and torque at r 25.4 mm [assumed]). Tested against `tools/fake_mega.py` only [SIM].
- Barney asked for a second version that reverses instead of braking: `CartJolt/two_load_reversal_test.py` (commit d9c422b): 3 back-to-back hard reversals between -0.8 and +0.8 m/s, same search and math (shared `run_search`, results prefixed `rev_`). A lower stall acceleration than the single speed-up would mean back-to-back reversals cost extra [SIM-tested only].
- Barney (testing at the rig): the skips and stutters look like the motor correcting itself; maybe commands are sent too fast? Built `CartJolt/command_style_test.py` (commit d488b8d): the same move (reversals, sine, steady cruise, or a replayed attempt) sent 7 ways: command period 10 ms (now) / 20 / 40 / 5 / 2 ms, 10 ms with timer hysteresis, 10 ms with 30 ms smoothing; blind shuffled order, operator scores 0/1/2/red, ranked summary. Streams commands without waiting for the Mega reply (stops if replies stop), prints the Mega round-trip time. Tested on the fake Mega only [SIM].
- Barney asked for a reversal test where the control method is picked with `--` options: `CartJolt/reversal_method_test.py` (commit 71d1db9). Same 3 reversals +/-0.8 m/s and climb/bisect stall search as `two_load_reversal_test.py`; `--method A..G` (A 10 ms + wait for each Mega reply = the swing-up; B 20, C 40 ms wait; D 5, E 2 ms stream; F hysteresis; G S-curve: accel flips over 30 ms, same top speed and middle accel, unlike the command style test's moving average) or custom `--period MS --smooth MS --hyst --send wait|stream`; `--method A,E,G` runs searches back to back; `--accel X --repeats N` scores one accel; `--summary` tables all searches; `--compute` per method. Results `results/revm_<method tag>_*.json`. Tested on the fake Mega only [SIM].
- Rig results of the reversal method test (stutter onset): E 2 ms about 20, D 5 ms about 19, F hysteresis about 18.5, G S-curve 13.4 m/s²; A not pasted. See the debug page. Asked for `--summary` and an alternating A/G check at 15 m/s².
