---
updated: 2026-10-29
updated_by: Ryan (Claude, math-folder session)
---
# 7. Simulations and rig results

[Back to Double](README.md) · Prev: [6. Balance vs swing-up](06_balance_vs_swingup.md)

## 7.1 What was simulated [SIM]

[`sims/double_sims.py`](sims/double_sims.py) runs the swing-up script's control loop ([`Math/shared/swing_sim.py`](../shared/swing_sim.py), `TeamSwingController`) and the balance script's loop (`TeamBalanceController`) against the nonlinear arm model:

- **Controller:** the scripts' gains (recomputed, identical), observer, TV-LQR, catch, balance, limits, torque-speed limit and timer rounding, step by step as in the scripts.
- **Plant:** the nonlinear model of [2.6](02_equations_of_motion.md#26-dividing-by-j1-the-codes-form) with its own ("true") ratios, integrated every 0.5 ms; the cart is a speed source that jumps to the rounded speed 8 ms after each sample (with the arm kick); encoders rounded to counts plus 1 count of noise; cart position rounded to steps.
- **Not simulated:** radio dropouts and timing jitter, sensor-age compensation (readings are exact in time), missed steps, belt stretch, Coulomb friction, the WAIT and RECOVER phases.

**Nominal** (true arms = the plan's model): the swing follows the plan, catches at 2.5 s and balances; cart within 0.250 m, speed up to 0.733 m/s.

![sim](images/fig09_swing_sim.png)

With the joint friction 1.5x the model's (dashed), the swing drifts from 1.3 s, the speed saturates at 0.831 m/s, the cart runs to -0.35 m and the attempt aborts at k = 169 (35° off the plan).

## 7.2 Which model errors the swing-up survives [SIM]

One error at a time, the stored plan, everything else as on the rig ([`robustness.json`](sims/robustness.json)):

![robustness](images/fig10_robustness.png)

| Error | Catches (as on the rig) | Catches (if the Arduino ran the exact speed) |
| --- | --- | --- |
| P1, P2, J2r or H off by ±2 % | all 8 | all 8 |
| ±4 % | 2 of 8 (P1 +4 %, P2 -4 %) | 4 of 8 |
| ±6 %, ±8 % | none | 1 of 16 |
| joint friction B2 x0.5, x1.5, x2, x3 | none | none |
| pivot friction B1 +0.02 to +0.1 | all | all |
| real motor delay 5-12 ms (plan assumes 8) | all | all |

So the swing-up needs P1, P2, J2r and H within about 2-3 % and the joint friction within well under ±50 %. The pivot friction and the delay barely matter. Removing the timer's speed ceiling helps a little but does not change the picture. This agrees with the team's digital twin ("about 3 % model ratio error, or B2 x1.5 or x0.5, makes it fail", [subsystems/swing-up.md](../../subsystems/swing-up.md)).

The ratio sets the team has used differ from each other by up to 10 % (P2) and 7 % (J2r) ([1.5](01_variables.md#15-the-ratios-what-the-scripts-and-system-id-really-use)): far more than this tolerance.

**The v060 plan** (`double_swingup_trajectory_v060.json`, PLAN_SPEED 0.60 m/s, branch `claude/project-thread-orcdoj` of TheBarnyard/ChatGPT-Pendulum-Project), same 28 single-error cases (±2, 4, 6 % in each ratio and B2 x0.5, 1.5, 2): 13 catches vs 11 for the stored plan. More speed headroom helps a little; it is not enough on its own [SIM].

## 7.3 What the rig did [HW]

All swing-up runs in the `logs` branch of etwan007/ENGT480, 2026-10-21 to 2026-10-28 ([`data/hw_double_attempts.csv`](data/hw_double_attempts.csv), [`data/hw_double_events.csv`](data/hw_double_events.csv)):

| | |
| --- | --- |
| Attempts | 35, in 15 runs, with 4 different plans and 3 ratio sets (the first one with B2 from 0.047 to 0.169) |
| Caught | 0 |
| Aborted at | k = 107 to 237 (1.07-2.37 s into the 2.5 s plan), median 160 |
| Abort reason | 24 angle (an arm > 35° off the plan), 11 cart (at 0.36 m) |
| Highest real cart speed | **0.831 m/s in every one of the 35** (commanded 0.858) |

![rig attempts](images/fig11_hw_attempts.png)

![rig replay](images/anim_double_swingup_hw.gif)

*Rig attempt 1 of `swingup_double_20261027_184605` (solid) against the plan (dashed) [HW].*

The five attempts of `swingup_double_20261027_184605` (stored plan, swing-fit ratios) in detail:

| Attempt | Largest error from the plan at k = 50 / 100 / 110 / 130 | First step at 0.831 m/s | Aborted at |
| --- | --- | --- | --- |
| 1 | 1.6° / 3.4° / 9.7° / 14.0° | k = 114 | k = 192 |
| 2 | 1.8° / 2.8° / 9.1° / 13.5° | 113 | 205 |
| 3 | 1.7° / 3.8° / 9.3° / 14.5° | 70 | 207 |
| 4 | 0.9° / 2.9° / 8.5° / 10.0° | 113 | 209 |
| 5 | 2.8° / 3.8° / 8.3° / 7.5° | 113 | 237 |

What this says:
1. For the first second the rig follows the plan within 1-4°, every attempt. The plan, the motor and the observer work.
2. Between k = 100 and 110 (1.0-1.1 s, while arm 2 swings over the top at about 300° and the cart reverses at full speed) the error jumps from about 3° to about 9°, in every attempt the same way. That is a **model error**, not noise: noise would differ between attempts.
3. From k = 113 the feedback asks for more speed than the 0.831 m/s ceiling, so it cannot correct, and the error grows to the abort.

## 7.4 Why every rig attempt tops out at 0.831 m/s

![speed cap](images/fig12_speed_cap.png)

The Arduino can only run step rates of $`125000/(N+1)`$ steps/s. Near 0.8 m/s the possible speeds are 0.733, 0.779, **0.831**, 0.890 m/s ($`N`$ = 16, 15, 14, 13). Going from 0.831 to 0.890 needs a requested speed above about 0.860 m/s (where the rounding flips), i.e. an acceleration of 2.9 m/s² within one 10 ms cycle. But the torque-speed limit allows only $`16\,(1 - 0.831/1.0)`$ = 2.7 m/s² when speeding up at 0.831 m/s: request at most 0.858 m/s, which rounds back to 0.831. So 0.831 m/s is a hard ceiling whenever the controller is speeding up, and 0.858 is exactly the commanded speed seen in every log. (Already recorded by the team in [debug/2026-10-27_double-swingup-aborts.md](../../debug/2026-10-27_double-swingup-aborts.md); confirmed here on all 35 attempts.)

The ceiling is the **symptom** that ends the attempts; the **cause** is the model error of 7.3 point 2 (the error grows before the ceiling is reached, and in simulation removing the ceiling saves only a few more cases).

## 7.5 What could make it catch (untested ideas)

All [HYP]; none of these has been tried on the rig.

| Idea | Why it might work | Cost |
| --- | --- | --- |
| Fit the ratios to the logged swing-up attempts themselves (the first 1.0-1.1 s of all 35, before the ceiling) | the model only needs to be right along this one motion; the logs contain exactly that motion, repeated | an offline fit; the swing-fit set was a first try with 5 attempts [HYP] |
| Iterative learning control: after each failed attempt, correct $`a_{\text{ref}}`$ by the error pattern it produced | attempts repeat almost identically for the first 1.1 s (7.3), which is the situation ILC is made for; it does not need a better model | more code; several attempts per tuning |
| Add a Coulomb (constant-torque) joint friction term to the model | B2 fits 0.03 for balancing and 0.114 for swinging, a typical sign of Coulomb friction (6.3) | one more parameter to fit |
| More speed headroom: lower `PLAN_SPEED_M_S`, or fix the rounding (choose the timer value nearest the request when accelerating) | the feedback can then act after k = 113 | v060 plan: 13 vs 11 of 28 in simulation |
| Plan robustly: one plan that works for several ratio sets at once (minimise the worst case) | trades effort for tolerance | longer planning |

## 7.6 Rerun everything

```bash
cd Math/Double/sims
python verify_against_team_code.py <path to LegacyPi/Code/DoublePendulum>   # 14 checks against the team code
python double_model.py      # every matrix and gain on these pages
python double_sims.py       # swing-up, robustness sweep, balance (about 1-2 min)
python make_figures.py      # ../images
python extract_hw_logs.py <folder with the run_logs>   # ../data from the full logs
```

Needs numpy, scipy, matplotlib, pillow; `casadi` only for `plan_team` in `Math/shared/nlink_cart.py`.

[Back to Double](README.md) · Prev: [6. Balance vs swing-up](06_balance_vs_swingup.md)
