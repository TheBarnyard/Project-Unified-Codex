---
updated: 2026-11-20
updated_by: Ryan (Claude, falling pendulum session)
---
# Falling single arm on a fixed pivot

One arm, pivot fixed (cart locked), let go at rest from θ0 (θ from straight up, clockwise +). Full write-up: [falling_pendulum.pdf](falling_pendulum.pdf) (derivation, key, plots). Interactive solver: https://claude.ai/artifact/WFymT1r6PRcSD5hDxvJsCw (source [falling_pendulum_calculator.html](falling_pendulum_calculator.html)). Python: [falling_pendulum.py](falling_pendulum.py) (`python falling_pendulum.py --theta0 30 --tau_c 0.002`).

## Key equations
- EOM (Lagrange + Rayleigh + Coulomb): `I θ'' = m g lc sin θ − b θ' − τc sgn θ'`, `I = Icm + m lc²`.
- Stick-slip: arm only moves if `m g lc |sin θ0| > τs`.
- Tip / any point s: `x = s sin θ, y = s cos θ`. IK: `θ = atan2(x, y)`, `θ' = (y x' − x y')/(x²+y²)`, `θ'' = (y x'' − x y'')/(x²+y²)`.
- No closed form with friction. Frictionless exact: `t(θ) = [K(κ) − F(β, κ)]/ωn`, `κ = cos(θ0/2)`, `sin β = sin((π−θ)/2)/κ`.
- Small angle near upright (viscous + Coulomb, falling phase): `θ = θc + (θ0−θc)(r2 e^{r1 t} − r1 e^{r2 t})/(r2−r1)`, `r1,2 = −b/2I ± sqrt((b/2I)² + m g lc/I)`, `θc = τc/(m g lc)`.
- Pivot force: `Rx = m lc(θ'' cos θ − θ'² sin θ)`, `Ry = m g − m lc(θ'' sin θ + θ'² cos θ)`.

## V2 arm 1 numbers (arm alone) [SIM]
m 0.0981 kg, L 0.200 m, lc 0.1478 m, I 2.484e-3 kg m² (STL model, [params.md](../../params.md)); b ≈ 1.63e-4 N m s = B1 0.0182 × J1 8.96e-3 (fit had arm 2 on, so [HYP] for the arm alone); τc not measured.
ωn 7.567 rad/s, Tn 0.830 s, ζ 0.0043, r1 7.534 1/s. From 10°: horizontal 0.3905 s, bottom 0.5083 s, 856 °/s at bottom, pivot force peaks 4.2 N (4.4 mg).
Checks: RK4 vs elliptic formula < 1e-6 s; vs SciPy solve_ivp < 0.001°.
