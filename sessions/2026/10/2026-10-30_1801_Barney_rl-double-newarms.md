---
type: session
date: 2026-10-30
time: 18:01 (UTC)
member: Barney
ai: Claude project thread
topics: [arms-and-model, swing-up]
status: done
pages_applied: yes
transcript: none
---
# RL training folder: double balance + double swing-up on the new arms

## Goal
One downloadable MuJoCo RL folder: training numbers from the older "BETTER TRAINING NUMBERS AND RESULT" version (best-looking double path), all program features from `ENGT481_update_v4_1` but not its training, the corrected new-arm model, only double balance and double swing-up, and swing-up auto-stop after 5 passes in a row instead of 3.

## What happened
- Inputs (Barney's uploads, 2026-10-30): `engt481_rl_BETTER TRAINING NUMBERS AND RESULT.zip` (train/env/dashboard/run_all; no common.py, watch.py, record.py or meshes), `ENGT481_update_v4_1.zip` (code only, no model, no record.py), `Corrected_Arms_MuJoCo_Model.zip` (double MJCF, meshes, params.json).
- Built `engt481_rl_double_newarms.zip`, saved to project files `RL_DoubleNewArms/`. Originals untouched.
- Kept from the better version: plain SAC (lr 3e-4, buffer 1M, batch 512, gamma 0.99, tau 0.005, learning_starts 5000, 256x256), gradient steps = envs for swing-up / envs/2 for balance, eval every 20k (swing-up) / 10k, cart velocity action set directly, reward `(0.2 mean + 0.8 prod of up) * centered * (0.8 + 0.2 calm) - effort`, rail penalty 10, swing-up 10% upright starts, pass tests (balance >=95% upright; swing-up hold >=6 s and >=55% upright, all episodes full length).
- Ported from v4.1: two ETAs + solve history, 60 s speed average, two-lane run_all view, `--only`, video every eval, best-replay folder, 100 Hz eval traces + behaviour flags, diag.jsonl, report.py + dashboard report button, Windows file-lock-safe saves, `--threads`, `--print-every`, `--model`, LQR in watch.py from params.json. `--action-mode accel` kept as an opt-in.
- Not ported (training changes): TQC + gSDE, v4 reward/shaping/anti-chatter factors, exploring starts, stall termination, accel as default.
- New: `record.py` (missing from both zips). Swing-up step budget raised 3M -> 10M so it runs until the 5 passes. Fixed a v4.1 bug where the end-of-budget eval repeated the last eval at the same step and counted a pass twice.

## Findings
- Double balance on the new arms solved (3/3 eval episodes full 10 s, 97-100% upright) at 70k and 120k steps on a 4-core VM, about 350 steps/s [SIM]. Old arms needed about 40k.
- The balance policy chatters (cart command reverses 50-100 times/s), the same velocity-action jiggle v4.1 diagnosed [SIM].
- LQR from the new-arm params.json holds double balance for the full 10 s in this MuJoCo model [SIM].

## Dead ends
- None.

## Decisions
- Treat the action mode, learner, reward and start distribution as "training" (kept from the better version), and logging, ETAs, reports and viewers as "features" (from v4.1). Claude's reading of Barney's request.

## Changed
- Code: project files `RL_DoubleNewArms/engt481_rl_double_newarms.zip` (not in a repo).

## Open questions and next steps
- Train the double swing-up on Barney's PC; expect hours.
- If the chatter matters for the rig, try `-- --action-mode accel` (changes training).
