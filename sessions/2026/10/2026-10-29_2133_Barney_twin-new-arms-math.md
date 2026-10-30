---
type: session
date: 2026-10-29
time: 21:33 (UTC)
member: Barney
ai: Claude project thread
topics: [arms-and-model, swing-up, pi-control]
status: done
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
- ~~The twin's double balance file is the 2026-10-26 upload, not the 12.8-minute version; swap in the exact Pi versions.~~ Done 2026-10-30, see below.
- Try the new-arms swing-up plan on the rig [?].

## Proposed page updates
Applied.

## Continued 2026-10-30 02:20 UTC: exact Pi versions
Barney approved reading etwan007/ENGT480 and said the double balance had not changed. Compared against `experiment/legacy-pi-recovery` @ ba019f9 (`LegacyPi/Code/`, the Pi files as of 2026-10-28):
- Single balance: the twin's `PythonMaster_autocalibrate.py` is byte for byte the Pi's `SinglePendulum/PythonMaster_auto.py`. Single swing-up `PythonMasterUpExpClaudeImproved.py` is byte for byte the same. Single helper `angle_packet_fallback.py` swapped to the Pi's (allows 10 misses instead of 2).
- Double balance: Barney is right that the code is the same. `PythonMasterDouble-Claude.py` (= `PythonMaster2_auto_improved.py` on the Pi) differs from the uploaded copy only in its settings: SYSID_RATIOS set (P1 5.22342, P2 2.01257, J2r 0.414023, H 0.394859), 9 ms latency, LQR cart speed 0.3 m/s and accel 1.3 m/s², limits 0.8 m/s and 15 m/s², 0.25 s ramp, 25° start, 5 misses. The twin now runs this file byte for byte. Gains match params.md exactly: K = [-192.219, -4.407, 283.906, 32.818, 20.537, 21.304, 0.418]. On the new arms (twin): 60 s upright, cart within 71 mm [SIM].
- Double swing-up: the Pi's `PythonMaster2_swingup.py` is the newer 2026-10-27 version (PLAN_TRACK 0.25 m, ARM1_PIVOT_FRICTION 0.0009, SWING_CART_M 0.25, MAX_ATTEMPTS 30, RECOVER_GAIN 0.20, STILL_ANGLE_DEG 2.5, its own fitted SYSID_RATIOS and plan). The new-arms copy was redone from it, and the plan was re-made with its own --plan (80 s): 2.5 s, effort 32.3, peak 0.250 m / 0.751 m/s / 8.0 m/s². Catches and balances in the twin (37 s upright of 40 s) [SIM]. Not tried on the rig.
- Twin republished (same link). Math tab double balance lesson and the code map now use the 12.8-minute settings. Build in project files `TwinV3/` (`ctl4/` = current controllers).
