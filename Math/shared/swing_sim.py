"""Closed-loop simulation of the team's swing-up-and-balance controller (PythonMaster2_swingup.py), for any
number of links. The controller part follows the script's control loop step by step; the plant is the
nonlinear n-link model driven by a stepper (speed jumps to the timer-rounded speed a short time after
each sample).

What is simulated, per 10 ms cycle (script line references are to PythonMaster2_swingup.py at
etwan007/ENGT480 commit ba019f9):
  1. measure: arm 1 angle and the joint angle(s) from 14-bit encoders (rounded to counts, optional noise),
     cart position from the step count (rounded to steps);
  2. observer correction x_hat += L (z - C x_hat), cart speed state set to the speed last sent;
  3. SWING: a = a_ref[k] - K_k [x_hat - z_ref[k]; a_prev - a_ref[k-1]], abort past 35 deg or 0.36 m;
     after the last plan sample: BALANCE: a = -K_bal [x_hat; a_prev], lost past 30 deg;
  4. limits: |a| <= 16, accelerating further only with the torque left 16 (1 - |v|/1.0), |v| <= 1.0;
  5. the Arduino timer rounds the speed: v_sent = 125000/(round(125000/f) - 1 + 1) steps/s;
  6. predict x_hat with the nonlinear staircase model, using the speed really sent.
Not simulated: the WAIT/RECOVER phases between attempts, sensor-age compensation (readings are taken
exactly at the sample), radio dropouts, auto-trim, the 1-step hold dither, missed steps.
"""
import numpy as np

import nlink_cart as nl

RAD_PER_COUNT = 2 * np.pi / 16384
M_PER_STEP = 0.638175 / 6400


