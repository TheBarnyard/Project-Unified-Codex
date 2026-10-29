"""Closed-loop simulation of the single pendulum running the logic of PythonMasterUpExpClaudeImproved.py.

What is simulated [SIM]:
  * Pendulum: rigid body on a pivot, driven only by the cart's acceleration,
        theta'' = (w0^2 / g) * (g*sin(theta) + x''*cos(theta)) - c*theta'
    theta = 0 is upright, theta = +-pi is hanging (same convention as the code).
    The true w0 and damping c come from the rig's IDENTIFY logs, not the CAD.
  * Cart: the stepper is a velocity source. Every 10 ms it jumps to the commanded
    speed, quantised exactly like the Arduino timer (f = 125000 / N steps/s).
    A speed jump dv kicks the arm: dtheta' = (w0^2/g)*cos(theta)*dv.
  * Sensors: 14-bit encoder quantisation, step-count cart position, the cart
    position used one cycle late (as in the code), a small command delay.
  * Controller: IDENTIFY -> SWING-UP -> LQG with the same constants, the same
    estimator, the same catch rules and the same auto-trim as the script.

Not simulated: radio dropouts, missed stepper steps, serial jitter, Coulomb friction.

Run:  python single_sim.py   (writes sim_run.npz used by make_figures.py)
"""
import numpy as np

import single_model as sm

G = 9.81
ENCODER_COUNTS = 16384
M_PER_STEP = 0.638175 / 6400            # code line 156
TIMER_HZ = 250000                       # Mega 16 MHz / 64 prescaler

# ---- constants copied from the script (lines 255-289) ----
SWING_ACCEL_MAX, SWING_SPEED_MAX, SWING_ENERGY_GAIN = 6.0, 0.6, 4.0
SWING_ENERGY_TARGET, SWING_TARGET_STEP = 1.03, 0.03
SWING_TARGET_MIN, SWING_TARGET_MAX = 0.97, 1.30
SWING_CENTER_KP, SWING_CENTER_KV, SWING_CENTER_SHAPE = 12.0, 6.0, 1
ID_KICK_ACCEL, ID_KICK_TIME, ID_SETTLE_S, ID_COAST_S, ID_HALF_SWINGS = 3.0, 0.12, 0.3, 3.0, 4
AUTO_TRIM_KX, AUTO_TRIM_KV, AUTO_TRIM_MAX_DEG, AUTO_TRIM_DELAY_S = 4.0, 5.0, 3.0, 0.5
CATCH_ANGLE_RAD, CATCH_RATE_RAD_S, CATCH_ENERGY_MIN, CATCH_ENERGY_MAX = 0.30, 3.5, 0.95, 1.15
CATCH_CART_MAX_M, BALANCE_LOST_RAD, BALANCE_CART_LIMIT_M = 0.12, 0.80, 0.22
LQG_SPEED_MAX, LQG_ACCEL_MAX, TRACK_SOFT_LIMIT_M = 0.8, 15.0, 0.30
ALPHA_TD = 0.3
IDENTIFY, SWING, LQG = 0, 1, 2


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def stepper_speed(v_cmd):
    """Speed the stepper really runs at for a commanded speed (code lines 793-802 + ArduinoSlave)."""
    f = -(v_cmd * 6400) / 0.638175
    if f > 2 or f < -2:
        pulses = int((0.5 / f) / (1.0 / 250000.0))
    elif f >= 0:
        pulses = 65535
    else:
        pulses = -65535
    if pulses == 0:
        pulses = 1
    # CTC mode counts 0..TOP, so one compare period is TOP+1 ticks; the pin toggles once per
    # period and the Arduino counts one step per falling edge: 2*(TOP+1) ticks per step.
    step_hz = (TIMER_HZ / 2) / (abs(pulses) + 1)
    direction = -1 if pulses > 0 else 1         # ArduinoSlave motorControl()
    return direction * step_hz * M_PER_STEP, pulses


def measure_natural_frequency(samples):
    """Copy of the script's measure_natural_frequency (lines 349-375)."""
    if len(samples) < 50:
        return None
    t = np.array([s[0] for s in samples], dtype=float) / 1000.0
    a = np.array([s[1] for s in samples], dtype=float)
    a = a - np.mean(a)
    crossings = []
    for i in range(1, len(a)):
        if a[i - 1] < 0 <= a[i] or a[i - 1] > 0 >= a[i]:
            f = a[i - 1] / (a[i - 1] - a[i])
            crossings.append(t[i - 1] + f * (t[i] - t[i - 1]))
    if len(crossings) < 4:
        return None
    half = np.diff(crossings)
    period = 2.0 * float(np.median(half))
    amplitude = float(np.max(np.abs(a)))
    period0 = period / (1.0 + amplitude**2 / 16.0)
    if not 0.3 < period0 < 3.0:
        return None
    edges = np.searchsorted(t, crossings)
    peaks = [float(np.max(np.abs(a[i:j]))) for i, j in zip(edges[:-1], edges[1:]) if j > i]
    decay = 0.0
    if len(peaks) >= 3 and peaks[0] > 0 and peaks[-1] > 0:
        decay = 1.0 - (peaks[-1] / peaks[0]) ** (2.0 / (len(peaks) - 1))
    return 2.0 * np.pi / period0, period0, amplitude, decay, len(half)


