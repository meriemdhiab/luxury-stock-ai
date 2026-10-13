from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def psi(expected, actual, bins=10):
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    cuts = np.quantile(expected, np.linspace(0, 1, bins + 1))
    cuts = np.unique(cuts)
    if len(cuts) < 3:
        return 0.0
    e = np.histogram(expected, bins=cuts)[0] / len(expected)
    a = np.histogram(actual, bins=cuts)[0] / len(actual)
    e = np.clip(e, 1e-6, None); a = np.clip(a, 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))

sales = pd.read_csv(ROOT / 'data/processed/sales_clean.csv')
calendar = pd.read_csv(ROOT / 'data/processed/calendar_clean.csv')
joined = sales.merge(calendar[['week_start','dataset_split']], on='week_start')
train = joined.loc[joined.dataset_split == 'TRAIN', 'net_units_sold']
test = joined.loc[joined.dataset_split == 'TEST', 'net_units_sold']
value = psi(train, test)
report = {
    'status': 'OK' if value < 0.2 else 'WARNING' if value < 0.25 else 'ALERT',
    'metric': 'PSI',
    'value': round(value, 6),
    'thresholds': {'warning': 0.2, 'alert': 0.25},
    'reference_period': 'TRAIN',
    'comparison_period': 'TEST',
    'action': 'Surveiller' if value < 0.2 else 'Analyser la cause et envisager un réentraînement',
}
(ROOT / 'reports/drift_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
