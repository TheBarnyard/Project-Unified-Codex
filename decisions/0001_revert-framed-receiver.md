---
type: decision
date: 2026-10-07
by: Barney
status: active
---
# Revert the framed receiver firmware

**Decision:** after the framed receiver firmware (`FramedReceiverMaster` + `encoder_link.py`) passed bench tests, re-flash the original `Receivermaster` and move the framed sketch out of the repo (`~/encoder_debug` on the Pi).

**Why:** keep the team's working code unchanged ([decision 0004](0004_work-in-copies.md)).

**Alternatives:** adopt the framed protocol. The ENGT480 team later added its own framed protocol v1.

**Source:** [debug record](../debug/2026-10-07_encoder-data-loss.md).
