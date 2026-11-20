---
type: session
date: 2026-11-20
time: 18:55 (UTC)
member: Barney
ai: Claude project thread
topics: [arms-and-model, swing-up, triple]
status: done
pages_applied: yes
transcript: none
---
# Double and triple rig scripts with Barney's 2026-11-20 arm estimates

## Goal
Barney asked for copies of the current double swing-up (V2b_D) and triple balance scripts using the arm values estimated in chat on 2026-11-20, plus Pi install/run commands.

## What happened
- Arm values (Barney's layout: parts fixed relative to the END shaft; arms 200/250/300 mm; arm 3 has no shaft or collars): bar 34.5 g per 200 mm, 2x608 bearings 23.6 g and shaft 39.2 g + 2 collars 11.0 g on the end axis, rest of the hub 57.1 g centred 29.1 mm inboard (k = 12 mm assumed). Results: arm 1 165.4 g, CoM 169.1 mm, Icm 3.586e-4 kg m²; arm 2 174.0 g, 209.5 mm, 6.692e-4; arm 3 132.5 g, 228.8 mm, 9.385e-4 [HYP].
- Double copy `PythonMaster2_swingup_V2b_D_NewArms.py`: `--model new` (default) / `--model fit` (= V2b_D). Re-planned for the new values: same_3.0s, same_3.5s (default), whip_3.0s, whip_3.5s. PLAN_SPEED_M_S 0.8 (0.75 has no "same" plan for the new values).
- Triple copy `PythonMaster3_triple_NewArms.py`: new values, `--arms old` for the 11-18 values.
- Code: ChatGPT-Pendulum-Project branch `claude/project-thread-evv7sw`, commit 3fa9c4d, folders `DoubleSwingUp_NewArms/`, `TripleBalance_NewArms/` (also in project files). Originals not changed.

## Findings
- In V2b_D the arm constants (207 g, 87 mm, ...) are not used: SYSID_RATIOS (11-04 fit) replaces them.
- Arm 1 estimate agrees with the rig: hanging period 0.856 s vs 0.84-0.89 s [HW], P1 5.210 vs fit 5.225.
- Arm 2 estimate disagrees with the 11-04 fit: P2 3.026 vs 2.015, J2r 0.689 vs 0.451, H 0.605 vs 0.403. On run excite_20261104_093436 (3 s windows) the new values give 13.7 / 19.0 deg median RMS (arm 1 / arm 2) vs 1.7 / 2.7 for the fit; without the joint-3 shaft and collars on arm 2: 9.7 / 13.4 [HW data, model check].
- Twin, double [SIM]: new script on new arms 4/4 first try (clean), 23 % of attempts with rig-like radio (fit on fit was 30 %); new script on fit arms 0/8 attempts; fit script on new arms 0/16. The plan must match the real arms.
- Simulated rig, triple [SIM]: new script holds with new arms (clean, countdown, rig radio 4/4 at 40 s), with arm 3 errors and arm 1/2 inertia errors; falls with arm 1 or 2 mass ±15 %, arm 1 CoM +20 mm, and with the 11-18 arms 1-2 + new arm 3. The old script on old arms survived arm 1 mass ±15 %. Heavier-ended arms make the triple less forgiving of arm 1/2 errors.
- Prediction to tell the models apart without the motor: joint 2 taped straight, small swings about the main pivot: 1.12 s (fit) vs 1.19 s (new values).

## Dead ends
- Re-planning same_4.0s, whip_4.5s, folded_4.5s for the new values by continuation from the V2 plans: no plan within ±0.30 m, 0.8 m/s, 8 m/s² (same_4.0s stuck at 25 % of the way). With 0.75 m/s even same_3.0s failed.
- Running 7 planners in parallel with default BLAS threads: load 24 on 4 cores, no progress in 15 min. With OMP/OPENBLAS_NUM_THREADS=1 a plan takes 20-120 s.

## Decisions
- Shaft and collars counted in the arm below (Barney's framing); a mass on the joint axis gives identical dynamics either way.
- Double default `--model new` (as asked), `--model fit` kept as a one-flag fallback.

## Changed
- Code: ChatGPT-Pendulum-Project `claude/project-thread-evv7sw` 3fa9c4d (new folders only).

## Open questions and next steps
- Weigh arm 2 and find its balance point, or time the locked-straight swing (11.2 s vs 11.9 s for 10 swings), to decide `--model new` vs `fit`. Does arm 2 now carry the joint-3 shaft and collars when running the double?

## Follow-up 2026-11-20 20:15 UTC
- Barney at the rig thinks the arms are heavier than the code assumes. Asked for logs to calibrate: pointed to PendulumExcite.py (same as the 11-04 fit run), 20-30 min, tar without esp32_raw.bin; plus weigh arm 2 and find its balance point.
- Added `--model b10 ... b50` to the double copy (the fit's ratios moved 10-50 % toward the new values, Barney asked for every 10 % up to 50). Plans same_3.5s + whip_3.5s for all, same_4.0s for b10/b20 (b30 found none). Twin, true arms = same step: b10/b30/b50 2/2 first try each [SIM]. Commit f704065 (plans), README later.
