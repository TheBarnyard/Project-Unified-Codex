# Triple pendulum simulation scripts

Standalone Python; there is no triple rig. The model and controller code is the shared n-link code in [`../../shared/`](../../shared/README.md).

```bash
python -m venv venv && . venv/bin/activate        # Windows: venv\Scripts\activate
pip install numpy scipy matplotlib pillow casadi   # casadi only for make_plans.py
cd Math/Triple/sims
python triple_model.py      # constants, A, B, modes, balance gain, tolerances (seconds); writes triple_model_numbers.json
python make_plans.py 4.0    # a swing-up plan into ../data (5-15 minutes per duration; the plans are already there)
python triple_sims.py       # balance and swing-up simulations, robustness sweeps (about 10 minutes)
python make_figures.py      # ../images
```

| File | What it is |
| --- | --- |
| `triple_model.py` | The assumed rig (`TRIPLE`, `TRIPLE_SWING`, `TRIPLE_LIGHT`, plus `DOUBLE` and `SINGLE` for comparison), `balance()` (the double balance script's design with n = 3), and the tolerance analysis (`entry_rig`, `physical_rig`, delay). |
| `make_plans.py` | Swing-up plans: loose limits first, then continuation toward the rig's limits. Writes `../data/triple_swingup_plan_<T>s.json`. |
| `triple_sims.py` | Closed-loop runs with the double scripts' loops (`TeamBalanceController`, `TeamSwingController`) for n = 3, and the model-error sweeps. |
| `make_figures.py` | All figures and GIFs in `../images`. |
| `triple_model_numbers.json`, `triple_sims.json`, `sim_results.npz` | Outputs, so the figures can be redrawn without re-running. |

Try a different third arm, for example the lighter STL arm:

```python
import triple_model as tm
d = tm.balance(tm.TRIPLE_LIGHT)
print(d["K"], tm.delay_tolerance(tm.TRIPLE_LIGHT, d))
```
