"""Triple pendulum on a cart: model, linear model, balance design and its tolerances [HYP rig].

There is no triple rig and no triple code. The rig assumed here is the double rig with a third arm on top:
  arm 1 and arm 2 = the team's physical values (Code/Global/physical_parameters.py, PythonMasterMath2.py),
  arm 3 = a copy of arm 2, hinged at the end of arm 2 (0.25 m from joint 2),
  joint friction = the double balance script's (B2 = 0.03 x J1 of the double) at joints 2 and 3,
  the swing-up uses the double swing-up script's fitted value (B2 = 0.114 x J1) instead, as that script does,
  sensors and motor as on the double: 14-bit encoders (arm 1 absolute, joints 2 and 3 relative),
  cart step count, stepper speed landing about 9 ms after each 10 ms sample.
The controllers are the double scripts' (PythonMasterDouble-Claude.py, PythonMaster2_swingup.py) with n = 3,
using Math/shared/nlink_cart.py and swing_sim.py.

Run:  python triple_model.py     (prints everything, writes triple_model_numbers.json; about 1 minute)
"""
import copy
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
import nlink_cart as nl  # noqa: E402

np.set_printoptions(precision=4, suppress=True, linewidth=140)

# ---- the assumed rig ----
ARM1 = nl.Link(m=0.207, c=0.087, L=0.2, I=0.00123324992)
ARM2 = nl.Link(m=0.210, c=0.106, L=0.25, I=0.00197563667)
J1_DOUBLE = ARM1.I + ARM1.m * ARM1.c**2 + ARM1.L**2 * ARM2.m       # 0.0112 kg m^2, the double's J1
B_BALANCE = 0.03 * J1_DOUBLE        # N m s/rad, BALANCE_B2 of the double scripts as an absolute value
B_SWING = 0.11396 * J1_DOUBLE       # the swing-fit B2 of PythonMaster2_swingup.py


def make(b=B_BALANCE, arm3=None):
    a2 = copy.copy(ARM2); a2.b = b
    a3 = copy.copy(arm3 or ARM2); a3.b = b
    return nl.Rig([copy.copy(ARM1), a2, a3], names=["arm 1", "arm 2", "arm 3"])


TRIPLE = make()                      # balance model
TRIPLE_SWING = make(B_SWING)         # swing-up model
DOUBLE = nl.Rig([copy.copy(ARM1), nl.Link(0.210, 0.106, 0.25, 0.00197563667, B_BALANCE)], names=["arm 1", "arm 2"])
SINGLE = nl.Rig([nl.Link(0.26, 0.05, 0.2, 0.001751)])          # single script, identified inertia
# a lighter top arm: the 2026-10-29 STL estimate of the new arm 2 alone, corrected version (params.md, pivot on
# the small hole, hub electronics at the far end; 111.9 g, CoM 186.5 mm, 6.17e-4 kg m^2 about its CoM) [?]
TRIPLE_LIGHT = make(arm3=nl.Link(m=0.1119, c=0.1865, L=0.25, I=6.17e-4))

# ---- the double balance script's settings, unchanged ----
BAL = dict(angle_deg=2.0, rate_deg_s=60.0, cart_m=0.05, cart_speed_m_s=0.3, accel_m_s2=1.3, latency_ms=9.0)


def balance(rig=TRIPLE, latency_ms=BAL["latency_ms"], accel=BAL["accel_m_s2"], angle=BAL["angle_deg"],
            rate=BAL["rate_deg_s"], **kal):
    Q = nl.bryson_Q(rig.n, angle, rate, BAL["cart_m"], BAL["cart_speed_m_s"])
    return nl.balance_design_ramp(rig, Q, np.array([[1 / accel**2]]), 0.01, latency_ms / 1000, **kal)


def modes(rig, upright=True):
    """Cart held still. Upright: growth rates (1/s) of the falling motions; hanging: swing frequencies (rad/s).
    Shapes normalised to theta_1 = 1."""
    H, p = rig.h(), rig.p()
    s2, V = np.linalg.eig(np.linalg.solve(H, nl.G * np.diag(p)))
    o = np.argsort(s2.real)
    return np.sqrt(s2.real[o]), (V[:, o] / V[0, o]).real


def entry_rig(base, kind, idx, pct):
    """One entry of p or H changed on its own (what an independent fit of the ratios can do)."""
    H, p = base.h(), base.p()
    if kind == "p":
        p[idx] *= 1 + pct / 100
    else:
        i, j = idx
        H[i, j] *= 1 + pct / 100
        H[j, i] = H[i, j]
    return nl.Rig([nl.Link(0, 0, 0, 0, lk.b) for lk in base.links], H_given=H, p_given=p)


