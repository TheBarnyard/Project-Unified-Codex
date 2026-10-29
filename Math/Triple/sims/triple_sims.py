"""Closed-loop simulations of a triple pendulum on the double rig, with the double scripts' controllers [SIM, HYP rig].

Run:  python triple_sims.py           (about 5-10 minutes; writes sim_results.npz and triple_sims.json)

  1. balance: PythonMasterDouble-Claude.py's loop with n = 3 (Kalman filter, a = -K [x_hat; a_prev], limits
     15 m/s^2 and 0.8 m/s, auto-trim, no start ramp), start 0.5/0/0.3 deg, encoder references 0.2/-0.1/0.1 deg
     off, a 0.1 rad/s tap on arm 3 at 5 s;
  2. balance limits: the largest start lean and the largest tap on each arm that it still catches;
     wobble caused by encoder noise of 1 to 5 counts;
  3. swing-up: PythonMaster2_swingup.py's loop with n = 3 (stored plan, TV-LQR, observer, catch, balance)
     on each plan in ../data, with the Arduino's timer rounding and 1-count encoder noise;
  4. swing-up robustness: real arms different from the model (one physical value at a time, or one entry of
     p or H alone), joint friction, motor delay.
The plans were made with Math/shared/nlink_cart.plan_team_homotopy (see make_plans.py).
"""
import copy
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
import nlink_cart as nl  # noqa: E402
import swing_sim as ss  # noqa: E402
import triple_model as tm  # noqa: E402

DATA = os.path.join(HERE, "..", "data")


# ---------------------------------------------------------------- balance
def balance_once(z0deg, offs_deg=None, trim=True, T=20.0, noise=1.0, tap=None, tau=0.009, seed=0, design=None):
    """tap = (time s, state index, rad/s added): a knock on one arm."""
    d = design or tm.balance()
    z0 = np.zeros(8)
    z0[[0, 2, 4]] = np.radians(z0deg)

    def knock(t, z):
        if abs(t - tap[0]) < 1e-9:
            z = z.copy(); z[tap[1]] += tap[2]
        return z
    c = ss.TeamBalanceController(d, 3, auto_trim=trim, start_ramp=0.0)
    r = ss.run(tm.TRIPLE, c, T, tau_true=tau, noise_counts=noise, z0=z0, disturb=knock if tap else None,
               enc_offsets=None if offs_deg is None else np.radians(offs_deg), seed=seed)
    return c, r


def balance_run():
    return balance_once([0.5, 0.0, 0.3], offs_deg=[0.2, -0.1, 0.1], tap=(5.0, 5, 0.1))


def balance_limits():
    out = {}
    for arm in range(3):
        held = 0.0
        for deg in (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0):
            z0 = [0.0, 0.0, 0.0]; z0[arm] = deg
            c, _ = balance_once(z0, trim=False, T=4.0)
            if c.mode != "BALANCE":
                break
            held = deg
        tap = 0.0
        for w in (0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2, 1.5):
            c, _ = balance_once([0, 0, 0], trim=False, T=4.0, tap=(1.0, 2 * arm + 1, w))
            if c.mode != "BALANCE":
                break
            tap = w
        out[f"arm {arm + 1}"] = dict(start_lean_deg=held, tap_rad_s=tap)
        print(f"  arm {arm + 1}: catches a start lean up to {held} deg and a tap up to {tap} rad/s", flush=True)
    return out


def noise_table():
    out = {}
    for counts in (1.0, 2.0, 3.0, 5.0):
        c, r = balance_once([0, 0, 0], trim=False, T=12.0, noise=counts)
        z = r["z"][200:]
        out[str(counts)] = dict(ok=c.mode == "BALANCE", arm_std_deg=np.degrees(z[:, [0, 2, 4]].std(0)).round(3).tolist(),
                                cart_std_mm=round(1000 * float(z[:, 6].std()), 1),
                                accel_std=round(float(np.std(r["a"][200:])), 2))
        print(f"  encoder noise {counts:g} counts: {out[str(counts)]}", flush=True)
    return out


# ---------------------------------------------------------------- swing-up
def load_plan(path):
    d = json.load(open(path))
    return d, np.array(d["z"]).T


def swing_setup(path):
    d, Z = load_plan(path)
    g = ss.build(tm.TRIPLE_SWING, Z, bal_rig=tm.TRIPLE)
    return d, Z, g


