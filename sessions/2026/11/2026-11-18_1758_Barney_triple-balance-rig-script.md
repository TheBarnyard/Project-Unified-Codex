---
type: session
date: 2026-11-18
time: 17:58 (UTC)
member: Barney
ai: Claude project thread
topics: [arms-and-model, controllers]
status: wip
pages_applied: yes
transcript: none
---
# Triple balance script for the rig (PythonMaster3_triple.py), checked on a simulated rig

## Goal
Barney will be at the rig about 2-3 h after 17:58 UTC to test the triple standing (and maybe the swing-up) and asked for the Pi code, and whether more training was needed first.

## What happened
- Answer to "more training first?": no. The RL policies are not rig-ready (cart 1.4 m/s, ~90 m/s²; the motor stalls at 16-18 m/s² reversals). Recommended today: triple balance with the team's own control structure, plus a 2 min free-swing log to measure arm 3. Swing-up later, after an arm 3 fit (the double swing-up has not caught on the rig yet).
- Built `PythonMaster3_triple.py` (new file; team files unchanged): `PythonMaster2_auto_improved.py` written for three arms. Physical arm model (mass, CoM, inertia per arm) from `RL_Triple_V2/model/params.json` 'triple' (arms 1-2 = the 2026-11-04 V2 fit; arm 3 = arm 2 stretched 50 mm with hub electronics [HYP]); LQR on [x; a_prev] with the 9 ms delay, steady Kalman filter, auto-trim of three references, same Arduino/receiver protocol and CSV logger.
- Modes: `--check` (motor off, live slots and angles to confirm the joint-2/joint-3 slots and joint 3's sign), `--log SECONDS` (free swings, motor holds the cart, CSV for fitting arm 3), `--countdown 3` (motor holds the cart, counts down, starts at GO so one person can hold the arms with both hands), `--slots` (default 1,3,2 = arm1, joint2, joint3; guess), `--joint3-sign`, `--arm3 full|bare`, `--arm3-mass-g/--arm3-com-mm/--arm3-period-s`, `--offsets`, `--accel-max`, `--latency-ms`, `--design-only`.
- New harness `TripleBalance/tools/fake_rig.py`: runs the unchanged script on a virtual clock with fake serial ports (nlink_cart triple plant, receiver protocol v1 frames, the 2026-11-04 rig-fitted FIFO radio model, Arduino command/reply timing, a simulated hand). About 50 cases (`tools/batch.py`, results `tools/batch_results.txt`, summary `SIM_RESULTS.md`).
- Delivered: `TheBarnyard/ChatGPT-Pendulum-Project` branch `claude/project-thread-8o7nnj`, `TripleBalance/`, commit dab0289 (pinned raw-URL install tested; SHA256SUMS in the folder); project files `TripleBalance/`. Pi folder `~/Desktop/TripleBalance`.

## Findings
- Gains for the V2 triple: cart acceleration per degree of lean +6.8 (arm 1), -18.0 (arm 2), +14.2 (arm 3) m/s²; fall time constants 65, 119, 232 ms [SIM].
- The script holds with clean radio, +2..+6 ms extra delay, arm 3 mass x0.8/x1.2, arm 3 CoM ±20 mm, a "bare" arm 3, arm 3 inertia x0.85..x1.4, arm 2 mass +15 % [SIM]. Arm 3 inertia x0.8 falls [SIM].
- Start catch (others upright): arm 1 up to 4°, arm 2 or arm 3 up to 1.5°; 2° or a 1/-1/1° pattern falls [SIM]. With `--countdown`, letting go 0.05 s early or on GO caught, 0.1 s early or 0.05 s late fell [SIM, crude hand model].
- Rig-like radio: with the double's filter settings (3 counts, stale readings used) it fell after a median 22 s (0 of 8 held 60 s). Skipping readings the receiver already sent (age >= 10 ms), moving fresh ones forward by (age - 3 ms) x estimated speed, and 6 counts of encoder noise after the first 2 s: 6 of 8 held 60 s, 2 stopped at 43 s on a TX1 gap > 80 ms (safety stop) [SIM]. Without the age correction: median 19.5 s; designed delay 10 ms: no help [SIM].
- Encoder reference errors are the triple's weak spot: steady cart offset = K_theta·delta / K_x (K_x only -18 per m), e.g. 246 mm for 0.3/-0.2/0.2° (arm1/joint2/joint3). Held: 0.1/-0.1/0.1, 0/0.15/-0.15, 0/-0.2/0, 0/0/0.25, 1/0/0, 0.5/-0.1/0.1; fell: -0.2/0.2/-0.2, 0.3/-0.2/0.2 [SIM]. For a rigid planar chain the hanging calibration is exact in theory (hanging and inverted equilibria share the first-moment directions), so real errors come from arms not settled, stiction and encoder nonlinearity (arm 1 only, 180° apart) [HYP].

## Dead ends
- Stiffer cart weight (LQR_CART_M 0.02-0.03 m) to shrink the zero-error drift: loses the 1.5° arm 3 catch and the arm 3 inertia x0.85 margin [SIM].
- Faster auto-trim (1 s) destabilises; 2 s does not help (the drift fails in 1-2 s) [SIM].
- Encoder noise 6 counts from the start: loses the 1.5° arm 3 catch and the countdown -0.05 s case, hence 3 counts for the first 2 s [SIM].
- Auto-start when the arms enter a 2° window: the cart starts under arms still held by the hand; replaced by the countdown [SIM].

## Decisions
- Triple balance only today; swing-up after the arm 3 fit (Claude's recommendation, 2026-11-18).
- Track soft limit 0.40 m (double 0.30 m), hanging stillness 25 counts (double 80), per-angle 8-frame miss limit, no start ramp, upright check 3 frames.

## Changed
- Code: ChatGPT-Pendulum-Project / claude/project-thread-8o7nnj / TripleBalance/ / dab0289.
- Firmware, wiring: none.
- Run logs: none yet.

## Open questions and next steps
- Barney's rig results: which slots joints 2 and 3 are on, joint 3's sign, whether it balances, the printed trims, and the free-swing CSV (`run_logs/freeswing_triple_*.csv`) to fit arm 3.
- Barney 2026-11-18 19:29 UTC: arm lengths 200, 250, 300 mm, and all parts on arm 3 sit at the same distance from the FAR end as on arm 2 (not the pivot end) [HW, Barney]. This matches the model's arm 3 (arm 2 design stretched 50 mm, hub parts moved 50 mm out, `--arm3 full`), so no change to the script. Arm 3's weight is still a guess (169.9 g).
- Still unanswered: arm 3 weight, how joint 3 reaches the Pi (TX3 slot), whether arm 2 is the 250 mm arm with the joint-3 shaft, which double script runs on the Pi now.
- The radio model is from 2026-11-04; radio changes since then are unknown.