class TeamSwingController:
    def __init__(self, rig_model, plan_Z, a_ref, Ks, bal, L_swing, T=0.01,
                 accel_max=16.0, speed_max=1.0, motor_top=1.0, abort_deg=35.0, abort_cart=0.36,
                 lost_deg=30.0, tau_model=0.008, timer=True):
        self.rig, self.Z, self.aref, self.Ks, self.bal, self.Ls = rig_model, plan_Z, a_ref, Ks, bal, L_swing
        self.T, self.amax, self.vmax, self.vtop = T, accel_max, speed_max, motor_top
        self.abort, self.abort_cart, self.lost, self.tau = np.radians(abort_deg), abort_cart, np.radians(lost_deg), tau_model
        self.timer = timer      # False: the Arduino would run exactly the requested speed (no rounding)
        n = rig_model.n
        self.n = n
        self.x_hat = np.zeros(2 * n + 2)
        self.x_hat[0:2 * n:2] = np.pi
        self.a_prev = 0.0
        self.v_state = 0.0
        self.k = 0
        self.mode = "SWING"
        self.why = ""
        self.first = True
        self.C = np.zeros((n + 1, 2 * n + 2))
        for i in range(n):
            self.C[i, 2 * i] = 1.0
        self.C[n, 2 * n] = 1.0

    def __call__(self, th_meas, cart_meas):
        """th_meas: absolute angles (rad, from upright, as the script builds them); returns the speed sent."""
        n, T = self.n, self.T
        xh = self.x_hat
        if self.first:
            xh[0] = np.pi + nl.wrap(th_meas[0] - np.pi)
            for i in range(1, n):
                xh[2 * i] = xh[2 * (i - 1)] + nl.wrap(th_meas[i] - th_meas[i - 1])
            self.first = False
        L = self.bal["L"] if self.mode == "BALANCE" else self.Ls
        innov = np.zeros(n + 1)
        for i in range(n):
            innov[i] = nl.wrap(th_meas[i] - xh[2 * i])
        innov[n] = cart_meas - xh[2 * n]
        xh = xh + L @ innov
        xh[2 * n + 1] = self.v_state
        a = 0.0
        if self.mode == "SWING":
            k = self.k
            e = np.concatenate([xh - self.Z[:, k], [self.a_prev - (self.aref[k - 1] if k > 0 else 0.0)]])
            for i in range(n):
                e[2 * i] = nl.wrap(e[2 * i])
            a = self.aref[k] - float((self.Ks[k] @ e)[0])
            err = max(abs(e[2 * i]) for i in range(n))
            if err > self.abort or abs(cart_meas) > self.abort_cart:
                self.mode = "ABORT"
                self.why = (f"{np.degrees(err):.0f} deg off the plan" if err > self.abort else
                            f"cart at {cart_meas * 1000:+.0f} mm")
                self.why += f" at k={k}"
                a = -np.sign(self.v_state) * self.amax if abs(self.v_state) > 0.05 else -self.v_state / T
            else:
                self.k += 1
                if self.k >= len(self.aref):
                    for i in range(n):
                        xh[2 * i] = nl.wrap(xh[2 * i])
                    self.mode = "BALANCE"
        elif self.mode == "BALANCE":
            for i in range(n):
                xh[2 * i] = nl.wrap(xh[2 * i])
            if max(abs(xh[2 * i]) for i in range(n)) > self.lost:
                self.mode = "LOST"
                self.why = "balance lost"
            a = -float((self.bal["K"] @ np.concatenate([xh, [self.a_prev]]))[0])
        else:   # ABORT / LOST: brake
            a = -np.sign(self.v_state) * min(self.amax, abs(self.v_state) / T)
        # limits (script lines "limits, speed command")
        a = float(np.clip(a, -self.amax, self.amax))
        if a * self.v_state > 0:
            a_lim = self.amax * max(0.05, 1.0 - abs(self.v_state) / self.vtop)
            a = float(np.clip(a, -a_lim, a_lim))
        v_cmd = float(np.clip(self.v_state + a * T, -self.vmax, self.vmax))
        v_sent = nl.timer_speed(v_cmd) if self.timer else v_cmd
        a = (v_sent - self.v_state) / T
        x_pred = nl.stair_step(self.rig, xh, self.a_prev, a, T, self.tau)
        self.a_prev = a
        self.v_state = v_sent
        x_pred[2 * n + 1] = v_sent
        self.log = dict(x_hat=xh.copy(), v_cmd=v_cmd, v_sent=v_sent, a=a, mode=self.mode, k=self.k)
        self.x_hat = x_pred
        return v_sent