def swing_once(d, Z, g, true_rig=None, tau=0.008, timer=True, noise=1.0, seed=0):
    lim = d["limits"]
    c = ss.TeamSwingController(tm.TRIPLE_SWING, Z, g["a_ref"], g["Ks"], g["bal"], g["Ls"],
                               accel_max=max(16.0, 1.5 * lim["accel_m_s2"]),
                               speed_max=max(1.0, lim["motor_top_speed_m_s"]),
                               motor_top=max(1.0, lim["motor_top_speed_m_s"]),
                               abort_cart=max(0.36, lim["track_m"] + 0.11), timer=timer)
    r = ss.run(true_rig or tm.TRIPLE_SWING, c, len(g["a_ref"]) * 0.01 + 3.0, tau_true=tau, noise_counts=noise, seed=seed)
    return r, dict(ok=bool(r["balanced"]), why=r["why"], max_v=float(np.abs(r["v_sent"]).max()),
                   max_x=float(np.abs(r["z"][:, 6]).max()))


def robustness(d, Z, g):
    base = tm.TRIPLE_SWING
    cases = [("nominal", base, 0.008)]
    for li in range(3):
        for attr, rels in (("m", (-0.05, -0.02, 0.02, 0.05)), ("I", (-0.1, -0.05, 0.05, 0.1))):
            cases += [(f"{attr}{li + 1} {rel * 100:+.0f}%", tm.physical_rig(base, li, attr, rel=rel), 0.008) for rel in rels]
        for attr in ("c", "L"):
            if attr == "L" and li == 2:
                continue
            cases += [(f"{attr}{li + 1} {mm:+d} mm", tm.physical_rig(base, li, attr, add=mm / 1000), 0.008)
                      for mm in (-3, -1, 1, 3)]
    for mult in (0.5, 1.5):
        r = copy.deepcopy(base); r.links[1].b *= mult; r.links[2].b *= mult
        cases.append((f"joint friction x{mult:g}", r, 0.008))
    cases += [("delay 5 ms", base, 0.005), ("delay 12 ms", base, 0.012)]
    for kind, idx, nm in tm.ENTRIES[3]:
        cases += [(f"{nm} alone {pct:+d}%", tm.entry_rig(base, kind, idx, pct), 0.008) for pct in (-1, 1)]
    out = {}
    for name, rig, tau in cases:
        _, s = swing_once(d, Z, g, rig, tau)
        out[name] = s
        print(f"  {name:22s} {'CATCH' if s['ok'] else 'fail ':5s} {s['why']}", flush=True)
    return out


def main():
    res, js = {}, {}
    print("1. balance run")
    c, r = balance_run()
    print(f"  {c.mode}, trims found (deg) {np.degrees(r['trim'][-1]).round(3)}")
    for k in ("t", "z", "a", "v_sent", "trim"):
        res["bal_" + k] = r[k]
    print("2. balance limits")
    js["balance_limits"] = balance_limits()
    js["noise"] = noise_table()
    js["delay"] = {}
    for tau in (0.012, 0.014, 0.016):
        c, _ = balance_once([0.5, 0, 0.3], trim=False, T=6.0, tau=tau)
        js["delay"][str(tau)] = c.mode
        print(f"  real motor delay {tau * 1000:.0f} ms: {c.mode}")
    print("3./4. swing-up")
    js["swing"] = {}
    for path in sorted(glob.glob(os.path.join(DATA, "triple_swingup_plan_*.json"))):
        name = os.path.basename(path)[len("triple_swingup_plan_"):-5]
        d, Z, g = swing_setup(path)
        r, s = swing_once(d, Z, g)
        print(f" plan {name}: {s}")
        js["swing"][name] = dict(nominal=s)
        for k in ("t", "z", "a", "v_sent", "mode", "k"):
            res[f"sw_{name}_{k}"] = r[k]
        res[f"sw_{name}_aref"] = g["a_ref"]
        res[f"sw_{name}_K"] = np.array([K[0] for K in g["Ks"]])
        if d.get("robustness", False):
            js["swing"][name]["robustness"] = robustness(d, Z, g)
    np.savez_compressed(os.path.join(HERE, "sim_results.npz"), **res)
    json.dump(js, open(os.path.join(HERE, "triple_sims.json"), "w"), indent=1)
    print("wrote sim_results.npz, triple_sims.json")


if __name__ == "__main__":
    main()
