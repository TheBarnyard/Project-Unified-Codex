"""n-link pendulum on a cart (n = 1, 2, 3, ...): model, linearisation, LQR, Kalman, trajectory
optimisation, time-varying LQR and a stepper-in-the-loop simulator. Used by Math/Double and Math/Triple.

Conventions (same as the team's double-pendulum code, PythonMasterMath2.py / PythonMaster2_swingup.py):
  * absolute angles theta_i from upright, positive = centre of mass toward +x
    (note: the single-pendulum script uses the opposite sign),
  * state z = [theta_1, w_1, ..., theta_n, w_n, x, v],
  * link i: mass m_i, pivot-to-CoM c_i, pivot-to-next-joint L_i, inertia I_i about its own CoM,
  * joint friction b_i is viscous on the RELATIVE rate (w_i - w_{i-1}), w_0 = 0 (the cart).

Two input choices:
  * force F on the cart (classic textbook model, used by PythonMasterMath2.py),
  * cart acceleration a (what a speed-controlled stepper really imposes).

General formulas (derived in Math/Double/02_equations_of_motion.md):
  p_j  = m_j c_j + L_j * sum_{k>j} m_k                 (first moment seen at joint j)
  h_ii = I_i + m_i c_i^2 + L_i^2 * sum_{k>i} m_k        (inertia of link i about its pivot, plus the links it carries)
  h_ij = L_i p_j  for i < j,  h_ji = h_ij
  sum_j h_ij cos(th_i - th_j) dw_j = g p_i sin th_i - p_i cos th_i * a - sum_j h_ij sin(th_i - th_j) w_j^2 + tau_i
"""
from dataclasses import dataclass, field

import numpy as np
from scipy.linalg import expm, solve_discrete_are

G = 9.81


@dataclass
class Link:
    m: float      # kg
    c: float      # m, pivot to CoM
    L: float      # m, pivot to next joint (also the drawn length of the last link)
    I: float      # kg m^2 about the link's own CoM
    b: float = 0.0  # N m s/rad, viscous friction at this link's pivot (relative rate)


@dataclass
class Rig:
    links: list
    M: float = 0.910          # cart kg (only used by the force-input model)
    b_cart: float = 0.0       # N s/m (force-input model only)
    names: list = field(default_factory=list)
    H_given: np.ndarray = None  # set by from_ratios: dynamics given directly as H/J1 and p/J1
    p_given: np.ndarray = None

    @classmethod
    def from_ratios(cls, P, Hn, B, names=None):
        """Rig in the team's ratio form (everything divided by J1): P = p/J1, Hn = H/J1, B = b/J1.
        Double: P = [P1, P2], Hn = [[1, H], [H, J2r]], B = [B1, B2]. Only the acceleration-input
        model can be used (the force model needs real masses)."""
        links = [Link(0.0, 0.0, 0.0, 0.0, float(b)) for b in B]
        return cls(links, names=names or [], H_given=np.array(Hn, float), p_given=np.array(P, float))

    @classmethod
    def from_team_ratios(cls, r):
        """From a dict like SYSID_RATIOS in PythonMaster2_swingup.py."""
        return cls.from_ratios([r["P1"], r["P2"]], [[1.0, r["H"]], [r["H"], r["J2r"]]],
                               [r.get("B1", 0.0), r.get("B2", 0.0)])

    @property
    def n(self):
        return len(self.links)

    def p(self):
        if self.p_given is not None:
            return self.p_given.copy()
        m = [lk.m for lk in self.links]
        return np.array([lk.m * lk.c + lk.L * sum(m[j + 1:]) for j, lk in enumerate(self.links)])

    def h(self):
        if self.H_given is not None:
            return self.H_given.copy()
        n, lk = self.n, self.links
        m = [l.m for l in lk]
        p = self.p()
        H = np.zeros((n, n))
        for i in range(n):
            H[i, i] = lk[i].I + lk[i].m * lk[i].c**2 + lk[i].L**2 * sum(m[i + 1:])
            for j in range(i + 1, n):
                H[i, j] = H[j, i] = lk[i].L * p[j]
        return H

    def ratios(self):
        """Team-style ratios, everything divided by J1 = h_11 (double: P1, P2, J2r, H)."""
        H, p = self.h(), self.p()
        J1 = H[0, 0]
        return {"J1": J1, "P": p / J1, "Hn": H / J1, "B": np.array([lk.b for lk in self.links]) / J1}


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


