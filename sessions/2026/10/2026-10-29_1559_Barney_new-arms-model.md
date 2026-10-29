---
type: session
date: 2026-10-29
time: 15:59 (UTC)
member: Barney
ai: Claude (claude.ai project thread "Build 3D model of new arm")
topics: [arms-and-model]
status: done
pages_applied: yes
transcript: transcripts/2026/10/2026-10-29_1559_Barney_new-arms-model.md
---
# 3D model and mass properties of the new arms from the team's STLs

## Goal
Accurate 3D model of the new arms with calculated mass, centre of mass and inertia, viewable 360° and downloadable.

## What happened
- Barney sent the mechanical team's files (OneDrive zip: 10 STLs, `arm_1.stp`, drawing `arm_1.pdf` dated 2026-10-25 by Vecter Fang) and measured weights (`Arm_phy_dataSheet1.csv`).
- Placed every printed part by matching its bolt pattern to the arm holes (STL slices). Modelled the purchased parts (608, 8x100 shaft, collar, magnet, XIAO, MT6701 board, LP653042, screws, wires, zip ties, switch).
- Published the viewer: [New Pendulum Arms](https://claude.ai/artifact/8SnLwfoxa9DyULJxHKt21b) (arm 1, arm 2, double layout, mass table, MuJoCo MJCF, zip download). Files also in the Claude project at `/mnt/project-files/NewArmModel_v2/` (GLB, STLs per part, `mass_properties.json`, `new_arms_double.xml`, `arm1_single.xml`, `build_arms_v2.py`).

## Findings
- Arm 1 alone (turning parts): 98.1 g, CoM 52.2 mm from hinge, Izz hinge 6.07e-4 kg m², Izz CoM 3.40e-4 kg m², predicted hanging period 0.691 s [?].
- Arm 2 alone (same mounts, arm mass scaled by volume): 107.1 g, CoM 66.3 mm, Izz hinge 1.069e-3 kg m² [?].
- Double link 1 incl. assumed joint-2 shaft 8x40, collar, magnet in arm 1's tip: 124.6 g, CoM 83.6 mm, Izz hinge 1.668e-3 kg m² [HYP layout].
- Printed arm_1 is 54 % of solid PLA (34.5 g vs 51.45 cm³ STL). The small mounts weigh ~100 % solid (holder 7.1 g measured = 7.1 g solid; sensor mount 5.2 = 5.2; battery case 7.8 vs 8.0).
- The 608 sits in the shaft holder's Ø22 seat (holder z 8-15, Ø20 retaining lip), matching the photos; the arm's own Ø22 pocket plus the holder's Ø23 bore leave a cavity for the shaft collar.
- Hole map (from the hinge): hub 6x on Ø32 (holder uses ±30°/±150°, sensor mount 0°/180°); arm 1 holes at 22, 30, 58, 75 mm; arm 2 at 22, 30, 58, 82 mm. ESP32 mount uses 30 and 58.
- arm_1_3dp.stl is a solid bar; the 2026-10-25 drawing shows a truss version.
- Conflict: predicted 0.691 s vs rig IDENTIFY 0.84-0.89 s. Unknown whether those runs used new arm 1 alone. Matching 0.86 s with this model needs about 100 g extra at the tip.

## Dead ends
- None.

## Decisions
- Kept decision 0003 (fitted ratios) as is; noted that its revisit trigger is now met.

## Changed
- Code: none in team repos. Model scripts `build_arms_v2.py`, `package_v2.py` in the viewer zip and `/mnt/project-files/NewArmModel_v2/`.
- Firmware flashed: none. Wiring or hardware: none. Run logs: none.

## Open questions and next steps
- Time 10 swings of arm 1 alone on its shaft (model: 6.91 s) and balance it on a pencil (model: 52 mm). Open question 10.
- Weigh the LiPo and the MT6701 board.
- Battery case hole spacing mismatch on arm 1 (open question 11); LiPo still on arm 1? solid vs truss arm? (12); double layout spacing and joint-2 shaft length (13).
- Compare the STL-based link parameters with the fitted double ratios once the ratio definitions are confirmed.

## Proposed page updates
Applied: params.md, subsystems/arms-and-model.md, open-questions.md (8 answered; 10-13 added), hardware-state.md, decisions/0003, BRIEF.md.
