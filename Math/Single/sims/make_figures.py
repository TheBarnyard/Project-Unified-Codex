"""Make every figure and animation used by the Math/Single pages.

Run:  python make_figures.py        (about 1-2 minutes; needs numpy, sympy, control, matplotlib, pillow)
Reads ../data/*.csv (real rig logs [HW]) and runs single_sim.py [SIM]. Writes ../images/.
"""
import csv
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation, patches
from scipy.special import ellipk

import single_model as sm
import single_sim as ss

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "images")
DATA = os.path.join(HERE, "..", "data")
os.makedirs(IMG, exist_ok=True)
RUN_A = os.path.join(DATA, "hw_run_balance_20261016_160234_984214.csv")
RUN_A_W0 = 7.4219      # IDENTIFY result logged in that run
G = 9.81

plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 110, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.spines.top": False, "axes.spines.right": False})
C_ID, C_SW, C_LQ = "#9aa5b1", "#e8a33d", "#3b82c4"
MODE_COLORS = {"IDENTIFY": C_ID, "SWING_UP": C_SW, "LQG": C_LQ, 0: C_ID, 1: C_SW, 2: C_LQ}


def save(fig, name):
    fig.savefig(os.path.join(IMG, name), bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def load_run(path):
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = {}
    for k in rows[0]:
        if k == "mode":
            out[k] = np.array([r[k] for r in rows])
        else:
            out[k] = np.array([float(r[k]) if r[k] not in ("",) else np.nan for r in rows])
    out["t"] = out["elapsed_s"] - out["elapsed_s"][0]
    return out


def shade_modes(ax, t, mode):
    start = 0
    for i in range(1, len(t) + 1):
        if i == len(t) or mode[i] != mode[start]:
            ax.axvspan(t[start], t[i - 1], color=MODE_COLORS[mode[start]], alpha=0.13, lw=0)
            start = i


def mode_legend(ax):
    handles = [patches.Patch(color=MODE_COLORS[m], alpha=0.35, label=n)
               for m, n in (("IDENTIFY", "IDENTIFY"), ("SWING_UP", "SWING-UP"), ("LQG", "LQG balance"))]
    ax.legend(handles=handles, loc="upper right", fontsize=8, ncol=3)


# ---------------------------------------------------------------- F1 coordinates
def fig_coordinates():
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.set_aspect("equal"); ax.axis("off"); ax.grid(False)
    ax.plot([-0.45, 0.45], [-0.03, -0.03], color="k", lw=2)
    for xx in np.linspace(-0.44, 0.44, 23):
        ax.plot([xx, xx - 0.02], [-0.03, -0.05], color="k", lw=0.8)
    cx = 0.05
    ax.add_patch(patches.FancyBboxPatch((cx - 0.08, -0.02), 0.16, 0.06, boxstyle="round,pad=0.005", fc="#dbe7f3", ec="k"))
    piv = np.array([cx, 0.04])
    th = np.deg2rad(25)
    tip = piv + 0.30 * np.array([-np.sin(th), np.cos(th)])
    com = piv + 0.13 * np.array([-np.sin(th), np.cos(th)])
    ax.plot([piv[0], tip[0]], [piv[1], tip[1]], color="#444", lw=6, solid_capstyle="round")
    ax.plot(*piv, "o", color="k", ms=6)
    ax.plot(*com, "o", ms=11, mfc="white", mec="k"); ax.plot(*com, "o", ms=4, color="k")
    ax.plot([piv[0], piv[0]], [piv[1], piv[1] + 0.33], "k--", lw=0.8)
    arc = np.linspace(np.pi/2, np.pi/2 + th, 30)
    ax.plot(piv[0] + 0.2*np.cos(arc), piv[1] + 0.2*np.sin(arc), "k", lw=1)
    ax.annotate("", xy=(piv[0] + 0.2*np.cos(arc[-1]), piv[1] + 0.2*np.sin(arc[-1])),
                xytext=(piv[0] + 0.2*np.cos(arc[-3]), piv[1] + 0.2*np.sin(arc[-3])), arrowprops=dict(arrowstyle="->"))
    ax.text(piv[0] - 0.035, piv[1] + 0.215, r"$\theta>0$", fontsize=12)
    ax.text(com[0] + 0.02, com[1] - 0.01, "CoM\n" + r"$m_1,\ I$ (about CoM)", fontsize=9)
    mid = (piv + com) / 2
    ax.text(mid[0] + 0.015, mid[1] - 0.02, r"$l$", fontsize=12)
    ax.annotate("", xy=(cx + 0.2, 0.01), xytext=(cx + 0.09, 0.01), arrowprops=dict(arrowstyle="->", lw=2, color="#c0392b"))
    ax.text(cx + 0.205, 0.0, r"$F$ (+x)", color="#c0392b", fontsize=11)
    ax.text(cx - 0.05, -0.012, r"$M$ cart", fontsize=9)
    ax.annotate("", xy=(0.33, -0.11), xytext=(-0.33, -0.11), arrowprops=dict(arrowstyle="->"))
    ax.text(0.34, -0.12, r"$x$", fontsize=12)
    ax.plot([0, 0], [-0.13, -0.09], "k", lw=1); ax.text(-0.03, -0.165, "x = 0 (start)", fontsize=8)
    ax.annotate("", xy=(-0.38, 0.12), xytext=(-0.38, 0.26), arrowprops=dict(arrowstyle="->"))
    ax.text(-0.42, 0.18, r"$g$", fontsize=12)
    ax.text(-0.45, 0.36, "CoM position:\n" + r"$x_p = x - l\sin\theta$" + "\n" + r"$y_p = l\cos\theta$", fontsize=10)
    ax.set_xlim(-0.47, 0.47); ax.set_ylim(-0.18, 0.45)
    ax.set_title(r"Coordinates used by the code: $\theta=0$ upright, $\theta=\pm\pi$ hanging")
    save(fig, "fig01_coordinates.png")


# ---------------------------------------------------------------- F2 energy phase portrait
def fig_energy_portrait(hw, sim):
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    th = np.linspace(-np.pi, np.pi, 400)
    w = np.linspace(-3.2, 3.2, 400)
    TH, W = np.meshgrid(th, w)
    E = 0.5 * W**2 + np.cos(TH)
    for ax, (title, t_th, t_w) in zip(axs, (
            ("Real rig, run balance_20261016_160234 [HW]", hw[0], hw[1]),
            ("Simulation of the same code [SIM]", sim[0], sim[1]))):
        cs = ax.contour(TH, W, E, levels=[-0.9, -0.5, 0, 0.5, 1.5, 2.5], colors="#bbb", linewidths=0.7)
        ax.clabel(cs, fontsize=7, fmt="e=%.1f")
        ax.contour(TH, W, E, levels=[1.0], colors="k", linewidths=1.6)
        t_th, t_w = np.asarray(t_th, dtype=float).copy(), np.asarray(t_w, dtype=float).copy()
        jumps = np.where(np.abs(np.diff(t_th)) > np.pi)[0]
        pth, pw = np.insert(t_th, jumps + 1, np.nan), np.insert(t_w, jumps + 1, np.nan)
        ax.plot(pth, pw, color=C_SW, lw=1.2)
        ax.plot(t_th[-1], t_w[-1], "o", color=C_LQ, ms=8, label="catch (switch to LQG)")
        ax.plot(t_th[0], t_w[0], "s", color="k", ms=6, label="start (hanging)")
        ax.add_patch(patches.Rectangle((-0.30, -3.5 / RUN_A_W0), 0.60, 7.0 / RUN_A_W0, fc=C_LQ, alpha=0.2, ec=C_LQ))
        ax.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi]); ax.set_xticklabels(["-180 (hanging)", "-90", "0 (upright)", "90", "180"])
        ax.set_xlabel(r"$\theta$ [deg]"); ax.set_title(title, fontsize=10)
        ax.legend(loc="lower left", fontsize=8)
    axs[0].set_ylabel(r"$\dot\theta/\omega_0$")
    axs[0].text(-0.6, 2.5, "e = 1 separatrix\n(just reaches upright)", fontsize=8)
    axs[1].text(0.35, 0.05, "catch window\n|θ|<0.30 rad,\n|θ̇|<3.5 rad/s", fontsize=8, color=C_LQ)
    fig.suptitle(r"Swing-up in the energy plane: $e=\frac{1}{2}(\dot\theta/\omega_0)^2+\cos\theta$ grows from $-1$ (hanging) to $+1$ (upright)")
    save(fig, "fig02_energy_phase_portrait.png")


