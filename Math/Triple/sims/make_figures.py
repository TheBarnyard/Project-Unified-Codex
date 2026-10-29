"""Make every figure and animation used by the Math/Triple pages.

Run:  python triple_model.py && python triple_sims.py && python make_figures.py   (numpy, scipy, matplotlib, pillow)
Reads triple_model_numbers.json, triple_sims.json, sim_results.npz and the plans in ../data. Writes ../images/.
Everything here is [SIM] on an assumed rig [HYP]; there is no triple rig.
"""
import glob
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation, patches

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
import nlink_cart as nl  # noqa: E402
import triple_model as tm  # noqa: E402

IMG = os.path.join(HERE, "..", "images")
DATA = os.path.join(HERE, "..", "data")
os.makedirs(IMG, exist_ok=True)
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 110, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.spines.top": False, "axes.spines.right": False})
COL = ["#3b82c4", "#e8a33d", "#5a9e6f"]          # arm 1, arm 2, arm 3
CX, CP, CR = "#555555", "#9aa5b1", "#c94c4c"
LEN = [0.2, 0.25, 0.25]
CAP = 0.831
MAIN_PLAN = "4.0s"


def save(fig, name):
    fig.savefig(os.path.join(IMG, name), bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def numbers():
    return json.load(open(os.path.join(HERE, "triple_model_numbers.json")))


def sims():
    return json.load(open(os.path.join(HERE, "triple_sims.json"))), np.load(os.path.join(HERE, "sim_results.npz"))


def plans():
    out = {}
    for p in sorted(glob.glob(os.path.join(DATA, "triple_swingup_plan_*.json"))):
        d = json.load(open(p))
        out[os.path.basename(p)[len("triple_swingup_plan_"):-5]] = (d, np.array(d["z"]).T)
    return out


def draw_rig(ax, x, th, alpha=1.0, lw=5, ghost=False):
    """Cart at x, arms at absolute angles th (from upright, + = toward +x)."""
    pts = [np.array([x, 0.0])]
    for t, L in zip(th, LEN):
        pts.append(pts[-1] + L * np.array([np.sin(t), np.cos(t)]))
    P = np.array(pts)
    if ghost:
        ax.plot(P[:, 0], P[:, 1], color=CP, lw=2, alpha=alpha, ls="--")
        return
    ax.add_patch(patches.FancyBboxPatch((x - 0.06, -0.035), 0.12, 0.05, boxstyle="round,pad=0.004",
                                        fc="#dbe7f3", ec="k", alpha=alpha))
    for i in range(len(th)):
        ax.plot(P[i:i + 2, 0], P[i:i + 2, 1], color=COL[i], lw=lw, solid_capstyle="round", alpha=alpha)
    ax.plot(P[:-1, 0], P[:-1, 1], "ko", ms=4, alpha=alpha)


def track(ax, plan_lim=0.25, abort=0.36, lim=0.40):
    ax.plot([-lim - 0.04, lim + 0.04], [-0.04, -0.04], color="k", lw=2)
    for xx, c in ((plan_lim, "#7aa974"), (abort, CR), (lim, "k")):
        for s in (-1, 1):
            ax.plot([s * xx, s * xx], [-0.075, -0.005], color=c, lw=1.2)


# ---------------------------------------------------------------- F1 the assumed rig
def fig_rig():
    fig, ax = plt.subplots(figsize=(7.6, 6.2))
    ax.set_aspect("equal"); ax.axis("off"); ax.grid(False)
    ax.plot([-0.32, 0.70], [-0.04, -0.04], color="k", lw=2)
    th = np.radians([15, -20, 25])
    draw_rig(ax, 0.0, th, lw=7)
    P = [np.array([0.0, 0.0])]
    for t, L in zip(th, LEN):
        P.append(P[-1] + L * np.array([np.sin(t), np.cos(t)]))
    cs = [0.087, 0.106, 0.106]
    for i in range(3):
        c = P[i] + cs[i] * np.array([np.sin(th[i]), np.cos(th[i])])
        ax.plot(*c, "o", ms=11, mfc="white", mec=COL[i], mew=2.5)
        ax.plot([P[i][0], P[i][0]], [P[i][1], P[i][1] + 0.12], color="k", ls=":", lw=1)
        a = np.linspace(0, th[i], 20)
        ax.plot(P[i][0] + 0.09 * np.sin(a), P[i][1] + 0.09 * np.cos(a), "k", lw=1)
        ax.text(P[i][0] + (0.012 if th[i] > 0 else -0.06), P[i][1] + 0.10, rf"$\theta_{i + 1}$", fontsize=12)
    lab = dict(fontsize=9, va="center")
    texts = [r"arm 1 (as the double): $L_1$ 200 mm, $m_1$ 207 g, $c_1$ 87 mm, $I_1$ 1.233e-3",
             r"arm 2 (as the double): $L_2$ 250 mm to joint 3, $m_2$ 210 g, $c_2$ 106 mm, $I_2$ 1.976e-3",
             r"arm 3 [HYP]: a copy of arm 2, $m_3$ 210 g, $c_3$ 106 mm, $I_3$ 1.976e-3"]
    ys = [0.10, 0.30, 0.52]
    for i in range(3):
        c = P[i] + cs[i] * np.array([np.sin(th[i]), np.cos(th[i])])
        ax.annotate(texts[i], c, xytext=(0.20, ys[i]), color=COL[i], arrowprops=dict(arrowstyle="-", color=COL[i]), **lab)
    ax.annotate("joint 3 (a third encoder and transmitter on arm 2's tip)", P[2], xytext=(0.20, 0.42),
                arrowprops=dict(arrowstyle="-"), **lab)
    ax.annotate("joint 2 (encoder 2)", P[1], xytext=(0.20, 0.21), arrowprops=dict(arrowstyle="-"), **lab)
    ax.text(0.36, 0.74, "Same convention as the double scripts:\nabsolute angles from upright,\n+ = centre of mass toward +x.\n"
            "Encoders read θ1, θ2-θ1, θ3-θ2.\nInertias in kg m² about each CoM.", fontsize=9, va="top",
            bbox=dict(fc="#f5f5f5", ec="#bbb"))
    ax.set_xlim(-0.33, 0.72); ax.set_ylim(-0.10, 0.75)
    ax.set_title("The triple assumed on these pages: the double rig with a third arm on top [HYP]", fontsize=10)
    save(fig, "fig01_rig.png")


# ---------------------------------------------------------------- F2 modes
def fig_modes():
    su, Vu = tm.modes(tm.TRIPLE)
    fig, axs = plt.subplots(2, 3, figsize=(10.5, 7.2))
    for row, base in enumerate((0.0, np.pi)):
        for j in range(3):
            ax = axs[row, j]
            ax.set_aspect("equal"); ax.axis("off"); ax.grid(False)
            v = Vu[:, j] / np.max(np.abs(Vu[:, j])) * 0.40
            for s, al in ((1, 1.0), (-1, 0.3)):
                draw_rig(ax, 0.0, base + s * v, alpha=al, lw=4)
            ax.set_xlim(-0.45, 0.45); ax.set_ylim((-0.08, 0.72) if base == 0.0 else (-0.72, 0.08))
            shape = "θ1 : θ2 : θ3 = 1 : %+.2f : %+.2f" % (Vu[1, j], Vu[2, j])
            if base == 0.0:
                ttl = f"upright, mode {j + 1}: grows as e^({su[j]:.1f} t)\n(doubles every {np.log(2) / su[j] * 1000:.0f} ms)\n{shape}"
            else:
                ttl = f"hanging, mode {j + 1}: {su[j]:.2f} rad/s\n(period {2 * np.pi / su[j]:.2f} s)\n{shape}"
            ax.set_title(ttl, fontsize=9.5)
    fig.suptitle("Three links, three ways to move: the same shapes falling (top) and swinging (bottom), cart held still",
                 fontsize=10.5)
    save(fig, "fig02_modes.png")


# ---------------------------------------------------------------- F3 poles of single, double, triple
def fig_poles():
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    rows = [("single (identified I)", tm.SINGLE), ("double", tm.DOUBLE), ("triple [HYP]", tm.TRIPLE)]
    for i, (lab, rig) in enumerate(rows):
        A, _ = nl.linear_accel(rig)
        ev = np.sort(np.linalg.eigvals(A).real)
        ax.scatter(ev, np.full_like(ev, i), s=60, c=[CR if e > 1e-9 else (COL[0] if e < -1e-9 else CX) for e in ev], zorder=3)
        for e in ev[ev > 1e-9]:
            ax.annotate(f"+{e:.1f}", (e, i), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8.5)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlabel("pole (1/s), cart acceleration as the input; red = unstable (falls over)")
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_title("Each extra link adds one unstable pole, and the fastest one gets faster", fontsize=10)
    save(fig, "fig03_poles.png")


# ---------------------------------------------------------------- F4 the B column: how the cart reaches each arm
def fig_bcol():
    n = numbers()
    cases = [("double", [n["B_double"][1][0], n["B_double"][3][0], np.nan]),
             ("triple", [n["B"][1][0], n["B"][3][0], n["B"][5][0]]),
             ("triple,\narm 2 mass +20 %\n(physical)", [n["B_m2_plus20"][i] for i in (1, 3, 5)]),
             ("triple,\np2 alone +2 %\n(inconsistent)", [n["B_p2_plus2"][i] for i in (1, 3, 5)])]
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.0), gridspec_kw=dict(width_ratios=[1, 1.4]))
    x = np.arange(len(cases))
    for j in range(3):
        vals = [c[1][j] for c in cases]
        axs[0].bar(x + (j - 1) * 0.26, vals, 0.24, color=COL[j], label=f"arm {j + 1}")
    axs[0].set_xticks(x); axs[0].set_xticklabels([c[0] for c in cases], fontsize=7.5)
    axs[0].set_ylabel("rad/s² per m/s² of cart acceleration"); axs[0].legend(fontsize=8)
    axs[0].set_title("Direct effect of the cart on each arm (B)", fontsize=9.5)
    for j in (1, 2):
        vals = [c[1][j] for c in cases]
        axs[1].bar(x + (j - 1.5) * 0.3, vals, 0.28, color=COL[j], label=f"arm {j + 1}")
        for xi, v in zip(x, vals):
            if np.isfinite(v):
                axs[1].text(xi + (j - 1.5) * 0.3, v + (0.02 if v >= 0 else -0.06), f"{v:+.2f}", ha="center", fontsize=8)
    axs[1].axhline(0, color="k", lw=0.8)
    axs[1].set_xticks(x); axs[1].set_xticklabels([c[0] for c in cases], fontsize=7.5)
    axs[1].set_title("Zoom on arms 2 and 3: small numbers made of near-cancellations", fontsize=9.5)
    axs[1].legend(fontsize=8)
    save(fig, "fig04_b_column.png")


