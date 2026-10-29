"""Make every figure and animation used by the Math/Double pages.

Run:  python double_sims.py && python make_figures.py      (about 2 minutes; numpy, scipy, matplotlib, pillow)
Reads ../data (rig logs [HW] and the stored plan) and sim_results.npz / robustness.json [SIM]. Writes ../images/.
"""
import csv
import json
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation, patches

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
import nlink_cart as nl  # noqa: E402
import double_model as dm  # noqa: E402

IMG = os.path.join(HERE, "..", "images")
DATA = os.path.join(HERE, "..", "data")
os.makedirs(IMG, exist_ok=True)
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 110, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.spines.top": False, "axes.spines.right": False})
C1, C2, CX, CP, CR = "#3b82c4", "#e8a33d", "#555555", "#9aa5b1", "#c94c4c"
L1, L2 = 0.2, 0.25
CAP = 0.831


def save(fig, name):
    fig.savefig(os.path.join(IMG, name), bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def plan():
    d = json.load(open(os.path.join(DATA, "double_swingup_trajectory.json")))
    return d, np.array(d["z"]).T, np.array(d["a_knots"])


def sim():
    return np.load(os.path.join(HERE, "sim_results.npz"))


def read_csv(path):
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = {}
    for k in rows[0]:
        vals = [r[k] for r in rows]
        try:
            out[k] = np.array([float(v) if v != "" else np.nan for v in vals])
        except ValueError:
            out[k] = np.array(vals)
    return out


def draw_rig(ax, x, th1, th2, alpha=1.0, lw=5, ghost=False):
    """Cart at x, arm 1 at absolute angle th1, arm 2 at th2 (from upright, + = toward +x)."""
    p0 = np.array([x, 0.0])
    p1 = p0 + L1 * np.array([np.sin(th1), np.cos(th1)])
    p2 = p1 + L2 * np.array([np.sin(th2), np.cos(th2)])
    if ghost:
        ax.plot([p0[0], p1[0], p2[0]], [p0[1], p1[1], p2[1]], color=CP, lw=2, alpha=alpha, ls="--")
        return
    ax.add_patch(patches.FancyBboxPatch((x - 0.06, -0.035), 0.12, 0.05, boxstyle="round,pad=0.004",
                                        fc="#dbe7f3", ec="k", alpha=alpha))
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=C1, lw=lw, solid_capstyle="round", alpha=alpha)
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=C2, lw=lw, solid_capstyle="round", alpha=alpha)
    ax.plot(*p0, "ko", ms=4, alpha=alpha)
    ax.plot(*p1, "ko", ms=4, alpha=alpha)


def track(ax, lim=0.40, abort=0.36, plan_lim=0.25):
    ax.plot([-lim - 0.04, lim + 0.04], [-0.04, -0.04], color="k", lw=2)
    for xx, c in ((plan_lim, "#7aa974"), (abort, CR), (lim, "k")):
        for s in (-1, 1):
            ax.plot([s * xx, s * xx], [-0.075, -0.005], color=c, lw=1.2)


