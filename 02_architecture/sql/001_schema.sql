-- Luxury Stock AI, PostgreSQL schema
CREATE SCHEMA IF NOT EXISTS luxury_stock;
SET search_path TO luxury_stock;

DROP VIEW IF EXISTS vw_latest_inventory;
DROP VIEW IF EXISTS vw_sales_test;
DROP VIEW IF EXISTS vw_sales_train;
DROP TABLE IF EXISTS fact_forecast_weekly, fact_inventory_weekly, fact_sales_weekly, dim_calendar, dim_product CASCADE;

CREATE TABLE dim_product (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    collection TEXT NOT NULL,
    material TEXT NOT NULL,
    color TEXT NOT NULL,
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
    iso_week INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    season TEXT NOT NULL,
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
    channel TEXT NOT NULL,
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

CREATE TABLE fact_forecast_weekly (
    forecast_week_start DATE NOT NULL,
    product_id VARCHAR(10) NOT NULL REFERENCES dim_product(product_id),
    forecast_units NUMERIC(12,2) NOT NULL CHECK (forecast_units >= 0),
    model_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (forecast_week_start, product_id, model_name)
);

CREATE INDEX idx_sales_product_week ON fact_sales_weekly(product_id, week_start);
CREATE INDEX idx_inventory_product_week ON fact_inventory_weekly(product_id, week_start);
CREATE INDEX idx_sales_channel ON fact_sales_weekly(channel);

CREATE VIEW vw_sales_train AS
SELECT s.* FROM fact_sales_weekly s
JOIN dim_calendar c USING (week_start)
WHERE c.dataset_split = 'TRAIN';

CREATE VIEW vw_sales_test AS
SELECT s.* FROM fact_sales_weekly s
JOIN dim_calendar c USING (week_start)
WHERE c.dataset_split = 'TEST';

CREATE VIEW vw_latest_inventory AS
SELECT DISTINCT ON (product_id) *
FROM fact_inventory_weekly
ORDER BY product_id, week_start DESC;