# ------------------------------------------------------------------ dynamics (acceleration input)
def _friction(rig, w, np_=np):
    n = rig.n
    tau = [0.0] * n
    for i in range(n):
        rel = w[i] - (w[i - 1] if i > 0 else 0.0)
        tau[i] = tau[i] - rig.links[i].b * rel
        if i > 0:
            tau[i - 1] = tau[i - 1] + rig.links[i].b * rel
    return tau


def accel_dynamics(rig, z, a):
    """dz/dt for state z and cart acceleration a (numpy)."""
    n = rig.n
    th, w = z[0:2 * n:2], z[1:2 * n:2]
    H, p = rig.h(), rig.p()
    D = th[:, None] - th[None, :]
    Mq = H * np.cos(D)
    S = H * np.sin(D)
    rhs = G * p * np.sin(th) - p * np.cos(th) * a - S @ (w**2) + np.array(_friction(rig, w))
    dw = np.linalg.solve(Mq, rhs)
    out = np.empty_like(z)
    out[0:2 * n:2], out[1:2 * n:2] = w, dw
    out[2 * n], out[2 * n + 1] = z[2 * n + 1], a
    return out


def speed_jump(rig, z, dv):
    """A stepper changes speed at once: integrate the arm equations over an impulse in a."""
    n = rig.n
    th = z[0:2 * n:2]
    H, p = rig.h(), rig.p()
    Mq = H * np.cos(th[:, None] - th[None, :])
    z = z.copy()
    z[1:2 * n:2] += np.linalg.solve(Mq, -p * np.cos(th) * dv)
    z[2 * n + 1] += dv
    return z


def casadi_dynamics(rig):
    """Same dynamics as a CasADi function f(z, a)."""
    import casadi as ca
    n = rig.n
    z = ca.SX.sym("z", 2 * n + 2)
    a = ca.SX.sym("a")
    H, p = rig.h(), rig.p()
    th = [z[2 * i] for i in range(n)]
    w = [z[2 * i + 1] for i in range(n)]
    Mq = ca.SX(n, n)
    rhs = ca.SX(n, 1)
    tau = _friction(rig, w)
    for i in range(n):
        acc = G * p[i] * ca.sin(th[i]) - p[i] * ca.cos(th[i]) * a + tau[i]
        for j in range(n):
            Mq[i, j] = H[i, j] * ca.cos(th[i] - th[j])
            acc -= H[i, j] * ca.sin(th[i] - th[j]) * w[j]**2
        rhs[i] = acc
    dw = ca.solve(Mq, rhs)
    dz = []
    for i in range(n):
        dz += [w[i], dw[i]]
    dz += [z[2 * n + 1], a]
    return ca.Function("f", [z, a], [ca.vertcat(*dz)])


def rk4(f, z, a, dt):
    k1 = f(z, a)
    k2 = f(z + dt / 2 * k1, a)
    k3 = f(z + dt / 2 * k2, a)
    k4 = f(z + dt * k3, a)
    return z + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


# ------------------------------------------------------------------ linear models
def friction_matrix(rig):
    """Bf with tau = -Bf @ w: joint i resists the RELATIVE rate (w_i - w_{i-1}), and the reaction acts on link i-1."""
    n = rig.n
    Bf = np.zeros((n, n))
    for i in range(n):
        b = rig.links[i].b
        Bf[i, i] += b
        if i > 0:
            Bf[i, i - 1] -= b
            Bf[i - 1, i] -= b
            Bf[i - 1, i - 1] += b
    return Bf


def linear_accel(rig):
    """Continuous A, B at upright for cart-acceleration input (closed form):
    H dw = g diag(p) theta - p a - Bf w  =>  dw = g H^-1 diag(p) theta - H^-1 Bf w - H^-1 p a."""
    n = rig.n
    H, p = rig.h(), rig.p()
    Hi = np.linalg.inv(H)
    Ath = G * Hi @ np.diag(p)
    Aw = -Hi @ friction_matrix(rig)
    Bth = -Hi @ p
    A = np.zeros((2 * n + 2, 2 * n + 2))
    B = np.zeros((2 * n + 2, 1))
    for i in range(n):
        A[2 * i, 2 * i + 1] = 1.0
        for j in range(n):
            A[2 * i + 1, 2 * j] = Ath[i, j]
            A[2 * i + 1, 2 * j + 1] = Aw[i, j]
        B[2 * i + 1, 0] = Bth[i]
    A[2 * n, 2 * n + 1] = 1.0
    B[2 * n + 1, 0] = 1.0
    return A, B