# ---------------------------------------------------------------- F1 coordinates
def fig_coordinates():
    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    ax.set_aspect("equal"); ax.axis("off"); ax.grid(False)
    ax.plot([-0.30, 0.62], [-0.04, -0.04], color="k", lw=2)
    x = 0.0
    th1, th2 = np.radians(20), np.radians(-25)
    draw_rig(ax, x, th1, th2, lw=7)
    p1 = np.array([x + L1 * np.sin(th1), L1 * np.cos(th1)])
    p2 = p1 + L2 * np.array([np.sin(th2), np.cos(th2)])
    c1 = np.array([x + 0.087 * np.sin(th1), 0.087 * np.cos(th1)])
    c2 = p1 + 0.106 * np.array([np.sin(th2), np.cos(th2)])
    for c, col in ((c1, C1), (c2, C2)):
        ax.plot(*c, "o", ms=11, mfc="white", mec=col, mew=2.5)
    ax.plot([x, x], [0, 0.50], color="k", ls=":", lw=1)
    ax.plot([p1[0], p1[0]], [p1[1], p1[1] + 0.27], color="k", ls=":", lw=1)
    a = np.linspace(0, th1, 30)
    ax.plot(x + 0.13 * np.sin(a), 0.13 * np.cos(a), "k", lw=1)
    ax.text(x + 0.012, 0.145, r"$\theta_1$", fontsize=13)
    a = np.linspace(0, th2, 30)
    ax.plot(p1[0] + 0.13 * np.sin(a), p1[1] + 0.13 * np.cos(a), "k", lw=1)
    ax.text(p1[0] - 0.05, p1[1] + 0.145, r"$\theta_2$", fontsize=13)
    a = np.linspace(th1, th2, 30)
    ax.plot(p1[0] + 0.07 * np.sin(a), p1[1] + 0.07 * np.cos(a), color="#7a4fb5", lw=1.8)
    lab = dict(fontsize=9, va="center")
    ax.annotate(r"$\varphi=\theta_2-\theta_1$ (what encoder 2 measures)", p1 + [0.0, 0.07], xytext=(0.20, 0.36),
                color="#7a4fb5", arrowprops=dict(arrowstyle="-", color="#7a4fb5"), **lab)
    ax.annotate(r"arm 2: $L_2$ = 250 mm, $m_2$ = 210 g, $c_2$ = 106 mm," "\n" r"$I_2$ = 1.976e-3 kg m$^2$ about its CoM",
                c2, xytext=(0.20, 0.27), color=C2, arrowprops=dict(arrowstyle="-", color=C2), **lab)
    ax.annotate(r"joint (encoder 2, on arm 1's tip)", p1, xytext=(0.20, 0.18), arrowprops=dict(arrowstyle="-"), **lab)
    ax.annotate(r"arm 1: $L_1$ = 200 mm, $m_1$ = 207 g, $c_1$ = 87 mm," "\n" r"$I_1$ = 1.233e-3 kg m$^2$ about its CoM",
                c1, xytext=(0.20, 0.09), color=C1, arrowprops=dict(arrowstyle="-", color=C1), **lab)
    ax.annotate("main pivot (encoder 1)", (x, 0.0), xytext=(0.20, 0.015), arrowprops=dict(arrowstyle="-"), **lab)
    ax.annotate("", xy=(0.28, -0.075), xytext=(0.0, -0.075), arrowprops=dict(arrowstyle="->"))
    ax.text(0.14, -0.10, r"cart $x$ (+ to the right), $\dot x = v$, $\ddot x = a$; cart 0.910 kg", fontsize=9, ha="center")
    ax.text(-0.30, 0.14, "Team convention (double scripts):\nangles from upright, ABSOLUTE,\n+ = centre of mass toward +x",
            fontsize=9, va="top", bbox=dict(fc="#f5f5f5", ec="#bbb"))
    ax.set_xlim(-0.31, 0.63); ax.set_ylim(-0.12, 0.52)
    save(fig, "fig01_coordinates.png")


