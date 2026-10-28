---
type: decision
date: 2026-10-27
by: Barney (Claude advice)
status: active
---
# Keep fitted model ratios, not the CAD arm estimate

**Decision:** keep the measured or fitted double-pendulum ratios for the new arm 1. Do not plug in the CAD-based mass and inertia estimate.

**Why:** fitted ratios predict the new arm within about 7 deg at 0.9 s; the CAD estimate is off by about 32 deg.

**Revisit when:** the real arm is weighed and real STLs are available.

**Source:** [arms and model](../subsystems/arms-and-model.md).