def physical_rig(base, li, attr, rel=None, add=None):
    """One physical value of one arm changed (mass, CoM, inertia, joint position): p and H change together."""
    links = [copy.copy(lk) for lk in base.links]
    v = getattr(links[li], attr)
    setattr(links[li], attr, v * (1 + rel) if rel is not None else v + add)
    return nl.Rig(links)


def tolerance(f, step_fine=0.1, top=40.0):
    """Smallest change (in the units of f's argument) at which the closed loop becomes unstable."""
    from scipy.optimize import brentq
    grid = np.concatenate([np.arange(step_fine, 2, step_fine), np.arange(2, top + 0.25, 0.5)])
    prev = 0.0
    for g in grid:
        if f(g) > 1.0:
            return float(brentq(lambda x: f(x) - 1.0, prev, g, xtol=0.01)) if prev > 0 else float(g)
        prev = g
    return float("inf")


ENTRIES = {3: [("p", 0, "p1"), ("p", 1, "p2"), ("p", 2, "p3"), ("H", (0, 0), "h11"), ("H", (1, 1), "h22"),
               ("H", (2, 2), "h33"), ("H", (0, 1), "h12"), ("H", (0, 2), "h13"), ("H", (1, 2), "h23")],
           2: [("p", 0, "p1"), ("p", 1, "p2"), ("H", (0, 0), "h11"), ("H", (1, 1), "h22"), ("H", (0, 1), "h12")]}


def entry_tolerances(rig, design):
    out = {}
    for kind, idx, nm in ENTRIES[rig.n]:
        lo = tolerance(lambda x: nl.balance_closed_loop_radius(design, entry_rig(rig, kind, idx, -x)))
        hi = tolerance(lambda x: nl.balance_closed_loop_radius(design, entry_rig(rig, kind, idx, x)))
        out[nm] = (-lo, hi)
    return out


def physical_tolerances(rig, design):
    """Mass and inertia in % of their value; CoM distance c and joint position L in mm."""
    out = {}
    for li in range(rig.n):
        for attr in ("m", "I"):
            lo = tolerance(lambda x: nl.balance_closed_loop_radius(design, physical_rig(rig, li, attr, rel=-x / 100)), top=90)
            hi = tolerance(lambda x: nl.balance_closed_loop_radius(design, physical_rig(rig, li, attr, rel=x / 100)), top=200)
            out[f"{attr}{li + 1} (%)"] = (-lo, hi)
        for attr in ("c", "L"):
            if attr == "L" and li == rig.n - 1:
                continue        # the top arm's L is only its drawn length
            lo = tolerance(lambda x: nl.balance_closed_loop_radius(design, physical_rig(rig, li, attr, add=-x / 1000)), top=60)
            hi = tolerance(lambda x: nl.balance_closed_loop_radius(design, physical_rig(rig, li, attr, add=x / 1000)), top=60)
            out[f"{attr}{li + 1} (mm)"] = (-lo, hi)
    return out


def delay_tolerance(rig, design):
    return tolerance(lambda ms: nl.balance_closed_loop_radius(design, rig, ms / 1000), step_fine=0.5, top=60)


def to_list(a):
    return np.round(np.real(np.asarray(a)), 8).tolist()


