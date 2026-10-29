---
updated: 2026-10-29
updated_by: Barney (Claude, new arms model session, correction)
---
# Arms, model, system ID and digital twin

## Arms
- Arm 1: new PLA arm, installed 2026-10-27. ~~3D model estimated from photos ([viewer](https://claude.ai/artifact/AQVKjf288uwtq13xL7B2NK))~~ Superseded 2026-10-29 by [new arms model session](../sessions/2026/10/2026-10-29_1559_Barney_new-arms-model.md): rebuilt from the mechanical team's STLs and measured weights.
- **Mechanical STLs (2026-10-29, from Barney, designed by Vecter Fang):** `arm_1_3dp` (200 mm hinge to tip hole), `arm_2_3dp` (250 mm), `arm_shaft_holder` (608 seat, 4x M3 on the hub), `arm_sensor_mount` (MT6701 board, 2x M3 on the hub), `esp32-mount` (XIAO, holes 30 and 58 mm out), `arm-bat-case` (LP653042), plus `motor-mount`, a bearing removal tool, an unused 165 mm arm and a later 8 mm shaft holder. Arm: 30 mm wide, 8 mm thick, Ø40 hub, Ø22 H7 pocket, 6x M3 on Ø32, Ø8 H7 tip hole with M4 set screw. `arm_1.stp` and drawing `arm_1.pdf` (2026-10-25) also exist; the drawing shows a truss version, the STL is a solid bar. Copies: `/mnt/project-files/NewArmModel_v2/` in the Claude project.
- **Measured weights (Barney, 2026-10-29):** arm_1_3dp 34.5 g (54 % of solid PLA), shaft holder 7.1, sensor mount 5.2, ESP32 mount with XIAO 4.8, battery mount 7.8, 608 bearing 11.8, 8 mm shaft lock 5.5 (old one, new one pending), shaft 100 mm 39.2 g. LiPo and MT6701 board not weighed.
- **How the arms couple (Barney, 2026-10-29):** each arm pivots on its small Ø8 hole (M4 set screw). Arm 1's small hole clamps on the cart shaft (cart side carries TX1). Arm 1's hub (608 in the shaft holder, MT6701, XIAO = TX2, LiPo) is joint 2: the joint-2 shaft runs through that bearing, its magnet sits in arm 1's sensor mount, and it is clamped in arm 2's small hole, so it turns with arm 2. Arm 2 hangs on arm 1's shaft-holder side. Arm 2's hub electronics are for a future joint 3; no shaft there yet. CoM is far from each arm's pivot.
- **Mass properties (model from STLs + weights; single-arm period matches the rig within 3 %):** see [params.md](../params.md#new-arms-mass-properties-stls--measured-weights-2026-10-29). Viewer and downloads: [New Pendulum Arms](https://claude.ai/artifact/8SnLwfoxa9DyULJxHKt21b).
- Arm 2: old second arm.
- The mechanical team is updating the arms; more changes expected.

## Model
- Ratios and their history: [params.md](../params.md).
- The new arm swings almost identically to the old one; existing ratios predict it within about 7 deg at 0.9 s [HW]. The CAD estimate is off by about 32 deg; do not use it. See [decision 0003](../decisions/0003_keep-fitted-model-ratios.md).
- ~~2026-10-29: the STL-based model predicts a hanging period of 0.691 s for arm 1 alone. Rig IDENTIFY periods are 0.84-0.89 s, but it is not recorded which arm and tip load those runs used. See [open-questions.md](../open-questions.md) #10.~~ Superseded 2026-10-29 (same session): the model had the pivot at the hub. Corrected model: 0.830 s with the joint-2 shaft out, 0.858 s with it in, vs rig 0.84-0.89 s.

## System ID
- `PendulumSysID.py`, `analyze_sysid.py`, `apply_sysid.py` (2026-10-16 on rig): within 7% of calculated values; joint friction about 19x the calculated value.
- `PendulumExcite.py` (2026-10-27): endless cart-excitation logger for model fitting; tested only on a simulated rig, then installed at `~/Desktop/GitHub Repository/ENGT481/Code/Single/PendulumExcite`. Code on branch `claude/project-thread-34e9kd` of `TheBarnyard/ChatGPT-Pendulum-Project`. Run `excite_20261027_154016` is bad (arm cable plugged in).

## Digital twin
- Browser page (`Pendulum_Digital_Twin_1.html`, Pyodide) running the repo Python unchanged against emulated firmware (Arduino, ESP32 receiver, TX1/TX2), stepper and nonlinear arms.
- Tuning is by SysID fit plus comparing metrics (arm RMS, cart std, time upright) and robustness sweeps. There is no learning algorithm in it.
- MuJoCo RL is planned after the arms are final; reward terms not yet defined.
