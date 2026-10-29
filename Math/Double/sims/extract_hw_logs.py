"""Make the compact rig-data files in ../data from the full double-pendulum run logs.

The full logs are on the `logs` branch of etwan007/ENGT480 (raspberrypi-c8674ffe/Code/DoublePendulum/run_logs/).
A cheap way to get them:
    git clone --filter=blob:none --no-checkout --single-branch -b logs https://github.com/etwan007/ENGT480 logs
    cd logs && git show HEAD:raspberrypi-c8674ffe/Code/DoublePendulum/run_logs/<file> > <file>
Run:  python extract_hw_logs.py <folder with the run_logs CSVs>

Writes
  ../data/hw_double_events.csv                         every config/swing/abort/catch/lost/fault event, all runs
  ../data/hw_double_attempts.csv                       one row per swing-up attempt (where and why it stopped)
  ../data/hw_double_balance_20261021_161621_10hz.csv   the 767 s balance run, every 10th sample
  ../data/hw_double_swingup_20261027_184605.csv        the SWING phases of a 5-attempt run, every sample
"""
import csv
import glob
import gzip
import json
import math
import os
import re
import sys

csv.field_size_limit(10**9)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SRC = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(DATA, exist_ok=True)


def rows(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", newline="") as fh:
        r = csv.reader(fh)
        hdr = next(r)
        for row in r:
            if row:
                yield dict(zip(hdr, row))


def short(v, digits=5):
    """Round a numeric CSV field to keep the extracts small."""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return v
    return f"{x:.{digits}g}"


def f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return math.nan


files = sorted(glob.glob(os.path.join(SRC, "*_double_*.csv*")))
events, attempts = [], []
for path in files:
    name = os.path.basename(path).replace(".csv.gz", "").replace(".csv", "")
    script, plan = "", ""
    cur = None
    for r in rows(path):
        rt = r["record_type"]
        if rt == "config":
            try:
                c = json.loads(r["message"])
                script = c.get("script", "")
                tr = c.get("trajectory") or {}
                plan = json.dumps({"made": tr.get("made"), "limits": tr.get("limits"), "ratios": c.get("model_ratios")},
                                  separators=(",", ":"))
            except ValueError:
                pass
            events.append((name, script, rt, r["elapsed_s"], plan))
        elif rt == "sample":
            if cur is not None:
                m = re.search(r"mode=(\w+); k=(\d+)", r["message"])
                if m and m.group(1) == "SWING":
                    k = int(m.group(2))
                    v = f(r["cart_velocity_command_m_s"])
                    cur["k_last"] = k
                    cur["max_abs_v_cmd"] = max(cur["max_abs_v_cmd"], abs(v))
                    cur["max_abs_cart_m"] = max(cur["max_abs_cart_m"], abs(f(r["cart_m"])))
                    tm = f(r["motor_timer_command"])      # what the Arduino really runs: 125000/(|timer|+1) steps/s
                    if not math.isnan(tm) and abs(tm) < 65535:
                        cur["max_abs_v_sent"] = max(cur["max_abs_v_sent"], 125000.0 / (abs(tm) + 1) * 0.638175 / 6400)
        else:
            events.append((name, script, rt, r["elapsed_s"], r["message"][:200]))
            if rt == "swing":
                cur = dict(run=name, attempt=r["message"], t_start=f(r["elapsed_s"]), k_last=0, max_abs_v_cmd=0.0,
                           max_abs_v_sent=0.0, max_abs_cart_m=0.0, result="", detail="")
                attempts.append(cur)
            elif rt in ("abort", "catch", "fault", "stop") and cur is not None and not cur["result"]:
                cur["result"] = rt
                cur["detail"] = r["message"][:120]
                cur = None

with open(os.path.join(DATA, "hw_double_events.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["run", "script", "event", "elapsed_s", "message"])
    w.writerows(events)
with open(os.path.join(DATA, "hw_double_attempts.csv"), "w", newline="") as fh:
    keys = ["run", "attempt", "t_start", "k_last", "result", "max_abs_v_cmd", "max_abs_v_sent", "max_abs_cart_m", "detail"]
    w = csv.DictWriter(fh, fieldnames=keys)
    w.writeheader()
    for a in attempts:
        w.writerow({k: (round(a[k], 4) if isinstance(a[k], float) else a[k]) for k in keys})
print(f"{len(events)} events, {len(attempts)} swing-up attempts")

# ---- long balance run, decimated
BAL = os.path.join(SRC, "balance_double_20261021_161621_899189.csv.gz")
if os.path.exists(BAL):
    cols = ["elapsed_s", "measured_angle_1_deg", "measured_angle_2_deg", "joint_angle_2_deg", "cart_m",
            "est_theta1_rate_rad_s", "est_theta2_rate_rad_s", "force_command_n", "cart_velocity_command_m_s",
            "reference_upright_1_counts", "reference_aligned_2_counts"]
    n = 0
    with open(os.path.join(DATA, "hw_double_balance_20261021_161621_10hz.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([c.replace("force_command_n", "accel_command_m_s2") for c in cols])
        for i, r in enumerate(x for x in rows(BAL) if x["record_type"] == "sample"):
            if i % 10 == 0:
                w.writerow([short(r[c], 7 if c == "elapsed_s" else 5) for c in cols])
                n += 1
    print("balance rows", n)

# ---- swing-up run, SWING phases only (plus 0.3 s after each abort)
SW = os.path.join(SRC, "swingup_double_20261027_184605_859262.csv")
if os.path.exists(SW):
    cols = ["elapsed_s", "message", "measured_angle_1_rad", "measured_angle_2_rad", "est_theta1_rad",
            "est_theta1_rate_rad_s", "est_theta2_rad", "est_theta2_rate_rad_s", "cart_m", "previous_force_n",
            "force_command_n", "cart_velocity_command_m_s", "step_frequency_hz", "motor_timer_command"]
    out = []
    tail = 0
    for r in rows(SW):
        if r["record_type"] != "sample":
            continue
        swing = "mode=SWING" in r["message"]
        if swing:
            tail = 30
        if swing or tail > 0:
            out.append([r[c] if c == "message" else short(r[c], 7 if c == "elapsed_s" else 6) for c in cols])
            if not swing:
                tail -= 1
    with open(os.path.join(DATA, "hw_double_swingup_20261027_184605.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([c.replace("previous_force_n", "a_prev_m_s2").replace("force_command_n", "a_m_s2") for c in cols])
        w.writerows(out)
    print("swing rows", len(out))