# ---------------------------------------------------------------- F3 poles
def fig_poles():
    I_id = sm.inertia_from_w0(7.2881)
    sys, K, L = sm.design_lqg(I_id)
    Ad, Bd, Cd = (np.asarray(m, dtype=float) for m in (sys.A, sys.B, sys.C))
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6))
    A, B = sm.continuous_ab(I_id)
    p = np.linalg.eigvals(A)
    ax = axs[0]
    ax.axvline(0, color="k", lw=0.8); ax.axhline(0, color="k", lw=0.8)
    ax.plot(p.real, p.imag, "x", ms=12, mew=2.5, color="#c0392b")
    for k, pr in enumerate(sorted(p.real)):
        ax.annotate(f"{pr:+.2f}", (pr, 0), textcoords="offset points", xytext=(-14, 12 if k % 2 else -20), fontsize=9)
    ax.set_xlabel("Re(s) [1/s]"); ax.set_ylabel("Im(s)"); ax.set_xlim(-9, 9); ax.set_ylim(-3, 3)
    ax.set_title("Open-loop poles of the linear model (continuous)\n+7.49 = falling over; 0 = cart position; -0.41 = cart drag", fontsize=10)
    ax = axs[1]
    c = np.linspace(0, 2*np.pi, 400)
    ax.plot(np.cos(c), np.sin(c), "k", lw=0.8)
    sets = (("open loop  eig(Ad)", np.linalg.eigvals(Ad), "x", "#c0392b"),
            ("LQR as designed  eig(Ad-Bd K)", np.linalg.eigvals(Ad - Bd @ K), "o", "#7f8c8d"),
            ("as run (u = -2K y)  eig(Ad-2Bd K)", np.linalg.eigvals(Ad - 2 * Bd @ K), "o", C_LQ),
            ("estimator as used  eig(Ad - Ad L C)", np.linalg.eigvals(Ad - Ad @ L @ Cd), "^", "#27ae60"))
    for lab, z, mk, col in sets:
        ax.plot(z.real, z.imag, mk, ms=9, mfc="none" if mk == "o" and col == "#7f8c8d" else col, mec=col, mew=2, label=lab, ls="none")
    ax.set_aspect("equal"); ax.set_xlim(-0.1, 1.15); ax.set_ylim(-0.35, 0.35)
    ax.set_xlabel("Re(z)"); ax.set_ylabel("Im(z)")
    ax.set_title("Discrete poles (Ts = 0.01 s), identified inertia\ninside the unit circle = stable", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    save(fig, "fig03_poles.png")


# ---------------------------------------------------------------- F4 balance Q vs swing-up Q
def lqg_from_catch(Q, T=4.0, theta0_deg=16.8, thd0=-2.0, v0=0.25):
    plant = ss.Plant(7.2881, 0.20, theta0=np.deg2rad(theta0_deg))
    plant.thd, plant.v = thd0, v0
    ctl = ss.Controller()
    ctl.w0 = 7.2881
    ctl.ss, ctl.K, ctl.L = sm.design_lqg(sm.inertia_from_w0(7.2881), Q)
    ctl.Ad, ctl.Bd, ctl.C = (np.asarray(m, dtype=float) for m in (ctl.ss.A, ctl.ss.B, ctl.ss.C))
    ctl.mode = ss.LQG; ctl.loop = 250; ctl.catch_time = 0.0
    ctl.Ylast = np.array([[np.deg2rad(theta0_deg)], [thd0], [0.0], [v0]])
    ctl.theta_prev = np.deg2rad(theta0_deg) - thd0 * 0.01; ctl.theta_prev_ms = -10; ctl.theta_dot = thd0
    ctl.xdiv_sent = v0
    rec = {"t": [], "th": [], "x": [], "v": [], "lost": None}
    x_meas = 0.0
    for k in range(int(T / 0.01)):
        t = k * 0.01
        v = ctl.step(t, ctl.measure(plant), x_meas, 0.0)
        if ctl.mode != ss.LQG and rec["lost"] is None:
            rec["lost"] = t
        plant.advance(0.002); plant.set_speed(ss.stepper_speed(v)[0]); plant.advance(0.001)
        x_meas = round(plant.x / ss.M_PER_STEP) * ss.M_PER_STEP
        plant.advance(0.007)
        rec["t"].append(t); rec["th"].append(ss.wrap(plant.th)); rec["x"].append(plant.x); rec["v"].append(plant.v)
    return {k: np.array(v) if k != "lost" else v for k, v in rec.items()}, ctl.K.flatten()


def fig_gain_compare():
    fig, axs = plt.subplots(3, 1, figsize=(8, 7.5), sharex=True)
    for Q, col, name in ((sm.Q_SWINGUP_SCRIPT, C_LQ, "swing-up script Q = diag(40, 5, 150, 60)"),
                         (sm.Q_BALANCE_SCRIPTS, "#c0392b", "balance scripts Q = diag(5, 5, 5, 5)")):
        r, K = lqg_from_catch(Q)
        lab = f"{name}\nK = [{K[0]:.1f}, {K[1]:.2f}, {K[2]:.2f}, {K[3]:.2f}]"
        if r["lost"] is not None:
            lab += f"  -> drops at {r['lost']:.2f} s (cart limit)"
        axs[0].plot(r["t"], np.rad2deg(r["th"]), color=col, label=lab)
        axs[1].plot(r["t"], r["x"], color=col)
        axs[2].plot(r["t"], r["v"], color=col)
    axs[0].set_ylabel("θ [deg]"); axs[1].set_ylabel("cart x [m]"); axs[2].set_ylabel("cart speed [m/s]")
    for lim in (0.22, -0.22):
        axs[1].axhline(lim, color="k", ls="--", lw=0.8)
    axs[1].text(3.0, 0.225, "BALANCE_CART_LIMIT_M", fontsize=8)
    axs[2].set_xlabel("time after catch [s]")
    axs[0].legend(fontsize=8)
    axs[0].set_title("Same catch (θ = 16.8°, θ̇ = -2 rad/s, cart 0.25 m/s), two LQR weightings [SIM]", fontsize=10)
    save(fig, "fig04_balanceQ_vs_swingupQ.png")


# ---------------------------------------------------------------- F5 actuation quantisation
def fig_actuation():
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    v = np.linspace(0.0, 1.0, 4000)
    va = np.array([abs(ss.stepper_speed(-vv)[0]) for vv in v])
    axs[0].plot(v, v, "k--", lw=0.8, label="ideal")
    axs[0].plot(v, va, color=C_LQ, label="what the timer can make")
    axs[0].set_xlabel("commanded speed [m/s]"); axs[0].set_ylabel("actual speed [m/s]")
    axs[0].set_title("Stepper speed is quantised: v = 12.464 / (N+1) m/s (N = timer top)", fontsize=10)
    axs[0].legend(fontsize=8)
    N = np.arange(8, 400)
    vN = 125000 / (N + 1) * ss.M_PER_STEP
    dv = vN[:-1] - vN[1:]
    axs[1].semilogy(vN[1:], dv, color=C_LQ, label="speed jump between neighbouring N")
    axs[1].axhline(15 * 0.01, color="#c0392b", ls="--", label="LQG_ACCEL_MAX x Ts = 0.15 m/s")
    axs[1].axhline(6 * 0.01, color=C_SW, ls="--", label="SWING_ACCEL_MAX x Ts = 0.06 m/s")
    axs[1].set_xlabel("speed [m/s]"); axs[1].set_ylabel("Δv per timer count [m/s]"); axs[1].set_xlim(0, 1.6)
    axs[1].set_title("Speed resolution gets coarse at high speed", fontsize=10)
    axs[1].legend(fontsize=8)
    save(fig, "fig05_actuation_quantisation.png")


# ---------------------------------------------------------------- F6 identify
def fig_identify(hw, sim):
    fig, axs = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    for ax, (name, t, th, mode, res) in zip(axs, (("[HW] run balance_20261016_160234", hw["t"], hw["measured_angle_rad"], hw["mode"], "period 0.8466 s, w0 7.42 rad/s, decay 13.2 %/period"),
                                                  ("[SIM] single_sim.py", sim["t"], sim["th_m"], np.where(sim["mode"] == 0, "IDENTIFY", "x"),
                                                   "period {period:.4f} s, w0 {w0:.2f} rad/s, decay {d:.1f} %/period".format(d=100 * sim["identify"]["decay"], **sim["identify"])))):
        m = mode == "IDENTIFY"
        tt, a = t[m], np.rad2deg((th[m] % (2*np.pi)) - np.pi)
        ax.plot(tt, a, color="k", lw=1)
        ax.axvspan(0, 0.48, color=C_SW, alpha=0.2, lw=0); ax.text(0.02, a.max()*0.8, "wiggle\n+a,-a,-a,+a", fontsize=8)
        ax.axvspan(0.48, 0.78, color="#ddd", alpha=0.5, lw=0); ax.text(0.5, a.max()*0.8, "settle", fontsize=8)
        sel = tt > 0.78
        aa = a[sel] - a[sel].mean(); t2 = tt[sel]
        cr = [t2[i-1] + aa[i-1]/(aa[i-1]-aa[i])*(t2[i]-t2[i-1]) for i in range(1, len(aa)) if (aa[i-1] < 0 <= aa[i]) or (aa[i-1] > 0 >= aa[i])]
        ax.plot(cr, np.full(len(cr), a[sel].mean()), "o", color="#c0392b", ms=5, label="zero crossings (timed)")
        ax.set_title(f"{name}: {res}", fontsize=10)
        ax.set_ylabel("angle from hanging [deg]")
        ax.legend(fontsize=8, loc="lower right")
    axs[1].set_xlabel("time since motor start [s]")
    fig.suptitle("IDENTIFY: kick the arm, then time the free swings (model said 1.063 s; the arm really swings at about 0.85 s)", fontsize=10)
    save(fig, "fig06_identify.png")


# ---------------------------------------------------------------- F7/F8 swing-up timelines
def timeline(t, th_deg, thd, e, target, x, vcmd, mode, title, name, tmax=9.0):
    m = t <= tmax
    t, th_deg, thd, e, target, x, vcmd, mode = (a[m] for a in (t, th_deg, thd, e, target, x, vcmd, mode))
    fig, axs = plt.subplots(4, 1, figsize=(9, 9), sharex=True)
    th_plot = th_deg.astype(float).copy()
    th_plot[1:][np.abs(np.diff(th_deg)) > 180] = np.nan     # do not draw the wrap from +180 to -180
    axs[0].plot(t, th_plot, color="k", lw=1); axs[0].set_ylabel("θ [deg]\n(0 = upright)")
    axs[0].axhspan(-17.2, 17.2, color=C_LQ, alpha=0.15); axs[0].set_yticks([-180, -90, 0, 90, 180])
    axs[1].plot(t, thd, color="k", lw=1); axs[1].set_ylabel("θ̇ estimate [rad/s]")
    axs[1].axhspan(-3.5, 3.5, color=C_LQ, alpha=0.08)
    axs[2].plot(t, e, color=C_SW, lw=1.2, label="e (normalised energy)")
    axs[2].plot(t, target, color="k", ls="--", lw=1, label="energy target")
    axs[2].axhspan(0.95, 1.15, color=C_LQ, alpha=0.15); axs[2].set_ylabel("e"); axs[2].set_ylim(-1.2, 1.6)
    axs[2].legend(fontsize=8, loc="lower right")
    axs[3].plot(t, x, color="k", lw=1, label="cart x [m]")
    axs[3].plot(t, vcmd, color=C_SW, lw=1, label="speed command [m/s]")
    axs[3].legend(fontsize=8, loc="lower right"); axs[3].set_xlabel("time [s]")
    for ax in axs:
        shade_modes(ax, t, mode)
    mode_legend(axs[0])
    axs[0].set_title(title, fontsize=10)
    save(fig, name)


# ---------------------------------------------------------------- F9 HW balance
def fig_balance_hw(hw):
    m = hw["mode"] == "LQG"
    t = hw["t"][m]
    fig, axs = plt.subplots(4, 1, figsize=(9, 8.5), sharex=True)
    axs[0].plot(t, np.rad2deg(hw["measured_angle_rad"][m]), color="k", lw=0.8)
    axs[0].set_ylabel("θ [deg]")
    axs[1].plot(t, hw["cart_m"][m], color="k", lw=0.8); axs[1].set_ylabel("cart x [m]")
    axs[2].plot(t, hw["force_command_n"][m], color=C_LQ, lw=0.6); axs[2].set_ylabel("u = -2Kŷ [N]\n(model force)")
    axs[3].plot(t, hw["offset_deg"][m], color=C_SW); axs[3].set_ylabel("auto-trim\nupright offset [deg]")
    axs[3].set_xlabel("time [s]")
    axs[0].set_title(f"[HW] LQG balance after the catch, run balance_20261016_160234: θ std {np.nanstd(np.rad2deg(hw['measured_angle_rad'][m])):.2f}°, cart std {np.nanstd(hw['cart_m'][m])*100:.1f} cm", fontsize=10)
    save(fig, "fig09_balance_hw.png")


# ---------------------------------------------------------------- F10 period vs amplitude
def fig_period():
    a = np.linspace(0.01, np.deg2rad(120), 200)
    exact = 2 / np.pi * ellipk(np.sin(a / 2)**2)
    approx = 1 + a**2 / 16
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(np.rad2deg(a), exact, color="k", label=r"exact: $T/T_0 = \frac{2}{\pi}K(\sin^2\frac{\theta_0}{2})$")
    ax.plot(np.rad2deg(a), approx, color=C_SW, ls="--", label=r"code line 366: $T/T_0 \approx 1+\theta_0^2/16$")
    ax.axvspan(18, 23, color=C_LQ, alpha=0.2); ax.text(19, 1.25, "IDENTIFY\namplitudes\non the rig", fontsize=8)
    ax.set_xlabel("swing amplitude θ0 [deg]"); ax.set_ylabel("period / small-swing period")
    ax.set_title("Big swings are slower: the code removes this before computing w0", fontsize=10)
    ax.legend(fontsize=9)
    save(fig, "fig10_period_vs_amplitude.png")


# ---------------------------------------------------------------- F11 pumping law
def fig_pumping():
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    th = np.linspace(-np.pi, np.pi, 400); w = np.linspace(-3, 3, 300)
    TH, W = np.meshgrid(th, w)
    S = np.sign(W * np.cos(TH))
    ax.contourf(TH, W, S, levels=[-2, 0, 2], colors=["#f6d7d2", "#d6e6f5"])
    ax.contour(TH, W, 0.5 * W**2 + np.cos(TH), levels=[-0.5, 0, 0.5, 1], colors="#888", linewidths=0.7)
    for tc in (-135, -45, 45, 135):
        for wc in (1.9, -1.9):
            sgn = np.sign(wc * np.cos(np.deg2rad(tc)))
            ax.text(np.deg2rad(tc), wc, "+x" if sgn > 0 else "-x", ha="center", va="center", fontsize=13,
                    color="#1f4e79" if sgn > 0 else "#922b21", weight="bold")
    ax.text(0, 2.65, "blue: cart accelerates +x     red: cart accelerates -x     (both add energy when the energy is short)",
            ha="center", fontsize=8.5, bbox=dict(fc="white", ec="none", alpha=0.8))
    for v in (-np.pi/2, np.pi/2):
        ax.axvline(v, color="k", lw=0.8, ls=":")
    ax.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi]); ax.set_xticklabels(["-180\nhanging", "-90", "0\nupright", "90", "180\nhanging"])
    ax.set_xlabel("θ [deg]"); ax.set_ylabel(r"$\dot\theta/\omega_0$")
    ax.set_title(r"Pumping direction = sign($\dot\theta\cos\theta$): it flips when the arm passes horizontal (dotted)", fontsize=10)
    save(fig, "fig11_pumping_direction.png")


