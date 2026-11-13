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

- Triple swing-up v1 sat still [SIM]: Barney's run (12-core PC, CPU, about 100 st/s) and Claude's run both did this. Evals at 150k-700k scored return 0, arm max 0.7 rad/s, tip height 0.00. At 300k it fan-bladed once (11.6 turns, tip factor 0.99), then went back to still. Causes: the plain reward `0.2*mean + 0.8*prod` of (1+cos)/2 is about 0 short of all three arms up, so with the rail penalty, standing still is the safe local optimum. The warm start from the balance policy also left the SAC entropy coef at about 0.004 (balance began at 1.0).
- v2b (14:45 UTC, commit 1cb7d28, zip sha256 c149b8db...) changes only `triple_swingup`: height reward `0.5*h^2 + 0.5*prod(up_i)` (h = summed link-end heights, 0 hanging to 1 upright); 30 % random-pose training starts (eval always hanging); entropy coef reset to 0.1 on warm start (`--ent-coef-init`). Upright-start probability now applies to training envs only.

- v2b test (Claude, 4 cores): evals from hanging still motionless at 100-150k (arm max 0.6-0.7 rad/s); SAC entropy coef fell back to 0.006 within 100k even after the 0.1 reset. Cause [HYP]: `h^2` has zero slope at hanging (quartic in the swing angle).
- v2c (commit 97a6696): `turbo.py`. It benchmarks learner layouts (CPU 8/8/512, 16/8/1024; CUDA 16/8/1024, 32/8/2048, 64/8/4096 as envs/gradient steps/batch, all 512 samples per collected step), runs 2 seeds in parallel at below-normal priority with 2 cores kept free and evals every 200k, and the first to solve stops the others (STOP file). Barney's PC: RTX 4060 8 GB; the standard layout benchmarked CPU 122 vs CUDA 111 st/s.
- v2d (commit 4d5e87d, zip sha256 e47032b5...): `triple_swingup` reward = `0.3*h + 0.2*max(0, 1-|E/E_up - 1|) + 0.5*prod(up_i)`, with arm energy E in the cart frame (potential + kinetic via `mj_mulM`). Optional `--spin-penalty` (per rad/s above 25). Turbo runs one seed with energy and one with energy-spin. Test: evals swing from the start (return 70 to 293 by 125k) but fan-blade (arms up to 50 rad/s), 0 % upright so far [SIM].

- v2d test, longer run: return 338 at 250k, still fan-blading (arms 41-48 rad/s), 0 % upright [SIM]. Barney's v2c turbo runs (v2b reward, `cuda,64,8,4096`, about 470 st/s per seed) also sat still at 700k [SIM].
- Barney's turbo benchmark (RTX 4060, single run, st/s): cpu 8/8/512 126, cpu 16/8/1024 160, cuda 16/8/1024 219, cuda 32/8/2048 412, cuda 64/8/4096 750.
- v2e (commit b00f4c6, zip sha256 73f61984...), asked for by Barney: turbo seed 1 = cart acceleration cap of 18 m/s² (commanded speed slew-limited per 1 ms step, measured 19 m/s²); seed 2 = no cap, with the reward multiplied by a smooth-acceleration factor 1/((1+ea²)(1+ej²)), where ea = (|a|-5)/15 and ej = (|Δa per 10 ms|-5)/20 are clipped at 0. Multiplicative, so standing still can never pay. Max cart acceleration (10 ms average) is now shown wherever max speed was, plus a cart v/a HUD line.

## Dead ends
- v2b `h^2` height reward: evals from hanging still sit still (flat reward at hanging).
- Triple swing-up with the double folder's plain reward and a balance warm start: collapses to "do nothing" within 350k steps (see above).

## Changed
- Code: new folder only, as above. No team code was edited.

## Open questions and next steps
- Weigh arm 3 and time its hanging period once it exists, then rebuild the model. Also confirm whether arm 3 carries electronics.
- The velocity action chatters at 50 Hz. The real motor stalls at 16-18 m/s² reversals ([cart jolt debug](../../../debug/2026-11-05_cart-jolt-red-led.md)), so the policy is not rig-ready as it stands.
