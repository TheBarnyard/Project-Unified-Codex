---
type: decision
date: 2026-10-07
by: Barney
status: active
---
# Never edit original source files; work in copies

**Decision:** debugging or experimental changes go into a new file or sibling folder (for example `DebugReceiverMaster`, `FramedReceiverMaster`), never into the team's original sources such as `Receivermaster.ino`, `TX1.ino`, `TX2.ino`, `PythonMaster.py`, `PythonMasterControl2.py`, `ArduinoSlave.ino`.

**Why:** avoid losing working code.

**Applies to:** every AI working on the project.