# ---------------------------------------------------------------- F12 velocity filter
def fig_velocity_filter():
    a, Ts = 0.3, 0.01
    f = np.logspace(-1, np.log10(50), 400)
    z = np.exp(1j * 2 * np.pi * f * Ts)
    H = (1 - a) * (1 - 1 / z) / Ts / (1 - a / z)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    axs[0].loglog(f, np.abs(H), color=C_LQ, label="IIR-filtered difference (α = 0.3)")
    axs[0].loglog(f, 2 * np.pi * f, "k--", lw=0.8, label="ideal derivative |jω|")
    axs[0].axvline(7.29 / (2*np.pi), color=C_SW, ls=":"); axs[0].text(1.2, 2, "arm w0\n1.16 Hz", fontsize=8)
    axs[0].set_xlabel("frequency [Hz]"); axs[0].set_ylabel("gain [1/s]"); axs[0].legend(fontsize=8)
    axs[0].set_title("Magnitude: a derivative up to about 5 Hz", fontsize=10)
    lag = -(np.angle(H) - np.pi/2) / (2*np.pi*f) * 1000
    axs[1].semilogx(f, lag, color=C_LQ); axs[1].set_xlabel("frequency [Hz]"); axs[1].set_ylabel("time lag vs ideal derivative [ms]")
    axs[1].axvline(7.29 / (2*np.pi), color=C_SW, ls=":")
    axs[1].set_title(f"Lag: {lag[np.argmin(abs(f-1.16))]:.1f} ms at the swing frequency", fontsize=10)
    save(fig, "fig12_velocity_filter.png")


