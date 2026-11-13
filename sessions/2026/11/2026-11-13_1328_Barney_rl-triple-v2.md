---
type: session
date: 2026-11-13
time: 13:28 (UTC)
member: Barney
ai: Claude project thread
topics: [arms-and-model]
status: wip
pages_applied: yes
transcript: none
---
# Triple-arm RL training folder (balance + swing-up, V2 arms + 300 mm arm 3)

## Goal
Barney asked for code to train triple-arm balance and triple-arm swing-up on the V2 arms, with a third arm 50 mm longer than arm 2. Barney wanted the code before Claude tested it, so they could start training (on their PC) right away.

## What happened
- Copied the double RL folder `engt481_rl_double_newarms` (2026-10-30) and kept its SAC settings, reward, action and tooling unchanged. Added `model/build_triple_v2.py`, which writes `model/triple_pendulum.xml` and a `triple` entry in `params.json`, plus the tasks `triple_balance` and `triple_swingup`.
- Delivered at 13:40 UTC as `engt481_rl_triple_v2arms.zip`: project files `RL_Triple_V2/`, and `TheBarnyard/ChatGPT-Pendulum-Project` branch `claude/project-thread-8o7nnj`, `RL_Triple_V2/`, commit 1929eb3 (zip sha256 b456ddaf065c329ed06f54204246d7db06f7570848ca757f28de111f6feb41cd).
- Tested in the cloud (4 CPU cores).

## Findings
- Triple model (V2) [HYP for arm 3]:
  | Link | Length | Mass | CoM from own pivot | I about CoM | Source |
  |---|---|---|---|---|---|
  | 1 | 200 mm | 98.1 g | 147.8 mm | 3.40e-4 kg m² | STL + weights; its P1 = 5.233 vs V2 fit 5.2253 |
  | 2 (+ joint-2 shaft) | 250 mm | 161.8 g | 111.5 mm | 2.02e-3 kg m² | mass from the STL model; CoM and I solved from the V2 fit P2 and J2r |
  | 3 (+ joint-3 shaft) | 300 mm | 169.9 g | 135.4 mm | 3.06e-3 kg m² | arm 2 stretched 50 mm (bar 50.6 g, hub parts moved 50 mm out), then arm 2's fit correction applied (first moment x0.865, pivot inertia x0.895) |
  Joint damping b1 1.63e-4 and b2 1.24e-4 N m s come from the fit B1/B2; b3 = b2 is assumed. Arm 3 is assumed to carry a full copy of arm 2's hub electronics (`--arm3-hub bare` builds the version without). The 25 mm arm-plane spacing is assumed.
- LQR (`watch.py --lqr`) balances the triple model in 4 of 5 random starts [SIM].
- `triple_balance` was solved at 190k steps (3 passing evals in a row) in 60 min on 4 cores [SIM]. It chatters like the double: the command flips up to 100 times/s, dominant 49.9 Hz, cart up to 0.97 m/s. Files: project files `RL_Triple_V2/test_2026-11-13/` (best.zip, video, report).

## Changed
- Code: new folder only, as above. No team code was edited.

## Open questions and next steps
- Weigh arm 3 and time its hanging period once it exists, then rebuild the model. Also confirm whether arm 3 carries electronics.
- The velocity action chatters at 50 Hz. The real motor stalls at 16-18 m/s² reversals ([cart jolt debug](../../../debug/2026-11-05_cart-jolt-red-led.md)), so the policy is not rig-ready as it stands.
- Triple swing-up training: test still running (see below).
