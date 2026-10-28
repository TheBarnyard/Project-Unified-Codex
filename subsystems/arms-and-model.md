---
updated: 2026-10-28
updated_by: Barney (Claude, PUC setup session)
---
# Arms, model, system ID and digital twin

## Arms
- Arm 1: new PLA arm, installed 2026-10-27. 3D model estimated from photos ([viewer](https://claude.ai/artifact/AQVKjf288uwtq13xL7B2NK)); pivot to tip hole 200 mm, 608 bearing, 8x100 mm shaft, LP653042 battery in a cage, XIAO at 46 mm. Replace with real STLs when the mechanical team shares them.
- Arm 2: old second arm.
- The mechanical team is updating the arms; more changes expected.

## Model
- Ratios and their history: [params.md](../params.md).
- The new arm swings almost identically to the old one; existing ratios predict it within about 7 deg at 0.9 s [HW]. The CAD estimate is off by about 32 deg; do not use it. See [decision 0003](../decisions/0003_keep-fitted-model-ratios.md).

## System ID
- `PendulumSysID.py`, `analyze_sysid.py`, `apply_sysid.py` (2026-10-16 on rig): within 7% of calculated values; joint friction about 19x the calculated value.
- `PendulumExcite.py` (2026-10-27): endless cart-excitation logger for model fitting; tested only on a simulated rig, then installed at `~/Desktop/GitHub Repository/ENGT481/Code/Single/PendulumExcite`. Code on branch `claude/project-thread-34e9kd` of `TheBarnyard/ChatGPT-Pendulum-Project`. Run `excite_20261027_154016` is bad (arm cable plugged in).

## Digital twin
- Browser page (`Pendulum_Digital_Twin_1.html`, Pyodide) running the repo Python unchanged against emulated firmware (Arduino, ESP32 receiver, TX1/TX2), stepper and nonlinear arms.
- Tuning is by SysID fit plus comparing metrics (arm RMS, cart std, time upright) and robustness sweeps. There is no learning algorithm in it.
- MuJoCo RL is planned after the arms are final; reward terms not yet defined.