# ---------------------------------------------------------------- F13 catches on the rig
def fig_catches():
    with open(os.path.join(DATA, "hw_events.csv"), newline="") as fh:
        ev = list(csv.DictReader(fh))
    th, thd, e, lost_cart, lost_angle = [], [], [], 0, 0
    for r in ev:
        if r["type"] != "mode_switch":
            continue
        a = float(re.search(r"theta_deg=([-\d.]+)", r["text"]).group(1))
        if "to=LQG" in r["text"]:
            th.append(a); thd.append(float(re.search(r"thetaDot_rad_s=([-\d.]+)", r["text"]).group(1)))
            e.append(float(re.search(r"energy_norm=([-\d.]+)", r["text"]).group(1)))
        elif abs(np.deg2rad(a)) < 0.8:
            lost_cart += 1
        else:
            lost_angle += 1
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.3))
    axs[0].add_patch(patches.Rectangle((-17.19, -3.5), 34.38, 7, fc=C_LQ, alpha=0.15, ec=C_LQ))
    axs[0].plot(th, thd, "o", color=C_LQ, ms=6, mec="k")
    axs[0].set_xlabel("θ at catch [deg]"); axs[0].set_ylabel("θ̇ at catch [rad/s]")
    axs[0].set_title(f"{len(th)} catches in 28 rig runs [HW]: nearly all at the window edge, falling inward", fontsize=10)
    axs[0].set_xlim(-25, 25); axs[0].set_ylim(-4.5, 4.5)
    axs[1].bar(["cart past 0.22 m", "arm past 0.80 rad"], [lost_cart, lost_angle], color=[C_SW, "#c0392b"])
    axs[1].set_ylabel("count"); axs[1].set_title("Why LQG handed back to swing-up [HW]", fontsize=10)
    save(fig, "fig13_catches_hw.png")
    return len(th), lost_cart, lost_angle, np.mean(e), np.min(e), np.max(e)


