#!/usr/bin/env python3
import argparse
import subprocess
import csv
from datetime import datetime

FANOUT_VALUES = [12, 20, 30, 40, 50, 60, 80, 100]


def run_pgbench(db, sql_file, n_users, follows_per_user, clients, duration, progress, extra_args):
    cmd = [
        "pgbench", "-n", "-M", "prepared",
        "-f", sql_file,
        "-c", str(clients),
        "-T", str(duration),
        "-P", str(progress),
        "-d", db,
        f"-D", f"n_users={n_users}",
        f"-D", f"follows_per_user={follows_per_user}",
    ] + extra_args
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = proc.stdout
    tps = None
    lat_avg = None
    for line in out.splitlines():
        if tps is None and "tps =" in line:
            try:
                tps = float(line.split("tps =")[-1].split()[0])
            except Exception:
                pass
        if lat_avg is None and "latency average" in line:
            try:
                lat_avg = float(line.split("latency average =")[-1].split()[0])
            except Exception:
                pass
    return tps, lat_avg, out

# Ajout : fonction pour réinitialiser la base et charger les données
def reset_and_load_db(db, n_users, follows_per_user, posts_per_user=10):
    # 1. Réinitialiser le schéma
    subprocess.run([
        "psql", db, "-f", "schema.sql"
    ], check=True)
    # 2. Charger les données avec les bons paramètres
    load_cmd = [
        "psql", db, "-v", f"n_users={n_users}", "-v", f"follows_per_user={follows_per_user}", "-v", f"posts_per_user={posts_per_user}", "-f", "load.sql"
    ]
    subprocess.run(load_cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Benchmark en faisant varier le fanout (follows_per_user)")
    parser.add_argument("--db", default="tinyinsta", help="Nom de la base de données")
    parser.add_argument("--sql", default="load.sql", help="Fichier SQL à utiliser")
    parser.add_argument("--n-users", type=int, default=8, help="Nombre d'utilisateurs (const)")
    parser.add_argument("--clients", type=int, default=8, help="Nombre de clients pgbench")
    parser.add_argument("--duration", type=int, default=30, help="Durée de chaque run (s)")
    parser.add_argument("--progress", type=int, default=5, help="Période de progress pgbench (s)")
    parser.add_argument("--runs", type=int, default=1, help="Nombre de répétitions par valeur de fanout")
    parser.add_argument("--csv", default=None, help="Chemin du CSV de sortie")
    parser.add_argument("--extra", default="", help="Args supplémentaires pour pgbench")
    parser.add_argument("--fanout", default=None, help="Liste de fanouts à tester, ex: 12,20,30")
    args = parser.parse_args()

    fanouts = [int(x) for x in args.fanout.split(",")] if args.fanout else FANOUT_VALUES
    extra_args = args.extra.split() if args.extra.strip() else []
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    csv_path = args.csv or f"results_fanout_{ts}.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["fanout", "run", "tps", "latency_ms", "cmd"])
        writer.writeheader()
        for fanout in fanouts:
            for run in range(1, args.runs+1):
                print(f"[INFO] Reset DB et chargement données pour fanout={fanout}")
                reset_and_load_db(args.db, args.n_users, fanout)
                tps, lat, out = run_pgbench(
                    args.db, args.sql, args.n_users, fanout, args.clients, args.duration, args.progress, extra_args
                )
                cmd = f"pgbench ... -D n_users={args.n_users} -D follows_per_user={fanout} ..."
                writer.writerow({"fanout": fanout, "run": run, "tps": tps, "latency_ms": lat, "cmd": cmd})
                print(f"fanout={fanout} run={run} TPS={tps} latency={lat}ms")
    print(f"CSV sauvegardé dans {csv_path}")

if __name__ == "__main__":
    main()
