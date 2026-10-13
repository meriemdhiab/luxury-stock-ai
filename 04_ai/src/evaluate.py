from __future__ import annotations

from pathlib import Path
import json
import pickle
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import FEATURE_COLUMNS, TARGET, load_training_frame


def evaluate(root: Path = ROOT):
    df = load_training_frame(root)
    test_df = df[df["dataset_split"] == "TEST"].copy()
    with (root / "04_ai/models/candidate_model.pkl").open("rb") as f:
        artifact = pickle.load(f)
    model = artifact["model"]
    test_df["candidate_prediction"] = np.maximum(0, model.predict(test_df[FEATURE_COLUMNS]))
    test_df["baseline_prediction"] = np.maximum(0, test_df["rolling_mean_4"])
    baseline_mae = mean_absolute_error(test_df[TARGET], test_df["baseline_prediction"])
    baseline_rmse = mean_squared_error(test_df[TARGET], test_df["baseline_prediction"]) ** 0.5
    candidate_mae = mean_absolute_error(test_df[TARGET], test_df["candidate_prediction"])
    candidate_rmse = mean_squared_error(test_df[TARGET], test_df["candidate_prediction"]) ** 0.5
    predictions = test_df[["week_start", "product_id", TARGET, "baseline_prediction", "candidate_prediction"]]
    predictions.to_csv(root / "04_ai/predictions_test.csv", index=False)
    metrics = {
        "evaluation_protocol": "Temporal split, 104 train weeks and 12 test weeks",
        "target": TARGET,
        "baseline": {"name": "rolling_mean_4", "mae": round(float(baseline_mae), 4), "rmse": round(float(baseline_rmse), 4)},
        "candidate": {"name": "random_forest_regressor", "mae": round(float(candidate_mae), 4), "rmse": round(float(candidate_rmse), 4)},
        "improvement_mae_percent": round(float((baseline_mae - candidate_mae) / baseline_mae * 100), 2) if baseline_mae else 0.0,
        "test_rows": int(len(test_df)),
    }
    (root / "04_ai/metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return metrics

if __name__ == "__main__":
    evaluate()
