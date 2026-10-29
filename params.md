---
updated: 2026-10-29
updated_by: Barney (Claude, new arms model session, correction)
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
| Single upright raw value, auto-calibrated each run (hanging + 8192) | 11716-11978 counts on 2026-10-16, 11945-11948 on 2026-10-27 [HW] | `PythonMasterUpExpClaudeImproved.py` run logs |

## Single pendulum model and gains (`PythonMasterUpExpClaudeImproved.py`)
| Parameter | Value | Source |
| --- | --- | --- |
| m, M, l, I (code) | 0.260 kg, 0.969 kg, 0.05 m, 0.003 kg m² | script lines 168-177 |
| Arm w0 | **CONFLICT:** 5.911 rad/s (1.063 s) from the code's m, l, I vs **7.09-7.47 rad/s (0.84-0.89 s) measured** by IDENTIFY in 20 rig runs [HW] | open question 9 |
| I used for LQG after IDENTIFY | 0.001634-0.001888 kg m² | rig logs [HW] |
| LQR | Q = diag(40, 5, 150, 60), R = 1, applied ×2; K ≈ [51.7, 7.24, -10.8, -12.1] after IDENTIFY | [Math/Single 4](Math/Single/04_lqr.md) |
| Balance-only scripts LQR | Q = diag(5, 5, 5, 5), R = 1, ×2; K = [35.5, 6.27, -2.06, -4.29] | `PythonMaster.py`, `PythonMaster_auto.py` |
| Kalman | Q_N = 0.5 I4, R_N = 0.01 I2 | script line 230 |
| Swing-up | accel 6 m/s², speed 0.6 m/s, energy gain 4, target 1.03 (adapts 0.97-1.30) | [Math/Single 7.9](Math/Single/07_swing_up.md#79-every-swing-up-constant) |
| Catch window | 0.30 rad, 3.5 rad/s, e 0.95-1.15, cart < 0.12 m | same |
| Cart limits | LQG gives up at 0.22 m, soft stop 0.30 m; LQG clips 0.8 m/s, 15 m/s² | same |

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
~~106.6 g, CoM 46.1 mm from pivot, Izz about pivot 5.99e-4 kg m^2. Do not use for control; it does not match the rig. Weigh the real arm.~~ Superseded 2026-10-29 by [new arms model session](sessions/2026/10/2026-10-29_1559_Barney_new-arms-model.md): that estimate came from photos only.

## New arms mass properties (STLs + measured weights, 2026-10-29)
~~First version (pivot wrongly placed at the hub): arm 1 98.1 g, CoM 52.2 mm, Izz 6.07e-4 kg m², period 0.691 s; arm 2 107.1 g, 66.3 mm, 1.069e-3; link 1 with joint-2 shaft in its tip 124.6 g, 83.6 mm, 1.668e-3.~~ Superseded 2026-10-29 17:21 UTC by Barney's correction in the [same session](sessions/2026/10/2026-10-29_1559_Barney_new-arms-model.md): each arm pivots on its small Ø8 hole; the hub electronics measure the next joint.

Model from the team STLs and Barney's weights; LiPo (14 g) and MT6701 board (1.5 g) assumed. Frame: origin on the arm's own pivot (small Ø8 hole), x toward the hub (down when hanging). Link 1 = arm 1 with its hub parts (cart shaft on the axis, left out). Link 2 = arm 2 with its hub parts plus the joint-2 shaft (8x100, 39.2 g), collar, magnet and arm 1's bearing inner ring, because that shaft is clamped in arm 2's small hole.

| Body | Mass | CoM from own pivot | Izz about pivot | Izz about CoM | Hanging period |
| --- | --- | --- | --- | --- | --- |
| Arm 1 alone = link 1 (200 mm) | 98.1 g | 147.8 mm | 2.484e-3 kg m² | 3.40e-4 kg m² | 0.830 s |
| Arm 1 with joint-2 shaft parts in its hub, no arm 2 | 148.1 g | 165.4 mm | 4.482e-3 kg m² | 4.31e-4 kg m² | 0.858 s |
| Arm 2 alone (250 mm, same mounts, arm mass scaled by volume, no shaft in its hub) | 111.9 g | 186.5 mm | 4.506e-3 kg m² | 6.17e-4 kg m² | |
| Link 2 = arm 2 + joint-2 shaft parts | 161.8 g | 128.9 mm | 4.507e-3 kg m² | 1.818e-3 kg m² | |

Ratios ([Math/Double 1.5](Math/Double/01_variables.md#15-the-ratios-what-the-scripts-and-system-id-really-use) definitions) [?]:
| Set | P1 | P2 | J2r | H |
| --- | --- | --- | --- | --- |
| Model, new arm 1 + new arm 2 | 5.233 | 2.329 | 0.503 | 0.466 |
| Model new arm 1 + team's arm 2 constants (0.210 kg, 0.106 m, 0.00197564 kg m²) | 5.192 | 2.045 | 0.398 | 0.409 |

Rig check: single IDENTIFY period 0.84-0.89 s [HW] vs 0.830 s (shaft out) / 0.858 s (shaft in) here. Source: `build_arms_v3.py` in the [viewer](https://claude.ai/artifact/8SnLwfoxa9DyULJxHKt21b) download and `/mnt/project-files/NewArmModel_v2/` (Claude project).
