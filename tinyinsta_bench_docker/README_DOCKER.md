# TinyInsta Bench — Docker Compose

Bench minimal d'un schéma "Instagram-like" avec PostgreSQL + pgbench.

## Démarrage rapide

```bash
docker compose up -d db
docker compose run --rm bench ./scripts/init_db.sh

# Bench lecture (timeline LIMIT 50) avec export CSV
docker compose run --rm bench python3 bench.py --db postgresql://postgres:postgres@db:5432/tinyinsta   --sql timeline_limit.sql --n-users 10000 --clients 1,2,4,8,16,32 --duration 20 --runs 2 --extra "-r"

# Tracer les courbes
docker compose run --rm bench python3 plot.py results_timeline_limit_*.csv --out-prefix timeline_limit
```

## Raccourcis

```bash
# Sweep par défaut
docker compose run --rm bench ./scripts/run_bench.sh

# Personnaliser à la volée
docker compose run --rm -e CLIENTS=1,2,4,8,16,32,64 -e DURATION=30 bench ./scripts/run_bench.sh
``

## Paramètres importants

- Dataset (dans `load.sql`) : `n_users`, `posts_per_user`, `follows_per_user`.
- Index clés : `post(user_id, created_at DESC)` et `follower_followee(follower_id, followee_id)`.
- Ajouter `LIMIT 50` dans les requêtes de timeline pour simuler une UI (déjà fourni via `timeline_limit.sql`).

## Connexion locale

- DB: `tinyinsta`, user/pass `postgres/postgres`.
- Port exposé : `localhost:5432`.
