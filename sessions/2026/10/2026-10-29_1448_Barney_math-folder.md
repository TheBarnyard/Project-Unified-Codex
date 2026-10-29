---
type: session
date: 2026-10-29
time: 14:48 (UTC)
member: Barney
ai: Claude (claude.ai project thread)
topics: [math, swing-up, pi-control, arms-and-model]
status: done
pages_applied: yes
transcript: transcripts/2026/10/2026-10-29_1448_Barney_math-folder.md
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

## Part 2: Double and Triple (2026-10-29 afternoon)
- Wrote Math/Double: 7 pages (variables, equations, linear model, balance, swing-up, balance vs swing-up, results), shared n-link code `Math/shared/` (`nlink_cart.py`, `swing_sim.py`), sims, 12 figures, 3 GIFs, rig data extracts. Pushed a0a2d88.
- Wrote Math/Triple: 5 pages on an assumed rig (double + a copy of arm 2 on top) [HYP], sims, plans, 11 figures, 2 GIFs.
- Added two Double studies: `physical_errors.py` and `longer_plans.py`.

## Findings (part 2)
- All double matrices and gains reproduced exactly from the scripts (`verify_against_team_code.py`, 14 checks): gen 1 force model, `PythonMasterDouble-Claude.py` K = [-192.219, -4.407, 283.906, 32.818, 20.537, 21.304, 0.418] (matches the 767 s run's log), swing-up script balance K, TV-LQR gains, swing observer [0.512, 18.21].
- 35 rig swing-up attempts (15 runs, 2026-10-21 to 28): 0 caught, all reached exactly 0.831 m/s [HW]. In `swingup_double_20261027_184605` the error from the plan jumps from 1-4° (k = 100) to 8-10° (k = 110) in every attempt, before the cap at k ≈ 113 [HW] → model error is the cause, the cap the symptom [HYP].
- Stored 2.5 s plan tolerates about ±2 % per ratio, not B2 x0.5 or x1.5 [SIM] (agrees with the team's twin).
- **A 3.5 s plan with the same limits survives 25 of 36 single model errors vs 11 for the stored plan, incl. B2 x0.5 to x2** [SIM]. 3.0 s: 19 of 36. Plans written in the script's own format and checked with its `plan_problem` (mismatch 2e-11) and `load_trajectory`: `Math/Double/data/double_swingup_trajectory_3.5s.json`, `_3.0s.json`. Untested on the rig.
- The fitted ratio sets break H = L1·P2 (L1 = 0.200 m): implied L1 0.196 (SYSID), 0.206 (SysID new arm), 0.218 m (swing-fit). Swing-up tolerates physical errors (CoM ±10 mm, arm 1 mass -15/+20 %, L1 ±6 mm) far better than ratio errors; arm 2 mass (-8/+5 %) and inertia (-4/+6 %) are the sensitive values [SIM].
- Double balance tolerates about 5 % in the worst ratio direction, real motor delay up to about 22 ms (designed 9) [SIM].
- Triple [HYP rig, SIM]: unstable poles +16.5, +9.6, +4.5 /s; cart's direct effect on arm 3 only -0.07 (near-cancellation). Double's balance design with n = 3 holds; survives 14.1 ms delay; tolerates ±10 % real arm errors but under 1 % in one fitted number alone. Swing-up: 2.5 s needs ±0.37 m, 1.18 m/s, 15.6 m/s²; 4.0 s fits the rig's exact limits and survives every physical error tested.
- Sim tooling bug found and fixed: `swing_sim.run` integrated backwards for motor delays longer than 10 ms. Reran the double sims: no result changed.

## Decisions (part 2)
- None by the team. Team code only read (imported read-only for checks), never changed.

## Changed (part 2)
- PUC only: Math/Double, Math/Triple, Math/shared, Math/README.md, INDEX.md, BRIEF.md, params.md (implied L1, double gains), open-questions.md (14-16 new), gotchas.md (2 new), subsystems/swing-up.md, debug/2026-10-27_double-swingup-aborts.md.

## Open questions and next steps
- Try the 3.5 s double plan on the rig (open question 14).
- Refit the double ratios with H fixed to 0.2·P2, or in physical form (15); Coulomb joint friction (16).
- Measure arm 2's own swing period with arm 1 clamped (gives J2/p2, the most sensitive value) [HYP idea].
- Line-by-line code walkthrough pages for the double (like Single 9) not written yet.
- Which of m, l, I is wrong for the single arm (open question 9).
