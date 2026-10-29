---
updated: 2026-10-29
updated_by: Ryan (Claude, math-folder session)
---
# 2. Equations of motion

[Back to Double](README.md) · Prev: [1. Variables](01_variables.md) · Next: [3. Linear model](03_linear_model.md)

Where in the code: the Lagrangian is typed out in `PythonMasterMath2.py` (lines `T = (...)`, `U = ...`, `EL_x`, `EL_theta`, `EL_theta2`) and solved by SymPy; the swing-up script has the solved form by hand in `f(z, a, r)`; the balance script uses only its linear part (`continuous_model`). All three are the same equations, as shown below.

## 2.1 Where everything is

Using the [coordinates](01_variables.md) (angles from upright, + toward +x, cart at $`(x, 0)`$, pivot height 0):

```math
\begin{aligned}
\text{CoM of arm 1:}\quad & \mathbf r_1 = \big(x + c_1\sin\theta_1,\ \ c_1\cos\theta_1\big)\\
\text{joint:}\quad & \mathbf r_J = \big(x + L_1\sin\theta_1,\ \ L_1\cos\theta_1\big)\\
\text{CoM of arm 2:}\quad & \mathbf r_2 = \big(x + L_1\sin\theta_1 + c_2\sin\theta_2,\ \ L_1\cos\theta_1 + c_2\cos\theta_2\big)
\end{aligned}
```

Differentiate in time:

```math
\begin{aligned}
\dot{\mathbf r}_1 &= \big(\dot x + c_1\cos\theta_1\,\omega_1,\ \ -c_1\sin\theta_1\,\omega_1\big)\\
\dot{\mathbf r}_2 &= \big(\dot x + L_1\cos\theta_1\,\omega_1 + c_2\cos\theta_2\,\omega_2,\ \ -L_1\sin\theta_1\,\omega_1 - c_2\sin\theta_2\,\omega_2\big)
\end{aligned}
```

## 2.2 Kinetic and potential energy

Each arm has translational energy of its CoM plus rotational energy about its CoM:

```math
T = \tfrac12 M\dot x^2 + \tfrac12 m_1|\dot{\mathbf r}_1|^2 + \tfrac12 I_1\omega_1^2 + \tfrac12 m_2|\dot{\mathbf r}_2|^2 + \tfrac12 I_2\omega_2^2
```

Expanding the squares (use $`\sin^2+\cos^2 = 1`$ and $`\cos\theta_1\cos\theta_2 + \sin\theta_1\sin\theta_2 = \cos(\theta_1-\theta_2)`$):

```math
|\dot{\mathbf r}_2|^2 = \dot x^2 + L_1^2\omega_1^2 + c_2^2\omega_2^2 + 2L_1\cos\theta_1\,\dot x\omega_1 + 2c_2\cos\theta_2\,\dot x\omega_2 + 2L_1c_2\cos(\theta_1-\theta_2)\,\omega_1\omega_2
```

