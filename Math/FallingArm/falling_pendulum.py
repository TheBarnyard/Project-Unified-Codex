"""Falling single-arm pendulum on a fixed pivot (no cart), released from rest.

theta is measured from straight UP, positive clockwise (tip moves to +x).
Equation of motion (Lagrange + friction):
    I*thdd = m*g*lc*sin(th) - b*thd - tau_c*sgn(thd)
Coulomb friction uses stick-slip logic: while the arm is (almost) stopped,
friction cancels up to tau_c of the other torques, so the arm can stay put.

Default numbers = V2 arm 1 alone (PUC params.md, 2026-10-29 STL + weights
model, and B1 from the 2026-11-04 rig fit). tau_c is NOT measured (0).

Usage:  python falling_pendulum.py            -> prints a table, makes figures
        python falling_pendulum.py --theta0 30 --tend 3
"""
import argparse
import math
import os

import numpy as np

G = 9.81
V2_ARM1 = dict(m=0.0981, L=0.200, lc=0.1478, I=2.484e-3, b=1.63e-4, tau_c=0.0, g=G)


def rod_inertia(m, L):
    """Uniform rod about one end: I = m L^2 / 3."""
    return m * L * L / 3.0


def accel(th, w, p, eps=1e-4):
    """theta double-dot (rad/s^2) with stick-slip Coulomb friction."""
    tg = p["m"] * p["g"] * p["lc"] * math.sin(th) - p["b"] * w   # gravity + viscous
    tc = p["tau_c"]
    if abs(w) > eps:
        return (tg - tc * math.copysign(1.0, w)) / p["I"]
    if abs(tg) <= tc:            # static: friction holds it
        return 0.0
    return (tg - tc * math.copysign(1.0, tg)) / p["I"]


def simulate(theta0_deg, p=V2_ARM1, t_end=3.0, dt=2e-4, w0=0.0):
    """Fixed-step RK4. Returns dict of arrays: t, th, w, a (rad, rad/s, rad/s^2)."""
    n = int(round(t_end / dt)) + 1
    t = np.linspace(0.0, (n - 1) * dt, n)
    th = np.empty(n); w = np.empty(n); a = np.empty(n)
    th[0] = math.radians(theta0_deg); w[0] = w0
    for i in range(n - 1):
        x, v = th[i], w[i]
        k1x, k1v = v, accel(x, v, p)
        k2x, k2v = v + 0.5 * dt * k1v, accel(x + 0.5 * dt * k1x, v + 0.5 * dt * k1v, p)
        k3x, k3v = v + 0.5 * dt * k2v, accel(x + 0.5 * dt * k2x, v + 0.5 * dt * k2v, p)
        k4x, k4v = v + dt * k3v, accel(x + dt * k3x, v + dt * k3v, p)
        th[i + 1] = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
        w[i + 1] = v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        if p["tau_c"] > 0 and abs(w[i + 1]) < 1e-4 and abs(p["m"] * p["g"] * p["lc"] * math.sin(th[i + 1])) <= p["tau_c"]:
            w[i + 1] = 0.0
    for i in range(n):
        a[i] = accel(th[i], w[i], p)
    return dict(t=t, th=th, w=w, a=a)


def kinematics(sim, p, s=None):
    """Position/velocity/acceleration of a point a distance s from the pivot (default tip)."""
    s = p["L"] if s is None else s
    th, w, a = sim["th"], sim["w"], sim["a"]
    x, y = s * np.sin(th), s * np.cos(th)
    vx, vy = s * w * np.cos(th), -s * w * np.sin(th)
    ax = s * (a * np.cos(th) - w ** 2 * np.sin(th))
    ay = s * (-a * np.sin(th) - w ** 2 * np.cos(th))
    return dict(x=x, y=y, vx=vx, vy=vy, ax=ax, ay=ay)


def pivot_force(sim, p):
    """Force the pivot puts on the arm, world frame (x right, y up), N."""
    k = kinematics(sim, p, p["lc"])
    return p["m"] * k["ax"], p["m"] * k["ay"] + p["m"] * p["g"]


