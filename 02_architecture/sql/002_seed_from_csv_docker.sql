-- Chargement utilisé par Docker Compose (monté sous le nom 002_seed_from_csv.sql
-- dans /docker-entrypoint-initdb.d). Le dossier data/ du projet est monté sur /data.
-- Exécuté une seule fois, à la création du volume PostgreSQL : après une
-- régénération des données, lancer `docker compose down -v` pour recharger.
\set ON_ERROR_STOP on
SET search_path TO luxury_stock;

BEGIN;
\copy dim_product FROM '/data/raw/products.csv' WITH (FORMAT csv, HEADER true);
\copy dim_calendar FROM '/data/raw/calendar.csv' WITH (FORMAT csv, HEADER true);
\copy fact_sales_weekly FROM '/data/raw/sales_weekly.csv' WITH (FORMAT csv, HEADER true);
\copy fact_inventory_weekly FROM '/data/raw/inventory_weekly.csv' WITH (FORMAT csv, HEADER true);
COMMIT;
