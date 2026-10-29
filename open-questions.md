# Open questions

Unresolved questions and conflicting information. When one is answered, strike it and link the session that answered it.

| # | Question | Raised | By | Notes |
| --- | --- | --- | --- | --- |
| 1 | Is the single pendulum upright calibration 10687.7 or about 8994? | 2026-10-07 | Barney (Claude) | Depends on whether raw 802 was free-hanging. See [params.md](params.md) |
| 2 | Does the TX1 5 V fix hold over a 20+ min controller run? | 2026-10-27 | Barney (Claude) | [debug](debug/2026-10-27_angle-dropouts.md) |
| 3 | Does the PLAN_SPEED 0.60 double swing-up plan catch on the rig? | 2026-10-28 | Barney (Claude) | [debug](debug/2026-10-27_double-swingup-aborts.md) |
| 4 | Should the stepper timer round toward the requested speed, or MOTOR_TOP_SPEED be raised (stall risk)? | 2026-10-28 | Barney (Claude) | Alternative fix for the 0.83 m/s cap |
| 5 | Which receiver protocol is flashed now: 6-byte unframed or v1 framed? | 2026-10-28 | Barney (Claude) | `*_autocalibrate` controllers and PendulumExcite use v1; `PythonMaster.py` uses 6-byte |
| 6 | Are the limit switches more than 0.40 m from centre? | 2026-10-27 | Barney (Claude) | Needed for TRACK_SOFT_LIMIT_M 0.40 |
| 7 | `PythonMaster2_swingup.py`, `double_swingup_trajectory.json` and other Barney scripts live only on the Pi legacy checkout. Push them to a repo? | 2026-10-26 | Barney (Claude) | Risk of losing them. 2026-10-29: Ethan copied the whole legacy checkout (84 files, as of 2026-10-28) to etwan007/ENGT480 branch `experiment/legacy-pi-recovery`, commit ba019f9, folder `LegacyPi/` (seen in the [math session](sessions/2026/10/2026-10-29_1448_Barney_math-folder.md)). Copies exist now; whether they get merged is still open. |
| 8 | Real mass, CoM and STLs of the new arm 1 | 2026-10-27 | Barney (Claude) | CAD estimate is off |
| 9 | Single arm: with m = 0.260 kg, l = 0.05 m, I = 0.003 kg m² (code values) the arm should swing at 1.063 s; on the rig it swings at 0.84-0.89 s (w0 7.09-7.47 rad/s). Which of m, l, I is wrong? | 2026-10-29 | Barney (Claude) | `PythonMasterUpExpClaudeImproved.py` sidesteps it by measuring w0 each run and setting I ≈ 0.00175. Balance-only scripts still use I = 0.003. [Math/Single 7.3](Math/Single/07_swing_up.md#73-identify-measure-ω0-on-the-rig) |
