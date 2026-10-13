#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
pg_dump --format=custom --file="backups/luxury_stock_$(date +%Y%m%d_%H%M%S).dump" "${DATABASE_URL:?DATABASE_URL must be set}"
