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
- Barney is leaving the rig until the swing-up test. He was asked to measure the cart travel from centre to each limit switch ([open question 6](../../../open-questions.md)), to report the swing-up script's sha256, to decide whether to reflash TX2 to ID 1, and to unplug the arm LiPos.
- Next: plan candidate double swing-up paths with these ratios and compare them in simulation.
