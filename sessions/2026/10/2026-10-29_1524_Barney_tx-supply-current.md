---
type: session
date: 2026-10-29
time: 15:24 (UTC)
member: Barney
ai: Claude (claude.ai project thread "Fix recurring angle dropouts")
topics: [encoders-and-transmitters, receiver]
status: wip
pages_applied: yes
transcript: none
---
# Transmitter dropouts depend on supply current, not voltage

## Goal
Interpret Barney's bench supply test on a XIAO transmitter.

## What happened
- Barney powered one transmitter from a DC bench supply and varied voltage and current limit.

## Findings
- 3.3 V vs 5 V: little or no difference in radio age or timeouts [HW].
- Average draw 120 to 170 mA (mostly 120 to 150 mA); a 150 mA current limit reproduces the usual dropouts [HW].
- ESP32-C3 TX peaks are up to 335 mA (datasheet v1.2 Table 16); Espressif recommends 500 mA+ supply. The supply must cover the peaks [HYP, consistent with the test].
- Earlier this week (2026-10-28): receiver ESP32 went silent twice (0 bytes, USB still enumerated) after runs; reset with EN fixes it. Cause not found (bootloader vs hang check sent, no answer yet) [?].
- 2026-10-28: angle 2 had a 108 ms wireless_timeout mid swing-up (6-miss stop) [HW]; antenna/battery check suggested.

## Decisions
- None yet.

## Changed
- PUC: debug/2026-10-27_angle-dropouts.md (bench test section), gotchas.md.

## Open questions and next steps
- Add bulk capacitors (220-470 uF + 0.1 uF) at each XIAO; retest.
- Optional: low TX power firmware copies, retest at 150 mA limit.
- Test whether one transmitter dropping out affects the other (expected: no).
- Receiver lockup cause (esptool chip-id --before no-reset check).
