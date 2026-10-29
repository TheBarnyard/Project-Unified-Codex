---
type: session
date: 2026-10-29
time: 14:48 (UTC)
member: Barney
ai: Claude (claude.ai project thread)
topics: [math, swing-up, pi-control]
status: wip
pages_applied: yes
transcript: none
---
# Add a Math teaching folder (single, double, triple)

## Goal
In-depth math pages (variables, equations, derivations, simulations, images, animations) for balance and swing-up of the single, double and triple pendulum, and, for the single first, a direct comparison with our exact code.

## What happened
- Created the `Math/` skeleton with `Single/`, `Double/`, `Triple/` (commit 0fd892b) so Barney could confirm PUC is connected. Barney confirmed, asked for commit messages as `PUC: Ryan - ...`, and set context to `topic`.
- Located the best single swing-up script (named by Barney): `PythonMasterUpExpClaudeImproved.py`, etwan007/ENGT480 branch `experiment/legacy-pi-recovery`, commit ba019f9, `LegacyPi/Code/SinglePendulum/`.
- Found 28 rig runs of that script on the ENGT480 `logs` branch (`raspberrypi-c8674ffe/Code/SinglePendulum/run_logs/balance_202610{16,19,21,27}_*.csv`, config `swing_up_control = identify_then_normalised_energy_pumping`).
- Wrote Math/Single: 10 pages, a simulator of the script's logic, 14 figures, 3 GIFs, compact rig data.

## Findings
- `PythonMasterUpExpClaude.py` and `PythonMasterUpExpClaudeImproved.py` are byte-identical [verified with diff].
- Rig arm w0 is 7.09-7.47 rad/s (period 0.84-0.89 s) in 20 IDENTIFY runs; the code's m, l, I give 5.91 rad/s (1.063 s) [HW]. Identified I 0.00163-0.00189 vs 0.003. Added as open question 9.
- Swing-up after IDENTIFY: median 1.75 s (1.62-3.41 s, 16 runs); 39 catches, energy at catch 0.958-1.066 [HW].
- 23 of 24 LQG→swing-up hand-backs were the 0.22 m cart limit (20 with the arm within 11° of upright) [HW]. Longest LQG stretch 114 s (balance_20261027_150517).
- The motor gets the Kalman estimator's cart-speed state, not the LQR force: the force only drives the estimator prediction (a "virtual cart" integrator). M and b_c act as controller parameters.
- `ctrl.dlqe` returns the predictor gain A·M; the code applies it as a filter-form correction. Stable (error poles 0.005, 0.015, 0.984±0.006j) [SIM]; not textbook.
- The ×2 on the LQR force moves the fastest closed-loop pole from z = 0.859 to 0.611 [SIM].
- Arduino Timer3 real step rate is 125000/(N+1), not 125000/N; with int() rounding the cart runs 1-3 % slow at 0.6-0.8 m/s.
- 1° of angle offset parks the cart 8.3 cm off centre under LQG; auto-trim removes it (0.35° on 2026-10-16 run [HW]).

## Decisions
- None by the team. Original code not edited.

## Changed
- PUC only: Math/ folder, params.md, open-questions.md (7 updated, 9 new), subsystems/swing-up.md, subsystems/pi-control.md, members.md (Ethan's surname from git), INDEX.md.

## Open questions and next steps
- Double and Triple math pages (in progress in this session).
- Which of m, l, I is wrong for the single arm (open question 9).
