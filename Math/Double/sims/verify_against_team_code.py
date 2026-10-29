"""Check that Math/shared/nlink_cart.py reproduces the team's double-pendulum code exactly.

Run:  python verify_against_team_code.py <path to LegacyPi/Code/DoublePendulum of etwan007/ENGT480>
      (branch experiment/legacy-pi-recovery, commit ba019f9). The team files are only imported, never changed.

Checks:
  1. PythonMasterMath2.py (force model): discrete A, B, LQR Kd and Kalman Ld against control_matrices2.txt.
  2. PythonMasterDouble-Claude.py (= PythonMaster2_auto_improved.py, balance): K and L from design().
  3. PythonMaster2_swingup.py: dynamics f, step(), balance_design() K/P/L, swing observer gain,
     the staircase reference and the TV-LQR gains along double_swingup_trajectory.json.
"""
import importlib.util
import os
import re
import sys
import types

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
import nlink_cart as nl  # noqa: E402

team = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
sys.path.insert(0, team)
sys.modules.setdefault("serial", types.ModuleType("serial"))   # the scripts import pyserial at the top


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(team, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def report(what, a, b, tol=1e-6):
    """Relative to the largest entry: the txt file keeps 6 significant digits, and the TV-LQR gains
    come from finite differences."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    err = float(np.max(np.abs(a - b)) / max(1.0, np.max(np.abs(b))))
    print(f"{'OK ' if err < tol else 'BAD'} {what:55s} max relative diff {err:.1e}")
    return err < tol


ok = True
# 1. force model ------------------------------------------------------------------
txt = open(os.path.join(team, "control_matrices2.txt")).read()


def block(title, shape):
    body = re.search(r"--- " + re.escape(title) + r" ---\s*(.*?)(?=---|\Z)", txt, re.S).group(1)
    return np.array([float(v) for v in re.findall(r"[-+]?\d*\.?\d+(?:e[-+]?\d+)?", body)]).reshape(shape)


rig = nl.Rig([nl.Link(0.207, 0.087, 0.2, 0.00123324992), nl.Link(0.210, 0.106, 0.25, 0.00197563667)], M=0.910)
Ad, Bd = nl.c2d(*nl.linear_force(rig), 0.01)
K, _ = nl.dlqr(Ad, Bd, np.diag([100, 1, 100, 1, 20, 10.0]), np.array([[0.1]]))
C = np.zeros((3, 6)); C[0, 0] = C[1, 2] = C[2, 4] = 1
L, _ = nl.dlqe(Ad, C, np.diag([0.2, 0.001, 0.2, 0.001, 0.2, 0.001]), 0.01 * np.eye(3))
ok &= report("PythonMasterMath2 A (5 digits in the txt)", Ad, block("Matrix A (Linearized)", (6, 6)), 1e-5)
ok &= report("PythonMasterMath2 B", Bd, block("Matrix B", (6, 1)), 1e-7)
ok &= report("PythonMasterMath2 Kd", K, block("LQR Gain (Kd)", (1, 6)), 1e-4)
ok &= report("PythonMasterMath2 Ld", L, block("Kalman Gain (Ld)", (6, 3)), 1e-5)

# 2. balance script ----------------------------------------------------------------
bc = load("bal", "PythonMasterDouble-Claude.py")
d = bc.design()
r = bc.arm_ratios()
rigr = nl.Rig.from_team_ratios(r)
Q = nl.bryson_Q(2, [bc.LQR_ARM1_ANGLE_DEG, bc.LQR_ARM2_ANGLE_DEG], bc.LQR_ARM_RATE_DEG_S, bc.LQR_CART_M,
                bc.LQR_CART_SPEED_M_S)
R = np.array([[1 / bc.LQR_CART_ACCEL_M_S2**2]])
mine = nl.balance_design_ramp(rigr, Q, R, 0.01, bc.CONTROL_LATENCY_MS / 1000, arm_disturbance=bc.ARM_DISTURBANCE_RAD_S2,
                              encoder_noise_counts=bc.ENCODER_NOISE_COUNTS)
ok &= report("PythonMasterDouble-Claude continuous A", mine["A"], d["A"], 1e-9)
ok &= report("PythonMasterDouble-Claude K", mine["K"], d["K"], 1e-6)
ok &= report("PythonMasterDouble-Claude L", mine["L"], d["L"], 1e-9)
print("    K =", np.array2string(d["K"], precision=4))

# 3. swing-up script ---------------------------------------------------------------
su = load("swing", "PythonMaster2_swingup.py")
r = su.arm_ratios()
rigs = nl.Rig.from_team_ratios(r)
z = np.array([2.1, -3.0, 2.6, 5.0, 0.1, -0.4])
ok &= report("swing-up f(z, a) vs accel_dynamics", su.f(z, 3.0, r), nl.accel_dynamics(rigs, z, 3.0), 1e-9)
ok &= report("swing-up step() vs stair_step", su.step(z, 1.0, 3.0, r), nl.stair_step(rigs, z, 1.0, 3.0, 0.01, 0.008), 1e-9)
bal = su.balance_design(r)
rb = dict(r); rb["B2"] = su.BALANCE_B2
Qb = nl.bryson_Q(2, [su.LQR_ARM1_ANGLE_DEG, su.LQR_ARM2_ANGLE_DEG], su.LQR_ARM_RATE_DEG_S, su.LQR_CART_M,
                 su.LQR_CART_SPEED_M_S)
mb = nl.balance_design_stair(nl.Rig.from_team_ratios(rb), Qb, np.array([[1 / su.LQR_CART_ACCEL_M_S2**2]]), 0.01,
                             su.BALANCE_LATENCY_MS / 1000)
ok &= report("swing-up balance_design K", mb["K"], bal["K"], 1e-5)
ok &= report("swing-up balance_design L", mb["L"], bal["L"], 1e-7)
ok &= report("swing-up observer gain", nl.swing_observer_gain(2, disturbance=su.SWING_DISTURBANCE_RAD_S2),
             su.swing_observer_gain(), 1e-12)
traj = su.load_trajectory(r)
aref = nl.stair_reference(traj["z"].T, 0.01, su.CONTROL_LATENCY_MS / 1000)
ok &= report("staircase reference a_k", aref, traj["a"], 1e-9)
Ks_team = su.tvlqr(traj, r, bal["P"])
Qs = nl.bryson_Q(2, su.SWING_ANGLE_DEG, su.SWING_RATE_DEG_S, su.SWING_CART_M, su.SWING_CART_SPEED_M_S)
Ks = nl.tvlqr_stair(rigs, traj["z"].T, traj["a"], Qs, np.array([[1 / su.SWING_ACCEL_M_S2**2]]), bal["P"], 0.01,
                    su.CONTROL_LATENCY_MS / 1000)
ok &= report("TV-LQR gains along the stored plan (250 steps)", np.vstack(Ks), np.vstack(Ks_team), 1e-6)
print("ALL MATCH" if ok else "MISMATCH")