def run(rig_true, ctrl, T_total, Ts=0.01, tau_true=0.008, h=0.0005, noise_counts=0.0, seed=0, z0=None,
        stop_on_fail=True, disturb=None, enc_offsets=None):
    """Simulate. Returns dict of arrays sampled every Ts (state at the sample instant, before the command)."""
    n = rig_true.n
    rng = np.random.default_rng(seed)
    z = np.zeros(2 * n + 2) if z0 is None else z0.astype(float).copy()
    if z0 is None:
        z[0:2 * n:2] = np.pi
    f = lambda zz, aa: nl.accel_dynamics(rig_true, zz, aa)

    def coast(z, dt):
        if dt <= 0:
            return z
        m = max(1, int(round(dt / h)))
        for _ in range(m):
            z = nl.rk4(f, z, 0.0, dt / m)
        return z

    out = {k: [] for k in ("t", "z", "x_hat", "v_cmd", "v_sent", "a", "mode", "k")}
    pending = []
    steps = int(round(T_total / Ts))
    for s in range(steps):
        t = s * Ts
        if disturb is not None:
            z = disturb(t, z)
        # sensors: encoder 1 absolute, encoders 2..n measure the joint (relative) angle
        th = z[0:2 * n:2]
        rel = np.concatenate([[th[0]], np.diff(th)])
        if enc_offsets is not None:
            rel = rel + np.asarray(enc_offsets)     # calibration error of each encoder's reference
        cnt = np.round(nl.wrap(rel) / RAD_PER_COUNT + noise_counts * rng.standard_normal(n))
        rel_m = cnt * RAD_PER_COUNT
        th_m = np.cumsum(rel_m)
        x_m = np.round(z[2 * n] / M_PER_STEP) * M_PER_STEP
        v = ctrl(th_m, x_m)
        out["t"].append(t); out["z"].append(z.copy()); out["x_hat"].append(ctrl.log["x_hat"])
        out["v_cmd"].append(ctrl.log["v_cmd"]); out["v_sent"].append(v); out["a"].append(ctrl.log["a"])
        out["mode"].append(ctrl.log["mode"]); out["k"].append(ctrl.log["k"])
        if "trim" in ctrl.log:
            out.setdefault("trim", []).append(ctrl.log["trim"])
        # the new speed lands tau_true after the sample; with tau_true > Ts it lands in a later period
        pending.append((t + tau_true, v))
        cur = t
        while pending and pending[0][0] <= t + Ts + 1e-12:
            ta, vv = pending.pop(0)
            z = coast(z, ta - cur)
            z = nl.speed_jump(rig_true, z, vv - z[2 * n + 1])
            cur = ta
        z = coast(z, t + Ts - cur)
        if stop_on_fail and ctrl.mode in ("ABORT", "LOST") and abs(z[2 * n + 1]) < 1e-6:
            break
        if not np.all(np.isfinite(z)):
            break
    res = {k: np.array(v) for k, v in out.items()}
    for extra in ("trim",):
        if extra in ctrl.log:
            res[extra] = np.array(out.get(extra, []))
    res["why"] = ctrl.why
    res["caught"] = ctrl.mode == "BALANCE" or (ctrl.mode == "LOST")
    res["balanced"] = ctrl.mode == "BALANCE"
    return res


def build(rig_model, plan_Z, settings=None, bal_rig=None):
    """Gains the way the script builds them at startup (PythonMaster2_swingup.run, first lines)."""
    s = dict(SWING_ANGLE_DEG=5.0, SWING_RATE_DEG_S=120.0, SWING_CART_M=0.25, SWING_CART_SPEED_M_S=0.3,
             SWING_ACCEL_M_S2=5.0, LQR_ARM_ANGLE_DEG=2.0, LQR_ARM_RATE_DEG_S=60.0, LQR_CART_M=0.05,
             LQR_CART_SPEED_M_S=0.3, LQR_CART_ACCEL_M_S2=1.3, BALANCE_LATENCY_MS=9.0, CONTROL_LATENCY_MS=8.0,
             SWING_DISTURBANCE_RAD_S2=3.0)
    if settings:
        s.update(settings)
    n = rig_model.n
    tau = s["CONTROL_LATENCY_MS"] / 1000
    Qb = nl.bryson_Q(n, s["LQR_ARM_ANGLE_DEG"], s["LQR_ARM_RATE_DEG_S"], s["LQR_CART_M"], s["LQR_CART_SPEED_M_S"])
    bal = nl.balance_design_stair(bal_rig or rig_model, Qb, np.array([[1 / s["LQR_CART_ACCEL_M_S2"]**2]]), 0.01,
                                  s["BALANCE_LATENCY_MS"] / 1000)
    a_ref = nl.stair_reference(plan_Z, 0.01, tau)
    Qs = nl.bryson_Q(n, s["SWING_ANGLE_DEG"], s["SWING_RATE_DEG_S"], s["SWING_CART_M"], s["SWING_CART_SPEED_M_S"])
    Ks = nl.tvlqr_stair(rig_model, plan_Z, a_ref, Qs, np.array([[1 / s["SWING_ACCEL_M_S2"]**2]]), bal["P"], 0.01, tau)
    Ls = nl.swing_observer_gain(n, disturbance=s["SWING_DISTURBANCE_RAD_S2"])
    return dict(bal=bal, a_ref=a_ref, Ks=Ks, Ls=Ls, settings=s, tau=tau)