class Plant:
    def __init__(self, w0=7.2881, damping=0.20, theta0=np.pi - 0.002, x0=0.0):
        self.w0, self.c = w0, damping
        self.th, self.thd, self.x, self.v = theta0, 0.0, x0, 0.0

    def set_speed(self, v_new):
        dv = v_new - self.v
        self.thd += (self.w0**2 / G) * np.cos(self.th) * dv    # impulse from the speed jump
        self.v = v_new

    def push(self, dthd):
        self.thd += dthd

    def advance(self, dt, h=0.0005):
        n = max(1, int(round(dt / h)))
        h = dt / n
        f = lambda th, thd: (thd, self.w0**2 * np.sin(th) - self.c * thd)
        for _ in range(n):
            k1 = f(self.th, self.thd)
            k2 = f(self.th + h/2*k1[0], self.thd + h/2*k1[1])
            k3 = f(self.th + h/2*k2[0], self.thd + h/2*k2[1])
            k4 = f(self.th + h*k3[0], self.thd + h*k3[1])
            self.th += h/6*(k1[0] + 2*k2[0] + 2*k3[0] + k4[0])
            self.thd += h/6*(k1[1] + 2*k2[1] + 2*k3[1] + k4[1])
            self.x += self.v * h


class Controller:
    """State and per-cycle logic of the script's control loop (lines 585-850)."""

    def __init__(self, angle_offset_deg=0.0):
        self.Ts = sm.Ts
        self.ss, self.K, self.L = sm.design_lqg(sm.Ival)
        self.Ad, self.Bd, self.C = (np.asarray(m, dtype=float) for m in (self.ss.A, self.ss.B, self.ss.C))
        self.w0_model = sm.w0_from_inertia(sm.Ival)
        self.w0 = self.w0_model
        self.offset_err = np.deg2rad(angle_offset_deg)   # calibration error the trim must remove
        self.upright_offset_deg = 0.0
        self.mode = IDENTIFY
        self.u = np.zeros((1, 1))
        self.Ylast = np.zeros((4, 1))
        self.theta_prev = None
        self.theta_prev_ms = None
        self.theta_dot = 0.0
        self.energy_target = SWING_ENERGY_TARGET
        self.swing_direction = 0
        self.xdiv_swing = 0.0
        self.xdiv_sent = 0.0
        self.swing_accel = 0.0
        self.theta_prev_swing = None
        self.swing_peak = -1.0
        self.catch_time = 0.0
        self.catches = []
        self.losses = []
        self.identify_log = []
        self.identify_result = None
        self.loop = 0
        self.e = -1.0
        self.force = 0.0

    def measure(self, plant):
        # encoder counts relative to the calibrated upright, then the trim offset
        th = wrap(plant.th + self.offset_err - np.deg2rad(self.upright_offset_deg))
        q = 2 * np.pi / ENCODER_COUNTS
        return wrap(np.round(th / q) * q)

    def step(self, t, theta_m, x_m, x_start):
        """One control cycle. Returns the cart speed command (m/s)."""
        dt = self.Ts
        if self.loop < 250:
            self.loop += 1
        Yest = self.Ad @ self.Ylast + self.Bd @ self.u
        # velocity from receiver timestamps (lines 324-340)
        ms = int(round(t * 1000))
        if self.theta_prev is not None:
            el = ms - self.theta_prev_ms
            raw = wrap(theta_m - self.theta_prev) / (el / 1000.0)
            self.theta_dot = ALPHA_TD * self.theta_dot + (1 - ALPHA_TD) * raw
        self.theta_prev, self.theta_prev_ms = theta_m, ms
        # correction (angle_packet_fallback.estimate_with_angle)
        meas = np.array([[theta_m], [x_m]])
        Yfin = Yest + self.L @ (meas - self.C @ Yest)
        th1 = theta_m
        self.Ylast = Yfin.copy()
        if abs(x_m - x_start) > TRACK_SOFT_LIMIT_M:
            raise RuntimeError("soft limit")
        self.e = 0.5 * (self.theta_dot / self.w0)**2 + np.cos(th1)

        if self.mode == IDENTIFY:
            kick_end = 4 * ID_KICK_TIME
            if t < kick_end:
                k = int(t // ID_KICK_TIME)
                self.swing_accel = {0: ID_KICK_ACCEL, 1: -ID_KICK_ACCEL, 2: -ID_KICK_ACCEL, 3: ID_KICK_ACCEL}.get(k, 0.0)
                self.xdiv_swing = float(np.clip(self.xdiv_swing + self.swing_accel * dt, -SWING_SPEED_MAX, SWING_SPEED_MAX))
            else:
                self.swing_accel = 0.0
                self.xdiv_swing = 0.0
                if t > kick_end + ID_SETTLE_S:
                    self.identify_log.append((ms, (th1 % (2 * np.pi)) - np.pi))
            done = t > kick_end + ID_SETTLE_S + ID_COAST_S
            if not done and len(self.identify_log) > 50 and self.loop % 10 == 0:
                early = measure_natural_frequency(self.identify_log)
                done = early is not None and early[4] >= ID_HALF_SWINGS
            if done:
                res = measure_natural_frequency(self.identify_log)
                if res is not None:
                    self.w0 = res[0]
                    I_id = sm.inertia_from_w0(self.w0)
                    self.ss, self.K, self.L = sm.design_lqg(I_id)
                    self.Ad, self.Bd, self.C = (np.asarray(m, dtype=float) for m in (self.ss.A, self.ss.B, self.ss.C))
                    self.identify_result = dict(t=t, w0=res[0], period=res[1], amp=res[2], decay=res[3], I=I_id, K=self.K.flatten().tolist())
                self.mode = SWING
        elif self.mode == SWING:
            e = 0.5 * (self.theta_dot / self.w0)**2 + np.cos(th1)
            pump = np.clip(SWING_ENERGY_GAIN * (self.energy_target - e), -1.0, 1.0)
            direction = np.sign(self.theta_dot * np.cos(th1))
            center = -SWING_CENTER_KP * (x_m - x_start) - SWING_CENTER_KV * self.xdiv_swing
            if SWING_CENTER_SHAPE:
                center *= 1.0 / (1.0 + (self.theta_dot * np.cos(th1) / self.w0)**2)
            acc = float(np.clip(SWING_ACCEL_MAX * pump * direction + center, -SWING_ACCEL_MAX, SWING_ACCEL_MAX))
            self.xdiv_swing = float(np.clip(self.xdiv_swing + acc * dt, -SWING_SPEED_MAX, SWING_SPEED_MAX))
            self.swing_accel, self.e = acc, e
            self.swing_peak = max(self.swing_peak, e)
            nd = 1 if self.theta_dot > 0.3 else -1 if self.theta_dot < -0.3 else self.swing_direction
            if self.swing_direction and nd != self.swing_direction:
                if abs(th1) < 0.6 and self.swing_peak >= self.energy_target - 0.02:
                    short = 1.0 - np.cos(th1)
                    self.energy_target = min(self.energy_target + min(0.6 * short, 0.05), SWING_TARGET_MAX)
                self.swing_peak = -1.0
            self.swing_direction = nd
            if (self.theta_prev_swing is not None and self.theta_prev_swing * th1 < 0
                    and abs(th1) < 0.5 and abs(self.theta_dot) >= CATCH_RATE_RAD_S):
                self.energy_target = max(self.energy_target - SWING_TARGET_STEP, SWING_TARGET_MIN)
            self.theta_prev_swing = th1
            if (abs(th1) < CATCH_ANGLE_RAD and abs(self.theta_dot) < CATCH_RATE_RAD_S
                    and CATCH_ENERGY_MIN <= e <= CATCH_ENERGY_MAX and abs(x_m - x_start) < CATCH_CART_MAX_M):
                self.mode = LQG
                self.catches.append((t, th1, self.theta_dot, e))
                self.catch_time = t
                self.loop = 250
                self.Ylast = np.array([[th1], [self.theta_dot], [x_m], [self.xdiv_swing]])
                Yfin = self.Ylast.copy()
                self.u = np.zeros((1, 1))
        elif self.mode == LQG:
            if abs(th1) > BALANCE_LOST_RAD or abs(x_m - x_start) > BALANCE_CART_LIMIT_M:
                self.mode = SWING
                self.losses.append((t, th1, x_m - x_start))
                self.xdiv_swing = float(np.clip(Yfin[3].item(), -SWING_SPEED_MAX, SWING_SPEED_MAX))
                self.swing_direction, self.theta_prev_swing, self.swing_peak = 0, None, -1.0
            elif t - self.catch_time > AUTO_TRIM_DELAY_S:
                trim = (AUTO_TRIM_KX * x_m + AUTO_TRIM_KV * Yfin[3].item()) * dt
                new = float(np.clip(self.upright_offset_deg + trim, -AUTO_TRIM_MAX_DEG, AUTO_TRIM_MAX_DEG))
                trim = new - self.upright_offset_deg
                self.upright_offset_deg = new
                self.Ylast[0, 0] -= np.deg2rad(trim)
                self.theta_prev = wrap(self.theta_prev - np.deg2rad(trim))

        if self.mode == LQG:
            self.u = -self.K @ Yfin * 2.0
            if self.loop < 200:
                self.u = self.u * (self.loop / 200.0)
            dv = LQG_ACCEL_MAX * dt
            xdiv = float(np.clip(Yfin[3].item(), -LQG_SPEED_MAX, LQG_SPEED_MAX))
            xdiv = float(np.clip(xdiv, self.xdiv_sent - dv, self.xdiv_sent + dv))
        else:
            self.u = np.zeros((1, 1))
            self.Ylast = np.array([[th1], [self.theta_dot], [x_m], [self.xdiv_swing]])
            Yfin = self.Ylast.copy()
            xdiv = self.xdiv_swing
        self.force = self.u.item()
        self.xdiv_sent = xdiv
        self.Yfin = Yfin
        return xdiv


def run(T=40.0, w0_true=7.2881, damping=0.20, angle_offset_deg=0.0, cmd_delay=0.002,
        pushes=(), seed=0):
    """pushes: list of (time_s, delta_theta_dot_rad_s) taps on the arm."""
    rng = np.random.default_rng(seed)
    plant = Plant(w0_true, damping, theta0=np.pi - 0.003 + 0.002 * rng.standard_normal())
    ctl = Controller(angle_offset_deg)
    Ts = sm.Ts
    x_meas = round(plant.x / M_PER_STEP) * M_PER_STEP
    x_start = x_meas
    pushes = sorted(pushes)
    log = {k: [] for k in ("t", "th", "thd", "x", "v", "th_m", "thd_est", "e", "mode", "vcmd",
                           "force", "target", "trim", "accel", "est_th", "est_thd", "est_x", "est_v")}
    n = int(T / Ts)
    for k in range(n):
        t = k * Ts
        while pushes and pushes[0][0] <= t:
            plant.push(pushes.pop(0)[1])
        th_m = ctl.measure(plant)
        try:
            vcmd = ctl.step(t, th_m, x_meas, x_start)
        except RuntimeError:
            break
        plant.advance(cmd_delay)
        v_real, _ = stepper_speed(vcmd)
        plant.set_speed(v_real)
        plant.advance(0.003 - cmd_delay)
        x_meas = round(plant.x / M_PER_STEP) * M_PER_STEP     # positionRead after the command
        plant.advance(Ts - 0.003)
        for key, val in (("t", t), ("th", wrap(plant.th)), ("thd", plant.thd), ("x", plant.x), ("v", plant.v),
                         ("th_m", th_m), ("thd_est", ctl.theta_dot), ("e", ctl.e), ("mode", ctl.mode),
                         ("vcmd", vcmd), ("force", ctl.force), ("target", ctl.energy_target),
                         ("trim", ctl.upright_offset_deg), ("accel", ctl.swing_accel),
                         ("est_th", ctl.Yfin[0, 0]), ("est_thd", ctl.Yfin[1, 0]),
                         ("est_x", ctl.Yfin[2, 0]), ("est_v", ctl.Yfin[3, 0])):
            log[key].append(val)
    out = {k: np.array(v) for k, v in log.items()}
    out["identify"] = ctl.identify_result
    out["catches"] = ctl.catches
    out["losses"] = ctl.losses
    return out


if __name__ == "__main__":
    r = run(T=40.0, angle_offset_deg=1.0, pushes=[(20.0, 1.2), (30.0, -2.5)])
    print("identify:", {k: (round(v, 5) if isinstance(v, float) else v) for k, v in r["identify"].items()})
    print("catches:", [(round(a, 2), round(np.rad2deg(b), 1), round(c, 2), round(d, 3)) for a, b, c, d in r["catches"]])
    print("losses:", [(round(a, 2), round(np.rad2deg(b), 1), round(c, 3)) for a, b, c in r["losses"]])
    lqg = r["mode"] == LQG
    print("ran %.1f s; LQG %.1f s; final trim %.3f deg; theta std in LQG %.3f deg; cart std %.4f m"
          % (r["t"][-1], lqg.sum() * sm.Ts, r["trim"][-1], np.rad2deg(np.std(r["th"][lqg])), np.std(r["x"][lqg])))
    np.savez("sim_run.npz", **{k: v for k, v in r.items() if isinstance(v, np.ndarray)})
