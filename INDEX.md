# PUC index

Every page in PUC, one line each. Add new pages here.

## Top level
- [BRIEF.md](BRIEF.md): current state of the project
- [direction.md](direction.md): goals, deadlines, priorities
- [members.md](members.md): team, ownership, AI tools, PUC preferences
- [hardware-state.md](hardware-state.md): what is on the rig right now
- [params.md](params.md): key constants and settings, with conflicts
- [gotchas.md](gotchas.md): traps that cost time
- [open-questions.md](open-questions.md): unresolved questions and conflicts

## Subsystems
- [subsystems/encoders-and-transmitters.md](subsystems/encoders-and-transmitters.md): MT6701 encoders, XIAO ESP32-C3 TX1/TX2, ESP-NOW
- [subsystems/receiver.md](subsystems/receiver.md): ESP32-WROOM receiver to Pi serial link and packet formats
- [subsystems/cart-arduino.md](subsystems/cart-arduino.md): Mega 2560 stepper cart driver
- [subsystems/pi-control.md](subsystems/pi-control.md): Raspberry Pi LQG balance controllers
- [subsystems/swing-up.md](subsystems/swing-up.md): single and double swing-up
- [subsystems/arms-and-model.md](subsystems/arms-and-model.md): arms, model ratios, system ID, digital twin, MuJoCo
- [subsystems/repos-and-pi-workflow.md](subsystems/repos-and-pi-workflow.md): repos, branches, Pi checkouts, logs branch, run logs

## Hardware
- [Hardware/Datasheets/README.md](Hardware/Datasheets/README.md): datasheets, pinouts and manuals for every rig part (MT6701, XIAO ESP32-C3, ESP32-WROOM-32, Mega 2560, Pi 4B, UIM5756PM motor)

## Math
- [Math/README.md](Math/README.md): teaching pages for the math behind balance and swing-up
- [Math/Single/README.md](Math/Single/README.md): single pendulum math and code comparison
- [Math/Double/README.md](Math/Double/README.md): double pendulum math
- [Math/Triple/README.md](Math/Triple/README.md): triple pendulum math

## Debug records
- [debug/2026-10-07_encoder-data-loss.md](debug/2026-10-07_encoder-data-loss.md): bad angles and startup junk on the receiver link
- [debug/2026-10-27_angle-dropouts.md](debug/2026-10-27_angle-dropouts.md): ANGLE1_MISSING dropouts (TX1 power) and TX2 never received
- [debug/2026-10-27_double-swingup-aborts.md](debug/2026-10-27_double-swingup-aborts.md): double swing-up aborts on the rig (cart speed cap)

## Decisions
- [decisions/0001_revert-framed-receiver.md](decisions/0001_revert-framed-receiver.md): framed receiver firmware reverted to original (2026-10-07)
- [decisions/0002_tx1-power-from-5v.md](decisions/0002_tx1-power-from-5v.md): TX1 powered from Mega 5 V instead of 3.3 V (2026-10-27)
- [decisions/0003_keep-fitted-model-ratios.md](decisions/0003_keep-fitted-model-ratios.md): keep fitted ratios, not the CAD arm estimate (2026-10-27)
- [decisions/0004_work-in-copies.md](decisions/0004_work-in-copies.md): never edit original source files; work in copies (2026-10-07)

## Other
- [templates/](templates/): session, debug, decision, subsystem templates
- [prompts/](prompts/): start and end prompts for ChatGPT and other AIs without git
- [tools/claude-skill/SKILL.md](tools/claude-skill/SKILL.md): the PUC skill for Claude
