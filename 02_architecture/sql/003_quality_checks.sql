-- Contrôles qualité SQL après chargement.
-- Les contraintes du schéma (CHECK, clés, références) garantissent déjà les
-- valeurs négatives, les doublons et les références inconnues : ce script
-- vérifie ce que les contraintes ne peuvent pas exprimer.
--   CRITICAL : échec bloquant (le script lève une erreur)
--   WARN     : incohérence métier à examiner, non bloquante
\set ON_ERROR_STOP on
SET search_path TO luxury_stock;

-- Volumétrie (information)
SELECT 'dim_product' AS table_name, COUNT(*) AS row_count FROM dim_product
UNION ALL SELECT 'dim_calendar', COUNT(*) FROM dim_calendar
UNION ALL SELECT 'fact_sales_weekly', COUNT(*) FROM fact_sales_weekly
UNION ALL SELECT 'fact_inventory_weekly', COUNT(*) FROM fact_inventory_weekly;

SELECT dataset_split, COUNT(*) AS weeks, MIN(week_start) AS first_week, MAX(week_start) AS last_week
FROM dim_calendar GROUP BY dataset_split ORDER BY first_week;

CREATE TEMP TABLE quality_results (
    check_id TEXT, severity TEXT, description TEXT, violations BIGINT
);

-- Contrôles critiques
INSERT INTO quality_results
SELECT 'Q01', 'CRITICAL', 'Semaines du calendrier non consécutives (écart différent de 7 jours)', COUNT(*)
FROM (SELECT week_start, LEAD(week_start) OVER (ORDER BY week_start) AS next_week FROM dim_calendar) w
WHERE next_week IS NOT NULL AND next_week - week_start <> 7;

INSERT INTO quality_results
SELECT 'Q02', 'CRITICAL', 'week_start qui n''est pas un lundi', COUNT(*)
FROM dim_calendar WHERE EXTRACT(ISODOW FROM week_start) <> 1;

INSERT INTO quality_results
SELECT 'Q03', 'CRITICAL', 'Fuite temporelle : semaine TRAIN postérieure à la première semaine TEST', COUNT(*)
FROM dim_calendar
WHERE dataset_split = 'TRAIN'
  AND week_start > (SELECT MIN(week_start) FROM dim_calendar WHERE dataset_split = 'TEST');

INSERT INTO quality_results
SELECT 'Q04', 'CRITICAL', 'Ventes : écart avec la grille complète produits x semaines',
       ABS((SELECT COUNT(*) FROM dim_product) * (SELECT COUNT(*) FROM dim_calendar)
           - (SELECT COUNT(*) FROM fact_sales_weekly));

INSERT INTO quality_results
SELECT 'Q05', 'CRITICAL', 'Stocks : écart avec la grille complète produits x semaines',
       ABS((SELECT COUNT(*) FROM dim_product) * (SELECT COUNT(*) FROM dim_calendar)
           - (SELECT COUNT(*) FROM fact_inventory_weekly));

INSERT INTO quality_results
SELECT 'Q06', 'CRITICAL', 'Ligne de ventes sans ligne de stock correspondante', COUNT(*)
FROM fact_sales_weekly s
LEFT JOIN fact_inventory_weekly i ON i.week_start = s.week_start AND i.product_id = s.product_id
WHERE i.product_id IS NULL;

-- Contrôles métier (avertissements)
INSERT INTO quality_results
SELECT 'W01', 'WARN', 'net_units_sold différent de units_sold - returns_units', COUNT(*)
FROM fact_sales_weekly WHERE net_units_sold <> units_sold - returns_units;

INSERT INTO quality_results
SELECT 'W02', 'WARN', 'Stock final différent de stock initial + entrées - ventes', COUNT(*)
FROM fact_inventory_weekly
WHERE closing_stock_units <> opening_stock_units + inbound_units - units_sold;

INSERT INTO quality_results
SELECT 'W03', 'WARN', 'units_sold différent entre ventes et stocks', COUNT(*)
FROM fact_sales_weekly s
JOIN fact_inventory_weekly i ON i.week_start = s.week_start AND i.product_id = s.product_id
WHERE s.units_sold <> i.units_sold;

INSERT INTO quality_results
SELECT 'W04', 'WARN', 'Ventes avant la date de lancement du produit', COUNT(*)
FROM fact_sales_weekly s
JOIN dim_product p ON p.product_id = s.product_id
WHERE s.week_start < p.launch_date AND s.units_sold > 0;

INSERT INTO quality_results
SELECT 'W05', 'WARN', 'Chiffre d''affaires éloigné de plus de 5 % de net_units_sold x prix catalogue', COUNT(*)
FROM fact_sales_weekly s
JOIN dim_product p ON p.product_id = s.product_id
WHERE ABS(s.revenue_eur - s.net_units_sold * p.unit_price_eur) > 0.05 * GREATEST(s.revenue_eur, 1);

INSERT INTO quality_results
SELECT 'W06', 'WARN', 'iso_week différent de la semaine ISO calculée', COUNT(*)
FROM dim_calendar WHERE iso_week <> EXTRACT(WEEK FROM week_start)::int;

-- Synthèse
SELECT check_id, severity, description, violations,
       CASE WHEN violations = 0 THEN 'PASS'
            WHEN severity = 'CRITICAL' THEN 'FAIL'
            ELSE 'WARN' END AS status
FROM quality_results
ORDER BY check_id;

DO $$
DECLARE n INTEGER;
BEGIN
    SELECT COUNT(*) INTO n FROM quality_results WHERE severity = 'CRITICAL' AND violations > 0;
    IF n > 0 THEN
        RAISE EXCEPTION 'Contrôles qualité critiques en échec : % (voir la synthèse ci-dessus)', n;
    END IF;
END $$;
