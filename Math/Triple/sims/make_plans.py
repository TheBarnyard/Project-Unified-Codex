"""Swing-up plans for the assumed triple rig [SIM, HYP rig].

Run:  python make_plans.py [T ...]      (default 2.5 3.0 3.5 4.0; about 5-15 minutes per duration, needs casadi)

For each duration T:
  1. solve the double script's --plan problem (Math/shared/nlink_cart.plan_team: multiple shooting, knots
     every 0.05 s, minimise the integral of a^2) with loose limits: track 0.60 m, speed 2.0 m/s, 30 m/s^2,
     motor top speed 3.0 m/s;
  2. tighten the limits step by step toward the rig's (0.25 m, 0.75 m/s, 8 m/s^2, top 1.0 m/s), each solve
     starting from the last plan that worked; a step that fails is halved (plan_team_homotopy);
  3. write ../data/triple_swingup_plan_<T>s.json with the tightest limits that worked.
IPOPT finds local optima: "infeasible" from one starting plan does not prove that no plan exists. The limits
reached are therefore an upper bound on what the rig needs, not the exact minimum.
"""
import datetime
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
import nlink_cart as nl  # noqa: E402
import triple_model as tm  # noqa: E402

RIG_LIMITS = (0.25, 0.75, 8.0, 1.0)
LOOSE = (0.6, 2.0, 30.0, 3.0)


def save(plan, T, path, robustness=False):
    rig = tm.TRIPLE_SWING
    lk = [dict(m=l.m, c=l.c, L=l.L, I=l.I, b=l.b) for l in rig.links]
    X, V, A, Vt = (plan["limits_reached"][k] for k in ("X", "V", "A", "Vtop")) if "limits_reached" in plan else \
        (plan["limits"][k] for k in ("X", "V", "A", "Vtop"))
    out = dict(version=1, T=T, dt=0.01, z=np.round(plan["Z"].T, 8).tolist(), a=np.round(plan["a"], 8).tolist(),
               a_knots=np.round(plan["knots"], 8).tolist(), knot_dt=0.05, model_links=lk,
               limits=dict(track_m=X, speed_m_s=V, accel_m_s2=A, motor_top_speed_m_s=Vt),
               effort=plan["effort"], peak=dict(track_m=plan["peak"]["x"], speed_m_s=plan["peak"]["v"],
                                               accel_m_s2=plan["peak"]["a"]),
               fraction_to_rig_limits=plan.get("lam", 1.0), robustness=robustness,
               made=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
               note="assumed triple rig (Math/Triple/sims/triple_model.py, TRIPLE_SWING) [HYP]")
    json.dump(out, open(path, "w"))


def make(T, log=print):
    t0 = time.time()
    lg = lambda s: log(f"{s}  ({time.time() - t0:.0f} s)")
    first = nl.plan_team(tm.TRIPLE_SWING, T, *LOOSE, max_iter=3000)
    lg(f"T = {T} s, loose limits: {first['status']}, effort {first['effort']:.1f}")
    if not first["ok"]:
        return None
    return nl.plan_team_homotopy(tm.TRIPLE_SWING, T, *RIG_LIMITS, start_limits=LOOSE, min_step=1 / 32,
                                 guess=(first["Z"], first["knots"]), log=lg)


if __name__ == "__main__":
    for T in [float(a) for a in sys.argv[1:]] or [2.5, 3.0, 3.5, 4.0]:
        p = make(T)
        if p is not None:
            save(p, T, os.path.join(HERE, "..", "data", f"triple_swingup_plan_{T:.1f}s.json"))
            print("limits reached:", p["limits_reached"], "effort", round(p["effort"], 1))