# ---------------------------------------------------------------- F5 tolerances
def fig_tolerance():
    n = numbers()
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.6), gridspec_kw=dict(width_ratios=[0.7, 1.2, 1.5]))
    d = n["delay_ms"]
    axs[0].barh([0, 1], [d["double"], d["triple"]], color=[CP, COL[2]])
    axs[0].axvline(9, color="k", ls=":", lw=1); axs[0].text(9.3, 1.55, "designed\nfor 9 ms", fontsize=8)
    for i, v in enumerate([d["double"], d["triple"]]):
        axs[0].text(v + 0.3, i, f"{v:.1f} ms", va="center", fontsize=9)
    axs[0].set_yticks([0, 1]); axs[0].set_yticklabels(["double", "triple"])
    axs[0].set_xlabel("longest real motor delay\nthe balance survives (ms)"); axs[0].set_xlim(0, 27)
    axs[0].set_ylim(-0.6, 2.1)
    for ax, key, ttl, unit in ((axs[1], "entry", "one entry of p or H changed alone (%)", "%"),
                               (axs[2], "physical", "one physical value changed (% or mm)", "")):
        names = list(n[key]["triple"].keys())
        y = np.arange(len(names))
        for k, (who, col, off) in enumerate((("double", CP, -0.18), ("triple", COL[2], 0.18))):
            for i, nm in enumerate(names):
                if nm not in n[key][who]:
                    continue
                lo, hi = n[key][who][nm]
                lo, hi = max(lo, -60), min(hi, 60)
                ax.plot([lo, hi], [i + off, i + off], color=col, lw=6, solid_capstyle="butt",
                        label=who if i == 0 else None)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8)
        ax.invert_yaxis()
        ax.set_title(ttl, fontsize=9.5)
        ax.legend(fontsize=8, loc="lower right")
        ax.set_xlim(-40 if key == "entry" else -62, 40 if key == "entry" else 62)
    axs[1].set_xlabel("range that still balances (linear, incl. Kalman filter)")
    axs[2].set_xlabel("range that still balances (bars cut at ±60)")
    fig.suptitle("How much the balance tolerates [SIM]: errors that break the physical structure are the dangerous ones",
                 fontsize=10.5)
    save(fig, "fig05_balance_tolerance.png")