class TeamBalanceController:
    """The control loop of PythonMasterDouble-Claude.py (= PythonMaster2_auto_improved.py), for n links:
    Kalman correction (cart speed state set to the speed the script tracks), a = -K [x_hat; a_prev], start ramp,
    limits, the AVERAGE speed over the coming period is sent (v + a T/2), prediction with Phi, G0, G1,
    and auto-trim of the angle references (time constant 6 s, after 1 s, max 3 deg)."""

    def __init__(self, design, n, x0=None, T=0.01, accel_max=15.0, speed_max=0.8, lost_deg=30.0, start_ramp=0.25,
                 auto_trim=True, trim_tc=6.0, trim_delay=1.0, trim_max_deg=3.0):
        self.d, self.n, self.T = design, n, T
        self.amax, self.vmax, self.lost, self.ramp = accel_max, speed_max, np.radians(lost_deg), start_ramp
        self.auto_trim, self.trim_tc, self.trim_delay, self.trim_max = auto_trim, trim_tc, trim_delay, np.radians(trim_max_deg)
        self.x_pred = np.zeros(2 * n + 2) if x0 is None else x0.astype(float).copy()
        self.a_prev = 0.0
        self.v_state = 0.0
        self.off = np.zeros(n)          # trims of encoder 1 and of the joint encoders
        self.t = 0.0
        self.mode, self.why, self.k = "BALANCE", "", 0
        self.first = x0 is None

    def __call__(self, th_meas, cart_meas):
        n, T, d = self.n, self.T, self.d
        rel = np.concatenate([[th_meas[0]], np.diff(th_meas)]) - self.off
        th = np.cumsum(rel)
        if self.first:
            self.x_pred[0:2 * n:2] = th
            self.first = False
        if max(abs(th)) > self.lost and self.mode == "BALANCE":
            self.mode, self.why = "LOST", "angle limit"
        y = np.concatenate([th, [cart_meas]])
        xh = self.x_pred + d["L"] @ (y - d["C"] @ self.x_pred)
        xh[2 * n + 1] = self.v_state
        if self.mode == "BALANCE":
            a = -float((d["K"] @ np.concatenate([xh, [self.a_prev]]))[0])
            if self.ramp > 0 and self.t < self.ramp:
                a *= self.t / self.ramp
        else:
            a = -np.sign(self.v_state) * min(self.amax, abs(self.v_state) / T)
        a = float(np.clip(a, -self.amax, self.amax))
        v_end = self.v_state + a * T
        if abs(v_end) > self.vmax:
            v_end = np.sign(v_end) * self.vmax
            a = (v_end - self.v_state) / T
        v_cmd = self.v_state + 0.5 * a * T
        v_sent = timer_speed_avg(v_cmd)
        x_pred = d["Phi"] @ xh + d["G0"][:, 0] * a + d["G1"][:, 0] * self.a_prev
        self.a_prev = a
        self.v_state = v_end
        x_pred[2 * n + 1] = v_end
        if self.auto_trim and self.t > self.trim_delay and self.mode == "BALANCE":
            k = T / self.trim_tc
            dd = np.clip(k * rel, -self.trim_max - self.off, self.trim_max - self.off)
            self.off += dd
            cum = np.cumsum(dd)
            xh[0:2 * n:2] -= cum
            x_pred[0:2 * n:2] -= cum
        self.log = dict(x_hat=xh.copy(), v_cmd=v_cmd, v_sent=v_sent, a=a, mode=self.mode, k=0, trim=self.off.copy())
        self.x_pred = x_pred
        self.t += T
        return v_sent


def timer_speed_avg(v):
    """The balance script's timer: same rounding as the swing-up script, with its 0.3 mm/s deadband."""
    if abs(v) < 0.0003:
        return 0.0
    return nl.timer_speed(v)
