#!/usr/bin/env bash
set -euo pipefail

DB_URI="${DB_URI:-postgresql://postgres:postgres@db:5432/tinyinsta}"

echo "Waiting for db..."
until pg_isready -h db -p 5432 -U postgres -d tinyinsta >/dev/null 2>&1; do
  sleep 1
done
echo "DB is ready."

echo "Applying schema.sql ..."
psql "$DB_URI" -f schema.sql

echo "Loading data (this can take a bit)..."
psql "$DB_URI" -f load.sql

echo "Done."
