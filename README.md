# TinyInsta Benchmark

This is a minimal benchmark for a tiny Instagram-like schema in PostgreSQL.

## Setup

1. Create a database:

```bash
createdb tinyinsta
```

2. Load schema:

```bash
psql tinyinsta -f schema.sql
```

3. Load data (adjust variables inside load.sql):

```bash
psql tinyinsta -f load.sql
```

## Run Benchmarks

- Timeline query (full feed):

```bash
pgbench -n -M prepared -f timeline.sql -c 16 -T 30 -P 5 -d tinyinsta -D n_users=10000
```

- Timeline with LIMIT 50 (more realistic):

```bash
pgbench -n -M prepared -f timeline_limit.sql -c 16 -T 30 -P 5 -d tinyinsta -D n_users=10000
```

- Insert posts (write throughput):

```bash
pgbench -n -M prepared -f insert_post.sql -c 16 -T 30 -P 5 -d tinyinsta -D n_users=10000
```

## Notes

- Adjust `n_users`, `posts_per_user`, and `follows_per_user` in `load.sql`.
- Use `-c 1,2,4,8,16,32` to sweep client concurrency and observe throughput scaling.
- Ensure PostgreSQL has enough `work_mem` for sorts.

## Auto sweep + CSV + plots

Two helper scripts are included:

- `bench.py` — run a sweep over client counts and export a CSV
- `plot.py`  — generate simple PNG charts from the CSV

### Example: sweep timeline with LIMIT 50

```bash
# run with 1,2,4,8,16,32 clients for 20s each, twice
python3 bench.py --db tinyinsta --sql timeline_limit.sql --n-users 10000 \
  --clients 1,2,4,8,16,32 --duration 20 --runs 2 --extra "-r"
# -> produces results_timeline_limit_YYYYmmdd-HHMMSS.csv

# plot the CSV
python3 plot.py results_timeline_limit_*.csv --out-prefix timeline_limit
# -> timeline_limit_throughput.png + timeline_limit_latency.png
```

> Notes
> - Requires `pgbench` in PATH and Python packages: `pandas`, `matplotlib` for plotting (`pip install pandas matplotlib`).
> - Use `--extra "-r"` to get pgbench per-statement latency reports included in output (optional).