# ---------------------------------------------------------------- F14 sim recovery
def fig_recovery(sim):
    m = (sim["t"] >= 27) & (sim["t"] <= 36)
    t = sim["t"][m]
    fig, axs = plt.subplots(3, 1, figsize=(9, 6.5), sharex=True)
    axs[0].plot(t, np.rad2deg(sim["th"][m]), color="k"); axs[0].set_ylabel("θ [deg]")
    axs[1].plot(t, sim["x"][m], color="k"); axs[1].set_ylabel("cart x [m]")
    axs[1].axhline(0.22, ls="--", color="k", lw=0.8); axs[1].axhline(-0.22, ls="--", color="k", lw=0.8)
    axs[2].plot(t, sim["e"][m], color=C_SW); axs[2].set_ylabel("e"); axs[2].set_xlabel("time [s]")
    for ax in axs:
        shade_modes(ax, t, sim["mode"][m])
    mode_legend(axs[0])
    axs[0].axvline(30.0, color="#c0392b"); axs[0].text(30.05, 60, "push: θ̇ += -2.5 rad/s", color="#c0392b", fontsize=8)
    axs[0].set_title("[SIM] a hard push: LQG saves the arm but the cart runs past 0.22 m, so it drops and re-swings", fontsize=10)
    save(fig, "fig14_push_recovery_sim.png")


