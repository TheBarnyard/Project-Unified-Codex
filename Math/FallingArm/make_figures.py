"""Make the PDF figures from falling_pendulum.py (V2 arm 1 defaults)."""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from falling_pendulum import *

plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 150, "savefig.bbox": "tight", "font.family": "serif"})
P = dict(V2_ARM1)
C = ["#1f5fa8", "#c2410c", "#15803d", "#7c3aed", "#b91c1c"]
out = "figures/"

# 1 theta(t) for several release angles
fig, ax = plt.subplots(figsize=(6, 3))
for c, th0 in zip(C, (1, 5, 15, 45, 90)):
    s = simulate(th0, P, 2.0)
    ax.plot(s["t"], np.degrees(s["th"]), color=c, label=fr"$\theta_0={th0}^\circ$")
for y in (90, 180, 270, 360):
    ax.axhline(y, color="k", lw=0.5, ls=":")
ax.set_xlabel("time $t$ (s)"); ax.set_ylabel(r"$\theta$ (deg from upright)")
ax.set_title("Angle after release from rest (V2 arm 1, rig friction)")
ax.legend(ncol=5, fontsize=7, loc="upper left"); ax.set_ylim(0, 400)
fig.savefig(out + "theta_vs_t.pdf"); plt.close(fig)

# 2 stroboscopic arm + tip path
s = simulate(10, P, 0.62)
k = kinematics(s, P)
fig, ax = plt.subplots(figsize=(4.2, 4.2))
ax.plot(k["x"], k["y"], color=C[0], lw=1.2, label="tip path")
idx = np.arange(0, len(s["t"]), int(0.05 / (s["t"][1] - s["t"][0])))
cm = plt.cm.viridis(np.linspace(0, 1, len(idx)))
for j, i in enumerate(idx):
    ax.plot([0, k["x"][i]], [0, k["y"][i]], color=cm[j], lw=2, alpha=0.8)
    if 0 < s["t"][i] < 0.17:
        continue
    ax.text(k["x"][i] * 1.12, k["y"][i] * 1.12, f"{s['t'][i]:.2f}", fontsize=6, ha="center", va="center")
ax.plot(0, 0, "ko", ms=5)
ax.set_aspect("equal"); ax.set_xlim(-0.25, 0.25); ax.set_ylim(-0.25, 0.25)
ax.set_xlabel("$x$ (m)"); ax.set_ylabel("$y$ (m)")
ax.set_title(r"Arm every 0.05 s, $\theta_0=10^\circ$ (labels = s)")
fig.savefig(out + "strobe.pdf"); plt.close(fig)

# 3 friction effect, long run
fig, ax = plt.subplots(figsize=(6, 3))
cases = [("no friction", 0, 0), (r"rig $b$ (1.63e-4)", 1.63e-4, 0), (r"$10\times b$", 1.63e-3, 0),
         (r"rig $b$ + $\tau_c$=2 mN m", 1.63e-4, 2e-3)]
for c, (lab, b, tc) in zip(C, cases):
    p = dict(P, b=b, tau_c=tc)
    s = simulate(10, p, 12.0, dt=5e-4)
    ax.plot(s["t"], np.degrees(s["th"]) - 180, color=c, lw=0.9, label=lab)
ax.set_xlabel("time $t$ (s)"); ax.set_ylabel(r"$\theta-180^\circ$ (deg from hanging)")
ax.set_title(r"Effect of friction, $\theta_0=10^\circ$ ($\tau_c$ value is illustrative)")
ax.legend(fontsize=7, loc="lower right", ncol=2)
fig.savefig(out + "friction.pdf"); plt.close(fig)

# 4 energy
fig, ax = plt.subplots(figsize=(6, 2.6))
for c, (lab, b, tc) in zip(C, cases):
    p = dict(P, b=b, tau_c=tc)
    s = simulate(10, p, 12.0, dt=5e-4)
    ax.plot(s["t"], energy(s, p) * 1e3, color=c, lw=0.9, label=lab)
ax.set_xlabel("time $t$ (s)"); ax.set_ylabel("$E$ (mJ)")
ax.set_title("Mechanical energy (zero = hanging at rest)"); ax.legend(fontsize=7, ncol=2)
fig.savefig(out + "energy.pdf"); plt.close(fig)

# 5 phase portrait
fig, ax = plt.subplots(figsize=(4.5, 3.4))
for c, (lab, b, tc) in zip(C, cases[1:3] + cases[3:]):
    p = dict(P, b=b, tau_c=tc)
    s = simulate(10, p, 12.0, dt=5e-4)
    ax.plot(np.degrees(s["th"]), np.degrees(s["w"]), color=c, lw=0.7, label=lab)
