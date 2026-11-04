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