# ---------------------------------------------------------------- F2 modes
def fig_modes():
    rig = dm.PHYS
    wh, Vh = dm.hanging_modes(rig)
    su, Vu = dm.upright_modes(rig)
    fig, axs = plt.subplots(1, 4, figsize=(11, 3.6))
    wh, su = np.real(wh), np.real(su)
    titles = [f"hanging, slow mode\n{wh[0]:.2f} rad/s (period {2 * np.pi / wh[0]:.2f} s)",
              f"hanging, fast mode\n{wh[1]:.2f} rad/s (period {2 * np.pi / wh[1]:.2f} s)",
              f"upright, slow mode\ngrows as e^({su[0]:.1f} t)", f"upright, fast mode\ngrows as e^({su[1]:.1f} t)"]
    shapes = [(np.pi, Vh[:, 0]), (np.pi, Vh[:, 1]), (0.0, Vu[:, 0]), (0.0, Vu[:, 1])]
    for ax, ttl, (base, v) in zip(axs, titles, shapes):
        ax.set_aspect("equal"); ax.axis("off"); ax.grid(False)
        v = np.real(v) / np.max(np.abs(np.real(v))) * 0.45
        for s, al in ((1, 1.0), (-1, 0.35)):
            draw_rig(ax, 0.0, base + s * v[0], base + s * v[1], alpha=al, lw=4)
        ax.set_xlim(-0.35, 0.35); ax.set_ylim(-0.5, 0.5)
        ax.set_title(ttl, fontsize=9.5)
        ax.text(0, -0.48 if base == 0 else 0.42, f"θ2/θ1 = {np.real(v[1] / v[0]):+.2f}", ha="center", fontsize=9)
    fig.suptitle("The two ways a double pendulum moves on its own (physical values, cart held still)", fontsize=10.5, y=1.08)
    save(fig, "fig02_modes.png")


# ---------------------------------------------------------------- F3 poles: single, double, triple
def fig_poles():
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    single = nl.Rig([nl.Link(0.26, 0.05, 0.2, 0.001751)])
    from importlib import util
    tri = None
    tp = os.path.join(HERE, "..", "..", "Triple", "sims", "triple_model.py")
    if os.path.exists(tp):
        spec = util.spec_from_file_location("tm", tp); tm = util.module_from_spec(spec); spec.loader.exec_module(tm)
        tri = tm.TRIPLE
    rows = [("single (identified I)", single), ("double", dm.PHYS)] + ([("triple [HYP]", tri)] if tri else [])
    for i, (lab, rig) in enumerate(rows):
        A, _ = nl.linear_accel(rig)
        ev = np.sort(np.linalg.eigvals(A).real)
        ax.scatter(ev, np.full_like(ev, i), s=60, c=[CR if e > 1e-9 else (C1 if e < -1e-9 else CX) for e in ev], zorder=3)
        for e in ev[ev > 1e-9]:
            ax.annotate(f"+{e:.1f}", (e, i), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8.5)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlabel("pole (1/s), cart acceleration as the input; red = unstable (falls over)")
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_title("Each extra link adds one unstable pole, and the fastest one gets faster", fontsize=10)
    save(fig, "fig03_poles.png")


# ---------------------------------------------------------------- F4 lean of arm 2: the cart first moves away
def fig_lean():
    s = sim()
    t, z, a = s["lean_t"], s["lean_z"], s["lean_a"]
    m = t < 1.6
    fig, axs = plt.subplots(3, 1, figsize=(7.5, 6.4), sharex=True)
    axs[0].plot(t[m], np.degrees(z[m, 0]), color=C1, label="arm 1, θ1")
    axs[0].plot(t[m], np.degrees(z[m, 2]), color=C2, label="arm 2, θ2")
    axs[0].set_ylabel("deg"); axs[0].legend(fontsize=8)
    axs[1].plot(t[m], a[m], color=CX); axs[1].set_ylabel("cart accel. command\nm/s²")
    axs[2].plot(t[m], 1000 * z[m, 4], color=CX); axs[2].set_ylabel("cart mm"); axs[2].set_xlabel("time (s)")
    axs[0].set_title("Balance controller [SIM]: arm 2 starts leaning 1° toward +x, arm 1 upright", fontsize=10)
    axs[1].annotate("first: cart accelerates toward -x\n(tips arm 1 toward +x, under arm 2)", (0.02, a[2]),
                    xytext=(0.45, -3.8), fontsize=8.5, arrowprops=dict(arrowstyle="->"))
    save(fig, "fig04_lean_response.png")