def main():
    out = {}
    print("=== Link constants ===")
    for name, rig in (("triple", TRIPLE), ("double", DOUBLE)):
        p, H = rig.p(), rig.h()
        print(f"{name}: p = {p} kg m\nH =\n{H} kg m^2")
        out[name] = dict(p=to_list(p), H=to_list(H))
    print("energy to add from hanging to upright, 2 g sum(p):",
          {k: round(2 * nl.G * r.p().sum(), 3) for k, r in (("single", SINGLE), ("double", DOUBLE), ("triple", TRIPLE))}, "J")
    out["energy_J"] = {k: 2 * nl.G * float(r.p().sum()) for k, r in (("single", SINGLE), ("double", DOUBLE), ("triple", TRIPLE))}

    print("\n=== Natural motions (cart held still) ===")
    for name, rig in (("single", SINGLE), ("double", DOUBLE), ("triple", TRIPLE), ("triple, light arm 3", TRIPLE_LIGHT)):
        su, Vu = modes(rig, True)
        print(f"{name}: upright growth {su} /s (doubling {np.log(2) / su * 1000} ms)\n   shapes (rows = arms):\n{Vu}")
        out.setdefault("modes", {})[name] = dict(growth=to_list(su), shapes=to_list(Vu),
                                                 hang_periods=to_list(2 * np.pi / su))
        print(f"   hanging periods {2 * np.pi / su} s")

    print("\n=== Linear model, cart acceleration input ===")
    A, B = nl.linear_accel(TRIPLE)
    print("A =\n", A, "\nB =", B.ravel())
    print("poles:", np.sort(np.linalg.eigvals(A).real))
    n = 3
    ctrb = np.hstack([np.linalg.matrix_power(A, k) @ B for k in range(2 * n + 2)])
    C = np.zeros((4, 8)); C[0, 0] = C[1, 2] = C[2, 4] = C[3, 6] = 1
    obsv = np.vstack([C @ np.linalg.matrix_power(A, k) for k in range(2 * n + 2)])
    print("rank controllability", np.linalg.matrix_rank(ctrb), " observability", np.linalg.matrix_rank(obsv))
    out["A"], out["B"], out["poles"] = to_list(A), to_list(B), to_list(np.sort(np.linalg.eigvals(A).real))
    print("B for comparison: double", nl.linear_accel(DOUBLE)[1].ravel(), " light arm 3", nl.linear_accel(TRIPLE_LIGHT)[1].ravel())
    Bp = nl.linear_accel(entry_rig(TRIPLE, "p", 1, 2.0))[1].ravel()
    Bm = nl.linear_accel(physical_rig(TRIPLE, 1, "m", rel=0.2))[1].ravel()
    print("B with p2 alone +2 %:", Bp, "\nB with arm 2 mass +20 %:", Bm)
    out["B_p2_plus2"], out["B_m2_plus20"] = to_list(Bp), to_list(Bm)
    out["B_double"], out["B_light"] = to_list(nl.linear_accel(DOUBLE)[1]), to_list(nl.linear_accel(TRIPLE_LIGHT)[1])

    print("\n=== Balance: the double script's design with n = 3 ===")
    d = balance()
    K = d["K"][0]
    print("K =", K)
    print("K per degree (m/s^2 per deg):", K[[0, 2, 4]] * np.pi / 180, " per deg/s:", K[[1, 3, 5]] * np.pi / 180,
          " per mm:", K[6] / 1000, " per m/s:", K[7], " a_prev:", K[8])
    print("closed-loop |eig| (sorted):", np.sort(np.abs(d["cl_eig"]))[::-1])
    print("Kalman filter gain L =\n", d["L"])
    out["K"], out["L"], out["cl_eig"] = to_list(K), to_list(d["L"]), to_list(np.sort(np.abs(d["cl_eig"]))[::-1])
    dd = balance(DOUBLE)
    print("double (same settings, physical values): K =", dd["K"][0])
    out["K_double_phys"] = to_list(dd["K"][0])
    for lat in (0.0, 3.0, 6.0, 9.0):
        print(f"   triple, design latency {lat} ms: K = {np.round(balance(latency_ms=lat)['K'][0], 1)}")

    print("\n=== Tolerances of the balance (linear closed loop incl. Kalman filter) ===")
    out["delay_ms"] = {}
    for name, rig in (("double", DOUBLE), ("triple", TRIPLE), ("triple, light arm 3", TRIPLE_LIGHT)):
        dz = balance(rig)
        md = delay_tolerance(rig, dz)
        out["delay_ms"][name] = md
        print(f"{name}: designed for 9 ms, holds up to {md:.1f} ms of real motor delay")
    out["entry"], out["physical"] = {}, {}
    for name, rig in (("double", DOUBLE), ("triple", TRIPLE)):
        dz = balance(rig)
        e = entry_tolerances(rig, dz)
        ph = physical_tolerances(rig, dz)
        out["entry"][name], out["physical"][name] = e, ph
        print(f"{name}, one entry of p or H alone:  " + ", ".join(f"{k} {v[0]:+.1f}/{v[1]:+.1f} %" for k, v in e.items()))
        print(f"{name}, one physical value:  " + ", ".join(f"{k} {v[0]:+.1f}/{v[1]:+.1f}" for k, v in ph.items()))
    json.dump(out, open(os.path.join(HERE, "triple_model_numbers.json"), "w"), indent=1)
    print("\nwrote triple_model_numbers.json")


if __name__ == "__main__":
    main()
