from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WARNING_THRESHOLD = 0.2
ALERT_THRESHOLD = 0.25


def psi(expected, actual, bins: int = 10) -> float:
    """Population Stability Index entre une distribution de référence et une distribution observée."""
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    cuts = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if len(cuts) < 3:
        return 0.0
    # Bornes ouvertes : les valeurs observées hors de la plage de référence doivent compter.
    cuts[0], cuts[-1] = -np.inf, np.inf
    e = np.histogram(expected, bins=cuts)[0] / len(expected)
    a = np.histogram(actual, bins=cuts)[0] / len(actual)
    e = np.clip(e, 1e-6, None)
    a = np.clip(a, 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))


def drift_status(value: float) -> str:
    if value < WARNING_THRESHOLD:
        return "OK"
    return "WARNING" if value < ALERT_THRESHOLD else "ALERT"


def main(root: Path = ROOT) -> dict:
    sales = pd.read_csv(root / "data/processed/sales_clean.csv")
    calendar = pd.read_csv(root / "data/processed/calendar_clean.csv")
    joined = sales.merge(calendar[["week_start", "dataset_split"]], on="week_start")
    train = joined.loc[joined["dataset_split"] == "TRAIN", "net_units_sold"]
    test = joined.loc[joined["dataset_split"] == "TEST", "net_units_sold"]
    value = psi(train, test)
    status = drift_status(value)
    report = {
        "status": status,
        "metric": "PSI",
        "value": round(value, 6),
        "thresholds": {"warning": WARNING_THRESHOLD, "alert": ALERT_THRESHOLD},
        "reference_period": "TRAIN",
        "comparison_period": "TEST",
        "action": "Surveiller" if status == "OK" else "Analyser la cause et envisager un réentraînement",
    }
    (root / "reports/drift_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    main()
