---
updated: 2026-10-28
updated_by: Barney (Claude, PUC setup session)
---
# Hardware state

What is physically on the rig right now. Update this whenever you flash, rewire, or swap something, with the date.

| Part | Current state | Since | Source |
| --- | --- | --- | --- |
| TX1 (XIAO ESP32-C3, arm 1 encoder) | Repo `TX1.ino`, restored from backup. MAC 80:F1:B2:52:DE:90. On a custom PCB wired to the Mega; powered from Mega **5 V** into the XIAO 5V pin | 2026-10-27 | [angle dropouts](debug/2026-10-27_angle-dropouts.md) |
| TX2 (XIAO ESP32-C3, arm 2 encoder) | Repo `TX2.ino`, reflashed. MAC e8:f6:0a:15:1b:48. LiPo battery, charged through the XIAO USB | 2026-10-27 | [angle dropouts](debug/2026-10-27_angle-dropouts.md) |
| Receiver (ESP32-WROOM, CP2102) | Original `Receivermaster` re-flashed after the framed test. [?] Which protocol version (6-byte unframed or v1 framed) is on it now | 2026-10-07 | [receiver](subsystems/receiver.md) |
| Mega 2560 | `ArduinoSlave` | [?] | [cart](subsystems/cart-arduino.md) |
| Arm 1 | New PLA arm | 2026-10-27 | [arms](subsystems/arms-and-model.md) |
| Arm 2 | Old second arm | | [arms](subsystems/arms-and-model.md) |
| Track limits | Limit switches must be more than 0.40 m from centre for current swing-up settings [?] unconfirmed | | [swing-up](subsystems/swing-up.md) |

Backups: `~/Desktop/TX2Diag/TX2_backup_20261027.bin` on the Pi is TX2. The TX1 backup there may have been overwritten; re-back-up TX1.