def energy(sim, p):
    """Mechanical energy relative to hanging at rest, J."""
    return 0.5 * p["I"] * sim["w"] ** 2 + p["m"] * p["g"] * p["lc"] * (np.cos(sim["th"]) + 1.0)


def inverse_kinematics(x, y, vx=0.0, vy=0.0):
    """Tip (x, y[, vx, vy]) -> theta (rad), theta-dot (rad/s), arm length."""
    th = math.atan2(x, y)
    r2 = x * x + y * y
    return th, (y * vx - x * vy) / r2, math.sqrt(r2)


def crossing_time(sim, target_deg):
    """First time |theta| reaches target_deg (linear interpolation). None if never."""
    tgt = math.radians(target_deg)
    th = np.abs(sim["th"])
    idx = np.nonzero(th >= tgt)[0]
    if len(idx) == 0:
        return None
    i = idx[0]
    if i == 0:
        return 0.0
    f = (tgt - th[i - 1]) / (th[i] - th[i - 1])
    return sim["t"][i - 1] + f * (sim["t"][i] - sim["t"][i - 1])


def small_angle(t, theta0_deg, p):
    """Closed form near upright (viscous + Coulomb, falling phase, theta0 > theta_c)."""
    I, b = p["I"], p["b"]
    k = p["m"] * p["g"] * p["lc"]
    th0 = math.radians(theta0_deg)
    thc = math.copysign(p["tau_c"] / k, th0)
    r1 = -b / (2 * I) + math.sqrt((b / (2 * I)) ** 2 + k / I)
    r2 = -b / (2 * I) - math.sqrt((b / (2 * I)) ** 2 + k / I)
    d = th0 - thc
    return thc + d * (r2 * np.exp(r1 * t) - r1 * np.exp(r2 * t)) / (r2 - r1)


def frictionless_time(theta0_deg, theta_deg, p):
    """Exact frictionless time from theta0 to theta via the energy integral."""
    from scipy.integrate import quad
    k = 2 * p["m"] * p["g"] * p["lc"] / p["I"]
    a0, a1 = math.radians(theta0_deg), math.radians(theta_deg)
    # substitute th = a0 + u^2 to remove the 1/sqrt singularity at the start
    f = lambda u: 2 * u / math.sqrt(k * (math.cos(a0) - math.cos(a0 + u * u)))
    val, _ = quad(f, 1e-12, math.sqrt(a1 - a0), limit=200)
    return val


def table(theta0_deg, p, t_end, step):
    sim = simulate(theta0_deg, p, t_end)
    k = kinematics(sim, p)
    every = int(round(step / (sim["t"][1] - sim["t"][0])))
    print(f"{'t s':>6} {'theta deg':>10} {'thd deg/s':>10} {'tip x m':>9} {'tip y m':>9}")
    for i in range(0, len(sim["t"]), every):
        print(f"{sim['t'][i]:6.3f} {math.degrees(sim['th'][i]):10.2f} {math.degrees(sim['w'][i]):10.1f} "
              f"{k['x'][i]:9.4f} {k['y'][i]:9.4f}")
    for tgt in (90, 180):
        tc = crossing_time(sim, tgt)
        print(f"time to {tgt} deg: {'never' if tc is None else f'{tc:.4f} s'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta0", type=float, default=10.0, help="release angle from upright, deg")
    ap.add_argument("--tend", type=float, default=2.0)
    ap.add_argument("--step", type=float, default=0.05, help="table row spacing, s")
    for key in ("m", "L", "lc", "I", "b", "tau_c", "g"):
        ap.add_argument("--" + key, type=float, default=None)
    ap.add_argument("--rod", action="store_true", help="uniform rod: lc = L/2, I = mL^2/3")
    a = ap.parse_args()
    p = dict(V2_ARM1)
    for key in ("m", "L", "lc", "I", "b", "tau_c", "g"):
        if getattr(a, key) is not None:
            p[key] = getattr(a, key)
    if a.rod:
        p["lc"], p["I"] = p["L"] / 2, rod_inertia(p["m"], p["L"])
    print("params:", p)
    table(a.theta0, p, a.tend, a.step)
