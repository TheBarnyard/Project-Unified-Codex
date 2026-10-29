---
type: session
date: 2026-10-29
time: 15:13 (UTC)
member: Barney
ai: Claude (claude.ai project thread)
topics: [hardware, cart-arduino]
status: done
pages_applied: yes
transcript: none
---
# Add hardware datasheets and pinouts to PUC

## Goal
Store the datasheets and pinouts for every part on the rig in PUC with clear names.

## What happened
- Added `Hardware/Datasheets/` with one folder per part (MT6701, XIAO ESP32-C3, ESP32-WROOM-32, Mega 2560, Raspberry Pi 4B, UIM5756PM motor) and a [README index](../../../Hardware/Datasheets/README.md). 14 files, about 40 MB.
- Also copied the one-page UIM344 wiring diagram from Barney's project files (`Manual_UIM5756PM.pdf`).

## Findings
- Cart motor is a UIM5756PM closed-loop integrated stepper with the UIM344 pulse-direction controller built in (Barney, this session). Default 1.8 deg step, 32 microsteps per the wiring diagram [?] actual DIP/config setting on the rig not checked.
- Pi is a Raspberry Pi 4 Model B, 8 GB (Barney, this session).

## Changed
- PUC: `Hardware/Datasheets/`, INDEX.md, `subsystems/cart-arduino.md`, `hardware-state.md`.

## Open questions and next steps
- Which microstep setting is configured on the UIM344 (affects step-rate to cart-speed scaling).
