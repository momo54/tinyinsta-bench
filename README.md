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


## Utilisation avec Citus (sharding PostgreSQL)

### Installation et activation

1. Installer Citus (macOS/Homebrew) :
   ```sh
   brew install citus
   ```
2. Ajouter dans `postgresql.conf` :
   ```
   shared_preload_libraries = 'citus'
   ```
3. Redémarrer PostgreSQL :
   ```sh
   brew services restart postgresql
   ```
4. Activer l'extension dans la base :
   ```sql
   CREATE EXTENSION citus;
   ```

### Recharger le schéma et les données

```sh
psql -d tinyinsta -f schema.sql
psql -d tinyinsta -f load.sql
```

### Commandes utiles Citus

- Voir les tables distribuées et de référence :
  ```sql
  SELECT * FROM citus_tables;
  ```
- Voir la liste des shards :
  ```sql
  SELECT shardid, 'post_' || shardid AS shard_table FROM pg_dist_shard WHERE logicalrelid = 'post'::regclass;
  ```
- Voir le contenu d'un shard :
  ```sql
  SELECT * FROM post_XXXXX LIMIT 10;  -- Remplacer XXXXX par l'ID du shard
  ```
- Voir la répartition physique des shards :
  ```sql
  SELECT * FROM pg_dist_placement;
  ```

### Analyse de requête distribuée

- EXPLAIN sur une requête sharded :
  ```sql
  EXPLAIN SELECT * FROM post WHERE user_id = 1;
  ```
  (Citus n'interroge qu'un seul shard)

- EXPLAIN sur une requête fanout (timeline) :
  ```sql
  EXPLAIN SELECT p.* FROM post p WHERE p.user_id = 1 OR p.user_id IN (SELECT followee_id FROM follower_followee WHERE follower_id = 1) ORDER BY p.created_at DESC;
  ```
  (Citus parallélise sur tous les shards)

> Astuce : Pour réinitialiser les données sans recréer le schéma :
> ```sql
> TRUNCATE TABLE follower_followee, post, users RESTART IDENTITY CASCADE;
> ```

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
