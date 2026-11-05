---
updated: 2026-11-05
updated_by: Barney (Claude, cart jolt session)
---
# Cart and Arduino Mega

An Arduino Mega 2560 runs `Code/ArduinoSlave/ArduinoSlave.ino`. It drives the cart stepper, talks to the Pi on `/dev/ttyACM0` at 115200 baud, and handles the limit switches and the stop button.

- Input: a 4-byte step-rate command from the Pi.
- Output: cart position back to the Pi.
- ~~Stepper driver manual: `Manual_UIM5756PM.pdf` [?] confirm this is the driver in use.~~ Superseded 2026-10-29 by [session](../sessions/2026/10/2026-10-29_1513_Barney_hardware-datasheets.md): Barney confirmed the motor.
- Motor: UIM5756PM closed-loop integrated stepper, UIM344 pulse-direction controller built in (Barney, 2026-10-29). Datasheets, manual and wiring: [Hardware/Datasheets/UIM5756PM_Motor](../Hardware/Datasheets/README.md). Microstep setting on the rig [?] (default 32). 2026-11-05: DISTANCE_PER_6400_STEPS_M 0.638175 implies 8 microsteps with a 2.00 in pitch-diameter pulley [HYP]; confirm with CFG344.

## Known limits
- Speed is quantized by the stepper timer. Near 0.83 m/s one timer step (0.831 to 0.890 m/s) needs 5.9 m/s^2 in 10 ms, more than the controller's torque-limited acceleration, so the speed rounds back: an effective cap of about 0.83 m/s [HW]. See [debug](../debug/2026-10-27_double-swingup-aborts.md).
- The Mega 3.3 V pin cannot power an ESP32-C3. See [gotchas](../gotchas.md).

## UIM344 driver (2026-11-05, [cart jolt](../debug/2026-11-05_cart-jolt-red-led.md))
- Settings live in the motor (EEPROM), read/set only over its UART (connector pins 7 GND, 8 TX, 9 RX) with the Windows tool CFG344 in [Hardware/Datasheets](../Hardware/Datasheets/README.md): I_work (A), I_idle (%), Micro-Stepping, Max. Pos. Error (pulses), Ultra-quiet Speed (rpm), LPR. Motor powered, driver disabled; re-power after SET. Rig values [?].
- Red LED with the driver on = error. Position error above Max. Pos. Error = lockout (motor stops, red LED), cleared by disable/enable (script start resets the Mega) or power cycle.
- No alarm output on the connector, and `position` in ArduinoSlave is commanded pulses, so run logs cannot show a lockout or belt skip.
- Rated 2.8 A, 1.2 N m holding, rotor 300 g cm², 24-48 V (abs max 50 V), radial load 75 N max.
