"""Closed-loop simulations of the team's double-pendulum scripts [SIM].

Run:  python double_sims.py            (about 2-4 minutes; writes sim_results.npz and robustness.json)

  1. swing-up: PythonMaster2_swingup.py's controller (stored plan, TV-LQR, catch, balance) on the model
     the plan was made for, with 1-count encoder noise and the Arduino's timer rounding;
  2. robustness: the same with the real arms different from the model (one ratio at a time), more
     joint/pivot friction, a different motor delay, and with the timer rounding switched off;
  3. balance: PythonMasterDouble-Claude.py's controller, start 1 deg off, a 0.3 rad/s tap on arm 2 at 3 s,
     encoder references 0.5 and -0.3 deg off (auto-trim finds them).
The stored plan (double_swingup_trajectory.json, made 2026-10-27 for the swing-fit ratios) is in ../data.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
import nlink_cart as nl  # noqa: E402
import swing_sim as ss  # noqa: E402
import double_model as dm  # noqa: E402

PLAN_FILE = os.path.join(HERE, "..", "data", "double_swingup_trajectory.json")


def load_plan():
    d = json.load(open(PLAN_FILE))
    return d, np.array(d["z"]).T


def swing_setup(plan_ratios):
    rig = nl.Rig.from_team_ratios(plan_ratios)
    rb = dict(plan_ratios); rb["B2"] = 0.03                     # BALANCE_B2
    _, Z = load_plan()
    g = ss.build(rig, Z, bal_rig=nl.Rig.from_team_ratios(rb))
    return rig, Z, g


def swing_once(rig_model, Z, g, true_ratios, tau_true=0.008, T=6.0, noise=1.0, timer=True, seed=0):
    c = ss.TeamSwingController(rig_model, Z, g["a_ref"], g["Ks"], g["bal"], g["Ls"], timer=timer)
    res = ss.run(nl.Rig.from_team_ratios(true_ratios), c, T, tau_true=tau_true, noise_counts=noise, seed=seed)
    z = res["z"]
    return res, dict(ok=bool(res["balanced"]), why=res["why"], k_end=int(res["k"][-1]),
                     max_v=float(np.abs(res["v_sent"]).max()), max_x=float(np.abs(z[:, 4]).max()),
                     capped=bool(np.any(np.isclose(np.abs(res["v_sent"]), 0.8310, atol=5e-4))))


def robustness(rig, Z, g, r0):
    cases = [("nominal", {}, 0.008)]
    for key in ("P1", "P2", "J2r", "H"):
        for pct in (-8, -6, -4, -2, 2, 4, 6, 8):
            cases.append((f"{key} {pct:+d}%", {key: r0[key] * (1 + pct / 100)}, 0.008))
    for mult in (0.5, 1.5, 2.0, 3.0):
        cases.append((f"B2 x{mult:g}", {"B2": r0["B2"] * mult}, 0.008))
    for add in (0.02, 0.05, 0.1):
        cases.append((f"B1 +{add:g}", {"B1": r0["B1"] + add}, 0.008))
    for lat in (0.005, 0.006, 0.010, 0.012):
        cases.append((f"delay {lat * 1000:.0f} ms", {}, lat))
    out = []
    for timer in (True, False):
        for name, ch, lat in cases:
            r = dict(r0); r.update(ch)
            _, s = swing_once(rig, Z, g, r, tau_true=lat, timer=timer)
            s.update(case=name, timer=timer)
            out.append(s)
            print(f"  {'timer' if timer else 'exact'} {name:14s} {'CATCH' if s['ok'] else 'fail '} {s['why']:28s} "
                  f"max v {s['max_v']:.3f} max x {s['max_x']:.3f}")
    return out


def balance_run():
    b = dm.balance_claude()
    rig = nl.Rig.from_team_ratios(dm.RATIOS["balance script SYSID (PythonMasterDouble-Claude.py)"])
    z0 = np.array([np.radians(1.0), 0, 0, 0, 0, 0])

    def tap(t, z):
        if abs(t - 3.0) < 1e-9:
            z = z.copy(); z[3] += 0.3
        return z
    c = ss.TeamBalanceController(b, 2)
    return ss.run(rig, c, 20.0, tau_true=0.009, noise_counts=1.0, z0=z0, disturb=tap,
                  enc_offsets=[np.radians(0.5), np.radians(-0.3)])


def lean_response():
    """Arm 2 alone starts 1 deg toward +x, everything else zero: what does the balance controller do first?"""
    b = dm.balance_claude()
    rig = nl.Rig.from_team_ratios(dm.RATIOS["balance script SYSID (PythonMasterDouble-Claude.py)"])
    c = ss.TeamBalanceController(b, 2, auto_trim=False, start_ramp=0.0)
    return ss.run(rig, c, 3.0, tau_true=0.009, z0=np.array([0, 0, np.radians(1.0), 0, 0, 0]))


def main():
    d, Z = load_plan()
    r0 = d["model_ratios"]
    t0 = time.time()
    rig, Z, g = swing_setup(r0)
    print(f"gains built in {time.time() - t0:.1f} s")
    res, s = swing_once(rig, Z, g, r0)
    print("nominal swing-up:", s)
    res_b2, s_b2 = swing_once(rig, Z, g, {**r0, "B2": r0["B2"] * 1.5})
    print("B2 x1.5:", s_b2)
    res_b2x, s_b2x = swing_once(rig, Z, g, {**r0, "B2": r0["B2"] * 1.5}, timer=False)
    print("B2 x1.5, no timer rounding:", s_b2x)
    bal = balance_run()
    print("balance: mode", bal["mode"][-1], "trim deg", np.degrees(bal["trim"][-1]))
    lean = lean_response()
    rob = robustness(rig, Z, g, r0)
    np.savez_compressed(os.path.join(HERE, "sim_results.npz"),
                        sw_t=res["t"], sw_z=res["z"], sw_xhat=res["x_hat"], sw_v=res["v_sent"], sw_vcmd=res["v_cmd"],
                        sw_a=res["a"], sw_k=res["k"],
                        b2_t=res_b2["t"], b2_z=res_b2["z"], b2_v=res_b2["v_sent"], b2_vcmd=res_b2["v_cmd"], b2_k=res_b2["k"],
                        b2x_t=res_b2x["t"], b2x_z=res_b2x["z"], b2x_v=res_b2x["v_sent"],
                        bal_t=bal["t"], bal_z=bal["z"], bal_a=bal["a"], bal_trim=bal["trim"], bal_v=bal["v_sent"],
                        lean_t=lean["t"], lean_z=lean["z"], lean_a=lean["a"],
                        a_ref=g["a_ref"], Ks=np.vstack(g["Ks"]), Kbal=g["bal"]["K"])
    with open(os.path.join(HERE, "robustness.json"), "w") as fh:
        json.dump(dict(nominal=s, b2x15=s_b2, b2x15_exact=s_b2x, cases=rob), fh, indent=1)
    print("wrote sim_results.npz, robustness.json")


if __name__ == "__main__":
    main()