# ---------------------------------------------------------------- F6 balance sim
def fig_balance_sim():
    js, s = sims()
    t, z, a, trim = s["bal_t"], s["bal_z"], s["bal_a"], s["bal_trim"]
    fig, axs = plt.subplots(4, 1, figsize=(9, 8.6), sharex=True)
    for j in range(3):
        axs[0].plot(t, np.degrees(z[:, 2 * j]), color=COL[j], lw=1, label=f"arm {j + 1}")
        axs[1].plot(t[:len(trim)], np.degrees(trim[:, j]), color=COL[j], lw=1.5,
                    label=["encoder 1 (true 0.2°)", "encoder 2 (true -0.1°)", "encoder 3 (true 0.1°)"][j])
    axs[0].set_ylabel("arm angle (deg)"); axs[0].legend(fontsize=8, ncol=3)
    axs[0].annotate("tap on arm 3\n(+0.1 rad/s)", (5.0, 0.3), xytext=(6.0, 0.9), fontsize=8, arrowprops=dict(arrowstyle="->"))
    axs[1].set_ylabel("auto-trim\n(deg)"); axs[1].legend(fontsize=8, ncol=3)
    axs[2].plot(t, 1000 * z[:, 6], color=CX); axs[2].set_ylabel("cart (mm)")
    axs[3].plot(t, a, color=CX, lw=0.6); axs[3].set_ylabel("cart accel.\n(m/s²)"); axs[3].set_xlabel("time (s)")
    axs[0].set_title("Triple balance with the double script's controller (n = 3) [SIM]: start 0.5/0/0.3°, "
                     "encoder references off, 1-count noise", fontsize=9.5)
    save(fig, "fig06_balance_sim.png")