# ---------------------------------------------------------------- F5 rig balance (767 s run)
def fig_balance_hw():
    b = read_csv(os.path.join(DATA, "hw_double_balance_20261021_161621_10hz.csv"))
    t = b["elapsed_s"] - b["elapsed_s"][0]
    fig, axs = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    axs[0].plot(t, b["measured_angle_1_deg"], color=C1, lw=0.6, label="arm 1")
    axs[0].plot(t, b["measured_angle_2_deg"], color=C2, lw=0.6, label="arm 2 (absolute)")
    axs[0].set_ylabel("angle from the\nreference, deg"); axs[0].legend(fontsize=8, loc="upper right")
    axs[1].plot(t, 1000 * b["cart_m"], color=CX, lw=0.6); axs[1].set_ylabel("cart mm")
    ref1 = b["reference_upright_1_counts"]; ref2 = b["reference_aligned_2_counts"]
    axs[2].plot(t, (ref1 - ref1[0]) * 360 / 16384, color=C1, label="arm 1 reference shift")
    axs[2].plot(t, (ref2 - ref2[0]) * 360 / 16384, color=C2, label="joint reference shift")
    axs[2].set_ylabel("auto-trim, deg"); axs[2].set_xlabel("time (s)"); axs[2].legend(fontsize=8)
    ok = t > 10
    txt = (f"after 10 s: arm 1 std {np.nanstd(b['measured_angle_1_deg'][ok]):.2f}°, arm 2 std "
           f"{np.nanstd(b['measured_angle_2_deg'][ok]):.2f}°, cart std {1000 * np.nanstd(b['cart_m'][ok]):.1f} mm")
    axs[0].set_title(f"Rig [HW]: balance_double_20261021_161621, PythonMasterDouble-Claude.py, {t[-1]:.0f} s\n{txt}",
                     fontsize=10)
    save(fig, "fig05_balance_hw.png")
    return txt


# ---------------------------------------------------------------- F6 plan
def fig_plan():
    d, Z, a = plan()
    t = np.arange(Z.shape[1]) * 0.01
    lim = d["limits"]
    fig, axs = plt.subplots(4, 1, figsize=(8.5, 8.2), sharex=True)
    axs[0].plot(t, np.degrees(Z[0]), color=C1, label="θ1")
    axs[0].plot(t, np.degrees(Z[2]), color=C2, label="θ2")
    for yy in (0, 180, 360):
        axs[0].axhline(yy, color="k", lw=0.5, ls=":")
    axs[0].set_ylabel("deg (0 = upright,\n180 = hanging)"); axs[0].legend(fontsize=8, ncol=2)
    axs[1].plot(t, Z[4], color=CX); axs[1].axhline(lim["track_m"], color="#7aa974", ls="--"); axs[1].axhline(-lim["track_m"], color="#7aa974", ls="--")
    axs[1].set_ylabel("cart x (m)")
    axs[2].plot(t, Z[5], color=CX); axs[2].axhline(lim["speed_m_s"], color="#7aa974", ls="--"); axs[2].axhline(-lim["speed_m_s"], color="#7aa974", ls="--")
    axs[2].axhline(CAP, color=CR, ls=":"); axs[2].axhline(-CAP, color=CR, ls=":")
    axs[2].text(0.02, CAP + 0.03, "0.831 m/s: fastest speed the rig reaches when accelerating (see 06)", color=CR, fontsize=8)
    axs[2].set_ylabel("cart speed (m/s)")
    axs[3].plot(t, a, color=CX, label="planned acceleration")
    v = Z[5]
    env = lim["accel_m_s2"] * (1 - np.abs(v) / lim["motor_top_speed_m_s"])
    lo = np.where(v > 0, -lim["accel_m_s2"], -env)
    hi = np.where(v > 0, env, lim["accel_m_s2"])
    axs[3].fill_between(t, lo, hi, color="#7aa974", alpha=0.15, label="allowed: full braking, less push at speed")
    axs[3].set_ylabel("m/s²"); axs[3].set_xlabel("time (s)"); axs[3].legend(fontsize=8, loc="lower left")
    axs[0].set_title(f"The stored plan double_swingup_trajectory.json (made {d['made'][:10]}): "
                     f"{d['T']:.1f} s, effort ∫a²dt = {d['effort']:.1f}", fontsize=10)
    save(fig, "fig06_plan.png")


