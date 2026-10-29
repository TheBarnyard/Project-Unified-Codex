---
type: session
date: 2026-10-29
time: 21:33 (UTC)
member: Barney
ai: Claude project thread
topics: [arms-and-model, swing-up, pi-control]
status: wip
pages_applied: yes
transcript: none
---
# Digital twin v3: new arms, 4 controllers, Math and Math-in-code tabs

## Goal
Update the browser digital twin to the new arms, keep only the 4 important controllers (single balance, double balance, single swing-up, double swing-up), and add tabs that teach the math interactively and map it to our code, assuming no trig or calculus.

## What happened
- Updated the existing twin artifact in place (same link): https://claude.ai/artifact/27Ekbq9KoELfP2hwoJJZir (v3, published 2026-10-29).
- Twin plant now uses the new arms from the [new-arms model session](2026-10-29_1559_Barney_new-arms-model.md): arm 1 98.1 g, CoM 147.8 mm, J(pivot) 2.48e-3 kg m²; arm 2 161.8 g, CoM 128.9 mm, J 4.51e-3 kg m². The 25 mm gap between the arms is a guess [?]. Old arms and the fitted model remain as presets.
- Controllers kept (Run tab): `SinglePendulum/PythonMaster_autocalibrate.py` (balance), `SinglePendulum/PythonMasterUpExpClaudeImproved.py` (swing-up), `DoublePendulum/PythonMaster2_auto_improved.py` (balance), `DoublePendulum/PythonMaster2_swingup_newarms.py` (swing-up, copy). Originals unchanged; the swing-up copy only changes ARM1/ARM2, sets SYSID_RATIOS = None and loads `double_swingup_trajectory_newarms.json`.
- New tabs: "Math" (16 interactive lessons: angles, ticks, twist, inertia, steps, cart, line model, LQR, Kalman, energy, pumping, two arms, double balance, plan, motor timer) and "Math in our code" (13/11/12/11 step line-by-line maps for the 4 scripts, each step links to its lesson and to the simulator).
- Build scripts, controller copies and tests saved to project files `TwinV3/`.

## Findings
- New-arms ratios: P1 5.233, P2 2.329, J2r 0.503, H 0.466 [SIM].
- New-arms double swing-up plan (T 2.5 s, 251 knots, same limits 0.30 m / 0.75 m/s / 8 m/s²): peak track 0.280 m, speed 0.753 m/s, accel 8.0 m/s². Catches and balances in the twin [SIM]. Not tried on the rig.
- Single swing-up identifies a 0.828 s period with the new arm 1 and catches [SIM] (model predicts 0.830 s).
- Single balance (`PythonMaster_autocalibrate.py`) holds but the cart drifts to about +0.245 m; the same happens with the old arms, so it is the script with the twin's encoder offset, not the new arm [SIM].
- Double balance holds [SIM].

## Dead ends
- none

## Decisions
- Kept the original `PythonMaster2_swingup.py` (hidden) and added a new-arms copy instead of editing it - Barney's rule: never edit original code.

## Changed
- Code: none in team repos. Twin artifact v3 (link above). Files: project files `TwinV3/`.
- Firmware flashed: none
- Wiring or hardware: none
- Run logs: none

## Open questions and next steps
- The twin's double balance file is the 2026-10-26 upload (old arm values, 6 ms, 1.5 m/s²), not the 12.8-minute 2026-10-21 version. Swap in the exact Pi versions from etwan007/ENGT480 (waiting for Barney's OK to read the repo), then rebuild.
- Confirm which single balance script is "the one" (twin uses `PythonMaster_autocalibrate.py` from main @ e8f82ea).
- Try the new-arms swing-up plan on the rig [?].

## Proposed page updates
Applied.