def linear_force(rig):
    """Continuous A, B at upright for force input (the textbook model, frictionless joints)."""
    n = rig.n
    H, p = rig.h(), rig.p()
    mtot = rig.M + sum(lk.m for lk in rig.links)
    Mfull = np.zeros((n + 1, n + 1))
    Mfull[:n, :n] = H
    Mfull[:n, n] = Mfull[n, :n] = p
    Mfull[n, n] = mtot
    Mi = np.linalg.inv(Mfull)
    K = np.zeros((n + 1, n + 1))       # generalized "stiffness" at upright: +g p_i on theta rows
    K[:n, :n] = np.diag(G * p)
    A = np.zeros((2 * n + 2, 2 * n + 2))
    B = np.zeros((2 * n + 2, 1))
    acc_q = Mi @ K                     # d2q/dt2 = Mi (K q + [0..0, F - b v])
    acc_v = -Mi[:, n] * rig.b_cart
    acc_F = Mi[:, n]
    for r in range(n + 1):
        A[2 * r, 2 * r + 1] = 1.0
        for c in range(n + 1):
            A[2 * r + 1, 2 * c] = acc_q[r, c]
        A[2 * r + 1, 2 * n + 1] += acc_v[r]
        B[2 * r + 1, 0] = acc_F[r]
    return A, B


def c2d(A, B, Ts):
    n = A.shape[0]
    Mx = expm(np.block([[A, B], [np.zeros((1, n + 1))]]) * Ts)
    return Mx[:n, :n], Mx[:n, n:]


def dlqr(Ad, Bd, Q, R):
    P = solve_discrete_are(Ad, Bd, Q, R)
    K = np.linalg.solve(R + Bd.T @ P @ Bd, Bd.T @ P @ Ad)
    return K, P


def dlqe(Ad, C, QN, RN):
    """Predictor gain as python-control's dlqe returns it (G = I)."""
    P = solve_discrete_are(Ad.T, C.T, QN, RN)
    return Ad @ P @ C.T @ np.linalg.inv(C @ P @ C.T + RN), P


# ------------------------------------------------------------------ swing-up planning (CasADi + IPOPT)
def plan_swingup(rig, T, N, x_max, v_max, a_max, guess=None, seed=0, start=None, effort_weight=1.0,
                 end_tol=0.0, print_level=0, max_iter=3000):
    """Direct multiple shooting: N intervals, piecewise-constant acceleration, RK4 with 2 substeps.
    Minimises the integral of a^2 (cart effort) plus a small smoothness term.
    Start: all links hanging (theta = pi), cart at rest at 0. End: all upright, at rest, cart at 0."""
    import casadi as ca
    n = rig.n
    nz = 2 * n + 2
    f = casadi_dynamics(rig)
    dt = T / N
    opti = ca.Opti()
    Z = opti.variable(nz, N + 1)
    A = opti.variable(1, N)
    z0 = np.zeros(nz)
    z0[0:2 * n:2] = np.pi if start is None else start
    opti.subject_to(Z[:, 0] == z0)
    for k in range(N):
        zk = Z[:, k]
        h = dt / 2
        for _ in range(2):
            zk = rk4(f, zk, A[0, k], h)
        opti.subject_to(Z[:, k + 1] == zk)
    zf = np.zeros(nz)
    if end_tol > 0:
        opti.subject_to(opti.bounded(-end_tol, Z[:, N] - zf, end_tol))
    else:
        opti.subject_to(Z[:, N] == zf)
    opti.subject_to(opti.bounded(-x_max, Z[2 * n, :], x_max))
    opti.subject_to(opti.bounded(-v_max, Z[2 * n + 1, :], v_max))
    opti.subject_to(opti.bounded(-a_max, A, a_max))
    effort = ca.sumsqr(A) * dt
    smooth = ca.sumsqr(A[0, 1:] - A[0, :-1]) * dt * 1e-3
    opti.minimize(effort_weight * effort + smooth)
    rng = np.random.default_rng(seed)
    if guess is not None:
        opti.set_initial(Z, guess[0])
        opti.set_initial(A, guess[1])
    else:
        tt = np.linspace(0, 1, N + 1)
        Zg = np.zeros((nz, N + 1))
        for i in range(n):
            Zg[2 * i, :] = z0[2 * i] * (1 - tt) + 0.3 * rng.standard_normal() * np.sin(np.pi * tt)
        opti.set_initial(Z, Zg)
        opti.set_initial(A, a_max * 0.3 * np.sin(2 * np.pi * (2 + n) * np.linspace(0, 1, N)) * rng.choice([-1, 1]))
    opti.solver("ipopt", {"print_time": 0, "expand": True},
                {"print_level": print_level, "max_iter": max_iter, "tol": 1e-8, "sb": "yes"})
    try:
        sol = opti.solve()
        ok = True
    except RuntimeError:
        sol = opti.debug
        ok = False
    Zs = np.array(sol.value(Z))
    As = np.array(sol.value(A)).reshape(-1)
    return {"ok": ok, "t": np.linspace(0, T, N + 1), "Z": Zs, "A": As, "dt": dt,
            "effort": float(np.sum(As**2) * dt), "T": T, "N": N,
            "limits": dict(x_max=x_max, v_max=v_max, a_max=a_max)}