def fig_plan_strobe():
    d, Z, a = plan()
    ks = list(range(0, 251, 10))
    fig, axs = plt.subplots(3, 9, figsize=(13, 5.2))
    for ax in axs.ravel():
        ax.set_aspect("equal"); ax.axis("off"); ax.grid(False)
    for ax, k in zip(axs.ravel(), ks):
        ax.plot([-0.3, 0.3], [-0.04, -0.04], color="k", lw=1)
        for s_ in (-0.25, 0.25):
            ax.plot([s_, s_], [-0.06, -0.02], color="#7aa974", lw=1)
        draw_rig(ax, Z[4, k], Z[0, k], Z[2, k], lw=3)
        ax.set_xlim(-0.48, 0.48); ax.set_ylim(-0.48, 0.48)
        ax.set_title(f"{k / 100:.1f} s   v {Z[5, k]:+.2f}", fontsize=8)
    fig.suptitle("The stored plan every 0.1 s (green ticks: the plan's ±0.25 m track limit)", fontsize=10.5)
    save(fig, "fig07_plan_strobe.png")


# ---------------------------------------------------------------- F8 TV-LQR gains
def fig_gains():
    s = sim()
    Ks = s["Ks"]; Kb = s["Kbal"][0]
    t = np.arange(len(Ks)) * 0.01
    names = ["θ1 (m/s² per rad)", "θ̇1 (per rad/s)", "θ2 (per rad)", "θ̇2 (per rad/s)", "x (per m)", "v (per m/s)",
             "a_prev (per m/s²)"]
    fig, axs = plt.subplots(4, 2, figsize=(10, 8.5), sharex=True)
    for i, ax in enumerate(axs.ravel()[:7]):
        ax.plot(t, Ks[:, i], color=[C1, C1, C2, C2, CX, CX, CP][i])
        ax.axhline(Kb[i], color="k", ls=":", lw=1)
        ax.set_title(names[i], fontsize=9)
    axs[-1, -1].axis("off")
    axs[-1, -1].text(0.0, 0.5, "solid: time-varying gain K_k along the plan\ndotted: the balance gain it hands over to\n\n"
                     "a = a_ref[k] - K_k (state - plan[k])", fontsize=9, va="center")
    for ax in axs[-1]:
        ax.set_xlabel("time in the plan (s)")
    fig.suptitle("TV-LQR gains of PythonMaster2_swingup.py along the stored plan (recomputed, match the script)", fontsize=10.5)
    save(fig, "fig08_tvlqr_gains.png")


# ---------------------------------------------------------------- F9 swing sim
def fig_swing_sim():
    s = sim()
    d, Z, a = plan()
    tp = np.arange(Z.shape[1]) * 0.01
    fig, axs = plt.subplots(3, 1, figsize=(8.5, 7), sharex=True)
    for key, ls, lab in (("sw", "-", "model = arms (catches)"), ("b2", "--", "real joint friction ×1.5 (fails)")):
        t, z = s[key + "_t"], s[key + "_z"]
        axs[0].plot(t, np.degrees(np.unwrap(z[:, 0])), color=C1, ls=ls)
        axs[0].plot(t, np.degrees(np.unwrap(z[:, 2])), color=C2, ls=ls)
        axs[1].plot(t, z[:, 4], color=CX, ls=ls, label=lab)
        axs[2].plot(t, s[key + "_v"], color=CX, ls=ls)
    axs[0].plot(tp, np.degrees(Z[0]), color=CP, lw=4, alpha=0.4, zorder=0)
    axs[0].plot(tp, np.degrees(Z[2]), color=CP, lw=4, alpha=0.4, zorder=0, label="plan")
    axs[0].legend(fontsize=8); axs[0].set_ylabel("θ1 (blue), θ2 (orange), deg")
    axs[1].plot(tp, Z[4], color=CP, lw=4, alpha=0.4, zorder=0)
    axs[1].axhline(-0.36, color=CR, ls=":"); axs[1].axhline(0.36, color=CR, ls=":")
    axs[1].set_ylabel("cart (m)"); axs[1].legend(fontsize=8)
    axs[2].plot(tp, Z[5], color=CP, lw=4, alpha=0.4, zorder=0)
    axs[2].axhline(CAP, color=CR, ls=":"); axs[2].axhline(-CAP, color=CR, ls=":")
    axs[2].set_ylabel("speed sent (m/s)"); axs[2].set_xlabel("time (s)")
    axs[0].set_xlim(0, 4.5)
    axs[0].set_title("PythonMaster2_swingup.py in simulation [SIM]: plan (grey), catch at 2.5 s, balance", fontsize=10)
    save(fig, "fig09_swing_sim.png")