# ---------------------------------------------------------------- animations
def animate(t, th, x, mode, e, name, title, fps=25, stride=4, tmax=9.0, t0=0.0):
    idx = np.where((t >= t0) & (t <= tmax))[0][::stride]
    fig = plt.figure(figsize=(6.4, 4.0))
    ax = fig.add_axes([0.03, 0.12, 0.78, 0.78]); ax.set_aspect("equal"); ax.axis("off")
    axe = fig.add_axes([0.86, 0.15, 0.05, 0.7])
    ax.set_xlim(-0.36, 0.36); ax.set_ylim(-0.26, 0.26)
    ax.plot([-0.33, 0.33], [-0.02, -0.02], color="k", lw=2)
    for lim, ls in ((0.30, "-"), (0.22, "--")):
        for s in (-1, 1):
            ax.plot([s*lim, s*lim], [-0.045, 0.0], color="#c0392b" if lim == 0.30 else "#888", ls=ls, lw=1)
    cart = patches.Rectangle((0, -0.035), 0.08, 0.035, fc="#dbe7f3", ec="k"); ax.add_patch(cart)
    arm, = ax.plot([], [], color="#333", lw=5, solid_capstyle="round")
    trail, = ax.plot([], [], color=C_SW, lw=1, alpha=0.6)
    txt = ax.text(-0.35, 0.22, "", fontsize=9, family="monospace")
    ax.set_title(title, fontsize=9)
    axe.set_ylim(-1.2, 1.6); axe.set_xticks([]); axe.set_title("e", fontsize=9)
    axe.axhspan(0.95, 1.15, color=C_LQ, alpha=0.3); axe.axhline(1.0, color="k", lw=0.8)
    bar = axe.bar([0], [0], color=C_SW, width=0.8)[0]
    names = {0: "IDENTIFY", 1: "SWING-UP", 2: "LQG", "IDENTIFY": "IDENTIFY", "SWING_UP": "SWING-UP", "LQG": "LQG"}
    hist = []

    def draw(k):
        i = idx[k]
        cx = x[i]
        cart.set_x(cx - 0.04)
        tip = (cx - 0.2 * np.sin(th[i]), 0.2 * np.cos(th[i]))
        arm.set_data([cx, tip[0]], [0, tip[1]])
        hist.append(tip)
        trail.set_data([p[0] for p in hist[-30:]], [p[1] for p in hist[-30:]])
        md = names[mode[i]]
        txt.set_text(f"t = {t[i]-t0:5.2f} s  {md:9s}\nθ = {np.rad2deg(th[i]):+7.1f}°  x = {cx:+.3f} m")
        txt.set_color(MODE_COLORS[mode[i]] if md != "IDENTIFY" else "#555")
        ev = e[i] if np.isfinite(e[i]) else -1
        bar.set_height(ev + 1.2); bar.set_y(-1.2)
        bar.set_color(MODE_COLORS[mode[i]])
        return arm, cart, txt, bar, trail

    ani = animation.FuncAnimation(fig, draw, frames=len(idx), interval=1000 / fps, blit=False)
    ani.save(os.path.join(IMG, name), writer=animation.PillowWriter(fps=fps))
    plt.close(fig)
    print("wrote", name)


