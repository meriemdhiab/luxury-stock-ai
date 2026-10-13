from __future__ import annotations

from pathlib import Path
import pandas as pd

FEATURE_COLUMNS = [
    "product_num", "week_index", "month", "quarter", "luxury_peak_flag",
    "lag_1", "lag_4", "lag_8", "rolling_mean_4",
]
TARGET = "net_units_sold"


def load_training_frame(root: Path) -> pd.DataFrame:
    sales = pd.read_csv(root / "data/processed/sales_clean.csv")
    calendar = pd.read_csv(root / "data/processed/calendar_clean.csv")
    products = pd.read_csv(root / "data/processed/products_clean.csv")
    df = sales.merge(calendar, on="week_start", how="left").merge(products[["product_id"]], on="product_id", how="left")
    df["week_start"] = pd.to_datetime(df["week_start"])
    df = df.sort_values(["product_id", "week_start"]).copy()
    product_order = {pid: i for i, pid in enumerate(sorted(df["product_id"].unique()), start=1)}
    df["product_num"] = df["product_id"].map(product_order)
    g = df.groupby("product_id", group_keys=False)
    df["lag_1"] = g[TARGET].shift(1)
    df["lag_4"] = g[TARGET].shift(4)
    df["lag_8"] = g[TARGET].shift(8)
    df["rolling_mean_4"] = g[TARGET].shift(1).rolling(4).mean().reset_index(level=0, drop=True)
    df = df.dropna(subset=FEATURE_COLUMNS + [TARGET]).reset_index(drop=True)
    return df
