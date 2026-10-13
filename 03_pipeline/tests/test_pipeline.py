from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "03_pipeline/src"))
from pipeline import clean_sales, validate_sales


def test_quality_fixture_detects_expected_issues():
    products = pd.read_csv(ROOT / "data/raw/products.csv")
    sales = pd.read_csv(ROOT / "data/quality/sales_quality_issues.csv")
    _, report = validate_sales(sales, products)
    assert report["issues"]["invalid_dates"] == 1
    assert report["issues"]["negative_units"] == 1
    assert report["issues"]["unknown_products"] == 1
    assert report["issues"]["duplicate_keys"] >= 2


def test_clean_sales_removes_invalid_rows():
    products = pd.read_csv(ROOT / "data/raw/products.csv")
    sales = pd.read_csv(ROOT / "data/quality/sales_quality_issues.csv")
    clean, quarantine, report = clean_sales(sales, products)
    assert len(clean) < len(sales)
    assert len(quarantine) > 0
    assert clean["week_start"].notna().all()
    assert (clean["units_sold"] >= 0).all()
    assert not clean["product_id"].eq("P999").any()
