#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser(description="Plot throughput and latency vs clients from CSV.")
    ap.add_argument("csv", help="CSV produced by bench.py")
    ap.add_argument("--out-prefix", default="plot", help="Prefix for output PNGs")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    # aggregate by clients (mean over runs)
    g = df.groupby("clients").agg(tps=("tps","mean"), latency_ms=("latency_ms","mean")).reset_index()

    # Throughput plot
    plt.figure()
    plt.plot(g["clients"], g["tps"], marker="o")
    plt.xlabel("Clients")
    plt.ylabel("TPS")
    plt.title("Throughput vs Clients")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{args.out_prefix}_throughput.png", dpi=160)

    # Latency plot
    plt.figure()
    plt.plot(g["clients"], g["latency_ms"], marker="o")
    plt.xlabel("Clients")
    plt.ylabel("Latency (ms)")
    plt.title("Latency vs Clients")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{args.out_prefix}_latency.png", dpi=160)

    print(f"Wrote {args.out_prefix}_throughput.png and {args.out_prefix}_latency.png")

if __name__ == "__main__":
    main()
