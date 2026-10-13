-- Run from the project root with psql.
SET search_path TO luxury_stock;

\copy dim_product FROM 'data/raw/products.csv' WITH (FORMAT csv, HEADER true);
\copy dim_calendar FROM 'data/raw/calendar.csv' WITH (FORMAT csv, HEADER true);
\copy fact_sales_weekly FROM 'data/raw/sales_weekly.csv' WITH (FORMAT csv, HEADER true);
\copy fact_inventory_weekly FROM 'data/raw/inventory_weekly.csv' WITH (FORMAT csv, HEADER true);