def resample_plan(plan, Ts):
    """Plan on the controller's grid (Ts): acceleration held per plan interval, states by integration."""
    n_out = int(round(plan["T"] / Ts))
    t = np.arange(n_out + 1) * Ts
    idx = np.minimum((t[:-1] / plan["dt"]).astype(int), len(plan["A"]) - 1)
    a = plan["A"][idx]
    return t, a


def jacobians(rig, z, a, eps=1e-6):
    n = len(z)
    f0 = accel_dynamics(rig, z, a)
    A = np.zeros((n, n))
    for i in range(n):
        dz = np.zeros(n); dz[i] = eps
        A[:, i] = (accel_dynamics(rig, z + dz, a) - accel_dynamics(rig, z - dz, a)) / (2 * eps)
    B = ((accel_dynamics(rig, z, a + eps) - accel_dynamics(rig, z, a - eps)) / (2 * eps)).reshape(-1, 1)
    return A, B


def tvlqr(rig, Zref, Aref, Ts, Q, R, P_end):
    """Backward Riccati recursion along the reference: K_k for k = 0..N-1."""
    N = len(Aref)
    P = P_end.copy()
    Ks = [None] * N
    for k in range(N - 1, -1, -1):
        Ac, Bc = jacobians(rig, Zref[:, k], Aref[k])
        Ad, Bd = c2d(Ac, Bc, Ts)
        K = np.linalg.solve(R + Bd.T @ P @ Bd, Bd.T @ P @ Ad)
        P = Q + Ad.T @ P @ (Ad - Bd @ K)
        P = 0.5 * (P + P.T)
        Ks[k] = K
    return Ks


# ------------------------------------------------------------------ stepper-in-the-loop simulation
M_PER_STEP = 0.638175 / 6400


def stepper_speed(v):
    f = -(v * 6400) / 0.638175
    if abs(f) > 2:
        N = int(125000.0 / f)
    else:
        N = 65535 if f >= 0 else -65535
    N = N if N != 0 else 1
    return (-1 if N > 0 else 1) * 125000.0 / (abs(N) + 1) * M_PER_STEP


def simulate(rig_true, controller, z0, T, Ts=0.01, cmd_delay=0.002, quant=True, h=0.0005,
             disturb=None):
    """controller(k, t, z_meas) -> commanded cart speed. The plant is rig_true; the cart is a speed
    source that jumps to the (quantised) commanded speed cmd_delay after each sample."""
    n = rig_true.n
    z = z0.astype(float).copy()
    q = 2 * np.pi / 16384
    out_t, out_z, out_v = [], [], []
    steps = int(round(T / Ts))

    def coast(z, dt):
        m = max(1, int(round(dt / h)))
        for _ in range(m):
            z = rk4(lambda zz, aa: accel_dynamics(rig_true, zz, aa), z, 0.0, dt / m)
        return z

    for k in range(steps):
        t = k * Ts
        if disturb is not None:
            z = disturb(t, z)
        zm = z.copy()
        if quant:
            zm[0:2 * n:2] = np.round(wrap(zm[0:2 * n:2]) / q) * q
            zm[2 * n] = np.round(zm[2 * n] / M_PER_STEP) * M_PER_STEP
        v_cmd = controller(k, t, zm)
        if v_cmd is None:
            break
        z = coast(z, cmd_delay)
        v_real = stepper_speed(v_cmd) if quant else v_cmd
        z = speed_jump(rig_true, z, v_real - z[2 * n + 1])
        z = coast(z, Ts - cmd_delay)
        out_t.append(t + Ts); out_z.append(z.copy()); out_v.append(v_cmd)
    return np.array(out_t), np.array(out_z), np.array(out_v)


