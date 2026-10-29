"""Single pendulum on a cart: the model and gains exactly as PythonMasterUpExpClaudeImproved.py builds them.

The symbolic part below is copied from the controller (lines 158-231 of
etwan007/ENGT480, branch experiment/legacy-pi-recovery, commit ba019f9,
LegacyPi/Code/SinglePendulum/PythonMasterUpExpClaudeImproved.py) so that every
number printed here is the number the rig uses. Only the function signature of
design_lqg was widened so the balance-only Q (5,5,5,5) can be compared.

Run:  python single_model.py          (prints every matrix and gain)
"""
import json

import control as ctrl
import numpy as np
import sympy as sp

# ---- copied from the controller: symbols, values, Lagrangian ----
t, g, l, m1, mcart, B_cart_drag = sp.symbols('t g l m1 mcart B_cart_drag', positive=True)
theta = sp.Function('theta')(t)
x = sp.Function('x')(t)
I, H, V, F, T_drag = sp.symbols('I H V F T_drag', real=True)

Ts = 1 / 100

length = 0.2
lval = 0.05
Ival = 0.003
m1val = 0.260
T_dragVal = 0.0
mcartVal = 0.969
B_cart_dragVal = 0.5
gval = 9.81
vals = {m1: m1val, mcart: mcartVal, l: lval, g: gval, I: Ival, T_drag: T_dragVal, B_cart_drag: B_cart_dragVal}

T = (1/2)*(mcart+m1)*x.diff(t)**2 - m1*l*sp.cos(theta)*x.diff(t)*theta.diff(t) + (1/2)*(m1*l**2+I)*theta.diff(t)**2
U = m1*g*l*sp.cos(theta)
L = T - U

EL_x = sp.Eq(sp.diff(sp.diff(L, x.diff(t)), t) - sp.diff(L, x), F - B_cart_drag * x.diff(t))
EL_theta = sp.Eq(sp.diff(sp.diff(L, theta.diff(t)), t) - sp.diff(L, theta), -T_drag)

Eq1 = EL_x.lhs - EL_x.rhs
Eq2 = EL_theta.lhs - EL_theta.rhs
x2div, theta2div = sp.symbols('x2div theta2div', real=True)
Eq1 = Eq1.subs({sp.Derivative(x, t, 2): x2div, sp.Derivative(theta, t, 2): theta2div})
Eq2 = Eq2.subs({sp.Derivative(x, t, 2): x2div, sp.Derivative(theta, t, 2): theta2div})
Subs = sp.solve([Eq1, Eq2], [x2div, theta2div], simplify=True)

Y1, Y2, Y3, Y4 = sp.symbols('Y1 Y2 Y3 Y4')
StateSubs = {theta: Y1, sp.Derivative(theta, t): Y2, x: Y3, sp.Derivative(x, t): Y4}
F1 = Subs[theta2div].subs(StateSubs)
F2 = Subs[x2div].subs(StateSubs)
NonLinMod = sp.Matrix([Y2, F1, Y4, F2])
Y = sp.Matrix([Y1, Y2, Y3, Y4])
A_sym = NonLinMod.jacobian(Y)
B_sym = NonLinMod.diff(F)
C = sp.Matrix([[1, 0, 0, 0], [0, 0, 1, 0]])
D = sp.Matrix([0, 0])
Equilibrium = {Y1: 0, Y2: 0, Y3: 0, Y4: 0}

Q_SWINGUP_SCRIPT = (40, 5, 150, 60)   # PythonMasterUpExpClaudeImproved.py line 229
Q_BALANCE_SCRIPTS = (5, 5, 5, 5)      # PythonMaster.py, PythonMaster_auto.py, PythonMasterSwingUpExp.py
R_LQR = 1
QN = (0.5, 0.5, 0.5, 0.5)             # process noise covariance (dlqe)
RN = 0.01                             # measurement noise covariance, times I2


def continuous_ab(I_value=Ival):
    v = dict(vals)
    v[I] = I_value
    A = np.array(A_sym.subs(v).subs(Equilibrium), dtype=float)
    B = np.array(B_sym.subs(v).subs(Equilibrium), dtype=float)
    return A, B


