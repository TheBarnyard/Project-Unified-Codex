---
updated: 2026-10-28
updated_by: Barney (Claude, PUC setup session)
---
# Receiver and Pi serial link

An ESP32-WROOM (CP2102 USB bridge) receives ESP-NOW packets from TX1 and TX2 and sends the angles to the Pi on `/dev/ttyUSB0` at 921600 baud, 100 Hz.

## Packet formats
- **Original (ENGT481):** 6-byte unframed packet of three 16-bit angles; 0xFFFF marks a stale angle. Used by `PythonMaster.py` and `CommunicationTest.py`.
- **Receiver protocol v1 (ENGT480):** framed, documented in `Code/Wireless/ANGLE_PROTOCOL.md` with `angle_protocol.h` / `angle_protocol.py`. Needed by the `*_autocalibrate` controllers and by PendulumExcite. Carries per-channel status, sequence numbers and radio age.
- **Framed test firmware (2026-10-07, not in use):** `FramedReceiverMaster` with an 11-byte frame (AA 55, seq, 3x u16, CRC-16/CCITT-FALSE). Worked on hardware, then reverted. See [decision 0001](../decisions/0001_revert-framed-receiver.md).

Which one is flashed now: [?] see [open question 5](../open-questions.md).

## Variants
- `Code/Wireless/ESP32_Code/Receivermaster`: production.
- `DebugReceiverMaster`: debug variant at 115200 baud.

## History
- 2026-10-07: data-loss investigation. [debug](../debug/2026-10-07_encoder-data-loss.md)
- 2026-10-27: radio age is measured on the receiver, so Pi load cannot cause dropouts. [debug](../debug/2026-10-27_angle-dropouts.md)
