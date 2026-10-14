-- Luxury Stock AI, schéma PostgreSQL (v1.0)
-- Source de vérité des colonnes : ce fichier. Le dictionnaire
-- 01_governance/data_dictionary.xlsx doit rester synchronisé
-- (contrôle automatique : tests/test_data_dictionary.py).
-- Convention : une colonne par ligne ; les contraintes de table commencent
-- par PRIMARY KEY ou CONSTRAINT, sur leur propre ligne.
\set ON_ERROR_STOP on

BEGIN;

CREATE SCHEMA IF NOT EXISTS luxury_stock;
SET search_path TO luxury_stock;

DROP VIEW IF EXISTS vw_latest_inventory;
DROP VIEW IF EXISTS vw_sales_test;
DROP VIEW IF EXISTS vw_sales_train;
DROP TABLE IF EXISTS fact_forecast_weekly, fact_inventory_weekly, fact_sales_weekly, dim_calendar, dim_product CASCADE;

CREATE TABLE dim_product (
    product_id VARCHAR(10) PRIMARY KEY CHECK (product_id ~ '^P[0-9]{3}$'),
    product_name TEXT NOT NULL CHECK (btrim(product_name) <> ''),
    category TEXT NOT NULL CHECK (btrim(category) <> ''),
    collection TEXT NOT NULL CHECK (btrim(collection) <> ''),
    material TEXT NOT NULL CHECK (btrim(material) <> ''),
    color TEXT NOT NULL CHECK (btrim(color) <> ''),
    unit_price_eur NUMERIC(12,2) NOT NULL CHECK (unit_price_eur > 0),
    base_weekly_demand NUMERIC(12,2) NOT NULL CHECK (base_weekly_demand >= 0),
    launch_date DATE NOT NULL,
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days > 0),
    minimum_stock_units INTEGER NOT NULL CHECK (minimum_stock_units >= 0),
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE dim_calendar (
    week_start DATE PRIMARY KEY,
    week_index INTEGER NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    iso_week INTEGER NOT NULL CHECK (iso_week BETWEEN 1 AND 53),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    season TEXT NOT NULL CHECK (btrim(season) <> ''),
    luxury_peak_flag BOOLEAN NOT NULL,
    dataset_split TEXT NOT NULL CHECK (dataset_split IN ('TRAIN','TEST'))
);

CREATE TABLE fact_sales_weekly (
    week_start DATE NOT NULL REFERENCES dim_calendar(week_start),
    product_id VARCHAR(10) NOT NULL REFERENCES dim_product(product_id),
    units_sold INTEGER NOT NULL CHECK (units_sold >= 0),
    returns_units INTEGER NOT NULL CHECK (returns_units >= 0),
    net_units_sold INTEGER NOT NULL CHECK (net_units_sold >= 0),
    revenue_eur NUMERIC(14,2) NOT NULL CHECK (revenue_eur >= 0),
    -- Liste fermée à ajouter quand les canaux sont arrêtés, par exemple :
    -- CHECK (channel IN ('boutique','ecommerce','wholesale'))
    channel TEXT NOT NULL CHECK (btrim(channel) <> ''),
    PRIMARY KEY (week_start, product_id)
);

CREATE TABLE fact_inventory_weekly (
    week_start DATE NOT NULL REFERENCES dim_calendar(week_start),
    product_id VARCHAR(10) NOT NULL REFERENCES dim_product(product_id),
    opening_stock_units INTEGER NOT NULL CHECK (opening_stock_units >= 0),
    inbound_units INTEGER NOT NULL CHECK (inbound_units >= 0),
    units_sold INTEGER NOT NULL CHECK (units_sold >= 0),
    closing_stock_units INTEGER NOT NULL CHECK (closing_stock_units >= 0),
    stockout_flag BOOLEAN NOT NULL,
    days_of_cover NUMERIC(12,2) NOT NULL CHECK (days_of_cover >= 0),
    PRIMARY KEY (week_start, product_id)
);

-- Prévisions : model_version, dataset_hash et run_id relient chaque prévision
-- à son modèle et à la version des données (traçabilité). forecast_lower et
-- forecast_upper portent un intervalle de prévision (facultatif).
CREATE TABLE fact_forecast_weekly (
    forecast_week_start DATE NOT NULL,
    product_id VARCHAR(10) NOT NULL REFERENCES dim_product(product_id),
    forecast_units NUMERIC(12,2) NOT NULL CHECK (forecast_units >= 0),
    model_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model_version TEXT,
    dataset_hash TEXT,
    run_id TEXT,
    forecast_lower NUMERIC(12,2),
    forecast_upper NUMERIC(12,2),
    PRIMARY KEY (forecast_week_start, product_id, model_name),
    CONSTRAINT ck_forecast_interval CHECK (
        (forecast_lower IS NULL OR forecast_lower <= forecast_units)
        AND (forecast_upper IS NULL OR forecast_units <= forecast_upper)
    )
);

-- La clé primaire (week_start, product_id) sert les accès par semaine ;
-- cet index sert les accès par produit.
CREATE INDEX idx_sales_product_week ON fact_sales_weekly(product_id, week_start);
CREATE INDEX idx_inventory_product_week ON fact_inventory_weekly(product_id, week_start);

CREATE VIEW vw_sales_train AS
SELECT s.* FROM fact_sales_weekly s
JOIN dim_calendar c USING (week_start)
WHERE c.dataset_split = 'TRAIN';

CREATE VIEW vw_sales_test AS
SELECT s.* FROM fact_sales_weekly s
JOIN dim_calendar c USING (week_start)
WHERE c.dataset_split = 'TEST';

-- Version portable (PostgreSQL et SQLite) : pas de DISTINCT ON.
CREATE VIEW vw_latest_inventory AS
SELECT i.*
FROM fact_inventory_weekly i
JOIN (
    SELECT product_id, MAX(week_start) AS week_start
    FROM fact_inventory_weekly
    GROUP BY product_id
) m USING (product_id, week_start);

COMMIT;