# ---------------------------------------------------------------- F7 plan
def fig_plan():
    d, Z = plans()[MAIN_PLAN]
    t = np.arange(Z.shape[1]) * 0.01
    a = np.array(d["a"])
    lim = d["limits"]
    fig, axs = plt.subplots(4, 1, figsize=(9, 8.5), sharex=True)
    for j in range(3):
        axs[0].plot(t, np.degrees(Z[2 * j]), color=COL[j], label=f"θ{j + 1}")
    axs[0].set_ylabel("angle (deg)\n180 = hanging"); axs[0].legend(fontsize=8, ncol=3)
    axs[1].plot(t, Z[6], color=CX); axs[1].set_ylabel("cart x (m)")
    axs[2].plot(t, Z[7], color=CX); axs[2].set_ylabel("cart v (m/s)")
    axs[3].plot(t[:len(a)], a, color=CX); axs[3].set_ylabel("cart a (m/s²)"); axs[3].set_xlabel("time (s)")
    for ax, key in ((axs[1], "track_m"), (axs[2], "speed_m_s"), (axs[3], "accel_m_s2")):
        for s_ in (-1, 1):
            ax.axhline(s_ * lim[key], color=CR, ls=":", lw=1)
    for ax, v in ((axs[1], 0.25), (axs[2], 0.75), (axs[3], 8.0)):
        for s_ in (-1, 1):
            ax.axhline(s_ * v, color="#7aa974", ls="--", lw=1)
    axs[0].set_title(f"Triple swing-up plan, {d['T']:.1f} s [SIM]: red dotted = the plan's limits, green dashed = the "
                     "double plan's limits (rig)", fontsize=9.5)
    save(fig, "fig07_plan.png")


def fig_plan_strobe():
    d, Z = plans()[MAIN_PLAN]
    N = Z.shape[1]
    ks = list(range(0, N, 10))
    cols = 9
    rows = int(np.ceil(len(ks) / cols))
    fig, axs = plt.subplots(rows, cols, figsize=(13, 2.15 * rows))
    for ax in axs.ravel():
        ax.set_aspect("equal"); ax.axis("off"); ax.grid(False)
    for ax, k in zip(axs.ravel(), ks):
        ax.plot([-0.3, 0.3], [-0.04, -0.04], color="k", lw=1)
        for s_ in (-0.25, 0.25):
            ax.plot([s_, s_], [-0.06, -0.02], color="#7aa974", lw=1)
        draw_rig(ax, Z[6, k], Z[[0, 2, 4], k], lw=2.5)
        ax.set_xlim(-0.62, 0.62); ax.set_ylim(-0.72, 0.72)
        ax.set_title(f"{k / 100:.1f} s  v {Z[7, k]:+.2f}", fontsize=7.5)
    fig.suptitle(f"The {d['T']:.1f} s triple plan every 0.1 s (green ticks: ±0.25 m)", fontsize=10.5)
    save(fig, "fig08_plan_strobe.png")


