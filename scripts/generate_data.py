from __future__ import annotations
import csv
import math
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
QUALITY = ROOT / 'data' / 'quality'
DB = ROOT / 'database'
for p in (RAW, QUALITY, DB):
    p.mkdir(parents=True, exist_ok=True)

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

# SQLite database for immediate local use and validation.
sqlite_path = DB/'luxury_stock.sqlite'
sqlite_path.unlink(missing_ok=True)
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


print('Generated project data under', ROOT)
print('Products:', len(products))
print('Weeks:', len(calendar))
print('Sales rows:', len(sales))
print('Inventory rows:', len(inventory))
print('SQLite:', sqlite_path)
