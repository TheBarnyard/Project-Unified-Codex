---
type: session
date: 2026-11-20
time: 19:24 (UTC)
member: Barney
ai: Claude project thread
topics: [encoders-and-transmitters, receiver]
status: wip
pages_applied: yes
transcript: none
---
# Check the new TX3 transmitter sketch for arm 3

## Goal
Barney is bringing up a 3rd arm. Find the new TX3 sketch made on the Pi and check it against TX1/TX2, the receiver and `PythonMaster3_triple.py`.

## What happened
- Found on the Pi (Barney, `find ~ -iname '*tx3*'`): legacy checkout `~/Desktop/GitHub Repository/ENGT481/Code/Wireless/Transmitters/TX3/TX3.ino` (3353 B, 2026-11-20 13:52 local) and a backup with build output `~/PendulumFirmwareBackups/TX3_20261120_135326_yGNICi/` (`source/TX3/TX3.ino` + `build/*.bin`, `*_flashed.bin`).
- GitHub upload skipped (Barney did not want a login on the Pi); checked with `diff` on the Pi instead.
- `diff TX2/TX2.ino TX3/TX3.ino`: only line 17 differs, `SENDER_ID 1` -> `SENDER_ID 2`. The backup source is identical to the checkout copy [HW, file read].

- 19:33 UTC: Barney sent `Pendulum_Firmware_20261120_143233.zip` (Pi sources: TX1, TX2, TX3, Receivermaster). TX1/TX2/TX3 are identical except SENDER_ID 0/1/2 (channel 6, master MAC FC:B4:67:F6:50:F4, 200 Hz). `Receivermaster.ino` + `angle_protocol.h` are byte-identical to ENGT480 main 5c79dca (framed v1, 37-byte frames, `NUM_SENDERS 3`), which is what `PythonMaster3_triple.py` reads (AnglePacketReader). `Receivermaster.ino.backup` is the old 6-byte unframed receiver; the triple script cannot read it [code read].
- 19:41 UTC: the XIAO plugged in for the TX2 reflash has MAC AC:27:6E:7D:42:9C, not the recorded e8:f6:0a:15:1b:48. Barney: TX2 was swapped with a new board. Gave flash commands (`arduino-cli` compile + upload, FQBN `esp32:esp32:XIAO_ESP32C3:CDCOnBoot=cdc`, port `/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_AC:27:6E:7D:42:9C-if00`). Pi `TX2.ino` has SENDER_ID 1.

## Findings
- TX3.ino is correct on its own: same channel, master MAC and encoder code as the working TX2; SENDER_ID 2 = receiver slot 3. Receivermaster (`NUM_SENDERS 3`) accepts IDs 0-2 [code read: ENGT480 main 5c79dca and legacy].
- Risk: TX2 was sending as SENDER_ID 2 (slot 3) since about 2026-11-04 ([open-questions](../../../open-questions.md) resolved row, [gotchas](../../../gotchas.md)). If TX2 was never reflashed, TX2 and TX3 collide in slot 3 [HYP, not checked on the rig].
- `PythonMaster3_triple.py` default `RECEIVER_SLOTS = [1, 3, 2]` assumes joint 2 on slot 3 (TX2 on ID 2). With TX2 on ID 1 and TX3 on ID 2 the triple script needs `--slots 1,2,3`.
- ENGT480 main now has PlatformIO transmitters (`Code/Wireless/Transmitters/src/main.cpp` + `config.tx1.hpp`/`config.tx2.hpp`, with TX1 diagnostics); no `config.tx3.hpp` there yet. The Pi TX3 is built from the legacy ENGT481 `TX2.ino`.
- The backup folder with `*_flashed.bin` suggests TX3 was flashed to a board at 13:53 local [HYP].

## Decisions
- Recommended: keep TX3 = ID 2 (matches repo order), reflash TX2 with the unchanged repo `TX2.ino` (ID 1) if `--check` shows arm 2 on slot 3, then run the triple script with `--slots 1,2,3`. No code changes needed.

## Changed
- Code: none.
- Firmware flashed: TX3 possibly at 13:53 local by Barney [?].

## Open questions and next steps
- Barney: run `PythonMaster3_triple.py --check` with TX3 off and wiggle arm 2; if slot 3 moves, reflash TX2.ino (FQBN `esp32:esp32:XIAO_ESP32C3:CDCOnBoot=cdc`).
- Then `--check --slots 1,2,3` and bend only arm 3 to confirm joint 3's slot and sign.
- Add `config.tx3.hpp` (SENDER_ID 2) to the team repo's PlatformIO transmitters if the team moves TX3 to it.