# ---------------------------------------------------------------- F9 what the swing-up needs vs duration
def fig_limits():
    P = plans()
    keys = sorted(P, key=lambda k: P[k][0]["T"])
    T = [P[k][0]["T"] for k in keys]
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.3))
    for ax, key, rig, ttl in zip(axs, ("track_m", "speed_m_s", "accel_m_s2", "motor_top_speed_m_s"),
                                 (0.25, 0.75, 8.0, 1.0), ("track (± m)", "plan speed (m/s)", "acceleration (m/s²)",
                                                          "motor top speed (m/s)")):
        ax.plot(T, [P[k][0]["limits"][key] for k in keys], "o-", color=COL[2], label="triple needs (found)")
        ax.axhline(rig, color="#7aa974", ls="--", label="double plan / rig")
        ax.set_title(ttl, fontsize=9.5); ax.set_xlabel("plan duration (s)")
    axs[0].legend(fontsize=8)
    fig.suptitle("Tightest limits a triple swing-up plan was found for, by duration [SIM] "
                 "(local optimum: tighter plans may exist)", fontsize=10, y=1.06)
    save(fig, "fig09_limits_vs_duration.png")


# ---------------------------------------------------------------- F10 closed-loop swing-up
def fig_swing_sim():
    js, s = sims()
    d, Z = plans()[MAIN_PLAN]
    p = f"sw_{MAIN_PLAN}_"
    t, z, v = s[p + "t"], s[p + "z"], s[p + "v_sent"]
    N = Z.shape[1]
    tp = np.arange(N) * 0.01
    fig, axs = plt.subplots(3, 1, figsize=(9, 7.4), sharex=True)
    for j in range(3):
        axs[0].plot(t, np.degrees(np.unwrap(z[:, 2 * j])), color=COL[j], label=f"θ{j + 1}")
        axs[0].plot(tp, np.degrees(Z[2 * j]), color=COL[j], ls="--", lw=1)
    axs[0].set_ylabel("angle (deg)"); axs[0].legend(fontsize=8, ncol=3)
    axs[1].plot(t, z[:, 6], color=CX); axs[1].plot(tp, Z[6], color=CX, ls="--", lw=1); axs[1].set_ylabel("cart x (m)")
    axs[2].plot(t, v, color=CX, label="speed sent"); axs[2].plot(tp, Z[7], color=CX, ls="--", lw=1, label="plan")
    for s_ in (-1, 1):
        axs[2].axhline(s_ * CAP, color=CR, ls=":", lw=1)
    axs[2].text(0.05, CAP + 0.04, "0.831 m/s timer ceiling of the Mega", fontsize=8, color=CR)
    axs[2].set_ylabel("cart v (m/s)"); axs[2].set_xlabel("time (s)"); axs[2].legend(fontsize=8)
    axs[0].axvline(d["T"], color="k", lw=0.8); axs[0].text(d["T"] + 0.05, 30, "catch", fontsize=8)
    axs[0].set_title("The double swing-up controller with n = 3 on the triple plan [SIM]: solid = simulated, dashed = plan",
                     fontsize=9.5)
    save(fig, "fig10_swing_sim.png")


