from __future__ import annotations
import csv, math, random, sqlite3
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
QUALITY = ROOT / 'data' / 'quality'
SQL = ROOT / '02_architecture' / 'sql'
DB = ROOT / 'database'
SCRIPTS = ROOT / 'scripts'
for p in (RAW, QUALITY, SQL, DB, SCRIPTS): p.mkdir(parents=True, exist_ok=True)

SEED = 20261012
rng = random.Random(SEED)
start = date(2024, 1, 1)  # Monday
train_weeks = 104
test_weeks = 12
all_weeks = train_weeks + test_weeks
forecast_horizon = 12

products = []
collections = ['Éclat', 'Atelier', 'Héritage', 'Nocturne']
categories = ['Sac à main', 'Portefeuille', 'Ceinture', 'Petite maroquinerie']
materials = ['Cuir grainé', 'Cuir lisse', 'Cuir embossé', 'Toile enduite']
colors = ['Noir', 'Camel', 'Bordeaux', 'Ivoire', 'Vert forêt', 'Bleu nuit']
for i in range(1, 37):
    category = categories[(i - 1) % len(categories)]
    collection = collections[(i - 1) % len(collections)]
    material = materials[(i - 1) % len(materials)]
    color = colors[(i * 3) % len(colors)]
    if category == 'Sac à main':
        price = 850 + ((i * 137) % 1150)
        base = 7.0 + ((i * 5) % 9)
    elif category == 'Portefeuille':
        price = 260 + ((i * 47) % 430)
        base = 11.0 + ((i * 3) % 10)
    elif category == 'Ceinture':
        price = 320 + ((i * 61) % 380)
        base = 8.0 + ((i * 4) % 8)
    else:
        price = 120 + ((i * 29) % 260)
        base = 14.0 + ((i * 2) % 10)
    products.append({
        'product_id': f'P{i:03d}',
        'product_name': f'{category} {collection} {i:02d}',
        'category': category,
        'collection': collection,
        'material': material,
        'color': color,
        'unit_price_eur': round(float(price), 2),
        'base_weekly_demand': round(base, 2),
        'launch_date': (date(2023, 1, 1) + timedelta(days=(i * 17) % 300)).isoformat(),
        'lead_time_days': [14, 21, 28, 35][(i - 1) % 4],
        'minimum_stock_units': 8 + ((i * 3) % 18),
        'active_flag': 1,
    })

# Calendar: 116 weeks, with a clean train/test split for temporal evaluation.
calendar = []
for w in range(all_weeks):
    d = start + timedelta(days=7*w)
    month = d.month
    quarter = (month - 1) // 3 + 1
    season = 'Hiver' if month in (1,2,12) else 'Printemps' if month in (3,4,5) else 'Été' if month in (6,7,8) else 'Automne'
    peak = 1 if month in (11, 12) else 0
    calendar.append({
        'week_start': d.isoformat(),
        'week_index': w + 1,
        'year': d.year,
        'iso_week': d.isocalendar().week,
        'month': month,
        'quarter': quarter,
        'season': season,
        'luxury_peak_flag': peak,
        'dataset_split': 'TRAIN' if w < train_weeks else 'TEST',
    })

