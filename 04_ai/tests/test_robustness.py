from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '03_pipeline/src'))
from pipeline import clean_sales

def test_quality_fixture_is_quarantined_under_stress():
    products = pd.read_csv(ROOT / 'data/raw/products.csv')
    source = pd.read_csv(ROOT / 'data/quality/sales_quality_issues.csv')
    stressed = pd.concat([source] * 5, ignore_index=True)
    clean, quarantine, report = clean_sales(stressed, products)
    assert len(quarantine) > 0
    assert len(clean) < len(stressed)
    assert report['quarantine_rows'] == len(quarantine)
