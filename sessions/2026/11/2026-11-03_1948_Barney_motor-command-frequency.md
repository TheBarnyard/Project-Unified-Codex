---
member: Barney
ai: Claude (Claude Code, project thread)
date: 2026-11-03
status: done
pages_applied: yes
---
# Motor command frequency (Q&A)

Barney asked what frequency we send to the motor. Answered from existing PUC pages (Math/Single/06_sensing_actuation.md 6.5, 01_variables.md) and the stale ENGT480 clone's ArduinoSlave.ino; latest ENGT480 main not re-checked.

- Pi -> Mega commands: one 4-byte timer-top N per control cycle, 10 ms, 100.0 Hz mean measured [HW].
- Mega -> UIM5756PM step pulses: f = 125000/(|N|+1) steps/s (Timer3 250 kHz, CTC toggle). Range: ~1.9 steps/s (N = 65535, "stopped") up to ~8.3 kHz at the effective 0.83 m/s cap (N = 14); 0.6 m/s ~ 6.0 kHz [HW/code].
- No page changes; nothing new learned.
