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
- [Math/Single/README.md](Math/Single/README.md): single pendulum math and code comparison (start here)
  - [01 variables](Math/Single/01_variables.md), [02 equations of motion](Math/Single/02_equations_of_motion.md), [03 linear model](Math/Single/03_linear_model.md), [04 LQR](Math/Single/04_lqr.md), [05 Kalman/LQG](Math/Single/05_kalman_lqg.md), [06 sensing and actuation](Math/Single/06_sensing_actuation.md), [07 swing-up](Math/Single/07_swing_up.md), [08 balance vs swing-up](Math/Single/08_balance_vs_swingup.md), [09 code walkthrough](Math/Single/09_code_walkthrough.md), [10 simulations and rig results](Math/Single/10_results.md), [sims](Math/Single/sims/README.md)
- [Math/Double/README.md](Math/Double/README.md): double pendulum math, balance and planned swing-up, every gain checked against the team's scripts, all 35 rig swing-up attempts
  - [01 variables](Math/Double/01_variables.md), [02 equations of motion](Math/Double/02_equations_of_motion.md), [03 linear model](Math/Double/03_linear_model.md), [04 balance](Math/Double/04_balance.md), [05 swing-up](Math/Double/05_swing_up.md), [06 balance vs swing-up](Math/Double/06_balance_vs_swingup.md), [07 simulations and rig results](Math/Double/07_results.md), [sims](Math/Double/sims/README.md)
- [Math/Triple/README.md](Math/Triple/README.md): triple pendulum math on an assumed rig (double + a third arm) [HYP][SIM]
  - [01 model](Math/Triple/01_model.md), [02 linear model](Math/Triple/02_linear_model.md), [03 balance](Math/Triple/03_balance.md), [04 swing-up](Math/Triple/04_swing_up.md), [05 comparison](Math/Triple/05_comparison.md), [sims](Math/Triple/sims/README.md)
- [Math/shared/README.md](Math/shared/README.md): n-link model, LQR, Kalman, swing-up planner, TV-LQR and the scripts' control loops in Python (used by Double and Triple)

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
- [SETUP-CHATGPT.md](SETUP-CHATGPT.md): step-by-step setup guide for teammates using ChatGPT
- [prompts/](prompts/): start and end prompts for ChatGPT and other AIs without git
- [tools/claude-skill/SKILL.md](tools/claude-skill/SKILL.md): the PUC skill for Claude
