# Base de données

## Démarrage immédiat

La base `luxury_stock.sqlite` peut être ouverte avec SQLite, DuckDB, Python ou un outil graphique.

Exemple :

```bash
sqlite3 database/luxury_stock.sqlite
.tables
SELECT COUNT(*) FROM fact_sales_weekly;
SELECT * FROM vw_sales_train LIMIT 5;
```

## PostgreSQL

Depuis la racine du projet :

```bash
createdb luxury_stock
psql -d luxury_stock -f 02_architecture/sql/001_schema.sql
psql -d luxury_stock -f 02_architecture/sql/002_seed_from_csv.sql
psql -d luxury_stock -f 02_architecture/sql/003_quality_checks.sql
```

Le schéma PostgreSQL est `luxury_stock`.
