# Transcript: new arms 3D model (2026-10-29, project content only, condensed)

**Barney:** Here are our new arms. Create a very accurate model and I want estimated/calculated center of mass and such. Give me a 3D model and allow me to open it up here as an artifact and 360 view and download it. (Attached: OneDrive zip with STLs, STEP, PDF drawing; Arm_phy_dataSheet1.csv with part weights.)

Weights CSV: arm_1_3dp 34.5 g; arm_shaft_holder 7.1 g; arm_sensor_mount 5.2 g; esp32-mount 4.8 g (with ESP32); battery mount 7.8 g; bearing 608 11.8 g; 8mm shaft lock 5.5 g ("wait new one"); shaft 39.2 g (100 mm).

**Claude:** Unpacked the files, sliced every STL to find hole patterns, assembled arm 1 and arm 2 with all mounts and purchased parts, and computed mass properties using the measured weights. Published the viewer https://claude.ai/artifact/8SnLwfoxa9DyULJxHKt21b with arm 1, arm 2 and an assumed double layout, plus a zip (GLB, STLs, mass table, MuJoCo MJCF, scripts).

Results: arm 1 alone 98.1 g, CoM 52.2 mm, Izz hinge 6.07e-4 kg m², hanging period 0.691 s; arm 2 alone 107.1 g, CoM 66.3 mm, Izz hinge 1.069e-3 kg m²; double link 1 with assumed joint-2 hardware 124.6 g, CoM 83.6 mm, Izz hinge 1.668e-3 kg m². Least certain: LiPo and encoder board (not weighed), battery case position on arm 1 (holes do not line up), double layout. The predicted 0.691 s period disagrees with the rig's 0.84-0.89 s IDENTIFY; which arm those runs used is unknown.
