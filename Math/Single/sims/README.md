# Single pendulum simulation scripts

Standalone Python; nothing here talks to the rig.

```bash
python -m venv venv && . venv/bin/activate        # Windows: venv\Scripts\activate
pip install numpy sympy control scipy matplotlib pillow
cd Math/Single/sims
python single_model.py      # prints A, B, Ad, Bd, K, L and poles for nominal and identified inertia, both Q sets
python single_sim.py        # 40 s closed-loop run: identify, swing-up, catch, balance, two pushes
python make_figures.py      # regenerates ../images (about 1 minute)
```

| File | What it is |
| --- | --- |
| `single_model.py` | Lines 158-231 of `PythonMasterUpExpClaudeImproved.py` copied unchanged (symbols, values, Lagrangian, `sp.solve`, Jacobians, `c2d`, `dlqr`, `dlqe`), plus helpers. Writes `single_model_numbers.json`. |
| `single_sim.py` | `Controller`: the script's loop logic (IDENTIFY, SWING, LQG, estimator, trim, clips, catch). `Plant`: arm driven by cart acceleration, stepper as a quantised speed source. `run()` returns every signal. |
| `make_figures.py` | All figures and GIFs in `../images`. |
| `extract_hw_logs.py` | Pulls the compact CSVs in `../data` out of the full run logs (instructions inside for a cheap clone of the `logs` branch). |

Try a change before taking it to the rig, for example a stiffer centering spring:

```python
import single_sim as s
s.SWING_CENTER_KP = 20.0
r = s.run(T=20)
print(r["identify"], r["catches"], r["losses"])
```

Limits of the simulation: see [10.1](../10_results.md#101-what-was-simulated-sim).
