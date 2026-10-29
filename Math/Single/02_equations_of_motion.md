---
updated: 2026-10-29
updated_by: Ryan (Claude, math-folder session)
---
# 2. Equations of motion (Lagrange)

[Back to Single](README.md) · Prev: [1. Variables](01_variables.md) · Next: [3. Linear model](03_linear_model.md)

This page derives, by hand, exactly what lines 158-208 of [the script](https://github.com/etwan007/ENGT480/blob/ba019f9c07369a59731eefc16b8dfa34f9be00f8/LegacyPi/Code/SinglePendulum/PythonMasterUpExpClaudeImproved.py#L158-L208) make SymPy derive. You can check every line with [`sims/single_model.py`](sims/single_model.py), which runs the same SymPy code and prints the results.

## 2.1 Why Lagrange

Newton's method needs the internal pivot forces (the code still declares `H` and `V` for them on line 162, a leftover). Lagrange's method skips them: write the kinetic energy $`T`$ and potential energy $`U`$ in terms of the two coordinates $`x`$ and $`\theta`$, and the equations fall out.

## 2.2 Positions and velocities

The pivot rides on the cart at $`(x, 0)`$. The arm's centre of mass is $`l`$ from the pivot, at angle $`\theta`$ from vertical:

```math
x_p = x - l\sin\theta, \qquad y_p = l\cos\theta
```

Differentiate with respect to time (chain rule, $`\tfrac{d}{dt}\sin\theta = \cos\theta\,\dot\theta`$):

```math
\dot x_p = \dot x - l\cos\theta\,\dot\theta, \qquad \dot y_p = -l\sin\theta\,\dot\theta
```

```math
v_p^2 = \dot x_p^2 + \dot y_p^2 = \dot x^2 - 2l\cos\theta\,\dot x\dot\theta + l^2\dot\theta^2
```

(the $`l^2\dot\theta^2`$ comes from $`\cos^2 + \sin^2 = 1`$).

## 2.3 Kinetic energy T (line 180)

Three pieces: the cart moving, the arm's centre of mass moving, and the arm spinning about its own centre of mass.

```math
T = \tfrac12 M\dot x^2 + \tfrac12 m v_p^2 + \tfrac12 I\dot\theta^2
```

Substitute $`v_p^2`$ and group:

```math
\boxed{T = \tfrac12 (M+m)\dot x^2 - m l\cos\theta\,\dot x\dot\theta + \tfrac12 (ml^2 + I)\dot\theta^2}
```

Code, line 180:
```python
T = (1/2)*(mcart+m1)*x.diff(t)**2 - m1*l*sp.cos(theta)*x.diff(t)*theta.diff(t) + (1/2)*(m1*l**2+I)*theta.diff(t)**2
```
Term by term the same. Note $`ml^2 + I = J_p`$, the inertia about the pivot (parallel-axis theorem). This is why `I` in the code is the inertia about the **centre of mass**.

The middle term $`-ml\cos\theta\,\dot x\dot\theta`$ is the **coupling**: it is the only place the cart and the arm talk to each other. Everything the controller does flows through it.

## 2.4 Potential energy U (line 181)

Height of the CoM above the pivot is $`l\cos\theta`$:

```math
\boxed{U = mgl\cos\theta}
```

$`U`$ is largest upright ($`\theta=0`$) and smallest hanging. Line 181: `U = m1*g*l*sp.cos(theta)`.

## 2.5 The Lagrangian (line 183)

```math
\mathcal{L} = T - U
```

## 2.6 Euler-Lagrange equations (lines 185-193)

For each coordinate $`q`$:

```math
\frac{d}{dt}\frac{\partial \mathcal L}{\partial \dot q} - \frac{\partial \mathcal L}{\partial q} = Q_q
```

where $`Q_q`$ is the generalized force that is not in $`U`$ (pushes, drag).

**Cart coordinate, $`q = x`$.** Outside force: the motor force $`F`$ minus viscous drag $`b_c\dot x`$ (line 187: `F - B_cart_drag * x.diff(t)`).

```math
\frac{\partial\mathcal L}{\partial\dot x} = (M+m)\dot x - ml\cos\theta\,\dot\theta
```
```math
\frac{d}{dt}\frac{\partial\mathcal L}{\partial\dot x} = (M+m)\ddot x - ml\cos\theta\,\ddot\theta + ml\sin\theta\,\dot\theta^2, \qquad \frac{\partial\mathcal L}{\partial x} = 0
```

```math
\boxed{(M+m)\ddot x - ml\cos\theta\,\ddot\theta + ml\sin\theta\,\dot\theta^2 = F - b_c\dot x} \qquad\text{(E1)}
```

**Arm coordinate, $`q = \theta`$.** Outside torque: pivot drag $`-\tau_d`$ (line 192; zero in our values).

```math
\frac{\partial\mathcal L}{\partial\dot\theta} = -ml\cos\theta\,\dot x + J_p\dot\theta
```
```math
\frac{d}{dt}\frac{\partial\mathcal L}{\partial\dot\theta} = ml\sin\theta\,\dot\theta\dot x - ml\cos\theta\,\ddot x + J_p\ddot\theta
```
```math
\frac{\partial\mathcal L}{\partial\theta} = ml\sin\theta\,\dot x\dot\theta + mgl\sin\theta
```

The $`ml\sin\theta\,\dot x\dot\theta`$ terms cancel:

```math
\boxed{J_p\ddot\theta - ml\cos\theta\,\ddot x - mgl\sin\theta = -\tau_d} \qquad\text{(E2)}
```

## 2.7 Solve for the accelerations (lines 195-201)

Lines 197-199 replace $`\ddot x`$ and $`\ddot\theta`$ by plain symbols `x2div`, `theta2div` so SymPy can treat (E1), (E2) as two linear equations in two unknowns. In matrix form:

```math
\begin{bmatrix} M+m & -ml\cos\theta \\ -ml\cos\theta & J_p \end{bmatrix}
\begin{bmatrix} \ddot x \\ \ddot\theta \end{bmatrix}
=
\begin{bmatrix} F - b_c\dot x - ml\sin\theta\,\dot\theta^2 \\ mgl\sin\theta - \tau_d \end{bmatrix}
```

The left matrix is the **mass matrix**. Its determinant:

```math
\Delta(\theta) = (M+m)J_p - m^2l^2\cos^2\theta = I(M+m) + Mml^2 + m^2l^2\sin^2\theta
```

It is always positive, so the system can always be solved. Cramer's rule gives (this is exactly what line 201 `sp.solve` returns; run `single_model.py` to see SymPy print it):

```math
\boxed{\ddot\theta = \frac{(M+m)(mgl\sin\theta - \tau_d) + ml\cos\theta\,(F - b_c\dot x - ml\sin\theta\,\dot\theta^2)}{\Delta(\theta)}}
```

```math
\boxed{\ddot x = \frac{J_p\,(F - b_c\dot x - ml\sin\theta\,\dot\theta^2) + ml\cos\theta\,(mgl\sin\theta - \tau_d)}{\Delta(\theta)}}
```

SymPy writes $`m^2gl^2\sin\theta\cos\theta`$ as `0.5*g*l**2*m1**2*sin(2.0*theta)` (same thing, $`\sin2\theta = 2\sin\theta\cos\theta`$).

## 2.8 State-space form (lines 203-209)

With $`\mathbf y = [\theta, \dot\theta, x, \dot x]`$ (`Y1..Y4`, line 204):

```math
\dot{\mathbf y} = f(\mathbf y, F) = \begin{bmatrix} \dot\theta \\ \ddot\theta(\mathbf y, F) \\ \dot x \\ \ddot x(\mathbf y, F) \end{bmatrix}
```

That is `NonLinMod = sp.Matrix([Y2, F1, Y4, F2])`, line 208. The code never simulates this nonlinear model; it only linearises it (next page).

## 2.9 The equation that really matters on our rig

Our cart is driven by a **stepper motor commanded by speed**, not by force. Within its torque limit, the stepper makes $`\dot x`$ whatever we ask, so $`\ddot x`$ is an *input* and (E1) only tells us what force the motor must supply. The arm only sees (E2). Divide (E2) by $`J_p`$ and use $`\omega_0^2 = mgl/J_p`$, so $`ml/J_p = \omega_0^2/g`$ (with $`\tau_d = 0`$):

```math
\boxed{\ddot\theta = \frac{\omega_0^2}{g}\left(g\sin\theta + \ddot x\cos\theta\right)}
```

Read it as: *the arm feels gravity plus the cart's acceleration, projected through $`\cos\theta`$*. Three consequences used by the code:

1. **Only $`\omega_0`$ matters** for how the arm responds to the cart. Two arms with the same swing period respond the same. That is why IDENTIFY measures $`\omega_0`$ and then picks an inertia that gives it (line 676, comment on line 675).
2. At $`\theta = \pm 90^\circ`$ (arm horizontal), $`\cos\theta = 0`$: the cart cannot move the arm at all. The swing-up uses this ([7](07_swing_up.md)).
3. Upright, small angles: $`\ddot\theta \approx \omega_0^2\theta + (\omega_0^2/g)\ddot x`$. With $`\omega_0 = 7.29`$ rad/s, a tilt grows by $`e^{7.29t}`$: it doubles every $`\ln 2/7.29 = 0.095`$ s. To hold it, 1 m/s² of cart acceleration is worth $`1/g = 0.102`$ rad = 5.8° of tilt.

This is also the plant used by the simulator [`sims/single_sim.py`](sims/single_sim.py).

## 2.10 The energy of the arm

Multiply (E2) by $`\dot\theta`$ and integrate. The arm's own energy (pivot frame) is

```math
E = \tfrac12 J_p\dot\theta^2 + mgl\cos\theta, \qquad \frac{dE}{dt} = ml\,\ddot x\,\dot\theta\cos\theta - \tau_d\dot\theta
```

The cart can only change the arm's energy through $`\ddot x\,\dot\theta\cos\theta`$. This one line is the whole swing-up controller; see [7. Swing-up](07_swing_up.md).

[Back to Single](README.md) · Prev: [1. Variables](01_variables.md) · Next: [3. Linear model](03_linear_model.md)