# ---------------------------------------------------------------- F10 robustness
def fig_robustness():
    rob = json.load(open(os.path.join(HERE, "robustness.json")))
    cases = [c for c in rob["cases"] if c["timer"]]
    ex = {c["case"]: c for c in rob["cases"] if not c["timer"]}
    groups = ["P1", "P2", "J2r", "H"]
    pcts = [-8, -6, -4, -2, 2, 4, 6, 8]
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.6), gridspec_kw=dict(width_ratios=[2.2, 1]))
    ax = axs[0]
    for gi, g in enumerate(groups):
        for pi, p in enumerate(pcts):
            name = f"{g} {p:+d}%"
            c = next(x for x in cases if x["case"] == name)
            e = ex[name]
            ax.add_patch(patches.Rectangle((pi, gi), 0.95, 0.45, color="#7aa974" if c["ok"] else CR))
            ax.add_patch(patches.Rectangle((pi, gi + 0.47), 0.95, 0.45, color="#7aa974" if e["ok"] else CR, alpha=0.55))
    ax.set_xlim(0, len(pcts)); ax.set_ylim(0, len(groups))
    ax.set_xticks(np.arange(len(pcts)) + 0.47); ax.set_xticklabels([f"{p:+d}%" for p in pcts])
    ax.set_yticks(np.arange(len(groups)) + 0.47); ax.set_yticklabels(groups)
    ax.grid(False)
    ax.set_title("Real arms differ from the plan's model by...  (green catch, red fail)\n"
                 "lower half of each cell: as on the rig (timer rounding); upper half: exact speeds", fontsize=9.5)
    ax = axs[1]
    other = [c for c in cases if c["case"].startswith(("B2", "B1", "delay"))]
    ax.barh(range(len(other)), [1] * len(other), color=["#7aa974" if c["ok"] else CR for c in other])
    ax.set_yticks(range(len(other))); ax.set_yticklabels([c["case"] for c in other], fontsize=8.5)
    ax.set_xticks([]); ax.grid(False)
    ax.set_title("friction and motor delay", fontsize=9.5)
    fig.suptitle("Which model errors the double swing-up survives [SIM] (one error at a time, stored plan)", fontsize=10.5, y=1.07)
    save(fig, "fig10_robustness.png")


