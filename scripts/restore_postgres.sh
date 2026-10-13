#!/usr/bin/env bash
set -euo pipefail
DUMP_FILE="${1:?Usage: restore_postgres.sh path/to/backup.dump}"
pg_restore --clean --if-exists --dbname="${DATABASE_URL:?DATABASE_URL must be set}" "$DUMP_FILE"
