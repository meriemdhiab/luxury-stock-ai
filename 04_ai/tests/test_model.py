from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_ai/src"))
from features import load_training_frame


def test_features_have_no_missing_values_after_warmup():
    df = load_training_frame(ROOT)
    assert len(df) > 0
    assert df[["lag_1", "lag_4", "lag_8", "rolling_mean_4"]].notna().all().all()


def test_temporal_split_is_present():
    df = load_training_frame(ROOT)
    assert set(df["dataset_split"]) == {"TRAIN", "TEST"}
    assert df.loc[df["dataset_split"] == "TRAIN", "week_index"].max() < df.loc[df["dataset_split"] == "TEST", "week_index"].min()