# ------------------------------------------------------------------ the team's stepper-model controllers, for n links
# PythonMaster2_swingup.py (double swing-up) and PythonMasterDouble-Claude.py (= PythonMaster2_auto_improved.py,
# double balance) written for any number of links. For n = 2 these reproduce the scripts' gains exactly
# (checked by Math/Double/sims/verify_against_team_code.py).
def coast(rig, z, dt, sub=2):
    """Cart at constant speed for dt (a = 0), as the scripts' internal model does it (2 RK4 substeps)."""
    f = lambda zz, aa: accel_dynamics(rig, zz, aa)
    for _ in range(sub):
        if dt > 0:
            z = rk4(f, z, 0.0, dt / sub)
    return z


def stair_step(rig, z, a_prev, a, T=0.01, tau=0.008):
    """One control period of the swing-up script's actuator model ("staircase" speed): the speed
    change a*T decided at this sample lands at once, tau after the sample (PythonMaster2_swingup.step)."""
    if tau < T:
        z = coast(rig, z, tau)
        z = speed_jump(rig, z, a * T)
        return coast(rig, z, T - tau)
    t1 = tau - T
    z = coast(rig, z, t1)
    z = speed_jump(rig, z, a_prev * T)
    return coast(rig, z, T - t1)


def linearize_stair(rig, z, a_prev, a, T=0.01, tau=0.008, eps=1e-6):
    """Discrete A, B of stair_step on the augmented state [z, a_prev] (size 2n+3)."""
    nz = len(z)
    base = np.concatenate([z, [a_prev]])
    A = np.zeros((nz + 1, nz + 1))
    for i in range(nz + 1):
        d = np.zeros(nz + 1); d[i] = eps
        zp = stair_step(rig, (base + d)[:nz], (base + d)[nz], a, T, tau)
        zm = stair_step(rig, (base - d)[:nz], (base - d)[nz], a, T, tau)
        A[:nz, i] = (zp - zm) / (2 * eps)
    B = np.zeros((nz + 1, 1))
    B[:nz, 0] = (stair_step(rig, z, a_prev, a + eps, T, tau) - stair_step(rig, z, a_prev, a - eps, T, tau)) / (2 * eps)
    B[nz, 0] = 1.0
    return A, B


def delay_discretize(A, B, T, tau):
    """Exact ZOH of a held input that takes effect tau after the sample (PythonMasterDouble-Claude.py):
    z[k+1] = Phi z[k] + G0 u[k] + G1 u[k-1]."""
    n = A.shape[0]

    def zoh(t):
        E = expm(np.block([[A, B], [np.zeros((1, n + 1))]]) * t)
        return E[:n, :n], E[:n, n:]
    tau = min(max(tau, 0.0), T)
    Phi, _ = zoh(T)
    E1, G0 = zoh(T - tau)
    _, Gt = zoh(tau)
    return Phi, G0, E1 @ Gt


def bryson_Q(n, angle_deg, rate_deg_s, cart_m, cart_speed_m_s):
    """Q = diag(1/size^2) for [th_1, w_1, ..., th_n, w_n, x, v, a_prev]. angle_deg may be a list per link."""
    ang = angle_deg if np.iterable(angle_deg) else [angle_deg] * n
    q = []
    for i in range(n):
        q += [1 / np.radians(ang[i])**2, 1 / np.radians(rate_deg_s)**2]
    q += [1 / cart_m**2, 1 / cart_speed_m_s**2, 0.0]
    return np.diag(q)


def kalman_physical(Phi, n, T=0.01, arm_disturbance=1.0, encoder_noise_counts=3.0, m_per_step=0.638175 / 6400):
    """The balance scripts' steady-state Kalman FILTER gain (filter form, unlike python-control's dlqe),
    with noise sizes from physical reasoning: arm accelerations off by arm_disturbance rad/s^2, encoder noise
    in counts, cart position to a quarter step."""
    C = np.zeros((n + 1, 2 * n + 2))
    for i in range(n):
        C[i, 2 * i] = 1.0
    C[n, 2 * n] = 1.0
    w = arm_disturbance * T
    qn = []
    for _ in range(n):
        qn += [(w * T / 2)**2, w**2]
    qn += [(m_per_step / 4)**2, (m_per_step / T / 4)**2]
    sa = encoder_noise_counts * 2 * np.pi / 16384
    # the second (and further) angles are arm1 + joint: noisier by about sqrt(2) (the scripts use 1.4)
    rn = [sa**2] + [(sa * 1.4)**2] * (n - 1) + [(m_per_step / np.sqrt(12))**2]
    Qn, Rn = np.diag(qn), np.diag(rn)
    Pk = solve_discrete_are(Phi.T, C.T, Qn, Rn)
    return Pk @ C.T @ np.linalg.inv(C @ Pk @ C.T + Rn), C