def fig_swing_robustness():
    js, _ = sims()
    plans_ = [k for k in ("3.5s", "4.0s") if js["swing"].get(k, {}).get("robustness")]
    if not plans_:
        return
    rows = []
    for li in (1, 2, 3):
        rows += [(f"arm {li} mass", [f"m{li} {v}" for v in ("-5%", "-2%", "+2%", "+5%")]),
                 (f"arm {li} inertia", [f"I{li} {v}" for v in ("-10%", "-5%", "+5%", "+10%")]),
                 (f"arm {li} CoM", [f"c{li} {v}" for v in ("-3 mm", "-1 mm", "+1 mm", "+3 mm")])]
        if li < 3:
            rows.append((f"joint {li + 1} position", [f"L{li} {v}" for v in ("-3 mm", "-1 mm", "+1 mm", "+3 mm")]))
    rows += [("joint friction", ["joint friction x0.5", "joint friction x1.5"]), ("motor delay", ["delay 5 ms", "delay 12 ms"])]
    rows += [(f"{e} alone", [f"{e} alone -1%", f"{e} alone +1%"]) for e in ("p1", "p2", "p3", "h11", "h22", "h33", "h12", "h13", "h23")]
    fig, axs = plt.subplots(1, len(plans_), figsize=(5.2 * len(plans_), 0.27 * len(rows) + 1.2))
    axs = np.atleast_1d(axs)
    for ax, pl in zip(axs, plans_):
        rob = js["swing"][pl]["robustness"]
        ax.set_xlim(0, 4); ax.set_ylim(len(rows), 0); ax.axis("off")
        for i, (lab, keys) in enumerate(rows):
            w = 4 / len(keys)
            for j, k in enumerate(keys):
                ok = rob[k]["ok"]
                ax.add_patch(patches.Rectangle((j * w + 0.03, i + 0.08), w - 0.06, 0.84, fc="#7aa974" if ok else CR, ec="none"))
                lab_k = k[len("delay "):] if k.startswith("delay") else (
                    k.split()[-1] if k.startswith("joint") or " alone " in k else k.split(" ", 1)[1])
                ax.text(j * w + w / 2, i + 0.5, lab_k, ha="center", va="center", fontsize=7.5, color="white")
            if ax is axs[0]:
                ax.text(-0.08, i + 0.5, lab, ha="right", va="center", fontsize=8.5)
        n_ok = sum(v["ok"] for k, v in rob.items() if k != "nominal")
        ax.set_title(f"{pl[:-1]} s plan: {n_ok} of {len(rob) - 1} catch", fontsize=10)
    fig.suptitle("Triple swing-up with the real arms different from the model, one error at a time [SIM] "
                 "(green = catches, red = fails)", fontsize=10)
    save(fig, "fig11_swing_robustness.png")


# ---------------------------------------------------------------- animations
def anim(name, frames, title, xlim=(-0.95, 0.95), ylim=(-0.75, 0.75), fps=25, plan_ghost=None):
    w = 4.8 * (xlim[1] - xlim[0]) / (ylim[1] - ylim[0])
    fig, ax = plt.subplots(figsize=(max(w, 3.6), 5.0))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.88)

    def draw(i):
        ax.clear(); ax.set_aspect("equal"); ax.grid(False); ax.axis("off")
        track(ax)
        f = frames[i]
        if plan_ghost is not None and f.get("k") is not None and 0 <= f["k"] < plan_ghost.shape[1]:
            zz = plan_ghost[:, f["k"]]
            draw_rig(ax, zz[6], zz[[0, 2, 4]], ghost=True, alpha=0.8)
        draw_rig(ax, f["x"], f["th"])
        ax.set_xlim(*xlim); ax.set_ylim(*ylim)
        ax.set_title(f"{title}\nt = {f['t']:.2f} s   {f.get('label', '')}", fontsize=8.5)
    an = animation.FuncAnimation(fig, draw, frames=len(frames), interval=1000 / fps)
    an.save(os.path.join(IMG, name), writer=animation.PillowWriter(fps=fps), dpi=80)
    plt.close(fig)
    print("wrote", name)


def gifs():
    js, s = sims()
    d, Z = plans()[MAIN_PLAN]
    p = f"sw_{MAIN_PLAN}_"
    t, z, kk = s[p + "t"], s[p + "z"], s[p + "k"]
    T = d["T"]
    end = min(len(t), int((T + 1.5) / 0.01))
    fr = [dict(t=t[i], x=z[i, 6], th=z[i, [0, 2, 4]], k=int(kk[i]) if t[i] < T else None,
               label="SWING (dashed: plan)" if t[i] < T else "BALANCE") for i in range(0, end, 4)]
    anim("anim_triple_swingup_sim.gif", fr, "Triple swing-up, double script's controller, n = 3 [SIM]", plan_ghost=Z)
    bt, bz = s["bal_t"], s["bal_z"]
    m = (bt > 4.6) & (bt < 7.6)
    fr = [dict(t=bt[i], x=bz[i, 6], th=bz[i, [0, 2, 4]] * 5,
               label=("tap on arm 3 (+0.1 rad/s) at 5.00 s" if bt[i] >= 5.0 else "balanced") + "; angles drawn x5")
          for i in np.where(m)[0][::3]]
    anim("anim_triple_balance_sim.gif", fr, "Triple balance [SIM]", xlim=(-0.3, 0.3), ylim=(-0.1, 0.75), fps=33)


if __name__ == "__main__":
    fig_rig()
    fig_modes()
    fig_poles()
    fig_bcol()
    fig_tolerance()
    fig_balance_sim()
    fig_plan()
    fig_plan_strobe()
    fig_limits()
    fig_swing_sim()
    fig_swing_robustness()
    gifs()