def design_lqg(I_value=Ival, Q=Q_SWINGUP_SCRIPT):
    """Same as the controller's design_lqg, with Q as an argument."""
    v = dict(vals)
    v[I] = I_value
    A_num = A_sym.subs(v).subs(Equilibrium)
    B_num = B_sym.subs(v).subs(Equilibrium)
    ss_disc = ctrl.c2d(ctrl.ss(A_num, B_num, C, D), Ts)
    K, _, _ = ctrl.dlqr(ss_disc, sp.diag(*Q), R_LQR)
    L_gain, _, _ = ctrl.dlqe(ss_disc.A, sp.diag(1, 1, 1, 1), ss_disc.C, sp.diag(*QN), RN * sp.diag(1, 1))
    return ss_disc, np.asarray(K, dtype=float), np.asarray(L_gain, dtype=float)


def w0_from_inertia(I_value):
    """Small-swing natural frequency of the hanging pendulum (pivot fixed)."""
    return float(np.sqrt(m1val * gval * lval / (I_value + m1val * lval**2)))


def inertia_from_w0(w0):
    """Controller line 676: the CoM inertia that makes the model swing at w0."""
    return max(m1val * gval * lval / w0**2 - m1val * lval**2, 1e-6)


def summary(I_value, Q):
    ss, K, Lg = design_lqg(I_value, Q)
    A, B = continuous_ab(I_value)
    Ad, Bd, Cd = (np.asarray(m, dtype=float) for m in (ss.A, ss.B, ss.C))
    return {
        "I": I_value, "Q": list(Q), "w0": w0_from_inertia(I_value),
        "A": A.tolist(), "B": B.flatten().tolist(),
        "open_loop_poles": sorted(np.linalg.eigvals(A).real.tolist()),
        "Ad": Ad.tolist(), "Bd": Bd.flatten().tolist(),
        "K": K.flatten().tolist(),
        "L": Lg.tolist(),
        "cl_poles_K": np.linalg.eigvals(Ad - Bd @ K).tolist(),
        "cl_poles_2K": np.linalg.eigvals(Ad - 2 * Bd @ K).tolist(),
        "est_poles_filter_form": np.linalg.eigvals(Ad - Ad @ Lg @ Cd).tolist(),
    }


if __name__ == "__main__":
    np.set_printoptions(precision=5, suppress=True, linewidth=120)
    print("theta'' =", sp.simplify(Subs[theta2div]))
    print("x''     =", sp.simplify(Subs[x2div]))
    print("A(eq)   =", sp.simplify(A_sym.subs(Equilibrium)))
    print("B(eq)   =", sp.simplify(B_sym.subs(Equilibrium)))
    I_hw = inertia_from_w0(7.2881)   # IDENTIFY result of run balance_20261027_150517
    out = {}
    for name, Iv, Q in (("nominal_swingQ", Ival, Q_SWINGUP_SCRIPT),
                        ("identified_swingQ", I_hw, Q_SWINGUP_SCRIPT),
                        ("nominal_balanceQ", Ival, Q_BALANCE_SCRIPTS),
                        ("identified_balanceQ", I_hw, Q_BALANCE_SCRIPTS)):
        s = summary(Iv, Q)
        out[name] = s
        print(f"\n== {name}: I={Iv:.6f} kg m^2, w0={s['w0']:.4f} rad/s, Q={Q}")
        print("A =\n", np.array(s["A"]))
        print("B =", np.array(s["B"]))
        print("open-loop poles:", np.round(s["open_loop_poles"], 4))
        print("Ad =\n", np.array(s["Ad"]))
        print("Bd =", np.array(s["Bd"]))
        print("K  =", np.array(s["K"]))
        print("L  =\n", np.array(s["L"]))
        print("|z| closed loop with K :", np.round(np.abs(s["cl_poles_K"]), 4))
        print("|z| closed loop with 2K:", np.round(np.abs(s["cl_poles_2K"]), 4))
        print("|z| estimator (as used):", np.round(np.abs(s["est_poles_filter_form"]), 4))
    with open("single_model_numbers.json", "w") as fh:
        json.dump(out, fh, indent=1, default=lambda z: [z.real, z.imag])
