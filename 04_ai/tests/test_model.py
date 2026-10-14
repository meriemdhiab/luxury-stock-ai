import pandas as pd
import pytest

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


def _forecast_frame(product_id: str, weekly_units: list[float], stock: int, lead_time_days: int, minimum_stock: int) -> pd.DataFrame:
    return pd.DataFrame({
        "forecast_week_start": pd.date_range("2026-03-23", periods=len(weekly_units), freq="7D").strftime("%Y-%m-%d"),
        "product_id": product_id,
        "forecast_units": weekly_units,
        "closing_stock_units": stock,
        "lead_time_days": lead_time_days,
        "minimum_stock_units": minimum_stock,
    })


def test_reorder_point_covers_lead_time_demand_plus_minimum_stock():
    # Délai de 14 jours = 2 semaines : 10 + 12 unités, plus 5 de stock minimal -> point de commande 27.
    # Les 2 semaines suivantes (8 + 6 unités) s'ajoutent à la commande.
    forecasts = pd.concat([
        _forecast_frame("P001", [10, 12, 8, 6, 100], stock=20, lead_time_days=14, minimum_stock=5),
        _forecast_frame("P002", [10, 12, 8, 6, 100], stock=50, lead_time_days=14, minimum_stock=5),
    ])
    result = add_stock_recommendations(forecasts).drop_duplicates("product_id").set_index("product_id")
    assert result.loc["P001", "reorder_point_units"] == 27
    assert bool(result.loc["P001", "risk_of_stockout"])
    assert result.loc["P001", "recommended_replenishment_units"] == 27 + 14 - 20
    assert not bool(result.loc["P002", "risk_of_stockout"])
    assert result.loc["P002", "recommended_replenishment_units"] == 0


def test_partial_lead_time_week_counts_as_a_full_week():
    # 15 jours -> 3 semaines de demande pendant le délai.
    result = add_stock_recommendations(_forecast_frame("P001", [1, 2, 3, 4, 5], stock=0, lead_time_days=15, minimum_stock=0))
    assert (result["reorder_point_units"] == 6).all()
    assert (result["recommended_replenishment_units"] == 6 + 9).all()


def test_short_horizon_is_rejected():
    with pytest.raises(ValueError, match="horizon"):
        add_stock_recommendations(_forecast_frame("P001", [1, 2], stock=0, lead_time_days=14, minimum_stock=0))


def test_future_forecast_has_consistent_recommendations(project_root):
    from train import train
    from predict import predict_future

    train(project_root)
    forecasts = predict_future(project_root)
    assert len(forecasts) == 12 * forecasts["product_id"].nunique()
    assert (forecasts["forecast_units"] >= 0).all()
    per_product = forecasts.groupby("product_id")
    for column in ["reorder_point_units", "risk_of_stockout", "recommended_replenishment_units"]:
        assert per_product[column].nunique().eq(1).all()
    assert (forecasts["reorder_point_units"] >= forecasts["minimum_stock_units"]).all()
    at_risk = forecasts["risk_of_stockout"]
    assert (forecasts.loc[at_risk, "recommended_replenishment_units"] > 0).all()


def test_psi_counts_values_outside_reference_range():
    reference = list(range(100))
    shifted = [v + 1000 for v in reference]
    assert psi(reference, reference) < 1e-6
    assert psi(reference, shifted) > 1
