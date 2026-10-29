"""Double swing-up: which model errors matter, physical values vs independent ratios [SIM].

Run:  python physical_errors.py      (about 5-10 minutes; needs casadi for the plan; writes physical_errors.json)

The ratio sweep in double_sims.py changes ONE ratio (P1, P2, J2r or H) at a time. A real arm cannot do that:
changing arm 2's mass changes P1, P2, J2r and H together, and H always equals L1 * P2 (L1 = 0.200 m, joint 2's
distance from the main pivot). Here the swing-up is tested against errors in the PHYSICAL values instead:
  1. plan model: the physical arm values of double_model.PHYS with the swing-fit joint friction B2 = 0.11396
     (so H = L1 * P2 holds exactly); plan made like the stored one (2.5 s, 0.25 m, 0.75 m/s, 8 m/s^2, top 1.0 m/s),
     warm-started from the stored plan;
  2. the same controller as PythonMaster2_swingup.py (TV-LQR, observer, timer rounding, 1-count noise);
  3. real arms: one physical value off at a time (mass, inertia, CoM distance, joint position),
     and for comparison one ratio off at a time around the same model.
"""
import copy
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
import nlink_cart as nl  # noqa: E402
import swing_sim as ss  # noqa: E402
import double_model as dm  # noqa: E402

J1 = dm.PHYS.h()[0, 0]
PLAN_OUT = os.path.join(HERE, "..", "data", "double_plan_physical_model.json")


def phys_rig(B2=0.11396, **chg):
    """dm.PHYS with joint friction B2 (as a ratio of J1); chg like m2=+0.01 (kg) or c1=-0.003 (m)."""
    l1, l2 = copy.copy(dm.ARM1), copy.copy(dm.ARM2)
    l2.b = B2 * J1
    for k, v in chg.items():
        lk = l1 if k[-1] == "1" else l2
        setattr(lk, k[:-1], getattr(lk, k[:-1]) + v)
    return nl.Rig([l1, l2])


def to_ratios(rig):
    H, p = rig.h(), rig.p()
    j = H[0, 0]
    return dict(P1=p[0] / j, P2=p[1] / j, J2r=H[1, 1] / j, H=H[0, 1] / j, B1=rig.links[0].b / j, B2=rig.links[1].b / j)


def make_plan(base):
    if os.path.exists(PLAN_OUT):
        return np.array(json.load(open(PLAN_OUT))["z"]).T
    d = json.load(open(os.path.join(HERE, "..", "data", "double_swingup_trajectory.json")))
    plan = nl.plan_team(base, 2.5, 0.25, 0.75, 8.0, 1.0, guess=(np.array(d["z"]).T, np.array(d["a_knots"])[::5]))
    print("plan:", plan["status"], "effort %.2f" % plan["effort"])
    json.dump(dict(T=2.5, dt=0.01, z=np.round(plan["Z"].T, 8).tolist(), a=np.round(plan["a"], 8).tolist(),
                   model_ratios=to_ratios(base), effort=plan["effort"],
                   limits=dict(track_m=0.25, speed_m_s=0.75, accel_m_s2=8.0, motor_top_speed_m_s=1.0),
                   note="plan for the physical arm values (double_model.PHYS) + swing-fit B2; made by physical_errors.py"),
              open(PLAN_OUT, "w"))
    return plan["Z"]


def main():
    base = phys_rig()
    r0 = to_ratios(base)
    Z = make_plan(base)
    rb = dict(r0); rb["B2"] = 0.03
    g = ss.build(base, Z, bal_rig=nl.Rig.from_team_ratios(rb))

    def once(true_rig):
        c = ss.TeamSwingController(base, Z, g["a_ref"], g["Ks"], g["bal"], g["Ls"])
        res = ss.run(true_rig, c, 6.0, tau_true=0.008, noise_counts=1.0, seed=0)
        return [bool(res["balanced"]), res["why"]]

    out = {"nominal": once(base)}
    for key in ("P1", "P2", "J2r", "H"):
        for pct in (-6, -4, -2, 2, 4, 6):
            r = dict(r0); r[key] *= 1 + pct / 100
            out[f"ratio {key} {pct:+d}%"] = once(nl.Rig.from_team_ratios(r))
    values = {"m1": dm.ARM1.m, "m2": dm.ARM2.m, "I1": dm.ARM1.I, "I2": dm.ARM2.I}
    for k, rels in (("m1", (-20, -15, -10, -5, 5, 10, 20)), ("m2", (-20, -10, -8, -6, -5, 5, 6, 8, 10, 20)),
                    ("I1", (-40, -20, -10, 10, 20, 30, 40)), ("I2", (-40, -20, -10, -6, -4, -2, 2, 4, 6, 10, 20, 40))):
        for pct in rels:
            out[f"phys {k} {pct:+d}%"] = once(phys_rig(**{k: values[k] * pct / 100}))
    for k in ("c1", "c2", "L1"):
        for mm in (-10, -6, -3, 3, 6, 10):
            out[f"phys {k} {mm:+d} mm"] = once(phys_rig(**{k: mm / 1000}))
    for name, (ok, why) in out.items():
        print(f"  {name:20s} {'CATCH' if ok else 'fail ':5s} {why}")
    json.dump(out, open(os.path.join(HERE, "physical_errors.json"), "w"), indent=1)
    print("wrote physical_errors.json")


if __name__ == "__main__":
    main()
