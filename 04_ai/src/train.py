from __future__ import annotations

from pathlib import Path
import pickle
import sys

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import FEATURE_COLUMNS, TARGET, load_training_frame

MODEL_DIR = ROOT / "04_ai/models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train(root: Path = ROOT):
    df = load_training_frame(root)
    train_df = df[df["dataset_split"] == "TRAIN"].copy()
    X = train_df[FEATURE_COLUMNS]
    y = train_df[TARGET]
    model = RandomForestRegressor(
        n_estimators=160,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y)
    artifact = {"model": model, "feature_columns": FEATURE_COLUMNS, "target": TARGET, "random_state": 42}
    with (MODEL_DIR / "candidate_model.pkl").open("wb") as f:
        pickle.dump(artifact, f)
    print(f"Modèle entraîné sur {len(train_df)} lignes")
    return artifact

if __name__ == "__main__":
    train()