def balance_design_ramp(rig, Q, R, T=0.01, tau=0.009, **kal):
    """PythonMasterDouble-Claude.py: acceleration held over the period, landing tau late; LQR on [z, a_prev]."""
    n = rig.n
    A, B = linear_accel(rig)
    Phi, G0, G1 = delay_discretize(A, B, T, tau)
    nz = 2 * n + 2
    Az = np.block([[Phi, G1], [np.zeros((1, nz)), np.zeros((1, 1))]])
    Bz = np.vstack([G0, [[1.0]]])
    K, P = dlqr(Az, Bz, Q, R)
    L, C = kalman_physical(Phi, n, T, **kal)
    return {"A": A, "B": B, "Phi": Phi, "G0": G0, "G1": G1, "Az": Az, "Bz": Bz, "K": K, "P": P, "L": L, "C": C,
            "cl_eig": np.linalg.eigvals(Az - Bz @ K)}


def balance_closed_loop_radius(design, rig_true, tau_true=0.009, T=0.01):
    """Largest |eigenvalue| of the LINEAR closed loop: the real arms (rig_true, motor delay tau_true of any
    length, also longer than T) with a ramp-model balance controller (balance_design_ramp: Kalman predictor
    + K on [z, a_prev]) designed for another model. Below 1 = the balance holds. Used for the delay and
    model-error tolerance tables of Math/Double and Math/Triple."""
    A, B = linear_accel(rig_true)
    nz = A.shape[0]
    m = int(np.floor(tau_true / T + 1e-12))       # whole periods of delay
    r = tau_true - m * T
    Phi, G0, G1 = delay_discretize(A, B, T, r)   # z+ = Phi z + G0 u[k-m] + G1 u[k-m-1]
    nh = m + 1                                   # stored commands u[k-1] ... u[k-m-1]
    K, L, C = design["K"], design["L"], design["C"]
    Kz, Ka = K[:, :nz], K[:, nz:]
    I = np.eye(nz)
    N = nz + nh + nz                             # [true z, command history, controller's prediction]
    urow = np.zeros((1, N))                      # u[k] = -Kz x_hat - Ka u[k-1], x_hat = (I-LC) x_pred + LC z
    urow[:, :nz] = -Kz @ L @ C
    urow[:, nz] = -Ka[:, 0]
    urow[:, nz + nh:] = -Kz @ (I - L @ C)
    M = np.zeros((N, N))
    if m == 0:
        M[:nz] = np.hstack([Phi, np.zeros((nz, nh + nz))]) + G0 @ urow
        M[:nz, nz] += G1[:, 0]
    else:
        M[:nz, :nz] = Phi
        M[:nz, nz + m - 1] += G0[:, 0]
        M[:nz, nz + m] += G1[:, 0]
    M[nz] = urow
    for i in range(1, nh):
        M[nz + i, nz + i - 1] = 1.0
    xh_row = np.hstack([L @ C, np.zeros((nz, nh)), I - L @ C])
    M[nz + nh:] = design["Phi"] @ xh_row + design["G0"] @ urow
    M[nz + nh:, nz] += design["G1"][:, 0]
    return float(np.abs(np.linalg.eigvals(M)).max())


def balance_design_stair(rig, Q, R, T=0.01, tau=0.009, **kal):
    """PythonMaster2_swingup.balance_design: same weights, staircase actuator model."""
    n = rig.n
    nz = 2 * n + 2
    Az, Bz = linearize_stair(rig, np.zeros(nz), 0.0, 0.0, T, tau)
    K, P = dlqr(Az, Bz, Q, R)
    L, C = kalman_physical(Az[:nz, :nz], n, T, **kal)
    return {"Az": Az, "Bz": Bz, "K": K, "P": P, "L": L, "C": C, "cl_eig": np.linalg.eigvals(Az - Bz @ K)}


