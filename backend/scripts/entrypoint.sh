#!/bin/bash
# Docker entrypoint for MuMuAINovel.
# Waits for PostgreSQL, runs Alembic migrations, then starts Uvicorn.

set -e

if [ -z "$APP_VERSION" ]; then
    if [ -f "/app/.env.example" ]; then
        APP_VERSION=$(grep "^APP_VERSION=" /app/.env.example | cut -d '=' -f2)
    fi
    APP_VERSION="${APP_VERSION:-1.0.0}"
fi

if [ -z "$APP_NAME" ]; then
    if [ -f "/app/.env.example" ]; then
        APP_NAME=$(grep "^APP_NAME=" /app/.env.example | cut -d '=' -f2)
    fi
    APP_NAME="${APP_NAME:-MuMuAINovel}"
fi

BUILD_TIME=$(date '+%Y-%m-%d %H:%M:%S')
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${POSTGRES_USER:-mumuai}"
DB_NAME="${POSTGRES_DB:-mumuai_novel}"

echo "================================================"
echo "Starting ${APP_NAME}"
echo "Version: v${APP_VERSION}"
echo "Started at: ${BUILD_TIME}"
echo "PGDATA: ${PGDATA:-<unset>}"
echo "DB target: ${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo "DATABASE_URL: ${DATABASE_URL:-<unset>}"
echo "================================================"

echo "Waiting for database socket..."
MAX_RETRIES=30
RETRY_COUNT=0

while ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Database connection timeout after ${MAX_RETRIES} attempts"
        exit 1
    fi
    echo "Database not ready yet (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 1
done

echo "Database socket is reachable"
echo "Waiting for PostgreSQL to accept SQL..."
sleep 3

if ! PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    echo "Initial SQL probe failed, waiting 5 more seconds..."
    sleep 5
fi

echo "PostgreSQL is ready"

echo "================================================"
echo "Running Alembic migrations..."
echo "================================================"

cd /app
alembic upgrade head

echo "Alembic migrations completed"
echo "================================================"
echo "Starting Uvicorn..."
echo "================================================"

exec uvicorn app.main:app \
    --host "${APP_HOST:-0.0.0.0}" \
    --port "${APP_PORT:-8000}" \
    --log-level info \
    --access-log \
    --use-colors
