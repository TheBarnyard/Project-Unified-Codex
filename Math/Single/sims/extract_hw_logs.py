"""Pull the data the Math/Single pages plot out of real rig logs [HW].

Source: etwan007/ENGT480, branch `logs`, folder
raspberrypi-c8674ffe/Code/SinglePendulum/run_logs/ (legacy ENGT481 checkout on the Pi).
Every run whose config row says "swing_up_control": "identify_then_normalised_energy_pumping"
was made by PythonMasterUpExpClaude.py / PythonMasterUpExpClaudeImproved.py (byte-identical files).

Cheap way to get the logs (never fetch all branches):
  git clone --depth 1 --filter=blob:none --no-checkout --single-branch --branch logs https://github.com/etwan007/ENGT480 logs
  cd logs && git show HEAD:raspberrypi-c8674ffe/Code/SinglePendulum/run_logs/<name>.csv > <name>.csv

Run:  python extract_hw_logs.py <folder with balance_*.csv>
Writes ../data/hw_run_<name>.csv (one run, compact), ../data/hw_events.csv (all runs).
"""
import csv
import glob
import json
import os
import re
import sys

KEEP_RUN = "balance_20261016_160234_984214.csv"     # clean run: identify, one catch, 43 s balance
KEEP_RUN_2 = "balance_20261027_150517_941267.csv"   # longest run: 290 s, 11 catches, cart-limit drops
COLS = ["elapsed_s", "receiver_uptime_ms", "raw_angle_1", "upright_correction_counts", "measured_angle_rad",
        "cart_m", "est_angle_rad", "est_angle_rate_rad_s", "est_cart_m", "est_cart_velocity_m_s",
        "force_command_n", "step_frequency_hz", "motor_timer_command", "cycle_period_ms"]


def short(v):
    try:
        return f"{float(v):.6g}"
    except ValueError:
        return v


def parse_message(msg):
    out = {"mode": "", "energy_norm": "", "target": "", "accel": "", "vcmd": "", "offset_deg": ""}
    m = re.search(r"mode=(\w+)", msg)
    if m:
        out["mode"] = m.group(1)
    for key, pat in (("energy_norm", r"energy_norm=([-\d.]+)"), ("target", r"target=([-\d.]+)"),
                     ("accel", r"accel_m_s2=([-\d.]+)"), ("vcmd", r"cart_velocity_command_m_s=([-\d.]+)"),
                     ("offset_deg", r"upright_offset_deg=([-+\d.]+)")):
        m = re.search(pat, msg)
        if m:
            out[key] = m.group(1)
    return out


def main(folder):
    here = os.path.dirname(os.path.abspath(__file__))
    data = os.path.join(here, "..", "data")
    os.makedirs(data, exist_ok=True)
    events = []
    for path in sorted(glob.glob(os.path.join(folder, "balance_*.csv"))):
        name = os.path.basename(path)
        rows = list(csv.reader(open(path, newline="")))
        hdr = rows[0]
        cfg = None
        for r in rows[1:]:
            if r[0] == "config":
                cfg = json.loads([v for v in r if v][-1])
        if not cfg or cfg.get("swing_up_control") != "identify_then_normalised_energy_pumping":
            continue
        for r in rows[1:]:
            if r[0] in ("identify", "mode_switch", "fault", "stop"):
                events.append({"run": name, "type": r[0], "elapsed_s": r[1], "text": [v for v in r[2:] if v][-1]})
        if name in (KEEP_RUN, KEEP_RUN_2):
            idx = [hdr.index(c) for c in COLS]
            out = os.path.join(data, "hw_run_" + name)
            with open(out, "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(COLS + ["mode", "energy_norm", "target", "accel", "vcmd", "offset_deg"])
                for r in rows[1:]:
                    if r[0] != "sample":
                        continue
                    if name == KEEP_RUN_2 and float(r[1]) > 30.0:
                        break   # keep the file small; the events file covers the rest
                    p = parse_message(r[-1])
                    w.writerow([short(r[i]) for i in idx] + [p[k] for k in ("mode", "energy_norm", "target", "accel", "vcmd", "offset_deg")])
            print("wrote", out)
    with open(os.path.join(data, "hw_events.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["run", "type", "elapsed_s", "text"])
        w.writeheader()
        w.writerows(events)
    print("events:", len(events))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