def swing_observer_gain(n, T=0.01, disturbance=3.0, encoder_noise_counts=3.0, cart_gain=0.9):
    """PythonMaster2_swingup.swing_observer_gain: per arm, a Kalman filter on angle'' = disturbance,
    used to correct the nonlinear prediction during the swing."""
    F = np.array([[1, T], [0, 1]])
    s = disturbance
    Qn = s * s * np.array([[T**4 / 4, T**3 / 2], [T**3 / 2, T * T]])
    Rn = np.array([[(encoder_noise_counts * 2 * np.pi / 16384)**2]])
    Hm = np.array([[1.0, 0.0]])
    P = solve_discrete_are(F.T, Hm.T, Qn, Rn)
    g = (P @ Hm.T @ np.linalg.inv(Hm @ P @ Hm.T + Rn))[:, 0]
    L = np.zeros((2 * n + 2, n + 1))
    for i in range(n):
        L[2 * i, i], L[2 * i + 1, i] = g
    L[2 * n, n] = cart_gain
    return L


def stair_reference(Zplan, Ts=0.01, tau=0.008):
    """PythonMaster2_swingup.load_trajectory: the speed change to decide at sample k so that the staircase
    speed (landing tau later) follows the planned speed: a_k = (v(kT+tau+T/2) - v(kT+tau-T/2)) / T."""
    nzp = Zplan.shape[0]
    vz = Zplan[nzp - 1]
    N = Zplan.shape[1] - 1
    tg = np.arange(N + 1) * Ts
    return np.array([(np.interp(k * Ts + tau + Ts / 2, tg, vz) - np.interp(k * Ts + tau - Ts / 2, tg, vz)) / Ts
                     for k in range(N)])


def tvlqr_stair(rig, Zref, Aref, Q, R, P_end, T=0.01, tau=0.008):
    """PythonMaster2_swingup.tvlqr: backward Riccati along the plan on the staircase model, ending in the
    balance controller's cost-to-go P_end."""
    N = len(Aref)
    P = P_end.copy()
    Ks = [None] * N
    for k in range(N - 1, -1, -1):
        a_prev = Aref[k - 1] if k > 0 else 0.0
        A, B = linearize_stair(rig, Zref[:, k], a_prev, Aref[k], T, tau)
        K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
        P = Q + A.T @ P @ (A - B @ K)
        P = 0.5 * (P + P.T)
        Ks[k] = K
    return Ks


def timer_speed(v, step_hz_clock=125000.0, m_per_step=0.638175 / 6400):
    """Speed the Arduino really runs for a requested speed, as the swing-up script rounds it:
    timer = round(125000/|f|) - 1, real rate 125000/(timer+1). Returns 0 below 2 steps per period."""
    if abs(v) < 2.0 * m_per_step:
        return 0.0
    f = abs(v) / m_per_step
    icr = max(1, min(65535, int(round(step_hz_clock / f)) - 1))
    return np.sign(v) * step_hz_clock / (icr + 1) * m_per_step


