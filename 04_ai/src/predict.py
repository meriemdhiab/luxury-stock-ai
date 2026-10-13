from __future__ import annotations

from pathlib import Path
import pickle
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import FEATURE_COLUMNS


def predict_future(root: Path = ROOT):
    sales = pd.read_csv(root / "data/processed/sales_clean.csv")
    calendar = pd.read_csv(root / "data/processed/calendar_clean.csv")
    products = pd.read_csv(root / "data/processed/products_clean.csv")
    horizon = pd.read_csv(root / "data/raw/forecast_horizon.csv")
    with (root / "04_ai/models/candidate_model.pkl").open("rb") as f:
        artifact = pickle.load(f)
    model = artifact["model"]
    product_order = {pid: i for i, pid in enumerate(sorted(products["product_id"]), start=1)}
    history = {pid: list(g.sort_values("week_start")["net_units_sold"].astype(float)) for pid, g in sales.groupby("product_id")}
    rows = []
    last_week_index = int(calendar["week_index"].max())
    for _, h in horizon.iterrows():
        week_index = last_week_index + int(h["horizon_week"])
        d = pd.to_datetime(h["forecast_week_start"])
        month = int(d.month)
        quarter = (month - 1) // 3 + 1
        peak = 1 if month in (11, 12) else 0
        for pid in sorted(products["product_id"]):
            hist = history[pid]
            lag_1 = hist[-1]
            lag_4 = hist[-4] if len(hist) >= 4 else float(np.mean(hist))
            lag_8 = hist[-8] if len(hist) >= 8 else float(np.mean(hist))
            rolling = float(np.mean(hist[-4:]))
            features = pd.DataFrame([{
                "product_num": product_order[pid], "week_index": week_index, "month": month,
                "quarter": quarter, "luxury_peak_flag": peak, "lag_1": lag_1,
                "lag_4": lag_4, "lag_8": lag_8, "rolling_mean_4": rolling,
            }])[FEATURE_COLUMNS]
            forecast = max(0.0, float(model.predict(features)[0]))
            hist.append(forecast)
            rows.append({"forecast_week_start": h["forecast_week_start"], "product_id": pid, "forecast_units": round(forecast, 2), "model_name": "random_forest_regressor"})
    forecasts = pd.DataFrame(rows)
    inv = pd.read_csv(root / "data/processed/inventory_clean.csv")
    latest = inv.sort_values("week_start").groupby("product_id").tail(1)[["product_id", "closing_stock_units"]]
    forecasts = forecasts.merge(latest, on="product_id", how="left")
    products_small = products[["product_id", "lead_time_days", "minimum_stock_units"]]
    forecasts = forecasts.merge(products_small, on="product_id", how="left")
    forecasts["risk_of_stockout"] = forecasts["closing_stock_units"] < forecasts["forecast_units"]
    forecasts["recommended_replenishment_units"] = np.maximum(0, np.ceil(forecasts["forecast_units"] * 2 - forecasts["closing_stock_units"]))
    forecasts.to_csv(root / "04_ai/forecast_future.csv", index=False)
    print(f"Prévisions futures générées: {len(forecasts)} lignes")
    return forecasts

if __name__ == "__main__":
    predict_future()
