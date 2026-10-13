from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

LOGGER = logging.getLogger("luxury_stock_pipeline")

@dataclass
class PipelinePaths:
    root: Path
    products: Path
    calendar: Path
    sales: Path
    inventory: Path
    processed_dir: Path
    sqlite_path: Path

    @classmethod
    def from_root(cls, root: Path) -> "PipelinePaths":
        return cls(
            root=root,
            products=root / "data/raw/products.csv",
            calendar=root / "data/raw/calendar.csv",
            sales=root / "data/raw/sales_weekly.csv",
            inventory=root / "data/raw/inventory_weekly.csv",
            processed_dir=root / "data/processed",
            sqlite_path=root / "database/luxury_stock_pipeline.sqlite",
        )


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def validate_sales(sales: pd.DataFrame, products: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    required = {"week_start", "product_id", "units_sold", "returns_units", "net_units_sold", "revenue_eur", "channel"}
    missing_columns = sorted(required - set(sales.columns))
    if missing_columns:
        raise ValueError(f"Colonnes sales manquantes: {missing_columns}")

    report: dict[str, Any] = {"input_rows": int(len(sales)), "issues": {}}
    work = sales.copy()
    work["week_start_parsed"] = pd.to_datetime(work["week_start"], errors="coerce")
    report["issues"]["invalid_dates"] = int(work["week_start_parsed"].isna().sum())
    for col in ["units_sold", "returns_units", "net_units_sold", "revenue_eur"]:
        work[col] = pd.to_numeric(work[col], errors="coerce")
    report["issues"]["missing_numeric_values"] = int(work[["units_sold", "returns_units", "net_units_sold", "revenue_eur"]].isna().any(axis=1).sum())
    report["issues"]["negative_units"] = int((work[["units_sold", "returns_units", "net_units_sold"]] < 0).any(axis=1).sum())
    report["issues"]["unknown_products"] = int((~work["product_id"].isin(set(products["product_id"]))).sum())
    report["issues"]["duplicate_keys"] = int(work.duplicated(subset=["week_start", "product_id"], keep=False).sum())
    report["rejected_rows"] = int(sum(report["issues"].values()))
    return work, report


def clean_sales(sales: pd.DataFrame, products: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    work, report = validate_sales(sales, products)
    work["_row_number"] = range(1, len(work) + 1)
    reasons = []
    reasons.append(work["week_start_parsed"].isna())
    numeric_cols = ["units_sold", "returns_units", "net_units_sold", "revenue_eur"]
    reasons.append(work[numeric_cols].isna().any(axis=1))
    reasons.append((work[["units_sold", "returns_units", "net_units_sold"]] < 0).any(axis=1))
    reasons.append(~work["product_id"].isin(set(products["product_id"])))
    duplicate_mask = work.duplicated(subset=["week_start", "product_id"], keep="first")
    reasons.append(duplicate_mask)
    reject_mask = reasons[0]
    for r in reasons[1:]: reject_mask = reject_mask | r
    quarantine = work.loc[reject_mask].copy()
    quarantine["rejection_reason"] = "validation_error"
    quarantine.loc[reasons[0], "rejection_reason"] = "invalid_date"
    quarantine.loc[reasons[1], "rejection_reason"] = "missing_numeric_value"
    quarantine.loc[reasons[2], "rejection_reason"] = "negative_units"
    quarantine.loc[reasons[3], "rejection_reason"] = "unknown_product"
    quarantine.loc[reasons[4], "rejection_reason"] = "duplicate_key"
    clean = work.loc[~reject_mask].copy()
    clean["week_start"] = clean["week_start_parsed"].dt.strftime("%Y-%m-%d")
    clean = clean.drop(columns=["week_start_parsed", "_row_number"])
    quarantine = quarantine.drop(columns=["week_start_parsed"])
    report["clean_rows"] = int(len(clean))
    report["quarantine_rows"] = int(len(quarantine))
    return clean, quarantine, report


def write_sqlite(paths: PipelinePaths, products: pd.DataFrame, calendar: pd.DataFrame, sales: pd.DataFrame, inventory: pd.DataFrame) -> None:
    paths.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    if paths.sqlite_path.exists(): paths.sqlite_path.unlink()
    con = sqlite3.connect(paths.sqlite_path)
    products.to_sql("dim_product", con, index=False)
    calendar.to_sql("dim_calendar", con, index=False)
    sales.to_sql("fact_sales_weekly", con, index=False)
    inventory.to_sql("fact_inventory_weekly", con, index=False)
    con.executescript("""
    CREATE INDEX idx_sales_product_week ON fact_sales_weekly(product_id, week_start);
    CREATE INDEX idx_inventory_product_week ON fact_inventory_weekly(product_id, week_start);
    CREATE VIEW vw_sales_train AS SELECT s.* FROM fact_sales_weekly s JOIN dim_calendar c USING (week_start) WHERE c.dataset_split='TRAIN';
    CREATE VIEW vw_sales_test AS SELECT s.* FROM fact_sales_weekly s JOIN dim_calendar c USING (week_start) WHERE c.dataset_split='TEST';
    """)
    con.commit(); con.close()


def run_pipeline(root: Path | str = ".") -> dict[str, Any]:
    root = Path(root).resolve()
    paths = PipelinePaths.from_root(root)
    paths.processed_dir.mkdir(parents=True, exist_ok=True)
    products = _read_csv(paths.products)
    calendar = _read_csv(paths.calendar)
    sales = _read_csv(paths.sales)
    inventory = _read_csv(paths.inventory)
    clean_sales_df, quarantine_df, report = clean_sales(sales, products)
    clean_sales_df.to_csv(paths.processed_dir / "sales_clean.csv", index=False)
    quarantine_df.to_csv(paths.processed_dir / "sales_quarantine.csv", index=False)
    calendar.to_csv(paths.processed_dir / "calendar_clean.csv", index=False)
    products.to_csv(paths.processed_dir / "products_clean.csv", index=False)
    inventory.to_csv(paths.processed_dir / "inventory_clean.csv", index=False)
    write_sqlite(paths, products, calendar, clean_sales_df, inventory)
    report.update({
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_sales": str(paths.sales),
        "output_database": str(paths.sqlite_path),
    })
    (paths.processed_dir / "quality_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    LOGGER.info("Pipeline terminé: %s", report)
    return report

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_pipeline(Path(__file__).resolve().parents[2])