# ------------------------------------------------------------------ swing-up planning, the team's formulation
def rk4_lin(f, z, a0, a1, dt):
    """RK4 with the input changing linearly from a0 to a1 over the step (PythonMaster2_swingup.rk4)."""
    am = 0.5 * (a0 + a1)
    k1 = f(z, a0)
    k2 = f(z + dt / 2 * k1, am)
    k3 = f(z + dt / 2 * k2, am)
    k4 = f(z + dt * k3, a1)
    return z + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def plan_team(rig, T=2.5, X=0.25, V=0.75, A=8.0, Vtop=1.0, knot_dt=0.05, dt=0.01, guess=None, start=None,
              print_level=0, max_iter=3000, seed=None, x_every=1):
    """The --plan problem of PythonMaster2_swingup.py, solved with CasADi + IPOPT instead of SciPy SLSQP:
      unknowns  : cart acceleration at knots every knot_dt (linear in between), states every dt;
      dynamics  : z[k+1] = RK4(z[k], a[k], a[k+1]) on the nonlinear model (every 10 ms step a constraint);
      start/end : all links hanging and still -> all upright and still, cart at 0 and at rest;
      limits    : |x| <= X, |v| <= V, |a_knot| <= A, and the motor torque limit
                  a*sign(v) <= A*(1 - |v|/Vtop) (accelerating further only with the torque left);
      cost      : sum of a^2 dt (gentlest cart motion)."""
    import casadi as ca
    n = rig.n
    nz = 2 * n + 2
    f = casadi_dynamics(rig)
    N = int(round(T / dt))
    M = int(round(T / knot_dt))
    W = np.zeros((N + 1, M + 1))
    for i in range(N + 1):
        t = i * dt
        j = min(int(t / knot_dt + 1e-9), M - 1)
        s = t / knot_dt - j
        W[i, j] += 1 - s
        W[i, j + 1] += s
    opti = ca.Opti()
    Z = opti.variable(nz, N + 1)
    U = opti.variable(1, M + 1)
    a = ca.mtimes(U, W.T)                     # 1 x (N+1)
    z0 = np.zeros(nz)
    z0[0:2 * n:2] = np.pi if start is None else start
    opti.subject_to(Z[:, 0] == z0)
    for k in range(N):
        opti.subject_to(Z[:, k + 1] == rk4_lin(f, Z[:, k], a[k], a[k + 1], dt))
    opti.subject_to(Z[:, N] == np.zeros(nz))
    xs = Z[2 * n, ::x_every]
    vs = Z[2 * n + 1, :]
    opti.subject_to(opti.bounded(-X, xs, X))
    opti.subject_to(opti.bounded(-V, vs, V))
    opti.subject_to(opti.bounded(-A, U, A))
    av = ca.sqrt(vs * vs + 1e-4)
    opti.subject_to(A * (1 - av / Vtop) - a * vs / av >= 0)
    opti.minimize(ca.sumsqr(a) * dt)
    if guess is not None:
        opti.set_initial(Z, guess[0])
        opti.set_initial(U, guess[1])
    else:
        tt = np.linspace(0, 1, N + 1)
        Zg = np.zeros((nz, N + 1))
        for i in range(n):
            Zg[2 * i] = z0[2 * i] * (1 - tt)
            Zg[2 * i + 1] = -z0[2 * i] / T
        opti.set_initial(Z, Zg)
        if seed is not None:
            opti.set_initial(U, np.random.default_rng(seed).normal(0, 3, M + 1))
    opti.solver("ipopt", {"print_time": 0, "expand": True},
                {"print_level": print_level, "max_iter": max_iter, "tol": 1e-8, "acceptable_tol": 1e-6,
                 "sb": "yes"})
    try:
        sol = opti.solve()
        ok = True
    except RuntimeError:
        sol = opti.debug
        ok = False
    Zs = np.array(sol.value(Z))
    Us = np.array(sol.value(U)).reshape(-1)
    As = Us @ W.T
    st = sol.stats()
    return {"ok": ok, "status": st.get("return_status"), "t": np.arange(N + 1) * dt, "Z": Zs, "a": As, "knots": Us,
            "dt": dt, "T": N * dt, "N": N, "effort": float(np.sum(As**2) * dt),
            "limits": dict(X=X, V=V, A=A, Vtop=Vtop),
            "peak": dict(x=float(np.abs(Zs[2 * n]).max()), v=float(np.abs(Zs[2 * n + 1]).max()),
                         a=float(np.abs(As).max()))}


def plan_team_homotopy(rig, T, X, V, A, Vtop=1.0, start_limits=(0.6, 2.0, 30.0, 3.0), min_step=1 / 64,
                       log=print, guess=None, **kw):
    """From scratch: solve with loose limits first, then tighten them toward (X, V, A, Vtop), each solve
    starting from the last plan that worked; a failed step is halved (the same continuation idea --plan
    uses to walk the stored plan over to new arm values). Returns the last plan; plan["lam"] says how far
    toward the requested limits it got (1.0 = all the way)."""
    X0, V0, A0, Vt0 = start_limits

    def lim(s):
        return (X0 + s * (X - X0), V0 + s * (V - V0), A0 + s * (A - A0), Vt0 + s * (Vtop - Vt0))
    plan = plan_team(rig, T, *lim(0.0), guess=guess, **kw)
    log(f"  limits x {X0:.2f} m, v {V0:.2f} m/s, a {A0:.1f} m/s^2, top {Vt0:.2f} m/s: {plan['status']} "
        f"effort {plan['effort']:.1f}")
    if not plan["ok"]:
        plan["lam"] = -1.0
        return plan
    lam, step, best = 0.0, 0.25, plan
    while lam < 1 - 1e-9 and step >= min_step:
        nxt = min(1.0, lam + step)
        p = plan_team(rig, T, *lim(nxt), guess=(best["Z"], best["knots"]), **kw)
        L = lim(nxt)
        log(f"  limits x {L[0]:.3f} m, v {L[1]:.3f} m/s, a {L[2]:.2f} m/s^2, top {L[3]:.2f} m/s: {p['status']} "
            f"effort {p['effort']:.1f}")
        if p["ok"]:
            lam, best = nxt, p
            step = min(step * 1.5, 0.5)
        else:
            step /= 2
    best["lam"] = lam
    best["limits_reached"] = dict(zip(("X", "V", "A", "Vtop"), lim(lam)))
    return best
