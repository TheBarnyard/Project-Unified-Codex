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
