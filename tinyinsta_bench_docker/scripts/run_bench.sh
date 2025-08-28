#!/usr/bin/env bash
set -euo pipefail

DB_URI="${DB_URI:-postgresql://postgres:postgres@db:5432/tinyinsta}"
SQL_FILE="${SQL_FILE:-timeline_limit.sql}"
N_USERS="${N_USERS:-10000}"
CLIENTS="${CLIENTS:-1,2,4,8,16,32}"
DURATION="${DURATION:-20}"
RUNS="${RUNS:-2}"
EXTRA="${EXTRA:--r}"

python3 bench.py --db "$DB_URI" --sql "$SQL_FILE" --n-users "$N_USERS"   --clients "$CLIENTS" --duration "$DURATION" --runs "$RUNS" --extra "$EXTRA"