def main():
    hw = load_run(RUN_A)
    sim = ss.run(T=40.0, angle_offset_deg=1.0, pushes=[(20.0, 1.2), (30.0, -2.5)])
    np.savez(os.path.join(HERE, "sim_run.npz"), **{k: v for k, v in sim.items() if isinstance(v, np.ndarray)})

    # energy for the HW run: e logged in SWING_UP rows; elsewhere recompute from logged estimate
    e_hw = 0.5 * (hw["est_angle_rate_rad_s"] / RUN_A_W0)**2 + np.cos(hw["measured_angle_rad"])
    e_hw[hw["mode"] == "SWING_UP"] = hw["energy_norm"][hw["mode"] == "SWING_UP"]
    first_lqg = np.argmax(hw["mode"] == "LQG")
    sw = (hw["mode"] == "SWING_UP")
    sw_idx = np.where(sw[:first_lqg + 1])[0].tolist() + [first_lqg]
    hw_traj = (hw["measured_angle_rad"][sw_idx], hw["est_angle_rate_rad_s"][sw_idx] / RUN_A_W0)
    s_first = np.argmax(sim["mode"] == ss.LQG)
    s_idx = np.where(sim["mode"][:s_first + 1] == ss.SWING)[0].tolist() + [s_first]
    sim_traj = (sim["th_m"][s_idx], sim["thd_est"][s_idx] / 7.2881)

    fig_coordinates()
    fig_energy_portrait(hw_traj, sim_traj)
    fig_poles()
    fig_gain_compare()
    fig_actuation()
    fig_identify(hw, sim)
    target_hw = np.where(np.isnan(hw["target"]), np.nan, hw["target"])
    vcmd_hw = -hw["step_frequency_hz"] * 0.638175 / 6400     # the speed actually sent (line 793 inverted)
    timeline(hw["t"], np.rad2deg(hw["measured_angle_rad"]), hw["est_angle_rate_rad_s"], e_hw, target_hw,
             hw["cart_m"], vcmd_hw, hw["mode"],
             "[HW] PythonMasterUpExpClaudeImproved.py on the rig, run balance_20261016_160234", "fig07_swingup_hw.png")
    smode = np.array(["IDENTIFY", "SWING_UP", "LQG"])[sim["mode"]]
    timeline(sim["t"], np.rad2deg(sim["th_m"]), sim["thd_est"], sim["e"],
             np.where(sim["mode"] == ss.SWING, sim["target"], np.nan), sim["x"], sim["vcmd"], smode,
             "[SIM] the same logic in single_sim.py (true w0 7.29 rad/s, pivot damping 0.2 1/s)", "fig08_swingup_sim.png")
    fig_balance_hw(hw)
    fig_period()
    fig_pumping()
    fig_velocity_filter()
    stats = fig_catches()
    print("catch stats (n, lost_cart, lost_angle, e_mean, e_min, e_max):", stats)
    fig_recovery(sim)
    animate(sim["t"], sim["th"], sim["x"], sim["mode"], sim["e"], "anim_swingup_sim.gif",
            "[SIM] identify, pump, catch (real time)")
    animate(hw["t"], hw["measured_angle_rad"], hw["cart_m"], hw["mode"], e_hw, "anim_swingup_hw.gif",
            "[HW] replay of run balance_20261016_160234 (real time)")
    animate(sim["t"], sim["th"], sim["x"], sim["mode"], sim["e"], "anim_push_recovery_sim.gif",
            "[SIM] push at 30 s: cart limit, drop, re-swing", t0=29.0, tmax=36.0)


if __name__ == "__main__":
    main()