sales = []
inventory = []
stock_by_product = {p['product_id']: 35 + ((int(p['product_id'][1:]) * 7) % 45) for p in products}
for w, cal in enumerate(calendar):
    month = cal['month']
    peak_factor = 1.0 + (0.42 if month in (11,12) else 0.0)
    spring_factor = 1.12 if month in (3,4,5) else 1.0
    for p in products:
        pid = p['product_id']
        pi = int(pid[1:])
        trend = 1.0 + 0.0018 * w
        collection_factor = {'Éclat': 1.08, 'Atelier': 0.95, 'Héritage': 1.18, 'Nocturne': 0.88}[p['collection']]
        category_factor = {'Sac à main': 0.92, 'Portefeuille': 1.20, 'Ceinture': 1.05, 'Petite maroquinerie': 1.35}[p['category']]
        campaign = 1.0 + (0.20 if (w % 26 == (pi % 7)) else 0.0)
        cyclical = 1.0 + 0.10 * math.sin((w + pi) / 5.5)
        expected = p['base_weekly_demand'] * peak_factor * spring_factor * trend * collection_factor * category_factor * campaign * cyclical
        demand = max(0, int(round(rng.gauss(expected, max(1.2, expected * 0.16)))))
        returns = int(round(demand * rng.uniform(0.01, 0.045)))
        revenue = round((demand - returns) * p['unit_price_eur'], 2)
        sales.append({
            'week_start': cal['week_start'],
            'product_id': pid,
            'units_sold': demand,
            'returns_units': returns,
            'net_units_sold': demand - returns,
            'revenue_eur': revenue,
            'channel': ['Boutique', 'E-commerce', 'Wholesale'][(pi + w) % 3],
        })
        opening = stock_by_product[pid]
        lead = p['lead_time_days']
        # Replenishment follows a simple policy, intentionally imperfect but explainable.
        target = max(p['minimum_stock_units'] * 2, int(expected * (lead / 7 + 2)))
        inbound = max(0, target - max(0, opening - demand)) if (w % max(2, lead // 7) == 0) else 0
        closing = max(0, opening + inbound - demand)
        stockout = 1 if opening + inbound < demand else 0
        inventory.append({
            'week_start': cal['week_start'],
            'product_id': pid,
            'opening_stock_units': opening,
            'inbound_units': inbound,
            'units_sold': demand,
            'closing_stock_units': closing,
            'stockout_flag': stockout,
            'days_of_cover': round((closing / max(expected, 0.1)) * 7, 2),
        })
        stock_by_product[pid] = closing

horizon = []
last = start + timedelta(days=7*(all_weeks-1))
for i in range(1, forecast_horizon + 1):
    d = last + timedelta(days=7*i)
    horizon.append({'forecast_week_start': d.isoformat(), 'horizon_week': i})

# Write CSV helper
def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

write_csv(RAW/'products.csv', products, list(products[0].keys()))
write_csv(RAW/'calendar.csv', calendar, list(calendar[0].keys()))
write_csv(RAW/'sales_weekly.csv', sales, list(sales[0].keys()))
write_csv(RAW/'inventory_weekly.csv', inventory, list(inventory[0].keys()))
write_csv(RAW/'forecast_horizon.csv', horizon, list(horizon[0].keys()))

# Create a controlled quality fixture for testing the pipeline.
quality = [dict(r) for r in sales[:50]]
quality.append(dict(quality[3]))  # duplicate
quality[7]['units_sold'] = ''  # missing value
quality[12]['week_start'] = '2024-99-99'  # invalid date
quality[18]['units_sold'] = '-4'  # invalid negative quantity
quality[25]['product_id'] = 'P999'  # unknown product
write_csv(QUALITY/'sales_quality_issues.csv', quality, list(sales[0].keys()))

# PostgreSQL schema and seed scripts.
(SQL/'001_schema.sql').write_text('''-- Luxury Stock AI, PostgreSQL schema\nCREATE SCHEMA IF NOT EXISTS luxury_stock;\nSET search_path TO luxury_stock;\n\nDROP VIEW IF EXISTS vw_latest_inventory;\nDROP VIEW IF EXISTS vw_sales_test;\nDROP VIEW IF EXISTS vw_sales_train;\nDROP TABLE IF EXISTS fact_forecast_weekly, fact_inventory_weekly, fact_sales_weekly, dim_calendar, dim_product CASCADE;\n\nCREATE TABLE dim_product (\n    product_id VARCHAR(10) PRIMARY KEY,\n    product_name TEXT NOT NULL,\n    category TEXT NOT NULL,\n    collection TEXT NOT NULL,\n    material TEXT NOT NULL,\n    color TEXT NOT NULL,\n    unit_price_eur NUMERIC(12,2) NOT NULL CHECK (unit_price_eur > 0),\n    base_weekly_demand NUMERIC(12,2) NOT NULL CHECK (base_weekly_demand >= 0),\n    launch_date DATE NOT NULL,\n    lead_time_days INTEGER NOT NULL CHECK (lead_time_days > 0),\n    minimum_stock_units INTEGER NOT NULL CHECK (minimum_stock_units >= 0),\n    active_flag BOOLEAN NOT NULL DEFAULT TRUE\n);\n\nCREATE TABLE dim_calendar (\n    week_start DATE PRIMARY KEY,\n    week_index INTEGER NOT NULL UNIQUE,\n    year INTEGER NOT NULL,\n    iso_week INTEGER NOT NULL,\n    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),\n    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),\n    season TEXT NOT NULL,\n    luxury_peak_flag BOOLEAN NOT NULL,\n    dataset_split TEXT NOT NULL CHECK (dataset_split IN ('TRAIN','TEST'))\n);\n\nCREATE TABLE fact_sales_weekly (\n    week_start DATE NOT NULL REFERENCES dim_calendar(week_start),\n    product_id VARCHAR(10) NOT NULL REFERENCES dim_product(product_id),\n    units_sold INTEGER NOT NULL CHECK (units_sold >= 0),\n    returns_units INTEGER NOT NULL CHECK (returns_units >= 0),\n    net_units_sold INTEGER NOT NULL CHECK (net_units_sold >= 0),\n    revenue_eur NUMERIC(14,2) NOT NULL CHECK (revenue_eur >= 0),\n    channel TEXT NOT NULL,\n    PRIMARY KEY (week_start, product_id)\n);\n\nCREATE TABLE fact_inventory_weekly (\n    week_start DATE NOT NULL REFERENCES dim_calendar(week_start),\n    product_id VARCHAR(10) NOT NULL REFERENCES dim_product(product_id),\n    opening_stock_units INTEGER NOT NULL CHECK (opening_stock_units >= 0),\n    inbound_units INTEGER NOT NULL CHECK (inbound_units >= 0),\n    units_sold INTEGER NOT NULL CHECK (units_sold >= 0),\n    closing_stock_units INTEGER NOT NULL CHECK (closing_stock_units >= 0),\n    stockout_flag BOOLEAN NOT NULL,\n    days_of_cover NUMERIC(12,2) NOT NULL CHECK (days_of_cover >= 0),\n    PRIMARY KEY (week_start, product_id)\n);\n\nCREATE TABLE fact_forecast_weekly (\n    forecast_week_start DATE NOT NULL,\n    product_id VARCHAR(10) NOT NULL REFERENCES dim_product(product_id),\n    forecast_units NUMERIC(12,2) NOT NULL CHECK (forecast_units >= 0),\n    model_name TEXT NOT NULL,\n    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,\n    PRIMARY KEY (forecast_week_start, product_id, model_name)\n);\n\nCREATE INDEX idx_sales_product_week ON fact_sales_weekly(product_id, week_start);\nCREATE INDEX idx_inventory_product_week ON fact_inventory_weekly(product_id, week_start);\nCREATE INDEX idx_sales_channel ON fact_sales_weekly(channel);\n\nCREATE VIEW vw_sales_train AS\nSELECT s.* FROM fact_sales_weekly s\nJOIN dim_calendar c USING (week_start)\nWHERE c.dataset_split = 'TRAIN';\n\nCREATE VIEW vw_sales_test AS\nSELECT s.* FROM fact_sales_weekly s\nJOIN dim_calendar c USING (week_start)\nWHERE c.dataset_split = 'TEST';\n\nCREATE VIEW vw_latest_inventory AS\nSELECT DISTINCT ON (product_id) *\nFROM fact_inventory_weekly\nORDER BY product_id, week_start DESC;\n''', encoding='utf-8')

(SQL/'002_seed_from_csv.sql').write_text('''-- Run from the project root with psql.\nSET search_path TO luxury_stock;\n\n\\copy dim_product FROM 'data/raw/products.csv' WITH (FORMAT csv, HEADER true);\n\\copy dim_calendar FROM 'data/raw/calendar.csv' WITH (FORMAT csv, HEADER true);\n\\copy fact_sales_weekly FROM 'data/raw/sales_weekly.csv' WITH (FORMAT csv, HEADER true);\n\\copy fact_inventory_weekly FROM 'data/raw/inventory_weekly.csv' WITH (FORMAT csv, HEADER true);\n''', encoding='utf-8')

(SQL/'003_quality_checks.sql').write_text('''SET search_path TO luxury_stock;\n\n-- Expected row counts\nSELECT 'products' AS table_name, COUNT(*) AS row_count FROM dim_product\nUNION ALL SELECT 'calendar', COUNT(*) FROM dim_calendar\nUNION ALL SELECT 'sales', COUNT(*) FROM fact_sales_weekly\nUNION ALL SELECT 'inventory', COUNT(*) FROM fact_inventory_weekly;\n\n-- Referential and business checks\nSELECT COUNT(*) AS negative_sales FROM fact_sales_weekly WHERE units_sold < 0 OR net_units_sold < 0;\nSELECT COUNT(*) AS invalid_inventory FROM fact_inventory_weekly WHERE closing_stock_units < 0 OR days_of_cover < 0;\nSELECT COUNT(*) AS duplicate_sales FROM (SELECT week_start, product_id, COUNT(*) FROM fact_sales_weekly GROUP BY 1,2 HAVING COUNT(*) > 1) d;\nSELECT COUNT(*) AS stockout_weeks FROM fact_inventory_weekly WHERE stockout_flag;\n''', encoding='utf-8')

# SQLite database for immediate local use and validation.
sqlite_path = DB/'luxury_stock.sqlite'
if sqlite_path.exists(): sqlite_path.unlink()
con = sqlite3.connect(sqlite_path)
cur = con.cursor()
cur.executescript('''
CREATE TABLE dim_product (product_id TEXT PRIMARY KEY, product_name TEXT, category TEXT, collection TEXT, material TEXT, color TEXT, unit_price_eur REAL, base_weekly_demand REAL, launch_date TEXT, lead_time_days INTEGER, minimum_stock_units INTEGER, active_flag INTEGER);
CREATE TABLE dim_calendar (week_start TEXT PRIMARY KEY, week_index INTEGER UNIQUE, year INTEGER, iso_week INTEGER, month INTEGER, quarter INTEGER, season TEXT, luxury_peak_flag INTEGER, dataset_split TEXT);
CREATE TABLE fact_sales_weekly (week_start TEXT, product_id TEXT, units_sold INTEGER, returns_units INTEGER, net_units_sold INTEGER, revenue_eur REAL, channel TEXT, PRIMARY KEY (week_start, product_id));
CREATE TABLE fact_inventory_weekly (week_start TEXT, product_id TEXT, opening_stock_units INTEGER, inbound_units INTEGER, units_sold INTEGER, closing_stock_units INTEGER, stockout_flag INTEGER, days_of_cover REAL, PRIMARY KEY (week_start, product_id));
CREATE TABLE forecast_horizon (forecast_week_start TEXT PRIMARY KEY, horizon_week INTEGER);
CREATE TABLE data_quality_issue_cases (issue_id INTEGER PRIMARY KEY, issue_type TEXT, description TEXT, source_file TEXT, expected_detection TEXT);
''')
cur.executemany('INSERT INTO dim_product VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', [tuple(p.values()) for p in products])
cur.executemany('INSERT INTO dim_calendar VALUES (?,?,?,?,?,?,?,?,?)', [tuple(c.values()) for c in calendar])
cur.executemany('INSERT INTO fact_sales_weekly VALUES (?,?,?,?,?,?,?)', [tuple(r.values()) for r in sales])
cur.executemany('INSERT INTO fact_inventory_weekly VALUES (?,?,?,?,?,?,?,?)', [tuple(r.values()) for r in inventory])
cur.executemany('INSERT INTO forecast_horizon VALUES (?,?)', [tuple(r.values()) for r in horizon])
issues = [
    (1,'duplicate','Duplicate sales row','data/quality/sales_quality_issues.csv','Primary key or duplicate check'),
    (2,'missing_value','Missing units_sold','data/quality/sales_quality_issues.csv','Not-null and completeness check'),
    (3,'invalid_date','Invalid week_start date','data/quality/sales_quality_issues.csv','Date parsing validation'),
    (4,'negative_value','Negative units_sold','data/quality/sales_quality_issues.csv','Business rule check'),
    (5,'unknown_reference','Unknown product_id P999','data/quality/sales_quality_issues.csv','Referential integrity check'),
]
cur.executemany('INSERT INTO data_quality_issue_cases VALUES (?,?,?,?,?)', issues)
cur.executescript('''
CREATE INDEX idx_sales_product_week ON fact_sales_weekly(product_id, week_start);
CREATE INDEX idx_inventory_product_week ON fact_inventory_weekly(product_id, week_start);
CREATE VIEW vw_sales_train AS SELECT s.* FROM fact_sales_weekly s JOIN dim_calendar c USING (week_start) WHERE c.dataset_split='TRAIN';
CREATE VIEW vw_sales_test AS SELECT s.* FROM fact_sales_weekly s JOIN dim_calendar c USING (week_start) WHERE c.dataset_split='TEST';
CREATE VIEW vw_latest_inventory AS SELECT i.* FROM fact_inventory_weekly i JOIN (SELECT product_id, MAX(week_start) AS week_start FROM fact_inventory_weekly GROUP BY product_id) x USING(product_id, week_start);
''')
con.commit(); con.close()


(ROOT/'data'/'README.md').write_text('''# Données Luxury Stock AI\n\nJeu de données synthétique reproductible, généré avec la graine `20261012`. Il ne contient aucune donnée personnelle.\n\n## Fichiers\n\n- `raw/products.csv` : catalogue produit, 36 produits.\n- `raw/calendar.csv` : 116 semaines, 104 semaines TRAIN et 12 semaines TEST.\n- `raw/sales_weekly.csv` : ventes hebdomadaires par produit.\n- `raw/inventory_weekly.csv` : état hebdomadaire des stocks.\n- `raw/forecast_horizon.csv` : 12 semaines après la dernière date observée, pour générer des prévisions futures.\n- `quality/sales_quality_issues.csv` : fixture volontairement dégradée pour tester les contrôles qualité.\n\n## Principe d'évaluation\n\nLes 104 premières semaines doivent être utilisées pour l'entraînement et les 12 dernières pour l'évaluation temporelle. Il ne faut pas utiliser les semaines TEST pour construire les variables d'entraînement.\n\n## Régénération\n\nDepuis le dossier `luxury-stock-ai` :\n\n```bash\npython scripts/generate_data.py\n```\n\nLa base SQLite est fournie pour un démarrage immédiat. Les scripts SQL du dossier `02_architecture/sql` permettent de charger les mêmes données dans PostgreSQL.\n''', encoding='utf-8')

(ROOT/'database'/'README.md').write_text('''# Base de données\n\n## Démarrage immédiat\n\nLa base `luxury_stock.sqlite` peut être ouverte avec SQLite, DuckDB, Python ou un outil graphique.\n\nExemple :\n\n```bash\nsqlite3 database/luxury_stock.sqlite\n.tables\nSELECT COUNT(*) FROM fact_sales_weekly;\nSELECT * FROM vw_sales_train LIMIT 5;\n```\n\n## PostgreSQL\n\nDepuis la racine du projet :\n\n```bash\ncreatedb luxury_stock\npsql -d luxury_stock -f 02_architecture/sql/001_schema.sql\npsql -d luxury_stock -f 02_architecture/sql/002_seed_from_csv.sql\npsql -d luxury_stock -f 02_architecture/sql/003_quality_checks.sql\n```\n\nLe schéma PostgreSQL est `luxury_stock`.\n''', encoding='utf-8')

(ROOT/'docs'/'dataset_profile.md').write_text(f'''# Profil du jeu de données\n\n- Graine aléatoire : `{SEED}`\n- Produits : `{len(products)}`\n- Semaines : `{len(calendar)}`\n- Lignes de ventes : `{len(sales)}`\n- Lignes d'inventaire : `{len(inventory)}`\n- Période TRAIN : `{calendar[0]["week_start"]}` à `{calendar[train_weeks-1]["week_start"]}`\n- Période TEST : `{calendar[train_weeks]["week_start"]}` à `{calendar[-1]["week_start"]}`\n- Horizon futur : `{horizon[0]["forecast_week_start"]}` à `{horizon[-1]["forecast_week_start"]}`\n- Données personnelles : aucune, données synthétiques\n\nLe jeu a été conçu pour permettre une démonstration des quatre blocs : gouvernance, architecture, pipeline et solution IA déployable.\n''', encoding='utf-8')

print('Generated project data under', ROOT)
print('Products:', len(products))
print('Weeks:', len(calendar))
print('Sales rows:', len(sales))
print('Inventory rows:', len(inventory))
print('SQLite:', sqlite_path)
