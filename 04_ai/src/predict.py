from __future__ import annotations

from pathlib import Path
import pickle
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import FEATURE_COLUMNS, MODEL_PATH, TARGET

# Couverture cible : le stock doit couvrir deux semaines de demande prévue.
TARGET_COVER_WEEKS = 2


def _feature_row(hist: list[float]) -> dict[str, float]:
    return {
        "lag_1": hist[-1],
        "lag_4": hist[-4] if len(hist) >= 4 else float(np.mean(hist)),
        "lag_8": hist[-8] if len(hist) >= 8 else float(np.mean(hist)),
        "rolling_mean_4": float(np.mean(hist[-4:])),
    }


def add_stock_recommendations(forecasts: pd.DataFrame) -> pd.DataFrame:
    target_stock = forecasts["forecast_units"] * TARGET_COVER_WEEKS
    forecasts["risk_of_stockout"] = forecasts["closing_stock_units"] < target_stock
    forecasts["recommended_replenishment_units"] = np.maximum(
        0, np.ceil(target_stock - forecasts["closing_stock_units"])
    ).astype(int)
    return forecasts


def predict_future(root: Path = ROOT) -> pd.DataFrame:
    processed = root / "data/processed"
    sales = pd.read_csv(processed / "sales_clean.csv")
    calendar = pd.read_csv(processed / "calendar_clean.csv")
    products = pd.read_csv(processed / "products_clean.csv")
    inventory = pd.read_csv(processed / "inventory_clean.csv")
    horizon = pd.read_csv(root / "data/raw/forecast_horizon.csv").sort_values("horizon_week")
    with (root / MODEL_PATH).open("rb") as f:
        artifact = pickle.load(f)
    model, order = artifact["model"], artifact["product_order"]

    history = {
        pid: g.sort_values("week_start")[TARGET].astype(float).tolist()
        for pid, g in sales.groupby("product_id")
    }
    product_ids = sorted(pid for pid in products["product_id"] if pid in history and pid in order)
    last_week_index = int(calendar["week_index"].max())

    # Prévision récursive : chaque semaine prédite alimente les retards de la suivante.
    rows = []
    for _, h in horizon.iterrows():
        d = pd.to_datetime(h["forecast_week_start"])
        calendar_features = {
            "week_index": last_week_index + int(h["horizon_week"]),
            "month": d.month,
            "quarter": (d.month - 1) // 3 + 1,
            "luxury_peak_flag": int(d.month in (11, 12)),
        }
        X = pd.DataFrame(
            [{"product_num": order[pid], **calendar_features, **_feature_row(history[pid])} for pid in product_ids]
        )[FEATURE_COLUMNS]
        week_forecast = np.maximum(0.0, model.predict(X))
        for pid, value in zip(product_ids, week_forecast):
            history[pid].append(float(value))
            rows.append({
                "forecast_week_start": h["forecast_week_start"],
                "product_id": pid,
                "forecast_units": round(float(value), 2),
                "model_name": "random_forest_regressor",
            })

    latest_stock = inventory.sort_values("week_start").groupby("product_id").tail(1)[["product_id", "closing_stock_units"]]
    forecasts = (
        pd.DataFrame(rows)
        .merge(latest_stock, on="product_id", how="left")
        .merge(products[["product_id", "lead_time_days", "minimum_stock_units"]], on="product_id", how="left")
    )
    forecasts = add_stock_recommendations(forecasts)
    forecasts.to_csv(root / "04_ai/forecast_future.csv", index=False)
    print(f"Prévisions futures générées: {len(forecasts)} lignes")
    return forecasts


if __name__ == "__main__":
    predict_future()
