#!/bin/bash
set -e

DB=postgres
USER=postgres
PASS=postgres
COORD_PORT=5432

PGPASSWORD=$PASS psql -h localhost -p $COORD_PORT -U $USER -d $DB -c "CREATE DATABASE tinyinsta;" || true

for WORKER in worker1 worker2; do
  docker exec -e PGPASSWORD=$PASS -u $USER $(basename $PWD)-coordinator-1 psql -h $WORKER -U $USER -d $DB -c "CREATE DATABASE tinyinsta;" || true
done

for WORKER in worker1 worker2; do
  docker exec -e PGPASSWORD=$PASS -u $USER $(basename $PWD)-coordinator-1 psql -h $WORKER -U $USER -d tinyinsta -c "CREATE EXTENSION citus;" || true
done

PGPASSWORD=$PASS psql -h localhost -p $COORD_PORT -U $USER -d tinyinsta -c "CREATE EXTENSION IF NOT EXISTS citus;"
PGPASSWORD=$PASS psql -h localhost -p $COORD_PORT -U $USER -d tinyinsta -c "SELECT * FROM master_add_node('worker1', 5432);"
PGPASSWORD=$PASS psql -h localhost -p $COORD_PORT -U $USER -d tinyinsta -c "SELECT * FROM master_add_node('worker2', 5432);"

PGPASSWORD=$PASS psql -h localhost -p $COORD_PORT -U $USER -d tinyinsta -f ../schema.sql
PGPASSWORD=$PASS psql -h localhost -p $COORD_PORT -U $USER -d tinyinsta -f ../load.sql

echo "Cluster Citus initialisé et base tinyinsta peuplée !"