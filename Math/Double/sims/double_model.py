"""Double pendulum on a cart: every model, matrix and gain the team's double scripts use, recomputed.

Uses Math/shared/nlink_cart.py (checked against the team code by verify_against_team_code.py).
Run:  python double_model.py      (prints everything, writes double_model_numbers.json; a few seconds)

Scripts covered (etwan007/ENGT480, branch experiment/legacy-pi-recovery, commit ba019f9, LegacyPi/Code/DoublePendulum):
  PythonMasterMath2.py + PythonMaster2_auto.py        force model, Q diag(100,1,100,1,20,10), R 0.1, x1.5
  PythonMasterDouble-Claude.py (= PythonMaster2_auto_improved.py on the Pi)   acceleration model, delay, Bryson
  PythonMaster2_swingup.py                             plan + TV-LQR + the same balance on a staircase model
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
import nlink_cart as nl  # noqa: E402

np.set_printoptions(precision=5, suppress=True, linewidth=140)

# ---- physical values (Code/Global/physical_parameters.py, PythonMasterMath2.py) ----
ARM1 = nl.Link(m=0.207, c=0.087, L=0.2, I=0.00123324992)
ARM2 = nl.Link(m=0.210, c=0.106, L=0.25, I=0.00197563667)
CART = 0.969 - 0.059
PHYS = nl.Rig([ARM1, ARM2], M=CART, names=["arm 1", "arm 2"])

# ---- ratio sets used on the rig (params.md) ----
RATIOS = {
    "physical (calculated)": None,
    "balance script SYSID (PythonMasterDouble-Claude.py)": dict(P1=5.22342, P2=2.01257, J2r=0.414023, H=0.394859,
                                                              B1=3.91127e-11, B2=0.03),
    "SysID new arm 1 (2026-10-27)": dict(P1=5.10701, P2=1.86426, J2r=0.389109, H=0.384233, B1=0.100002,
                                         B2=0.00487974),
    "swing-fit (stored plan, 2026-10-27)": dict(P1=5.16428, P2=1.80161, J2r=0.39142, H=0.39247, B1=0.0, B2=0.11396),
}


def rig_for(name):
    r = RATIOS[name]
    return PHYS if r is None else nl.Rig.from_team_ratios(r)


def ratios_of(rig):
    H, p = rig.h(), rig.p()
    J1 = H[0, 0]
    return dict(J1=J1, P1=p[0] / J1, P2=p[1] / J1, J2r=H[1, 1] / J1, H=H[0, 1] / J1)


def hanging_modes(rig):
    """Small swings about hanging: H th'' = -g diag(p) th  ->  frequencies and mode shapes."""
    H, p = rig.h(), rig.p()
    w2, V = np.linalg.eig(np.linalg.solve(H, nl.G * np.diag(p)))
    order = np.argsort(w2)
    w = np.sqrt(w2[order])
    V = V[:, order] / V[0, order]
    return w, V


def upright_modes(rig):
    """Cart held still (a = 0) at upright: H th'' = +g diag(p) th  ->  growth rates (unstable poles)."""
    H, p = rig.h(), rig.p()
    s2, V = np.linalg.eig(np.linalg.solve(H, nl.G * np.diag(p)))
    order = np.argsort(s2)
    return np.sqrt(s2[order]), V[:, order] / V[0, order]


def team_force_design():
    """PythonMasterMath2.py: force model, cart 0.910 kg, no drag; Ts 0.01."""
    A, B = nl.linear_force(PHYS)
    Ad, Bd = nl.c2d(A, B, 0.01)
    K, _ = nl.dlqr(Ad, Bd, np.diag([100, 1, 100, 1, 20, 10.0]), np.array([[0.1]]))
    C = np.zeros((3, 6)); C[0, 0] = C[1, 2] = C[2, 4] = 1
    L, _ = nl.dlqe(Ad, C, np.diag([0.2, 0.001, 0.2, 0.001, 0.2, 0.001]), 0.01 * np.eye(3))
    return dict(A=A, B=B, Ad=Ad, Bd=Bd, K=K, L=L, C=C,
                cl1=np.linalg.eigvals(Ad - Bd @ K), cl15=np.linalg.eigvals(Ad - 1.5 * Bd @ K))


def balance_claude(ratios=None, latency_ms=9.0, angle_deg=(2.0, 2.0), rate=60.0, cart=0.05, speed=0.3, accel=1.3):
    """PythonMasterDouble-Claude.py design() with its settings (the 767 s rig run used exactly these)."""
    r = ratios or RATIOS["balance script SYSID (PythonMasterDouble-Claude.py)"]
    rig = nl.Rig.from_team_ratios(r)
    Q = nl.bryson_Q(2, list(angle_deg), rate, cart, speed)
    return nl.balance_design_ramp(rig, Q, np.array([[1 / accel**2]]), 0.01, latency_ms / 1000)


def balance_swingup():
    """PythonMaster2_swingup.balance_design: swing-fit ratios with B2 replaced by BALANCE_B2 = 0.03."""
    r = dict(RATIOS["swing-fit (stored plan, 2026-10-27)"]); r["B2"] = 0.03
    Q = nl.bryson_Q(2, [2.0, 2.0], 60.0, 0.05, 0.3)
    return nl.balance_design_stair(nl.Rig.from_team_ratios(r), Q, np.array([[1 / 1.3**2]]), 0.01, 0.009)


def to_list(a):
    return np.round(np.real(np.asarray(a)), 8).tolist()


def main():
    out = {}
    print("=== Link constants (physical values) ===")
    p, H = PHYS.p(), PHYS.h()
    print("p  = m_j c_j + L_j * (mass carried) =", p, "kg m")
    print("H  =\n", H, "kg m^2")
    rr = ratios_of(PHYS)
    print("ratios:", {k: round(v, 5) for k, v in rr.items()})
    out["p"], out["H"], out["ratios_physical"] = to_list(p), to_list(H), rr

    print("\n=== Natural motions ===")
    out["modes"] = {}
    for name in RATIOS:
        rig = rig_for(name)
        wh, Vh = hanging_modes(rig)
        su, Vu = upright_modes(rig)
        print(f"{name}:\n  hanging  w = {wh} rad/s  (periods {2 * np.pi / wh} s), shapes th2/th1 = {Vh[1]}"
              f"\n  upright (cart held) growth = {su} /s, shapes th2/th1 = {Vu[1]}")
        out["modes"][name] = dict(hang_w=to_list(wh), hang_shape=to_list(Vh[1]), up_s=to_list(su),
                                  up_shape=to_list(Vu[1]))

    print("\n=== Acceleration-input linear model (physical values) ===")
    A, B = nl.linear_accel(PHYS)
    print("A =\n", A, "\nB =", B.ravel())
    print("open-loop poles:", np.sort_complex(np.linalg.eigvals(A)))
    Cm = np.zeros((3, 6)); Cm[0, 0] = Cm[1, 2] = Cm[2, 4] = 1
    ctrb = np.hstack([np.linalg.matrix_power(A, k) @ B for k in range(6)])
    obsv = np.vstack([Cm @ np.linalg.matrix_power(A, k) for k in range(6)])
    print("rank controllability", np.linalg.matrix_rank(ctrb), " observability (th1, th2, x)", np.linalg.matrix_rank(obsv))
    C1 = np.zeros((1, 6)); C1[0, 4] = 1
    print("observability with cart position only:", np.linalg.matrix_rank(np.vstack([C1 @ np.linalg.matrix_power(A, k) for k in range(6)])))
    out["accel_model"] = dict(A=to_list(A), B=to_list(B), poles=to_list(np.sort(np.linalg.eigvals(A).real)))

    print("\n=== PythonMasterMath2.py (force model) ===")
    f = team_force_design()
    print("A (continuous) =\n", f["A"], "\nB =", f["B"].ravel())
    print("open-loop poles:", np.sort(np.linalg.eigvals(f["A"]).real))
    print("Kd =", f["K"])
    print("Ld =\n", f["L"])
    print("|z| closed loop, u = -K y:", np.sort(np.abs(f["cl1"])))
    print("|z| closed loop, u = -1.5 K y (PythonMaster2_auto.py):", np.sort(np.abs(f["cl15"])))
    # virtual cart: the motor gets the estimator's cart speed; its rate of change is row 6 of the model
    row = f["A"][5] - 1.5 * f["B"][5, 0] * f["K"][0]
    print("effective cart acceleration law with x1.5: a =", row, "(per [th1, w1, th2, w2, x, v])")
    print("  B6 = 1/(effective mass) =", f["B"][5, 0], "-> effective mass", 1 / f["B"][5, 0], "kg")
    out["force"] = dict(A=to_list(f["A"]), B=to_list(f["B"]), Ad=to_list(f["Ad"]), Bd=to_list(f["Bd"]),
                        K=to_list(f["K"]), L=to_list(f["L"]), cl1=to_list(np.sort(np.abs(f["cl1"]))),
                        cl15=to_list(np.sort(np.abs(f["cl15"]))), accel_law=to_list(row))

    print("\n=== PythonMasterDouble-Claude.py (balance, acceleration model, 9 ms delay) ===")
    b = balance_claude()
    print("Phi =\n", b["Phi"], "\nG0 =", b["G0"].ravel(), "\nG1 =", b["G1"].ravel())
    print("K =", b["K"])
    print("L =\n", b["L"])
    print("closed-loop |z| (7 states):", np.sort(np.abs(b["cl_eig"])))
    s = np.log(b["cl_eig"].astype(complex)) / 0.01
    print("as continuous poles:", np.sort_complex(s))
    out["balance_claude"] = dict(Phi=to_list(b["Phi"]), G0=to_list(b["G0"]), G1=to_list(b["G1"]), K=to_list(b["K"]),
                                 L=to_list(b["L"]), cl_abs=to_list(np.sort(np.abs(b["cl_eig"]))),
                                 cl_s=[[float(v.real), float(v.imag)] for v in np.sort_complex(s)])
    for lat in (0.0, 6.0, 9.0, 12.0):
        bb = balance_claude(latency_ms=lat)
        print(f"  latency {lat:4.1f} ms -> K = {np.round(bb['K'][0], 2)}")
    out["balance_claude_latency"] = {str(lat): to_list(balance_claude(latency_ms=lat)["K"]) for lat in (0.0, 6.0, 9.0, 12.0)}

    print("\n=== PythonMaster2_swingup.py balance (staircase model, swing-fit ratios, B2 0.03) ===")
    bs = balance_swingup()
    print("K =", bs["K"])
    print("rig log 2026-10-27 18:46 balance_gain = [-138.669, 0.414, 232.784, 28.190, 20.548, 21.318, 0.0]")
    out["balance_swingup"] = dict(K=to_list(bs["K"]), cl_abs=to_list(np.sort(np.abs(bs["cl_eig"]))))

    print("\n=== Swing observer gain (PythonMaster2_swingup.swing_observer_gain) ===")
    Ls = nl.swing_observer_gain(2, disturbance=3.0)
    print(Ls)
    out["L_swing"] = to_list(Ls)

    with open(os.path.join(HERE, "double_model_numbers.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote double_model_numbers.json")


if __name__ == "__main__":
    main()
