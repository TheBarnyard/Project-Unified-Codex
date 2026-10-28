---
updated: 2026-10-28
updated_by: Barney (Claude, PUC setup session)
---
# Key parameters

Constants and settings people keep needing. Each value has a source. Conflicting values are listed side by side, never overwritten.

## Communication
| Parameter | Value | Source |
| --- | --- | --- |
| Receiver to Pi serial | `/dev/ttyUSB0`, 921600 baud, 100 Hz | `Receivermaster.ino` |
| Debug receiver variant | 115200 baud | `DebugReceiverMaster` |
| Mega to Pi serial | `/dev/ttyACM0`, 115200 baud | `ArduinoSlave.ino` |
| ESP-NOW rate per transmitter | 200 Hz | `TX1.ino`, `TX2.ino` |
| Encoder raw range | 0 to 16383 (MT6701, 14-bit, I2C) | TX firmware |
| Stale angle marker (6-byte format) | 0xFFFF | `Receivermaster.ino` |
| Fault trip | 10 consecutive misses (about 135 ms outage) | 2026-10-27 dropout logs |

## Calibration
| Parameter | Value | Source |
| --- | --- | --- |
| Single pendulum upright raw value | **CONFLICT:** 10687.7 in `PythonMaster.py` vs about 8994 if raw 802 is the free-hanging reading (about 37 deg apart) | Code vs 2026-10-07 bench. Unresolved, see [open-questions.md](open-questions.md) |

## Double pendulum model ratios (normalized by M11 = J1cm + m1 c1^2 + m2 L1^2)
| Set | P1 | P2 | J2r | H | B1 | B2 | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Previous ratios | 5.22342 | 2.01257 | 0.414 | 0.395 | | | Swing-up CSV config row, 2026-10-27 |
| SysID with new arm 1 | 5.107 | 1.864 | 0.389 | 0.384 | 0.100 | 0.0049 | `apply_sysid.py`, 2026-10-27 |
| Fit to 5 swing-ups | 5.164 | 1.802 | 0.391 | 0.392 | 0 | 0.114 | Swing window fit, 2026-10-27 [HYP] B2 about 20x the SysID value |

## Swing-up limits (double, as of 2026-10-28)
| Parameter | Value |
| --- | --- |
| CART_ACCEL_MAX | 16 m/s^2 |
| MOTOR_TOP_SPEED | 1.0 m/s |
| PLAN_TRACK_M | 0.30 (0.25 in the swingfit plan) |
| SWING_CART_ABORT_M | 0.36 |
| TRACK_SOFT_LIMIT_M | 0.40 |
| PLAN_SPEED (latest plan) | 0.60 m/s |

## New arm 1 estimate (CAD, not measured)
106.6 g, CoM 46.1 mm from pivot, Izz about pivot 5.99e-4 kg m^2. Do not use for control; it does not match the rig. Weigh the real arm.