# ---------------------------------------------------------------- F11 rig attempt vs plan
def fig_hw_attempts():
    h = read_csv(os.path.join(DATA, "hw_double_swingup_20261027_184605.csv"))
    d, Z, a = plan()
    k = np.array([int(m.group(1)) if (m := re.search(r"k=(\d+)", str(s))) else -1 for s in h["message"]])
    swing = np.array(["mode=SWING" in str(s) for s in h["message"]])
    starts = np.where(swing & (k == 0))[0]
    fig, axs = plt.subplots(3, 1, figsize=(8.5, 7.5), sharex=True)
    tp = np.arange(Z.shape[1]) * 0.01
    for j, s0 in enumerate(starts):
        e = s0
        while e + 1 < len(k) and swing[e + 1]:
            e += 1
        kk = k[s0:e + 1]
        tt = kk * 0.01
        al = 0.35 + 0.65 * j / max(1, len(starts) - 1)
        e1 = np.degrees(nl.wrap(h["est_theta1_rad"][s0:e + 1] - Z[0, kk]))
        e2 = np.degrees(nl.wrap(h["est_theta2_rad"][s0:e + 1] - Z[2, kk]))
        axs[0].plot(tt, e1, color=C1, alpha=al)
        axs[0].plot(tt, e2, color=C2, alpha=al)
        axs[1].plot(tt, h["cart_m"][s0:e + 1], color=CX, alpha=al)
        tm = h["motor_timer_command"][s0:e + 1]
        vs = -np.sign(tm) * 125000.0 / (np.abs(tm) + 1) * 0.638175 / 6400
        axs[2].plot(tt, vs, color=CX, alpha=al)
    axs[0].axhline(35, color=CR, ls=":"); axs[0].axhline(-35, color=CR, ls=":")
    axs[0].set_ylabel("estimate minus plan, deg\n(blue arm 1, orange arm 2)")
    axs[1].plot(tp, Z[4], color=CP, lw=4, alpha=0.5, zorder=0, label="plan")
    axs[1].axhline(-0.36, color=CR, ls=":"); axs[1].axhline(0.36, color=CR, ls=":"); axs[1].legend(fontsize=8)
    axs[1].set_ylabel("cart (m)")
    axs[2].plot(tp, Z[5], color=CP, lw=4, alpha=0.5, zorder=0)
    axs[2].axhline(CAP, color=CR, ls=":"); axs[2].axhline(-CAP, color=CR, ls=":")
    axs[2].set_ylabel("speed the Arduino ran (m/s)"); axs[2].set_xlabel("time in the plan (s)")
    axs[0].set_title(f"Rig [HW]: swingup_double_20261027_184605, {len(starts)} attempts with this plan, all aborted",
                     fontsize=10)
    save(fig, "fig11_hw_attempts.png")


# ---------------------------------------------------------------- F12 the speed cap
def fig_speed_cap():
    fig, ax = plt.subplots(figsize=(8, 4))
    vreq = np.linspace(0.70, 0.95, 2000)
    vgot = np.array([nl.timer_speed(v) for v in vreq])
    ax.plot(vreq, vgot, color=CX, label="speed the Arduino runs (timer rounding)")
    ax.plot(vreq, vreq, color=CP, ls="--", label="requested")
    v0 = CAP
    reach = v0 + 16 * (1 - v0 / 1.0) * 0.01
    ax.axvline(reach, color=CR, ls=":")
    ax.annotate(f"from {v0:.3f} m/s the torque limit allows\n16·(1-{v0:.3f}/1.0) = {16 * (1 - v0):.1f} m/s² → request "
                f"≤ {reach:.3f} m/s,\nwhich rounds back to {v0:.3f}", (reach, v0), xytext=(0.705, 0.89), fontsize=8.5,
                arrowprops=dict(arrowstyle="->"))
    for N in range(12, 17):
        v = 125000 / (N + 1) * 0.638175 / 6400
        ax.text(0.952, v, f"timer {N}: {v:.3f}", fontsize=7.5, va="center")
    ax.set_xlabel("requested speed (m/s)"); ax.set_ylabel("real speed (m/s)")
    ax.set_xlim(0.70, 1.0); ax.set_ylim(0.68, 0.98); ax.legend(fontsize=8, loc="lower right")
    ax.set_title("Why every rig swing-up attempt tops out at 0.831 m/s [HW]", fontsize=10)
    save(fig, "fig12_speed_cap.png")


