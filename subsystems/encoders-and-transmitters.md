---
updated: 2026-10-28
updated_by: Barney (Claude, PUC setup session)
---
# Encoders and transmitters

Each arm joint has an MT6701 magnetic encoder (14-bit, 0 to 16383, read over I2C) and a Seeed XIAO ESP32-C3 that sends the angle over ESP-NOW at 200 Hz to the receiver.

| Board | Code | SENDER_ID | Power | MAC |
| --- | --- | --- | --- | --- |
| TX1 (arm 1) | `Code/Wireless/Transmitters/TX1/TX1.ino` | 0 [?] | Mega 5 V via custom PCB | 80:F1:B2:52:DE:90 |
| TX2 (arm 2) | `Code/Wireless/Transmitters/TX2/TX2.ino` | 1 | LiPo LP653042, charged over XIAO USB | e8:f6:0a:15:1b:48 |

- TX1 and TX2 code differ only in SENDER_ID. There is no TX3 in the repo.
- ENGT480 also has a TX1 diagnostics build (`Code/Wireless/Transmitters/TX1/DIAGNOSTICS.md`) and `TX2Diag` exists on branch `claude/project-thread-24gc4b` of `TheBarnyard/ChatGPT-Pendulum-Project` (prints its own and target MAC, raw values).
- Flash command used on the Pi: `arduino-cli` with `--fqbn esp32:esp32:XIAO_ESP32C3:CDCOnBoot=cdc`.

## History
- 2026-10-27: dropouts traced to TX1 powered from the Mega 3.3 V pin; moved to 5 V [HW]. TX2 "never received" fixed by reflashing `TX2.ino` [HW]. See [debug](../debug/2026-10-27_angle-dropouts.md).
