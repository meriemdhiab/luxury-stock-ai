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

SALES_COLUMNS = {"week_start", "product_id", "units_sold", "returns_units", "net_units_sold", "revenue_eur", "channel"}
INVENTORY_COLUMNS = {
    "week_start", "product_id", "opening_stock_units", "inbound_units",
    "units_sold", "closing_stock_units", "stockout_flag", "days_of_cover",
}
NUMERIC_COLUMNS = ["units_sold", "returns_units", "net_units_sold", "revenue_eur"]
UNIT_COLUMNS = ["units_sold", "returns_units", "net_units_sold"]


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


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Colonnes {name} manquantes: {missing}")


def _validate(sales: pd.DataFrame, products: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Calcule une fois les anomalies ligne par ligne, partagées par la validation et le nettoyage."""
    _require_columns(sales, SALES_COLUMNS, "sales")
    work = sales.copy()
    work["week_start_parsed"] = pd.to_datetime(work["week_start"], format="%Y-%m-%d", errors="coerce")
    for col in NUMERIC_COLUMNS:
        work[col] = pd.to_numeric(work[col], errors="coerce")
    flags = pd.DataFrame({
        "invalid_date": work["week_start_parsed"].isna(),
        "missing_numeric_value": work[NUMERIC_COLUMNS].isna().any(axis=1),
        "negative_units": (work[UNIT_COLUMNS] < 0).any(axis=1),
        "unknown_product": ~work["product_id"].isin(set(products["product_id"])),
        # La première occurrence est conservée, les suivantes sont des doublons.
        "duplicate_key": work.duplicated(subset=["week_start_parsed", "product_id"], keep="first")
        & work["week_start_parsed"].notna(),
    })
    report: dict[str, Any] = {
        "input_rows": int(len(sales)),
        "issues": {
            "invalid_dates": int(flags["invalid_date"].sum()),
            "missing_numeric_values": int(flags["missing_numeric_value"].sum()),
            "negative_units": int(flags["negative_units"].sum()),
            "unknown_products": int(flags["unknown_product"].sum()),
            "duplicate_keys": int(flags["duplicate_key"].sum()),
        },
        # Une ligne peut cumuler plusieurs anomalies : on compte les lignes, pas les anomalies.
        "rejected_rows": int(flags.any(axis=1).sum()),
    }
    return work, flags, report


def validate_sales(sales: pd.DataFrame, products: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    work, _, report = _validate(sales, products)
    return work, report


def clean_sales(sales: pd.DataFrame, products: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    work, flags, report = _validate(sales, products)
    reject_mask = flags.any(axis=1)

    quarantine = sales.loc[reject_mask].copy()
    quarantine.insert(0, "source_row_number", quarantine.index + 1)
    quarantine["rejection_reason"] = flags.loc[reject_mask].apply(
        lambda row: ";".join(name for name, hit in row.items() if hit), axis=1
    )

    clean = work.loc[~reject_mask].copy()
    clean["week_start"] = clean["week_start_parsed"].dt.strftime("%Y-%m-%d")
    clean = clean.drop(columns=["week_start_parsed"])
    for col in UNIT_COLUMNS:
        clean[col] = clean[col].astype(int)

    report["clean_rows"] = int(len(clean))
    report["quarantine_rows"] = int(len(quarantine))
    return clean, quarantine, report


def write_sqlite(paths: PipelinePaths, products: pd.DataFrame, calendar: pd.DataFrame, sales: pd.DataFrame, inventory: pd.DataFrame) -> None:
    paths.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    paths.sqlite_path.unlink(missing_ok=True)
    with sqlite3.connect(paths.sqlite_path) as con:
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
    con.close()


def run_pipeline(root: Path | str = ".") -> dict[str, Any]:
    root = Path(root).resolve()
    paths = PipelinePaths.from_root(root)
    paths.processed_dir.mkdir(parents=True, exist_ok=True)
    products = _read_csv(paths.products)
    calendar = _read_csv(paths.calendar)
    sales = _read_csv(paths.sales)
    inventory = _read_csv(paths.inventory)
    _require_columns(inventory, INVENTORY_COLUMNS, "inventory")

    clean_sales_df, quarantine_df, report = clean_sales(sales, products)
    clean_sales_df.to_csv(paths.processed_dir / "sales_clean.csv", index=False)
    quarantine_df.to_csv(paths.processed_dir / "sales_quarantine.csv", index=False)
    calendar.to_csv(paths.processed_dir / "calendar_clean.csv", index=False)
    products.to_csv(paths.processed_dir / "products_clean.csv", index=False)
    inventory.to_csv(paths.processed_dir / "inventory_clean.csv", index=False)
    write_sqlite(paths, products, calendar, clean_sales_df, inventory)

    report.update({
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_sales": str(paths.sales.relative_to(root)),
        "output_database": str(paths.sqlite_path.relative_to(root)),
    })
    (paths.processed_dir / "quality_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    LOGGER.info("Pipeline terminé: %s", report)
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_pipeline(Path(__file__).resolve().parents[2])