Collecting terms, everything groups into the constants of [1.4](01_variables.md#14-the-combined-constants-the-equations-actually-use):

```math
\boxed{T = \tfrac12 (M + m_1 + m_2)\dot x^2 + \tfrac12 J_1\omega_1^2 + \tfrac12 J_2\omega_2^2 + p_1\cos\theta_1\,\dot x\,\omega_1 + p_2\cos\theta_2\,\dot x\,\omega_2 + h_{12}\cos(\theta_1-\theta_2)\,\omega_1\omega_2}
```

```math
\boxed{U = g\,(m_1c_1 + m_2L_1)\cos\theta_1 + g\,m_2c_2\cos\theta_2 = g\,(p_1\cos\theta_1 + p_2\cos\theta_2)}
```

This is exactly the `T` and `U` typed in `PythonMasterMath2.py` (there `l` = $`c_1`$, `lFull` = $`L_1`$, `l2` = $`c_2`$, `(m1*l**2 + m2*lFull**2 + I)` = $`J_1`$, `(m1*l + m2*lFull)` = $`p_1`$, `m2*lFull*l2` = $`h_{12}`$).

Reading the terms:
- $`p_1\cos\theta_1\,\dot x\,\omega_1`$: moving the cart while arm 1 turns. This term is how the cart drives the arms.
- $`h_{12}\cos(\theta_1-\theta_2)\,\omega_1\omega_2`$: the two arms push on each other through the joint. Without it the arms would be two independent pendulums.
- No term couples $`x`$ to $`\varphi`$ directly: the cart only reaches arm 2 through arm 1 and the joint.

## 2.3 Lagrange's equations

With $`\mathcal L = T - U`$, for each coordinate $`q \in \{x, \theta_1, \theta_2\}`$:

```math
\frac{d}{dt}\frac{\partial\mathcal L}{\partial\dot q} - \frac{\partial\mathcal L}{\partial q} = Q_q
```

where $`Q_q`$ is the outside force or torque on that coordinate: the motor force $`F`$ minus cart drag $`b_c\dot x`$ for $`x`$, and the friction torques $`\tau_1, \tau_2`$ for the arms.

**Arm 1.** $`\partial\mathcal L/\partial\omega_1 = J_1\omega_1 + p_1\cos\theta_1\,\dot x + h_{12}\cos(\theta_1-\theta_2)\,\omega_2`$. Its time derivative:

```math
J_1\dot\omega_1 + p_1\cos\theta_1\,\ddot x - p_1\sin\theta_1\,\omega_1\dot x + h_{12}\cos(\theta_1-\theta_2)\,\dot\omega_2 - h_{12}\sin(\theta_1-\theta_2)(\omega_1-\omega_2)\,\omega_2
```

and $`\partial\mathcal L/\partial\theta_1 = -p_1\sin\theta_1\,\dot x\omega_1 - h_{12}\sin(\theta_1-\theta_2)\,\omega_1\omega_2 + g\,p_1\sin\theta_1`$. Subtracting, the $`\dot x\omega_1`$ terms cancel and the $`\omega_1\omega_2`$ terms leave $`h_{12}\sin(\theta_1-\theta_2)\,\omega_2^2`$:

```math
J_1\dot\omega_1 + h_{12}\cos(\theta_1-\theta_2)\,\dot\omega_2 = g\,p_1\sin\theta_1 - p_1\cos\theta_1\,\ddot x - h_{12}\sin(\theta_1-\theta_2)\,\omega_2^2 + \tau_1
```

**Arm 2**, the same way:

```math
h_{12}\cos(\theta_1-\theta_2)\,\dot\omega_1 + J_2\dot\omega_2 = g\,p_2\sin\theta_2 - p_2\cos\theta_2\,\ddot x + h_{12}\sin(\theta_1-\theta_2)\,\omega_1^2 + \tau_2
```

**Cart:**

```math
(M + m_1 + m_2)\,\ddot x + p_1\cos\theta_1\,\dot\omega_1 + p_2\cos\theta_2\,\dot\omega_2 = F - b_c\dot x + p_1\sin\theta_1\,\omega_1^2 + p_2\sin\theta_2\,\omega_2^2
```

Each term, in words (arm 1's equation):

| Term | Meaning |
| --- | --- |
| $`J_1\dot\omega_1`$ | arm 1's own inertia (with arm 2's mass at the joint) |
| $`h_{12}\cos(\cdot)\dot\omega_2`$ | arm 2 speeding up pulls arm 1 the other way |
| $`g\,p_1\sin\theta_1`$ | gravity tipping arm 1 (with arm 2's weight at its tip) further over |
| $`-p_1\cos\theta_1\,\ddot x`$ | **the control**: cart acceleration tips arm 1 backward (inertia) |
| $`-h_{12}\sin(\cdot)\omega_2^2`$ | arm 2 whirling around pulls on the joint (centrifugal) |
| $`\tau_1`$ | friction at the main pivot and the joint |

## 2.4 Friction

Joint friction acts on the **relative** rate of the two parts it connects. The main pivot connects arm 1 to the cart; the joint connects arm 2 to arm 1:

```math
\tau_1 = -b_1\,\omega_1 + b_2\,(\omega_2 - \omega_1), \qquad \tau_2 = -b_2\,(\omega_2 - \omega_1)
```

The joint's torque acts on both arms with opposite signs. In the swing-up script: `R1 = ... - r["B1"] * w1 + r["B2"] * rel`, `R2 = ... - r["B2"] * rel` with `rel = w2 - w1`. `PythonMasterMath2.py` has a `T_drag` that acts on both arms the same way; its comment says "NOT MODELED CORRECTLY, LEAVE AS 0", and it is 0.

## 2.5 Two ways to drive the model

**Force input (PythonMasterMath2.py).** Keep all three equations. Three unknown accelerations $`\ddot x, \dot\omega_1, \dot\omega_2`$, three equations, linear in them:

```math
\begin{bmatrix}
M + m_1 + m_2 & p_1\cos\theta_1 & p_2\cos\theta_2\\
p_1\cos\theta_1 & J_1 & h_{12}\cos(\theta_1-\theta_2)\\
p_2\cos\theta_2 & h_{12}\cos(\theta_1-\theta_2) & J_2
\end{bmatrix}
\begin{bmatrix}\ddot x\\ \dot\omega_1\\ \dot\omega_2\end{bmatrix}
=
\begin{bmatrix}F - b_c\dot x + p_1\sin\theta_1\,\omega_1^2 + p_2\sin\theta_2\,\omega_2^2\\ g\,p_1\sin\theta_1 - h_{12}\sin(\theta_1-\theta_2)\,\omega_2^2 + \tau_1\\ g\,p_2\sin\theta_2 + h_{12}\sin(\theta_1-\theta_2)\,\omega_1^2 + \tau_2\end{bmatrix}
```

`sp.solve([Eq1, Eq2, Eq3], [x2div, theta2div, theta22div])` inverts this symbolically (slow, so the result is cached in `symbolic_model2.pkl`).

**Acceleration input (the balance and swing-up scripts).** A stepper moves the cart exactly as commanded, whatever force that takes. So $`\ddot x = a`$ is chosen by the controller, and the cart equation only tells us the force the motor had to supply. Drop it. Two equations remain, with the 2x2 mass matrix:

```math
\underbrace{\begin{bmatrix} J_1 & h_{12}c_{12}\\ h_{12}c_{12} & J_2\end{bmatrix}}_{\mathbf H(\theta)}
\begin{bmatrix}\dot\omega_1\\ \dot\omega_2\end{bmatrix}
=
\begin{bmatrix} g\,p_1\sin\theta_1 - p_1\cos\theta_1\,a - h_{12}s_{12}\,\omega_2^2 + \tau_1\\ g\,p_2\sin\theta_2 - p_2\cos\theta_2\,a + h_{12}s_{12}\,\omega_1^2 + \tau_2\end{bmatrix},
\qquad c_{12} = \cos(\theta_1-\theta_2),\ s_{12} = \sin(\theta_1-\theta_2)
```

The cart mass $`M`$ and cart drag are gone: they cannot matter when the motor forces the motion.

## 2.6 Dividing by J1: the code's form

Divide both rows by $`J_1`$. The mass matrix becomes $`\begin{bmatrix}1 & H c_{12}\\ H c_{12} & J_{2r}\end{bmatrix}`$ and only the ratios `P1, P2, J2r, H, B1, B2` remain. Solving the 2x2 system by Cramer's rule:

```math
\dot\omega_1 = \frac{J_{2r}R_1 - Hc_{12}\,R_2}{J_{2r} - H^2c_{12}^2}, \qquad \dot\omega_2 = \frac{R_2 - Hc_{12}\,R_1}{J_{2r} - H^2c_{12}^2}
```

```math
R_1 = gP_1\sin\theta_1 - P_1\cos\theta_1\,a - Hs_{12}\omega_2^2 - B_1\omega_1 + B_2(\omega_2-\omega_1),\qquad
R_2 = gP_2\sin\theta_2 - P_2\cos\theta_2\,a + Hs_{12}\omega_1^2 - B_2(\omega_2-\omega_1)
```

which is line for line `f(z, a, r)` in `PythonMaster2_swingup.py`:

```python
R1 = G * r["P1"] * np.sin(th1) - r["P1"] * np.cos(th1) * a - r["H"] * s * w2 * w2 - r["B1"] * w1 + r["B2"] * rel
R2 = G * r["P2"] * np.sin(th2) - r["P2"] * np.cos(th2) * a + r["H"] * s * w1 * w1 - r["B2"] * rel
M12 = r["H"] * c
det = r["J2r"] - M12 * M12
return np.stack([w1, (r["J2r"] * R1 - M12 * R2) / det, w2, (R2 - M12 * R1) / det, v, a * np.ones_like(v)], axis=-1)
```

`det` never reaches zero: $`J_{2r} - H^2 \ge 0.387 - 0.158 = 0.229`$ (physical values), because a real mass matrix is positive definite.

## 2.7 When the stepper jumps speed: the "kick"

The swing-up script sends a new speed every 10 ms and the stepper changes to it almost at once. Integrate the arm equations across a speed jump $`\Delta v`$ that happens in a very short time $`\epsilon`$: gravity, friction and the $`\omega^2`$ terms stay finite and contribute $`\approx 0\cdot\epsilon`$, while $`a = \Delta v/\epsilon`$ is huge. What is left:

```math
\mathbf H(\theta)\,\Delta\boldsymbol\omega = -\begin{bmatrix}p_1\cos\theta_1\\ p_2\cos\theta_2\end{bmatrix}\Delta v
\quad\Rightarrow\quad
\Delta\boldsymbol\omega = -\mathbf H(\theta)^{-1}\begin{bmatrix}p_1\cos\theta_1\\ p_2\cos\theta_2\end{bmatrix}\Delta v
```

This is `kick(z, dv, r)`. Near upright (physical values) $`\Delta\omega_1 = -5.60\,\Delta v`$ and $`\Delta\omega_2 = +0.62\,\Delta v`$: a 0.1 m/s step of the cart makes arm 1 instantly turn at 0.56 rad/s the other way, and arm 2 (pushed through the joint) slightly with the cart. Hanging, the signs flip.

## 2.8 Energy (used by the recovery mode)

The arms' energy (cart forced, so its kinetic energy is not counted):

```math
E = \tfrac12\,\boldsymbol\omega^T\mathbf H(\theta)\,\boldsymbol\omega + g\,(p_1\cos\theta_1 + p_2\cos\theta_2)
```

Upright at rest $`E = g(p_1+p_2) = +0.807`$ J; hanging at rest $`-0.807`$ J. A swing-up has to add **1.614 J**. Differentiating along the equations of 2.5 (the Coriolis terms cancel, as they always do):

```math
\frac{dE}{dt} = -a\,(p_1\cos\theta_1\,\omega_1 + p_2\cos\theta_2\,\omega_2) + \tau_1\omega_1 + \tau_2\omega_2
```

So the cart adds energy when it accelerates against $`p_1\cos\theta_1\omega_1 + p_2\cos\theta_2\omega_2`$ and removes it when it accelerates with it. The script's RECOVER mode uses $`a = 0.20\,(P_1\cos\theta_1\omega_1 + P_2\cos\theta_2\omega_2)`$ ("swing power"), so $`dE/dt = -0.20 J_1(\ldots)^2 \le 0`$: it only ever takes energy out, which settles the arms for the next attempt ([5.7](05_swing_up.md#57-abort-recover-and-retry)).

Why this law cannot do the swing-up the way it does for the single arm: [5.1](05_swing_up.md#51-why-not-energy-pumping-like-the-single).

## 2.9 Any number of links

The same steps for $`n`$ links on a cart (used for the [triple](../Triple/README.md)) give

```math
p_j = m_jc_j + L_j\sum_{k>j}m_k,\qquad h_{ii} = I_i + m_ic_i^2 + L_i^2\sum_{k>i}m_k,\qquad h_{ij} = h_{ji} = L_i\,p_j\ \ (i<j)
```

```math
\sum_j h_{ij}\cos(\theta_i-\theta_j)\,\dot\omega_j = g\,p_i\sin\theta_i - p_i\cos\theta_i\,a - \sum_j h_{ij}\sin(\theta_i-\theta_j)\,\omega_j^2 + \tau_i
```

For $`n = 2`$ this is 2.5. Code: [`Math/shared/nlink_cart.py`](../shared/nlink_cart.py) (`Rig.p`, `Rig.h`, `accel_dynamics`), checked against the team's `f()` to machine precision by [`sims/verify_against_team_code.py`](sims/verify_against_team_code.py).

[Back to Double](README.md) · Prev: [1. Variables](01_variables.md) · Next: [3. Linear model](03_linear_model.md)