ax.set_xlabel(r"$\theta$ (deg)"); ax.set_ylabel(r"$\dot\theta$ (deg/s)")
ax.set_title("Phase portrait, spirals into hanging (180°)"); ax.legend(fontsize=7)
fig.savefig(out + "phase.pdf"); plt.close(fig)

# 6 small-angle closed form vs numeric
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 2.7))
s = simulate(2, P, 0.75)
s = {k_: v[np.degrees(s["th"]) <= 90] for k_, v in s.items()}
th_lin = small_angle(s["t"], 2, P)
a1.plot(s["t"], np.degrees(s["th"]), color=C[0], label="RK4 (exact)")
a1.plot(s["t"], np.degrees(th_lin), "--", color=C[1], label="small-angle formula")
a1.set_ylim(0, 60); a1.set_xlabel("$t$ (s)"); a1.set_ylabel(r"$\theta$ (deg)")
a1.set_title(r"$\theta_0=2^\circ$"); a1.legend(fontsize=7)
err = np.degrees(th_lin - s["th"])
th_deg = np.degrees(s["th"])
a2.plot(th_deg, np.abs(err) / th_deg * 100, color=C[2])
a2.set_xlim(2, 90); a2.set_ylim(0, 6)
a2.set_xlabel(r"true $\theta$ (deg)"); a2.set_ylabel("formula error (%)")
a2.set_title("Error grows with angle")
fig.tight_layout(); fig.savefig(out + "small_angle.pdf"); plt.close(fig)
# print where error hits 1% and 5%
rel = np.abs(err) / th_deg * 100
for lim in (1, 5):
    i = np.nonzero(rel > lim)[0][0]
    print(f"small-angle error > {lim}% at theta = {th_deg[i]:.1f} deg")

# 7 fall time vs release angle
th0s = np.concatenate([np.linspace(0.5, 5, 10), np.linspace(6, 85, 40)])
t90 = []; t180 = []; tf90 = []
for th0 in th0s:
    s = simulate(th0, P, 3.0, dt=5e-4)
    t90.append(crossing_time(s, 90)); t180.append(crossing_time(s, 180))
    tf90.append(frictionless_time(th0, 90, dict(P, b=0, tau_c=0)))
fig, ax = plt.subplots(figsize=(6, 2.8))
ax.plot(th0s, t90, color=C[0], label="to horizontal (90°)")
ax.plot(th0s, t180, color=C[1], label="to bottom (180°)")
ax.plot(th0s, tf90, ":", color="k", label="to 90°, frictionless exact integral")
ax.set_xlabel(r"release angle $\theta_0$ (deg from upright)"); ax.set_ylabel("time (s)")
ax.set_title("Fall time vs release angle (V2 arm 1)"); ax.legend(fontsize=7)
fig.savefig(out + "fall_time.pdf"); plt.close(fig)

# 8 pivot force
s = simulate(10, P, 1.0)
Rx, Ry = pivot_force(s, P)
fig, ax = plt.subplots(figsize=(6, 2.6))
ax.plot(s["t"], Rx, color=C[0], label="$R_x$"); ax.plot(s["t"], Ry, color=C[1], label="$R_y$")
ax.plot(s["t"], np.hypot(Rx, Ry), color="k", lw=0.8, label=r"$|R|$")
ax.axhline(P["m"] * P["g"], ls=":", color="gray")
ax.set_xlabel("$t$ (s)"); ax.set_ylabel("N"); ax.legend(fontsize=7, ncol=3)
ax.set_title(r"Pivot force on the arm, $\theta_0=10^\circ$ (dotted = $mg$)")
fig.savefig(out + "pivot_force.pdf"); plt.close(fig)

# numbers for the PDF
s = simulate(10, P, 3.0)
print("t90", crossing_time(s, 90), "t180", crossing_time(s, 180), "max w deg/s", np.degrees(np.abs(s["w"]).max()),
      "max |R|", np.hypot(*pivot_force(s, P)).max())
k_ = P["m"]*P["g"]*P["lc"]
print("wn", math.sqrt(k_/P["I"]), "period", 2*math.pi*math.sqrt(P["I"]/k_), "zeta", P["b"]/(2*math.sqrt(P["I"]*k_)),
      "r1", -P["b"]/(2*P["I"])+math.sqrt((P["b"]/(2*P["I"]))**2+k_/P["I"]))
for th0 in (1,5,10,30):
    s=simulate(th0,P,3.0); print(th0, crossing_time(s,90), crossing_time(s,180))
