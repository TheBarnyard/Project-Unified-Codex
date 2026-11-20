"""Write tables.tex (worked-example numbers) for the PDF."""
import math
from falling_pendulum import *
P = dict(V2_ARM1)
s = simulate(10, P, 0.6)
k = kinematics(s, P)
Rx, Ry = pivot_force(s, P)
rows = []
dt = s["t"][1] - s["t"][0]
for tt in [0, 0.1, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]:
    i = int(round(tt / dt))
    rows.append(f"{tt:.2f} & {math.degrees(s['th'][i]):.2f} & {math.degrees(s['w'][i]):.1f} & {math.degrees(s['a'][i]):.0f} & "
                f"{k['x'][i]*1000:.1f} & {k['y'][i]*1000:.1f} & {math.hypot(Rx[i], Ry[i]):.3f} \\\\")
with open("tables.tex", "w") as f:
    f.write("\\begin{tabular}{rrrrrrr}\n\\toprule\n$t$ (s) & $\\theta$ (deg) & $\\dot\\theta$ (deg/s) & $\\ddot\\theta$ (deg/s$^2$) & $x_{tip}$ (mm) & $y_{tip}$ (mm) & $|R|$ (N)\\\\\n\\midrule\n")
    f.write("\n".join(rows))
    f.write("\n\\bottomrule\n\\end{tabular}\n")
rows = []
for th0 in (0.5, 1, 2, 5, 10, 20, 30, 45, 60, 80):
    s = simulate(th0, P, 3.0, dt=2e-4)
    t90, t180 = crossing_time(s, 90), crossing_time(s, 180)
    tf = frictionless_time(th0, 90, dict(P, b=0, tau_c=0))
    import numpy as np
    wmax = math.degrees(np.abs(s["w"][s["t"] <= t180 + 0.01]).max())
    rows.append(f"{th0:g} & {t90:.4f} & {tf:.4f} & {t180:.4f} & {wmax:.0f} \\\\")
with open("tables2.tex", "w") as f:
    f.write("\\begin{tabular}{rrrrr}\n\\toprule\n$\\theta_0$ (deg) & $t_{90}$ RK4 (s) & $t_{90}$ frictionless integral (s) & $t_{180}$ RK4 (s) & $|\\dot\\theta|_{max}$ (deg/s)\\\\\n\\midrule\n")
    f.write("\n".join(rows))
    f.write("\n\\bottomrule\n\\end{tabular}\n")
print(open("tables.tex").read()); print(open("tables2.tex").read())
