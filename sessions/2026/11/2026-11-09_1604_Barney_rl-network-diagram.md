---
type: session
date: 2026-11-09
time: 16:04 (UTC)
member: Barney
ai: Claude project thread
topics: [arms-and-model]
status: done
pages_applied: yes
transcript: none
---
# Lines-and-circles diagram of the RL policy network

## Goal
A simple, accurate picture of the project's neural network.

## What happened
Read the architecture from `engt481_rl_double_newarms.zip` (project files `RL_DoubleNewArms/`): `train.py` `build_model` and `pendulum_env.py` `_obs`. Drew it with matplotlib.

## Findings
- Policy = SB3 SAC actor, `MlpPolicy`, `net_arch=[256, 256]`, ReLU (SB3 default): 9 inputs -> 256 -> 256 -> 1 output.
- Inputs (double, velocity action mode): x/0.50 m, xdot/1.4 m/s, sin th1, sin th2, cos th1, cos th2, w1/10, w2/10, previous action (absolute arm angles). Accel mode adds a 10th input (v_cmd/1.4).
- Output: one action in [-1, 1] (tanh squashed) -> cart velocity command = action x 1.4 m/s, every 10 ms.
- SAC also trains two critics (Q nets, same 256x256) used only during training; not in the diagram. PPO option would be pi [128,128].

## Changed
- Diagram: project files `NeuralNetDiagram/rl_policy_network.png` and `.svg`.

## Open questions and next steps
- None.
