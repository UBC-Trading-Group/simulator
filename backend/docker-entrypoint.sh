#!/bin/bash
set -euo pipefail

echo "[entrypoint] starting container bootstrap..."

if [[ "${RUN_DB_MIGRATIONS:-true}" == "true" ]]; then
  echo "[entrypoint] running alembic migrations"
  uv run alembic upgrade head
else
  echo "[entrypoint] skipping alembic migrations (RUN_DB_MIGRATIONS=${RUN_DB_MIGRATIONS:-false})"
fi

if [[ "${RUN_DB_SEED:-true}" == "true" ]]; then
  echo "[entrypoint] seeding reference tables"
  uv run python scripts/populate_tables.py
  uv run python scripts/init_db.py
else
  echo "[entrypoint] skipping data seed (RUN_DB_SEED=${RUN_DB_SEED:-false})"
fi

echo "[entrypoint] launching application: $*"
exec "$@"

