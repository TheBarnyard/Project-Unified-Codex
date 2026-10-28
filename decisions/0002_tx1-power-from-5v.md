---
type: decision
date: 2026-10-27
by: Barney
status: active
---
# Power TX1 from the Mega 5 V pin

**Decision:** TX1's PCB feed moved from the Mega 3.3 V pin to the Mega 5 V pin, into the XIAO 5V pin. Encoder and I2C pull-ups stay on the XIAO 3V3.

**Why:** the Mega 3.3 V regulator sagged under ESP32-C3 transmit bursts, causing radio dropouts.

**Alternatives:** battery like TX2; change the Wi-Fi channel (not needed so far).

**Source:** [debug record](../debug/2026-10-27_angle-dropouts.md).
