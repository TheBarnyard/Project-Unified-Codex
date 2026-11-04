---
type: session
date: 2026-11-04
time: 10:12 (local)
member: Barney
ai: Claude project thread
topics: [arms-and-model, swing-up]
status: wip
pages_applied: yes
transcript: none
---
# V2 arms model fit from excite_20261104_093436

## Goal
Make the double simulation match the two V2 arms, so swing-up paths can be planned and compared before the next rig visit.

## What happened
- Barney ran PendulumExcite (`/home/engt481/DoubleExcite.py`, same code as 2026-10-27) for 2139 s with both V2 arms. The log `excite_20261104_093436` (Pi `/home/engt481/run_logs/`) was uploaded as a tar.xz without `esp32_raw.bin`. Arm 2 was on receiver slot 3 because TX2 was sending as ID 2; `arm2_abs_deg` is correct.
- Fitted the swing-up script's model `f(z, a, r)` with a simulation-error fit on 1 s windows (logged `v_sent` as instant speed jumps, start rates corrected per window), then validated on held-out windows of 0.5 to 3 s.

## Findings
- Fitted ratios (V2 arms): P1 5.2253, P2 2.0148, J2r 0.4506, H 0.4027, B1 0.0182, B2 0.0138 [HW].
- Held-out median RMS error arm 1 / arm 2: 0.5 s 1.2 / 2.0 deg; 3 s 1.7 / 2.7 deg. Older sets at 3 s: sysid 2026-10-27 5.0 / 7.9, swingfit 2026-10-27 5.8 / 8.4, STL model 9.1 / 12.5 deg [HW].
- H/P2 = 0.200 m equals arm 1's joint distance, which supports the fit.
- The STL model gets P1 right but its arm-2 terms are 12 to 16 % high [HW].
- Angle sign: theta = pi + arm_abs. Command latency is about 0 ms: the best fit was at 0 in a scan from -45 to +30 ms.
- Adding Coulomb friction and air drag improves it only slightly (3 s: 1.6 / 2.5 deg).
- Joint 2 friction B2 0.014 is much lower than the 0.114 fitted from the 2026-10-27 swing-up runs, which used the old arm 2 [HW].
- Coverage is limited: the cart stayed within +/-0.15 m, 0.54 m/s and 5.4 m/s². Only 8 test windows had arm 2 above 120 deg (error 4 / 9 deg there). Arm 2 spinning over the top is chaotic past about 1 s.

## Dead ends
- A first-order cart lag of 5 to 40 ms gives no consistent improvement.
- 2 s fitting windows get stuck when arm 2 goes chaotic; 1 s windows fit reliably.

## Decisions
- None yet. Barney still has to choose these ratios for the next plan.

## Changed
- Code: `TheBarnyard/ChatGPT-Pendulum-Project` branch `claude/project-thread-74rdr9`, `V2ArmsFit/` (fitlib.py, final.py, results, figure, log tar.xz), commit 82274d1.
- Run logs: `excite_20261104_093436` (copy in `V2ArmsFit/` and Claude project files `V2ArmsFit/`).

## Open questions and next steps
- Barney is leaving the rig until the swing-up test. Barney was asked to measure the cart travel from centre to each limit switch ([open question 6](../../../open-questions.md)), to report the swing-up script's sha256, to decide whether to reflash TX2 to ID 1, and to unplug the arm LiPos.
- ~~Next: plan candidate double swing-up paths with these ratios and compare them in simulation.~~ Done 17:40 UTC (style gallery, see update below).

