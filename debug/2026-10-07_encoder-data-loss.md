---
type: debug
status: parked
opened: 2026-10-07
by: Barney (Claude)
subsystems: [receiver, encoders-and-transmitters, pi-control]
---
# Encoder data loss and startup junk

## Symptoms
Bad or jumping angles on the Pi; junk bytes when the controller starts.

## Chain
MT6701 > I2C > XIAO ESP32-C3 > ESP-NOW > ESP32-WROOM receiver (CP2102) > USB serial > Pi.

## Tests and results
- Encoder, radio and receiver logic looked healthy [HW].
- Test A: junk appears only right after the port opens when it had been closed 5+ s (about 60% of opens), as one 32-byte chunk replayed byte for byte. The ESP32 never resets on open [HW].
- Test B: port held open, arm moving: clean [HW].
- Test C: framed firmware (`FramedReceiverMaster`, 11-byte frame with CRC) plus `encoder_link.py`: 0 CRC failures, replayed chunk caught [HW].

## Cause (best current understanding)
- Startup junk: CP2102 / USB host artifact on port open [HYP]. Production's 3 s wait plus flush probably hides it.
- Bad angles in production: the 6-byte unframed format plus `reset_input_buffer()` on every read, which can split packets [HYP]. Lead suspect.

## Outcome
Framed firmware worked, then Barney asked to revert everything ([decision 0001](../decisions/0001_revert-framed-receiver.md)). The ENGT480 team later added a framed receiver protocol v1 ([receiver](../subsystems/receiver.md)).

## Dead ends
- None of the radio or encoder logic was at fault.

## Files
- Full record: `Encoder_Data_Loss_Complete_Debugging_Record.md` (Barney's Claude project files). [?] copy into PUC if the team wants it.
- Framed test sketch: `~/encoder_debug` on the Pi.
