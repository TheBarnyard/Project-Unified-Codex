---
updated: 2026-10-29
updated_by: Ryan (Claude, math-folder session)
---
# Math

Teaching pages for the math behind the pendulum controllers: every variable, every equation, and how each one becomes code. Each pendulum has its own folder, with balance and swing-up covered separately and compared.

| Folder | Covers | Status |
| --- | --- | --- |
| [Single/](Single/README.md) | Single pendulum on a cart: model, LQR/LQG balance, swing-up, line-by-line comparison with `PythonMasterUpExpClaudeImproved.py`, simulator, rig data | Done (2026-10-29) |
| [Double/](Double/README.md) | Double pendulum on a cart: model, three balance designs, planned swing-up with TV-LQR, simulator, all 35 rig swing-up attempts; every gain checked against the team's scripts | Done (2026-10-29); line-by-line code walkthrough later |
| [Triple/](Triple/README.md) | Triple pendulum on a cart, on an assumed rig (the double + a third arm): model, balance, swing-up plans and simulations with the double scripts' methods | Done (2026-10-29) [HYP rig, SIM]; no rig or team code exists |

Tags follow [AGENTS.md](../AGENTS.md): `[HW]` verified on the rig, `[SIM]` simulation only, `[HYP]` hypothesis, `[?]` unconfirmed.

Shared Python for the double and triple (any number of links): [shared/](shared/README.md).
