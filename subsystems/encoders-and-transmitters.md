---
updated: 2026-11-20
updated_by: Ryan (Claude, TX3 check session)
---
# Encoders and transmitters

Each arm joint has an MT6701 magnetic encoder (14-bit, 0 to 16383, read over I2C) and a Seeed XIAO ESP32-C3 that sends the angle over ESP-NOW at 200 Hz to the receiver.

| Board | Code | SENDER_ID | Power | MAC |
| --- | --- | --- | --- | --- |
| TX1 (arm 1) | `Code/Wireless/Transmitters/TX1/TX1.ino` | 0 [?] | Mega 5 V via custom PCB | 80:F1:B2:52:DE:90 |
| TX2 (arm 2) | `Code/Wireless/Transmitters/TX2/TX2.ino` | 1 (board was sending 2 since about 2026-11-04 [HW]; reflash pending [?]) | LiPo LP653042, charged over XIAO USB | e8:f6:0a:15:1b:48 |
| TX3 (arm 3, joint 3) | Legacy Pi checkout only: `ENGT481/Code/Wireless/Transmitters/TX3/TX3.ino` (2026-11-20), = TX2.ino with SENDER_ID 2 | 2 | [?] | [?] |

- TX1 and TX2 code differ only in SENDER_ID. ~~There is no TX3 in the repo.~~ Superseded 2026-11-20 by [TX3 check](../sessions/2026/11/2026-11-20_1924_Barney_tx3-transmitter-check.md): TX3.ino exists in the Pi's legacy ENGT481 checkout (not pushed to ENGT480); ENGT480 main moved transmitters to PlatformIO (`Transmitters/src/main.cpp` + `config.tx1.hpp`/`config.tx2.hpp`), no `config.tx3.hpp` yet.
- Receiver slot = SENDER_ID + 1; Receivermaster takes IDs 0-2. TX2 and TX3 must not both send ID 2 (see [gotchas](../gotchas.md)).
- ENGT480 also has a TX1 diagnostics build (`Code/Wireless/Transmitters/TX1/DIAGNOSTICS.md`) and `TX2Diag` exists on branch `claude/project-thread-24gc4b` of `TheBarnyard/ChatGPT-Pendulum-Project` (prints its own and target MAC, raw values).
- Flash command used on the Pi: `arduino-cli` with `--fqbn esp32:esp32:XIAO_ESP32C3:CDCOnBoot=cdc`.

## History
- 2026-11-20: TX3 sketch checked (only SENDER_ID differs from TX2). Triple script needs `--slots 1,2,3` once TX2 is back on ID 1. [session](../sessions/2026/11/2026-11-20_1924_Barney_tx3-transmitter-check.md)
- 2026-10-27: dropouts traced to TX1 powered from the Mega 3.3 V pin; moved to 5 V [HW]. TX2 "never received" fixed by reflashing `TX2.ino` [HW]. See [debug](../debug/2026-10-27_angle-dropouts.md).