## Update 17:40 UTC: swing-up style gallery [SIM]
- Barney asked for GENERAL double swing-up styles to choose a look before detailed planning.
- Planned 120 swing-ups with the V2 fit (CasADi/IPOPT, `Math/shared/nlink_cart.plan_team`). Limits: |x| ≤ 0.30 m, |v| ≤ 0.75 m/s, |a| ≤ 8 m/s², motor top speed 1.0 m/s, cost ∫a²dt. They cover 4 arrival styles (same way up, folded/opposite, whip = arm 2 makes 1.5 turns, counter-whip), 2.5 to 5.0 s, and different cart pump counts. 88 were feasible and 69 are unique.
- 2.5 s plans do not fit these limits with the V2 arms (best got 87.5 % of the way, needing about 0.9 m/s). The shortest feasible is 3.0 s in every style.
- Each plan was checked closed-loop with the team's TV-LQR loop (`Math/shared/swing_sim`) under 11 model errors (±4 % on each ratio, B2 ×0.5/×2, B1 ×2) plus nominal. Every plan catches at nominal. The best catch all 12: same way up 3.5 s, 4.0 s and 4.5 s. The 3.0 s plans are less tolerant (5 to 10 of 12).
- Gallery: [Double Swing-Up Styles](https://claude.ai/artifact/WJcTh1yAmw7quvpkzteU65). Files are in Claude project files `SwingUpStyles/`.
- Next: Barney picks a style, then a rig plan is made for the measured track and in the script's trajectory format.

## Update 18:05 UTC: code for 7 chosen swing-ups [SIM]
- Barney picked same way up 3.0 s (5 rev), 3.5 s, 4.0 s (6 rev); whip 4.5 s (6 rev), 3.5 s (4 rev), 3.0 s (5 rev); folded 4.5 s (7 rev). The only 3.5 s same-way-up plan has 6 reversals, not 5.
- Built `PythonMaster2_swingup_V2.py` (copy; original unchanged) plus 7 plan files, checked with the script's own `plan_problem`/`load_trajectory` (mismatch below 1e-9) and on the digital twin with the exact script (results in [subsystems/swing-up.md](../../../subsystems/swing-up.md)).
- Delivered: `TheBarnyard/ChatGPT-Pendulum-Project` `claude/project-thread-74rdr9` `DoubleSwingUp_V2/` (commit 9949265), with Pi install commands that use a commit-pinned raw URL (the branch raw URL served stale files for a few minutes after a push). Also in Claude project files `DoubleSwingUp_V2/` (zip).
- Next: first rig run with `--path same_4.0s`. Track check still needed: plans reach ±300 mm, abort at 360 mm.

## Update 18:40 UTC: simulation visuals for the 7 paths [SIM]
- Barney asked for visuals of the simulations with the updated model, one per path with its name.
- Recorded one closed-loop digital-twin run per path (exact `PythonMaster2_swingup_V2.py`, emulated Arduino/receiver/TX1/TX2/stepper, fitted V2 arms) at nominal and with two arm-2 errors the script does not know about (inertia +10 %, mass -4 %).
- Nominal: all 7 catch on the first try, catch at swing start + T. Max tracking error in the first swing: same 3.0/3.5/4.0 s 1.0/0.8/1.0 deg, whip 3.0/3.5/4.5 s 2.4/1.4/1.7 deg, folded 2.6 deg.
- Arm 2 inertia +10 %: same_3.5s and same_4.0s still catch; same_3.0s, all whips and folded abort and retry without catching.
- Arm 2 mass -4 %: all same-way-up plans and whip_3.5s catch; whip_3.0s and folded abort; whip_4.5s catches but loses it after 0.09 s.
- Gotcha for the twin harness: the twin keeps running after the script's run time ends, so the arms fall at about 13.9 s (13 s run) and 26.9 s (26 s run). The visuals are cut there; it is not a balance failure.
- Page: [V2 Swing-Up Simulations](https://claude.ai/artifact/ALjwSAhuB8Vr3RKMJCCFU5) (bench with twin vs plan plots, 7 synced cards, case selector). GIFs per path and `all_7_paths.gif` in Claude project files `DoubleSwingUp_V2/visuals/` (scripts in `tools/`).

## Update 19:10 UTC: 3D version of the visuals [SIM]
- Barney asked for the simulations in the look of the 3D arm model (Rev C viewer, [new arms model](https://claude.ai/artifact/8SnLwfoxa9DyULJxHKt21b)).
- Page: [V2 Swing-Up in 3D](https://claude.ai/artifact/FSBrxtu7MeNzcgHL4LMWrU). The Rev C GLB arms on a cart and rail, posed from the same twin runs; path picker by name, "All 7" side by side, plan as see-through orange arms, arm-model cases, twin vs plan plots.
- Kinematics used: arm 1 rotation about the hinge = pi/2 - theta1, arm 2 at (200, 0, 25) mm in arm 1's frame with relative rotation theta1 - theta2 (script angles, from upright, positive toward +x). Arm 2's 25 mm offset is still assumed.
- 3D GIFs per path (`<path>_3d.gif`, `all_7_paths_3d.gif`) and build scripts in Claude project files `DoubleSwingUp_V2/visuals/` (`tools3d/`).

## Update 20:15 UTC: track length measured [HW]
- Barney: about 1080 mm from limit switch to limit switch, so about ±540 mm from the middle if the cart starts centred (the scripts measure cart position from where it starts).
- Against the V2 settings: plans reach ±300 mm, the swing aborts at 360 mm, the motor stops for good at 400 mm (TRACK_SOFT_LIMIT_M). That leaves about 140 mm minus half the cart width beyond the soft limit, so the current plans and limits fit with margin. Braking from 0.75 m/s at 8 m/s² takes about 35 mm.
- Keep the cart within about ±50 mm of the middle when starting: an off-centre start eats the margin on one side.
- Open: whether 1080 mm is between the switch trip points or the cart's own travel (half the cart width matters only in the first case). The extra track would allow plans with PLAN_TRACK_M up to about 0.40 m if wanted (not done).

## Update 20:35 UTC: angle diagnostic in the swing-up folder
- Barney is at the rig and wanted the angle diagnostic next to the swing-up script. Added `AngleSensorDiagnostic.py` (unchanged copy of the Pi's `LegacyPi/Code/SinglePendulum/AngleSensorDiagnostic.py`, ba019f9, sha256 8516940a…) to `TheBarnyard/ChatGPT-Pendulum-Project` `claude/project-thread-74rdr9` `DoubleSwingUp_V2/` (commit a6c3a65). It imports `angle_protocol.py`, which is identical to the copy already in that folder. Pi folder: `~/Desktop/DoubleSwingUpV2`.

## Update 20:45 UTC: first rig run of the V2 swing-up [HW]
- Run `swingup_double_20261104_153309_280984.csv` (Pi `~/Desktop/DoubleSwingUpV2/run_logs/`), `--path same_4.0s`. ARM2_CHANNEL auto found the joint encoder on slot 3. Calibration: arm 1 hanging 4703 counts (upright 12895), arm 2 aligned 14518.
- 5 attempts, no catch. Aborts: 36 deg off the plan at 1.62 s, 40 deg at 2.89 s, 36 deg at 2.48 s, 37 deg at 3.42 s, then cart at -362 mm at 2.08 s (it coasted to -386 mm).
- From the console lines: in every attempt the arms and cart follow the plan within about 3 deg and 5 mm for the first 1.6 s. Then the cart falls behind the plan (attempt 4: 33 mm at 2.13 s, 119 mm at 2.64 s) and arm 2 drifts off. The feedback reaches CART_ACCEL_MAX 16 m/s² at about 1.5 s. In attempt 2 the cart sat at +0.81 m/s with a = 0, which looks like the 0.83 m/s stepper speed cap seen on 2026-10-28 [HYP].
- Stop: `RuntimeError: 6 unusable angle frames in a row`, angle3 (TX2) wireless_timeout, radio_age 102 ms, right after attempt 5's abort.
- Next: CSV requested from Barney to check the speed cap and refit the model on the swing data.
