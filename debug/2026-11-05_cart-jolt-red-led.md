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

## Tests
Plan doc: https://claude.ai/artifact/7YmvrJBDnQpgkRZXUc57fp. Tools: ChatGPT-Pendulum-Project `claude/project-thread-wk3tn6` `CartJolt/`.
1. Read the UIM344 config with CFG344 (Windows + USB-TTL, motor powered, driver off).
2. Supply: 24-48 V, limit 3 A+, CC lamp, 1000-2200 µF bulk cap.
3. Mechanical (power off): push force along the track, belt tension, paint-pen witness marks on pulley/idler/clamps, mount bolts.
4. `motor_stress_test.py` arms off (18 trials, asks red LED / jolt / mark offset).
5. `replay_run_motor.py` a jolting attempt, arms off then on.
6. One change at a time, rerun 4-5.
7. Code: lower CART_ACCEL_MAX_M_S2 in a copy; `ArduinoSlaveRamp` (ramped step rate).

| Result | Points to |
| --- | --- |
| Red LED, stays on | lockout: torque vs demand (config/supply/code) |
| Off the tape mark, no red LED | belt skip or pulley slip (mechanical) |
| Jolts only with arms on in replay | arm reaction load |
| Never in replay, only live | controller/radio |

## Results
- 2026-11-05, log-analysis thread ("Analyze yesterday's double swing-up runs"), run `swingup_double_20261104_153309_280984` [HW log, HYP]: 200 ms windows fitting an extra constant cart accel dA on top of the commanded speed (V2 ratios). Below 3 m/s² commanded the cart follows (dA about 0). At 3 m/s² or more, 78 % of 54 windows come up short, mean 1.1 m/s²; the clear cases are short by about 3 m/s² (attempt 4, t 33.6-33.7 s: a_cmd +8, cart gave about half; attempt 5, t 43.7-43.9 s at the 0.83 m/s cap). No frozen cart: attempts 2-5 track fine at first, so any lockout cleared between attempts. Supports "motor cannot deliver the accel at speed", not belt skip specifically. 200 ms windows smear short jolts.
