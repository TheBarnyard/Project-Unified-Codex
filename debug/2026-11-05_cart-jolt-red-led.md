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
