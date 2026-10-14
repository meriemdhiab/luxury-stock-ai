from __future__ import annotations

from pathlib import Path

import pandas as pd

FEATURE_COLUMNS = [
    "product_num", "week_index", "month", "quarter", "luxury_peak_flag",
    "lag_1", "lag_4", "lag_8", "rolling_mean_4",
]
TARGET = "net_units_sold"
MODEL_PATH = Path("04_ai/models/candidate_model.pkl")


def product_order(product_ids) -> dict[str, int]:
    """Encodage stable produit -> entier, partagé par l'entraînement et la prédiction."""
    return {pid: i for i, pid in enumerate(sorted(set(product_ids)), start=1)}


def load_training_frame(root: Path) -> pd.DataFrame:
    processed = root / "data/processed"
    sales = pd.read_csv(processed / "sales_clean.csv")
    calendar = pd.read_csv(processed / "calendar_clean.csv")
    products = pd.read_csv(processed / "products_clean.csv")

    df = sales.merge(calendar, on="week_start", how="left")
    df["week_start"] = pd.to_datetime(df["week_start"])
    df = df.sort_values(["product_id", "week_start"]).reset_index(drop=True)
    df["product_num"] = df["product_id"].map(product_order(products["product_id"]))

    # Toutes les variables ne regardent que le passé du produit (shift avant rolling).
    previous = df.groupby("product_id")[TARGET].shift(1)
    df["lag_1"] = previous
    df["lag_4"] = df.groupby("product_id")[TARGET].shift(4)
    df["lag_8"] = df.groupby("product_id")[TARGET].shift(8)
    df["rolling_mean_4"] = previous.groupby(df["product_id"]).transform(lambda s: s.rolling(4).mean())

    return df.dropna(subset=FEATURE_COLUMNS + [TARGET]).reset_index(drop=True)
