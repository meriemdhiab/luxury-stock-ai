from __future__ import annotations

from pathlib import Path
import pickle
import sys

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import FEATURE_COLUMNS, MODEL_PATH, TARGET, load_training_frame, product_order

RANDOM_STATE = 42


def train(root: Path = ROOT) -> dict:
    df = load_training_frame(root)
    train_df = df[df["dataset_split"] == "TRAIN"]
    model = RandomForestRegressor(
        n_estimators=160,
        max_depth=12,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(train_df[FEATURE_COLUMNS], train_df[TARGET])

    products = pd.read_csv(root / "data/processed/products_clean.csv")
    artifact = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "target": TARGET,
        "random_state": RANDOM_STATE,
        "product_order": product_order(products["product_id"]),
        "train_rows": int(len(train_df)),
    }
    model_path = root / MODEL_PATH
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with model_path.open("wb") as f:
        pickle.dump(artifact, f)
    print(f"Modèle entraîné sur {len(train_df)} lignes")
    return artifact


if __name__ == "__main__":
    train()
