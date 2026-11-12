---
updated: 2026-11-12
updated_by: Ryan (Claude, V2 arms fit session, track length)
---
# Hardware state

What is physically on the rig right now. Update this whenever you flash, rewire, or swap something, with the date.

| Part | Current state | Since | Source |
| --- | --- | --- | --- |
| TX1 (XIAO ESP32-C3, arm 1 encoder) | Repo `TX1.ino`, restored from backup. MAC 80:F1:B2:52:DE:90. On a custom PCB wired to the Mega; powered from Mega **5 V** into the XIAO 5V pin | 2026-10-27 | [angle dropouts](debug/2026-10-27_angle-dropouts.md) |
| TX2 (XIAO ESP32-C3, arm 2 encoder) | Repo `TX2.ino`, reflashed. MAC e8:f6:0a:15:1b:48. LiPo battery, charged through the XIAO USB | 2026-10-27 | [angle dropouts](debug/2026-10-27_angle-dropouts.md) |
| Receiver (ESP32-WROOM, CP2102) | Original `Receivermaster` re-flashed after the framed test. [?] Which protocol version (6-byte unframed or v1 framed) is on it now | 2026-10-07 | [receiver](subsystems/receiver.md) |
| Mega 2560 | `ArduinoSlave` | [?] | [cart](subsystems/cart-arduino.md) |
| Cart motor | UIM5756PM closed-loop stepper, UIM344 controller built in. CFG344 read 2026-11-12: Micro-Stepping 4 (800 pulses/turn), LPR 1000, I_work 3.0 A, I_idle 100 %, Max. Pos. Error 1000 pulse, Ultra-quiet 4 rpm. Pulley 1 in pitch diameter (79.8 mm/turn) | 2026-11-12 (CFG344 read) | [datasheets](Hardware/Datasheets/README.md) |
| Cart motor supply | Bench supply, max 30 V / 5 A [?]; usually run at 24 V (2026-11-04 swings, unlabelled 11-11 tests), 30 V for the runs labelled "30V" on 2026-11-11; 2 A limit; draws up to 0.8 A (Barney, 2026-11-12). Bare-cart stall point is the same at 18, 24 and 30 V (12 V lower), so 24 V is fine (2026-11-12 sweep) [HW] | 2026-11-12 | [debug](debug/2026-11-05_cart-jolt-red-led.md) |
| Raspberry Pi | Raspberry Pi 4 Model B, 8 GB | 2026-10-29 (confirmed) | [datasheets](Hardware/Datasheets/README.md) |
| Arm 1 | New PLA arm (`arm_1_3dp`, 200 mm, 34.5 g printed). Pivots on the cart shaft at its small Ø8 hole. Hub = joint 2: shaft holder + 608, sensor mount + MT6701, ESP32 mount + XIAO (TX2), battery case + LiPo | 2026-10-27 | [arms](subsystems/arms-and-model.md) |
| Arm 2 | Old second arm. New `arm_2_3dp` (250 mm): clamps on the joint-2 shaft at its small hole; its hub electronics are for a future joint 3 (no shaft yet). Fitted on the rig? [?] | | [arms](subsystems/arms-and-model.md) |
| Track limits | About **1080 mm limit switch to limit switch** (Barney, 2026-11-04) [HW], so about ±540 mm from the middle if the cart starts centred. [?] Whether that is between the switch trip points (then subtract half the cart width for cart-centre travel) or the cart's own travel. ~~Limit switches must be more than 0.40 m from centre for current swing-up settings [?] unconfirmed~~ Superseded 2026-11-04 by [V2 arms fit session](sessions/2026/11/2026-11-04_1555_Barney_v2-arms-model-fit.md): measured | 2026-11-04 | [swing-up](subsystems/swing-up.md) |

Datasheets and pinouts for all parts: [Hardware/Datasheets](Hardware/Datasheets/README.md).

Backups: `~/Desktop/TX2Diag/TX2_backup_20261027.bin` on the Pi is TX2. The TX1 backup there may have been overwritten; re-back-up TX1.
