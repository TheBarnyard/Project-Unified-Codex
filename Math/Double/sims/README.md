# Double pendulum simulation scripts

Standalone Python; nothing here talks to the rig. The model and controller code is shared with the triple and lives in [`../../shared/`](../../shared/README.md).

```bash
python -m venv venv && . venv/bin/activate        # Windows: venv\Scripts\activate
pip install numpy scipy matplotlib pillow          # + casadi only to make new swing-up plans
cd Math/Double/sims
python verify_against_team_code.py <path to LegacyPi/Code/DoublePendulum>   # 14 checks, prints ALL MATCH
python double_model.py      # every matrix and gain on the pages; writes double_model_numbers.json
python double_sims.py       # swing-up, robustness sweep, balance (a few minutes); writes sim_results.npz, robustness.json
python physical_errors.py   # physical vs ratio model errors (5-10 minutes, casadi)
python longer_plans.py <path to LegacyPi/Code/DoublePendulum>   # 3.0/3.5 s plans + sweep (about 10 minutes)
python make_figures.py      # regenerates ../images (about 2 minutes)
python extract_hw_logs.py <folder with the run_logs>   # rebuilds ../data from the full logs
```

| File | What it is |
| --- | --- |
| `verify_against_team_code.py` | Imports the team's scripts read-only (a stub replaces `serial`) and compares their A, B, K, L, plan, TV-LQR gains and observer gains with ours. |
| `double_model.py` | The physical arm values, the four ratio sets, natural motions, the gen-1 force design, `balance_claude()` (the 12.8-minute balance gain) and `balance_swingup()`. |
| `double_sims.py` | Closed-loop runs of `PythonMaster2_swingup.py`'s and `PythonMasterDouble-Claude.py`'s loops against the nonlinear model, and the model-error sweep. |
| `physical_errors.py` | Swing-up against errors in physical values (mass, CoM, inertia, joint position) vs single ratio errors, around a plan for the physical arm values. Writes `physical_errors.json`. |
| `longer_plans.py` | 3.0 s and 3.5 s plans with the stored plan's model and limits, written in the script's file format and checked with the script's own `plan_problem` and `load_trajectory`; same error sweep. Writes `longer_plans.json`. |
| `make_figures.py` | All figures and GIFs in `../images`. Re-run after `../../Triple/sims/` changes (the pole figure includes the triple). |
| `extract_hw_logs.py` | Pulls the compact CSVs in `../data` out of the full run logs (`logs` branch of etwan007/ENGT480). |
| `double_model_numbers.json`, `robustness.json`, `sim_results.npz` | Outputs of the scripts above, so the figures can be redrawn without re-running the sims. |

Try a change before taking it to the rig, for example the real joint friction being 1.5x the model's:

```python
import double_sims as ds, double_model as dm
rig, Z, g = ds.swing_setup(dm.RATIOS["swing-fit (stored plan, 2026-10-27)"])
true = dict(dm.RATIOS["swing-fit (stored plan, 2026-10-27)"]); true["B2"] *= 1.5
res, info = ds.swing_once(rig, Z, g, true)
print(info)        # ok, why, k_end, max_v, max_x, capped
```

Limits of the simulation: see [7.1](../07_results.md#71-what-was-simulated-sim).
