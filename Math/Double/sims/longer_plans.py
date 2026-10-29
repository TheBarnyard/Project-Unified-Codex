"""Double swing-up: are longer plans (same rig limits) more tolerant of model errors? [SIM]

Run:  python longer_plans.py [path to LegacyPi/Code/DoublePendulum]     (about 10 minutes; needs casadi)

  1. plan 3.0 s and 3.5 s swing-ups for the swing-fit ratios (the stored plan's model) with the stored plan's
     limits (0.25 m, 0.75 m/s, 8 m/s^2, motor top 1.0 m/s): loose limits first, then continuation
     (nlink_cart.plan_team_homotopy);
  2. write them in PythonMaster2_swingup.py's own file format (double_swingup_trajectory_<T>s.json in ../data:
     z, a_knots per sample, p = SLSQP unknowns with S = 10 segments, model_ratios, limits, peak, made), and,
     if the path to the team's scripts is given, check them with the script's own plan_problem (its
     dynamics constraints and limits) and load_trajectory;
  3. run the same single-error sweep as double_sims.py (P1, P2, J2r, H +-2..8 %, B2 x0.5/1.5/2) on each,
     writes longer_plans.json.
"""
import datetime
import importlib.util
import json
import os
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
import nlink_cart as nl  # noqa: E402
import swing_sim as ss  # noqa: E402
import double_model as dm  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
R0 = dm.RATIOS["swing-fit (stored plan, 2026-10-27)"]
LIMITS = dict(track_m=0.25, speed_m_s=0.75, accel_m_s2=8.0, motor_top_speed_m_s=1.0)


def make(T):
    rig = nl.Rig.from_team_ratios(R0)
    first = nl.plan_team(rig, T, 0.6, 2.0, 30.0, 3.0)
    p = nl.plan_team_homotopy(rig, T, 0.25, 0.75, 8.0, 1.0, guess=(first["Z"], first["knots"]), min_step=1 / 32,
                              log=lambda s: print(s, flush=True))
    return p


def team_format(p, T, S=10):
    Z, a, knots = p["Z"], p["a"], p["knots"]
    N = Z.shape[1] - 1
    seg = N // S
    pv = np.concatenate([knots] + [Z[:, s * seg] for s in range(1, S)])
    return {"version": 1, "T": T, "dt": 0.01, "M": len(knots) - 1, "S": S, "p": pv.tolist(), "z": Z.T.tolist(),
            "a_knots": a.tolist(), "model_ratios": R0, "effort": float(np.sum(a**2) * 0.01),
            "limits": LIMITS,
            "peak": {"track_m": float(np.abs(Z[4]).max()), "speed_m_s": float(np.abs(Z[5]).max()),
                     "accel_m_s2": float(np.abs(a).max())},
            "made": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "note": "made by Math/Double/sims/longer_plans.py (CasADi/IPOPT), not by --plan [SIM]"}


def check_with_team(d, team_dir, path=None):
    """Load PythonMaster2_swingup.py read-only and test the plan with its own constraint functions."""
    sys.modules.setdefault("serial", types.ModuleType("serial"))
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("team_swingup", os.path.join(team_dir, "PythonMaster2_swingup.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    pr = m.plan_problem(d["model_ratios"], d["T"])
    p = np.array(d["p"])[None]
    out = {}
    for key in ("ceq", "cin"):
        if key in pr:
            out[key] = pr[key](p)
    tr, a = pr["sim"](p)
    z = np.concatenate([tr[0, s, :-1] for s in range(pr["S"])] + [tr[0, -1, -1:]])
    res = dict(n_unknowns=len(pr["p0"]), n_in_file=len(d["p"]), max_state_diff=float(np.abs(z - np.array(d["z"])).max()),
               max_accel_diff=float(np.abs(a[0] - np.array(d["a_knots"])).max()))
    if "ceq" in out:
        res["max_equality_violation"] = float(np.abs(out["ceq"]).max())
    if "cin" in out:
        res["min_inequality_margin"] = float(out["cin"].min())
    if path:
        from pathlib import Path
        m.TRAJECTORY_FILE = Path(path)          # in memory only; the script file is not changed
        tr = m.load_trajectory(d["model_ratios"])
        res["load_trajectory_N"] = int(tr["N"])
    return res


def sweep(d):
    rig = nl.Rig.from_team_ratios(R0)
    Z = np.array(d["z"]).T
    rb = dict(R0); rb["B2"] = 0.03
    g = ss.build(rig, Z, bal_rig=nl.Rig.from_team_ratios(rb))

    def once(r):
        c = ss.TeamSwingController(rig, Z, g["a_ref"], g["Ks"], g["bal"], g["Ls"])
        res = ss.run(nl.Rig.from_team_ratios(r), c, d["T"] + 3.5, tau_true=0.008, noise_counts=1.0, seed=0)
        return dict(ok=bool(res["balanced"]), why=res["why"], max_v=float(np.abs(res["v_sent"]).max()))
    out = {"nominal": once(R0)}
    for key in ("P1", "P2", "J2r", "H"):
        for pct in (-8, -6, -4, -2, 2, 4, 6, 8):
            r = dict(R0); r[key] *= 1 + pct / 100
            out[f"{key} {pct:+d}%"] = once(r)
    for mult in (0.5, 1.5, 2.0):
        r = dict(R0); r["B2"] *= mult
        out[f"B2 x{mult:g}"] = once(r)
    return out


def main():
    team_dir = sys.argv[1] if len(sys.argv) > 1 else None
    results = {}
    for T in (3.0, 3.5):
        path = os.path.join(DATA, f"double_swingup_trajectory_{T:.1f}s.json")
        if os.path.exists(path):
            d = json.load(open(path))
        else:
            p = make(T)
            if p["lam"] < 1:
                print(f"T = {T}: no plan inside the rig limits found"); continue
            d = team_format(p, T)
            json.dump(d, open(path, "w"))
        print(f"T = {T} s: effort {d['effort']:.2f}, peak {d['peak']}")
        results[f"{T:.1f}s"] = {"effort": d["effort"], "peak": d["peak"]}
        if team_dir:
            chk = check_with_team(d, team_dir, path)
            print("  checked with the team's plan_problem:", chk)
            results[f"{T:.1f}s"]["team_check"] = chk
        rob = sweep(d)
        n_ok = sum(v["ok"] for v in rob.values())
        print(f"  catches {n_ok} of {len(rob)}: fails {[k for k, v in rob.items() if not v['ok']]}")
        results[f"{T:.1f}s"]["robustness"] = rob
    json.dump(results, open(os.path.join(HERE, "longer_plans.json"), "w"), indent=1)
    print("wrote longer_plans.json")


if __name__ == "__main__":
    main()
