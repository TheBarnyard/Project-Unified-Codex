---
updated: 2026-10-29
updated_by: Ryan (Claude, math-folder session)
---
# Raspberry Pi control

A Raspberry Pi 4 runs the controllers in Python (`~/PythonLibraries/bin/python`): LQG = Kalman filter + LQR.

| Script | Purpose |
| --- | --- |
| `Code/CommunicationTest.py` | Link test (6-byte format) |
| `Code/SinglePendulum/PythonMaster.py` | Single balance (6-byte format) |
| `Code/SinglePendulum/PythonMaster_autocalibrate.py` | Single balance with auto-calibration (protocol v1) |
| `Code/SinglePendulum/PythonMasterSwingUpExp.py`, `swingup_control.py` | Single swing-up (earlier version) |
| `LegacyPi/Code/SinglePendulum/PythonMasterUpExpClaudeImproved.py` (ENGT480 `experiment/legacy-pi-recovery`) | Best single swing-up + LQG balance (Barney, 2026-10-29). Explained in [Math/Single](../Math/Single/README.md) |
| `Code/DoublePendulum/PythonMasterMath2.py` | Offline double-pendulum gains (`control_matrices2.txt`, `symbolic_model2.pkl`) |
| `Code/DoublePendulum/PythonMasterControl2.py`, `_autocalibrate.py` | Double balance |
| `PythonMaster2_auto_improved.py` | Double balance, 12.8 min record (2026-10-21). [?] which repo or branch |
| `run_csv_logger.py` | Per-run CSV logging (radio age, status, sequence, serial counters) |
| `Code/RunReview/balancing_visualizer.html` | Browser run replay |

Run logs go to `run_logs/` and are uploaded to the ENGT480 `logs` branch. See [repos and Pi workflow](repos-and-pi-workflow.md).

Planned: one launcher `Code/Launcher/pendulum.py` with TOML rig, arm and preset files and gains computed at startup. Design only ([design doc](https://claude.ai/artifact/HV6HEKrSekYexco3ES9HhB)).
