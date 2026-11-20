---
type: session
date: 2026-11-20
time: 16:52 (UTC)
member: Barney
ai: Claude project thread
topics: [Math, arms-and-model]
status: done
pages_applied: yes
transcript: none
---
# Falling single-arm pendulum: equations, PDF and solver

## Goal
Barney asked for the equations of motion and inverse kinematics of a single arm on a fixed pivot released from rest at any angle, with friction and moment of inertia, as a PDF with visuals and a variable key, plus an interactive table that solves itself.

## What happened
- Derived the EOM by Lagrange (Rayleigh for viscous, generalized torque for Coulomb, stick-slip rule), forward and inverse kinematics, inverse dynamics, pivot force, energy, frictionless elliptic solution, small-angle solutions at top and bottom.
- Wrote `falling_pendulum.py` (RK4, CLI), figures and tables, a 12-page LaTeX PDF and an HTML calculator (live RK4, plots, animation, table with CSV copy, inverse panels: tip → θ, time to angle, θ0 for a fall time).
- Saved in [Math/FallingArm/](../../../Math/FallingArm/README.md) and project files `FallingPendulum/`. Calculator: https://claude.ai/artifact/WFymT1r6PRcSD5hDxvJsCw

## Findings
- No closed form θ(t) once friction is in; frictionless time to any angle is exact with elliptic integrals (checked vs RK4 to < 1e-6 s) [SIM].
- V2 arm 1 alone from 10°: horizontal 0.3905 s, bottom 0.5083 s; halving θ0 adds about 0.092 s (ln2/r1) [SIM].
- Small-angle upright formula stays within 1 % of the true angle up to about 39° (5 % to 86°) [SIM].
- Arm-alone b ≈ 1.63e-4 N m s derived from the V2 fit B1 × J1; that fit had arm 2 attached [HYP]. Coulomb τc never measured [?].

## Dead ends
- None.

## Decisions
- Defaults use V2 arm 1 alone (STL model m, lc, I) with τc = 0, labelled as model values.

## Changed
- Code: PUC `Math/FallingArm/` (notes and tools only, no team code touched).

## Open questions and next steps
- Free-swing decay test with the cart locked would give the real b and τc for the arm (PDF section 12).

## Follow-up 2026-11-20 17:06 UTC
- Barney: drop the interactive part; wants the math in easy-to-read LaTeX with the variable key visible next to the equations.
- Built `Math/FallingArm/falling_pendulum_math.pdf` (11 landscape pages): key down the right side of every page, one-page equation sheet, step-by-step Lagrange derivation, a "where" list under each boxed result, exact frictionless θ(t) with the Jacobi sine, small-angle top/bottom solutions, pivot force, inverse dynamics, RK4, V2 arm 1 numbers.
