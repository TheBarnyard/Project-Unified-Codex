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
| 7 | `PythonMaster2_swingup.py`, `double_swingup_trajectory.json` and other Barney scripts live only on the Pi legacy checkout. Push them to a repo? | 2026-10-26 | Barney (Claude) | Risk of losing them |
| 8 | Real mass, CoM and STLs of the new arm 1 | 2026-10-27 | Barney (Claude) | CAD estimate is off |
