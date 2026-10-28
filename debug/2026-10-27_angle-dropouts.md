---
type: debug
status: likely-fixed
opened: 2026-10-27
by: Barney (Claude)
subsystems: [encoders-and-transmitters, receiver]
---
# Angle dropouts (ANGLE1_MISSING) and TX2 never received

## Symptoms
- Controller faults with ANGLE1_MISSING / wireless_timeout. Logs show TX1 packets lost in bursts (radio age 10 to 135 ms); the 10-miss fault trips on about 135 ms outages.
- Bad window 2026-10-27 14:24 to 15:24 local, losses growing within each run; clean from 15:42.
- Angle 2 never received at all.

## Ruled out (dead ends)
- Pi buffer, RAM or CPU: sequence numbers consecutive, serial gap counters flat, and radio age is timed on the receiver ESP32 [HW].
- Pi Wi-Fi interference: Pi is on 5 GHz (5540 MHz) [HW].
- Stepper motion: `RadioDropoutTest` (esp_only, arduino_idle, hold, move) clean; 277 s PendulumExcite run with 0 misses [HW].
- TX2 powered nearby: clean on battery and USB charger [HW].
- Crowded room: about 30 people at 20:15 and clean; the room was nearly empty during failures [HW].
- TX1 battery: TX1 has no battery.

## Cause and fix
- Dropouts: TX1 was powered from the Mega 3.3 V pin, a small regulator overloaded by ESP32-C3 transmit bursts. Rewired to Mega 5 V into the XIAO 5V pin; first diagnostic clean with radio age a steady ~4 ms (before: 1 to 20 ms) [HW]. 20+ min controller confirmation pending.
- Angle 2: wrong firmware on TX2. With `TX2Diag` and then the repo `TX2.ino`, angle 2 arrives (age 1 to 6 ms). Battery swing test: 0 timeouts in 32 s [HW]. Earlier gaps up to 3.7 s were from the USB cable.

## Side notes
- TX1 was flashed by mistake during this session and restored from backup (MAC 80:F1:B2:52:DE:90).
- 2.4 GHz survey: channel 1 has 10 APs, channel 6 has 5, channel 11 has 4. Channel-11 firmware copies offered, not built.

## Files
`RadioDropoutTest.py` and `TX2Diag/` on branch `claude/project-thread-24gc4b` of `TheBarnyard/ChatGPT-Pendulum-Project`. Logs on ENGT480 `logs` branch, `raspberrypi-c8674ffe/Code/SinglePendulum/run_logs/`.