# ---------------------------------------------------------------- GIFs
def anim(name, frames, title, xlim=(-0.46, 0.46), fps=25, plan_ghost=None, ylim=(-0.5, 0.5)):
    w = 4.8 * (xlim[1] - xlim[0]) / (ylim[1] - ylim[0])
    fig, ax = plt.subplots(figsize=(max(w, 3.6), 5.0))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.88)

    def draw(i):
        ax.clear(); ax.set_aspect("equal"); ax.grid(False); ax.axis("off")
        track(ax)
        f = frames[i]
        if plan_ghost is not None and f.get("k") is not None and 0 <= f["k"] < plan_ghost.shape[1]:
            zz = plan_ghost[:, f["k"]]
            draw_rig(ax, zz[4], zz[0], zz[2], ghost=True, alpha=0.8)
        draw_rig(ax, f["x"], f["th1"], f["th2"])
        ax.set_xlim(*xlim); ax.set_ylim(*ylim)
        ax.set_title(f"{title}\nt = {f['t']:.2f} s   {f.get('label', '')}", fontsize=8.5)
    an = animation.FuncAnimation(fig, draw, frames=len(frames), interval=1000 / fps)
    an.save(os.path.join(IMG, name), writer=animation.PillowWriter(fps=fps), dpi=85)
    plt.close(fig)
    print("wrote", name)


def gifs():
    s = sim()
    d, Z, a = plan()
    t, z, kk = s["sw_t"], s["sw_z"], s["sw_k"]
    fr = [dict(t=t[i], x=z[i, 4], th1=z[i, 0], th2=z[i, 2], k=int(kk[i]) if t[i] < 2.5 else None,
               label="SWING (dashed: plan)" if t[i] < 2.5 else "BALANCE") for i in range(0, min(len(t), 450), 4)]
    anim("anim_double_swingup_sim.gif", fr, "PythonMaster2_swingup.py [SIM]", plan_ghost=Z)
    h = read_csv(os.path.join(DATA, "hw_double_swingup_20261027_184605.csv"))
    k = np.array([int(m.group(1)) if (m := re.search(r"k=(\d+)", str(q))) else -1 for q in h["message"]])
    s0 = np.where(k == 0)[0][0]
    e = s0
    while e + 1 < len(k) and "SWING" in str(h["message"][e + 1]):
        e += 1
    e = min(e + 25, len(k) - 1)
    th1 = h["measured_angle_1_rad"]; th2 = h["measured_angle_2_rad"]
    fr = [dict(t=(i - s0) * 0.01, x=h["cart_m"][i], th1=th1[i], th2=th2[i], k=int(k[i]) if k[i] >= 0 else None,
               label=("SWING k=%d" % k[i]) if k[i] >= 0 else "aborted: braking") for i in range(s0, e + 1, 3)]
    anim("anim_double_swingup_hw.gif", fr, "Rig [HW] swingup_double_20261027_184605, attempt 1", plan_ghost=Z, fps=33)
    bt, bz = s["bal_t"], s["bal_z"]
    m = (bt > 2.6) & (bt < 5.6)
    fr = [dict(t=bt[i], x=bz[i, 4], th1=bz[i, 0] * 5, th2=bz[i, 2] * 5,
               label=("tap on arm 2 (+0.3 rad/s) at 3.00 s" if bt[i] >= 3.0 else "balanced") + "; angles drawn x5")
          for i in np.where(m)[0][::3]]
    anim("anim_double_balance_sim.gif", fr, "PythonMasterDouble-Claude.py balance [SIM]", xlim=(-0.3, 0.3),
         ylim=(-0.1, 0.5), fps=33)


if __name__ == "__main__":
    fig_coordinates()
    fig_modes()
    fig_poles()
    fig_lean()
    print(fig_balance_hw())
    fig_plan()
    fig_plan_strobe()
    fig_gains()
    fig_swing_sim()
    fig_robustness()
    fig_hw_attempts()
    fig_speed_cap()
    gifs()
