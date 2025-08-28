#!/usr/bin/env python3
import argparse
import csv
import os
import re
import subprocess
from datetime import datetime

TPS_RE = re.compile(r"tps\s*=\s*([0-9]+(?:\.[0-9]+)?)")
LAT_AVG_RE = re.compile(r"latency average\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*ms")
LAT_STD_RE = re.compile(r"latency stddev\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*ms")
FAIL_RE = re.compile(r"\b(errors|serialization failures|deadlocks)\b.*?:\s*([0-9]+)", re.IGNORECASE)

def run_pgbench(db, sql_file, n_users, clients, duration, progress, extra_args):
    cmd = [
        "pgbench", "-n", "-M", "prepared",
        "-f", sql_file,
        "-c", str(clients),
        "-T", str(duration),
        "-P", str(progress),
        "-d", db,
        "-D", f"n_users={n_users}",
    ] + extra_args
    env = os.environ.copy()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = proc.stdout
    # parse metrics
    tps = None
    lat_avg = None
    lat_std = None
    errors = 0
    for line in out.splitlines():
        if tps is None:
            m = TPS_RE.search(line)
            if m:
                tps = float(m.group(1))
        if lat_avg is None:
            m = LAT_AVG_RE.search(line)
            if m:
                lat_avg = float(m.group(1))
        if lat_std is None:
            m = LAT_STD_RE.search(line)
            if m:
                lat_std = float(m.group(1))
        m = FAIL_RE.search(line)
        if m:
            try:
                errors += int(m.group(2))
            except:
                pass
    return {
        "stdout": out,
        "tps": tps,
        "latency_ms": lat_avg,
        "latency_std_ms": lat_std,
        "errors": errors,
        "returncode": proc.returncode,
        "cmd": " ".join(cmd),
    }

def main():
    ap = argparse.ArgumentParser(description="Sweep pgbench concurrency and export CSV.")
    ap.add_argument("--db", default="tinyinsta", help="Database name / connstring (default: tinyinsta)")
    ap.add_argument("--sql", default="timeline.sql", help="SQL file to benchmark (default: timeline.sql)")
    ap.add_argument("--n-users", type=int, default=10000, help="Value for -D n_users (default: 10000)")
    ap.add_argument("--clients", default="1,2,4,8,16,32", help="Comma-separated list of client counts")
    ap.add_argument("--duration", type=int, default=30, help="Duration per run in seconds (default: 30)")
    ap.add_argument("--progress", type=int, default=5, help="pgbench progress period in seconds (default: 5)")
    ap.add_argument("--runs", type=int, default=1, help="Repeat each client setting N times (default: 1)")
    ap.add_argument("--csv", default=None, help="Output CSV path (default: auto)")
    ap.add_argument("--extra", default="", help='Extra args to pass to pgbench, e.g. "-r"')

    args = ap.parse_args()

    client_list = [int(x.strip()) for x in args.clients.split(",") if x.strip()]
    extra_args = args.extra.split() if args.extra.strip() else []

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    if args.csv:
        csv_path = args.csv
    else:
        base = os.path.splitext(os.path.basename(args.sql))[0]
        csv_path = f"results_{base}_{ts}.csv"

    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)

    fieldnames = [
        "timestamp","sql_file","n_users","clients","duration_s",
        "run_index","tps","latency_ms","latency_std_ms","errors","returncode","cmd"
    ]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for c in client_list:
            for r in range(1, args.runs+1):
                res = run_pgbench(args.db, args.sql, args.n_users, c, args.duration, args.progress, extra_args)
                row = {
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "sql_file": args.sql,
                    "n_users": args.n_users,
                    "clients": c,
                    "duration_s": args.duration,
                    "run_index": r,
                    "tps": res["tps"],
                    "latency_ms": res["latency_ms"],
                    "latency_std_ms": res["latency_std_ms"],
                    "errors": res["errors"],
                    "returncode": res["returncode"],
                    "cmd": res["cmd"],
                }
                w.writerow(row)
                print(f"[clients={c} run={r}] TPS={res['tps']} latency={res['latency_ms']} ms errors={res['errors']}")

    print(f"CSV saved to: {csv_path}")
    print("Done. Tip: plot with the provided plot script or your favorite tool.")

if __name__ == "__main__":
    main()
