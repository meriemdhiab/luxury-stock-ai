SET search_path TO luxury_stock;

-- Expected row counts
SELECT 'products' AS table_name, COUNT(*) AS row_count FROM dim_product
UNION ALL SELECT 'calendar', COUNT(*) FROM dim_calendar
UNION ALL SELECT 'sales', COUNT(*) FROM fact_sales_weekly
UNION ALL SELECT 'inventory', COUNT(*) FROM fact_inventory_weekly;

-- Referential and business checks
SELECT COUNT(*) AS negative_sales FROM fact_sales_weekly WHERE units_sold < 0 OR net_units_sold < 0;
SELECT COUNT(*) AS invalid_inventory FROM fact_inventory_weekly WHERE closing_stock_units < 0 OR days_of_cover < 0;
SELECT COUNT(*) AS duplicate_sales FROM (SELECT week_start, product_id, COUNT(*) FROM fact_sales_weekly GROUP BY 1,2 HAVING COUNT(*) > 1) d;
SELECT COUNT(*) AS stockout_weeks FROM fact_inventory_weekly WHERE stockout_flag;
