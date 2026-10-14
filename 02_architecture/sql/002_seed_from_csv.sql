-- Chargement des données brutes. À lancer depuis la racine du projet avec psql :
--   psql "$DATABASE_URL" -f 02_architecture/sql/002_seed_from_csv.sql
-- Un échec sur une ligne annule tout le chargement (transaction).
-- Les lignes non conformes sont traitées par le pipeline Python (quarantaine) ;
-- ce script suppose des CSV déjà valides.
\set ON_ERROR_STOP on
SET search_path TO luxury_stock;

BEGIN;
\copy dim_product FROM 'data/raw/products.csv' WITH (FORMAT csv, HEADER true);
\copy dim_calendar FROM 'data/raw/calendar.csv' WITH (FORMAT csv, HEADER true);
\copy fact_sales_weekly FROM 'data/raw/sales_weekly.csv' WITH (FORMAT csv, HEADER true);
\copy fact_inventory_weekly FROM 'data/raw/inventory_weekly.csv' WITH (FORMAT csv, HEADER true);
COMMIT;
