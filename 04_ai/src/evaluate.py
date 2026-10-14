from __future__ import annotations

from pathlib import Path
import json
import pickle
import sys

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import FEATURE_COLUMNS, MODEL_PATH, TARGET, load_training_frame


def _scores(y_true, y_pred) -> dict[str, float]:
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "rmse": round(float(mean_squared_error(y_true, y_pred) ** 0.5), 4),
    }


def evaluate(root: Path = ROOT) -> dict:
    df = load_training_frame(root)
    test_df = df[df["dataset_split"] == "TEST"].copy()
    train_weeks = int(df.loc[df["dataset_split"] == "TRAIN", "week_start"].nunique())
    test_weeks = int(test_df["week_start"].nunique())

    with (root / MODEL_PATH).open("rb") as f:
        model = pickle.load(f)["model"]
    test_df["candidate_prediction"] = np.maximum(0, model.predict(test_df[FEATURE_COLUMNS]))
    test_df["baseline_prediction"] = np.maximum(0, test_df["rolling_mean_4"])

    test_df[["week_start", "product_id", TARGET, "baseline_prediction", "candidate_prediction"]].to_csv(
        root / "04_ai/predictions_test.csv", index=False
    )

    baseline = _scores(test_df[TARGET], test_df["baseline_prediction"])
    candidate = _scores(test_df[TARGET], test_df["candidate_prediction"])
    improvement = (baseline["mae"] - candidate["mae"]) / baseline["mae"] * 100 if baseline["mae"] else 0.0
    metrics = {
        "evaluation_protocol": (
            f"Temporal split, {train_weeks} train weeks (after 8-week warm-up) and {test_weeks} test weeks, "
            "one-step-ahead (lags use observed values)"
        ),
        "target": TARGET,
        "baseline": {"name": "rolling_mean_4", **baseline},
        "candidate": {"name": "random_forest_regressor", **candidate},
        "improvement_mae_percent": round(improvement, 2),
        "test_rows": int(len(test_df)),
    }
    (root / "04_ai/metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return metrics


if __name__ == "__main__":
    evaluate()
