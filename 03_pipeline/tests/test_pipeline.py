import pandas as pd
import pytest

from pipeline import clean_sales, validate_sales


def test_quality_fixture_detects_expected_issues(quality_fixture, products):
    _, report = validate_sales(quality_fixture, products)
    assert report["issues"] == {
        "invalid_dates": 1,
        "missing_numeric_values": 1,
        "negative_units": 1,
        "unknown_products": 1,
        "duplicate_keys": 1,
    }
    assert report["rejected_rows"] == 5


def test_clean_sales_removes_invalid_rows(quality_fixture, products):
    clean, quarantine, report = clean_sales(quality_fixture, products)
    assert len(clean) + len(quarantine) == len(quality_fixture)
    assert report["quarantine_rows"] == len(quarantine) == report["rejected_rows"]
    assert clean["week_start"].notna().all()
    assert (clean["units_sold"] >= 0).all()
    assert not clean["product_id"].eq("P999").any()
    assert not clean.duplicated(subset=["week_start", "product_id"]).any()
    assert set(quarantine["rejection_reason"]) == {
        "invalid_date", "missing_numeric_value", "negative_units", "unknown_product", "duplicate_key",
    }


def test_duplicates_are_detected_on_normalised_dates(products):
    sales = pd.DataFrame({
        "week_start": ["2024-01-01", "2024-01-01"],
        "product_id": ["P001", "P001"],
        "units_sold": [5, 5], "returns_units": [0, 0], "net_units_sold": [5, 5],
        "revenue_eur": [10.0, 10.0], "channel": ["Boutique", "Boutique"],
    })
    clean, quarantine, _ = clean_sales(sales, products)
    assert len(clean) == 1
    assert quarantine["rejection_reason"].tolist() == ["duplicate_key"]


def test_missing_columns_raise(products):
    with pytest.raises(ValueError, match="Colonnes sales manquantes"):
        validate_sales(pd.DataFrame({"week_start": []}), products)


def test_run_pipeline_writes_outputs(project_root):
    processed = project_root / "data/processed"
    for name in ["sales_clean.csv", "sales_quarantine.csv", "quality_report.json"]:
        assert (processed / name).exists()
    assert (project_root / "database/luxury_stock_pipeline.sqlite").exists()
