---
updated: 2026-10-30
updated_by: Ryan (Claude, rl-double-newarms session)
---
# Project brief

Where the ENGT 480 pendulum project stands right now. Keep this under about 150 lines; details go in the linked pages.

## The rig in one paragraph

A cart on a rail is driven by a stepper motor through an Arduino Mega 2560. One or two pendulum arms hang from the cart. Each arm joint has an MT6701 magnetic encoder read by a Seeed XIAO ESP32-C3 transmitter (TX1, TX2), which sends angles over ESP-NOW at 200 Hz to an ESP32-WROOM receiver. The receiver forwards angles to a Raspberry Pi 4 over USB serial at 921600 baud (100 Hz). The Pi runs the controllers: LQG balance (Kalman filter + LQR) and swing-up. Details: [subsystems/](INDEX.md#subsystems).

## Best results so far

- Single pendulum balance: 22.8 min on 2026-10-14 [HW].
- Double pendulum balance: 12.8 min on 2026-10-21 with `PythonMaster2_auto_improved.py` [HW].
- Double swing-up: catches in the digital twin [SIM] (also with the new arms, 2026-10-29: [twin v3](https://claude.ai/artifact/27Ekbq9KoELfP2hwoJJZir)); fails on the rig so far.

## Current state (2026-10-28)

- **Double swing-up on the rig:** every attempt aborts around step 110 to 200 of 250. Latest lead: the cart gets stuck at about 0.83 m/s because the torque limit is smaller than one stepper timer step. A slower plan (PLAN_SPEED 0.60) was sent 2026-10-28, untested on the rig. 2026-10-29 [SIM]: a longer 3.5 s plan with the same limits survives about twice as many model errors; ready to try in `Math/Double/data/`. See [debug/2026-10-27_double-swingup-aborts.md](debug/2026-10-27_double-swingup-aborts.md).
- **Angle dropouts:** likely fixed by powering TX1 from the Mega 5 V instead of 3.3 V (2026-10-27). A 20+ min controller run to confirm is still pending. See [debug/2026-10-27_angle-dropouts.md](debug/2026-10-27_angle-dropouts.md).
- **TX2 (angle 2):** working since 2026-10-27 after reflashing the repo `TX2.ino`; the old firmware on it was wrong.
- **New arm 1 (PLA):** installed. The fitted model ratios still match it; the old photo-based estimate does not. 2026-10-29: arms rebuilt from the team's STLs and measured weights. Arm 1: 98.1 g, CoM 147.8 mm from its pivot (small hole), Izz pivot 2.48e-3 kg m²; predicted hanging period 0.83-0.86 s vs rig 0.84-0.89 s. See [subsystems/arms-and-model.md](subsystems/arms-and-model.md).
- **Unified launcher (`pendulum.py`):** design only, no code yet.
- **MuJoCo / RL:** double balance + double swing-up training folder on the new arms, 2026-10-30 (project files `RL_DoubleNewArms/`). Double balance solves in sim [SIM]; swing-up training is up to Barney's PC. See [subsystems/arms-and-model.md](subsystems/arms-and-model.md).
- **Gate Report 2:** drafted 2026-10-26.
- **PUC:** this codex was set up 2026-10-28.
- **Math teaching pages:** [Math/](Math/README.md) for single, double (both checked against the team's scripts) and triple (assumed rig), 2026-10-29.

## Where things live

- Team code and run logs: `etwan007/ENGT480` (`main`, experiment branches, `logs` branch). See [subsystems/repos-and-pi-workflow.md](subsystems/repos-and-pi-workflow.md).
- Barney's Claude work branches: `TheBarnyard/ChatGPT-Pendulum-Project`.
- Some scripts exist only on the Pi in the legacy `~/Desktop/GitHub Repository/ENGT481` checkout. See [open-questions.md](open-questions.md).

## Read next

[direction.md](direction.md) · [hardware-state.md](hardware-state.md) · [params.md](params.md) · [gotchas.md](gotchas.md) · [open-questions.md](open-questions.md)
