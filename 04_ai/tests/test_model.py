import pandas as pd

from check_drift import psi
from features import FEATURE_COLUMNS, TARGET, load_training_frame
from predict import add_stock_recommendations


def test_features_have_no_missing_values_after_warmup(project_root):
    df = load_training_frame(project_root)
    assert len(df) > 0
    assert df[FEATURE_COLUMNS].notna().all().all()


def test_lag_and_rolling_features_use_only_the_same_product_past(project_root):
    df = load_training_frame(project_root)
    sales = pd.read_csv(project_root / "data/processed/sales_clean.csv")
    sales["week_start"] = pd.to_datetime(sales["week_start"])
    sales = sales.sort_values(["product_id", "week_start"])
    grouped = sales.groupby("product_id")[TARGET]
    sales["expected_lag_1"] = grouped.shift(1)
    sales["expected_rolling"] = grouped.transform(lambda s: s.shift(1).rolling(4).mean())
    merged = df.merge(sales[["product_id", "week_start", "expected_lag_1", "expected_rolling"]], on=["product_id", "week_start"])
    assert len(merged) == len(df)
    assert (merged["lag_1"] == merged["expected_lag_1"]).all()
    assert (merged["rolling_mean_4"] - merged["expected_rolling"]).abs().max() < 1e-9


def test_temporal_split_is_present(project_root):
    df = load_training_frame(project_root)
    assert set(df["dataset_split"]) == {"TRAIN", "TEST"}
    assert df.loc[df["dataset_split"] == "TRAIN", "week_index"].max() < df.loc[df["dataset_split"] == "TEST", "week_index"].min()
    # Toutes les lignes de test sont évaluées (aucune perte liée aux variables).
    calendar = pd.read_csv(project_root / "data/processed/calendar_clean.csv")
    test_weeks = (calendar["dataset_split"] == "TEST").sum()
    assert (df["dataset_split"] == "TEST").sum() == test_weeks * df["product_id"].nunique()


def test_stock_recommendation_targets_two_weeks_of_cover():
    forecasts = pd.DataFrame({"forecast_units": [10.0, 10.0, 10.0], "closing_stock_units": [5, 20, 30]})
    result = add_stock_recommendations(forecasts)
    assert result["risk_of_stockout"].tolist() == [True, False, False]
    assert result["recommended_replenishment_units"].tolist() == [15, 0, 0]


def test_psi_counts_values_outside_reference_range():
    reference = list(range(100))
    shifted = [v + 1000 for v in reference]
    assert psi(reference, reference) < 1e-6
    assert psi(reference, shifted) > 1
