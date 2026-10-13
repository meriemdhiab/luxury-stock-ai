from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def run(command):
    print('>', ' '.join(command))
    subprocess.run(command, cwd=ROOT, check=True)

monitor_path = ROOT / 'reports/monitoring_report.json'
drift_path = ROOT / 'reports/drift_report.json'
if not monitor_path.exists() or not drift_path.exists():
    print('Rapports de monitoring absents, exécution du pipeline de référence.')
    should_retrain = True
else:
    monitoring = json.loads(monitor_path.read_text(encoding='utf-8'))
    drift = json.loads(drift_path.read_text(encoding='utf-8'))
    should_retrain = monitoring.get('status') == 'warning' or drift.get('status') in {'WARNING', 'ALERT'}
if should_retrain:
    run([sys.executable, '03_pipeline/src/run_pipeline.py'])
    run([sys.executable, '04_ai/src/train.py'])
    run([sys.executable, '04_ai/src/evaluate.py'])
    run([sys.executable, '04_ai/src/predict.py'])
    run([sys.executable, 'scripts/generate_reports.py'])
    run([sys.executable, 'scripts/check_drift.py'])
    print('Réentraînement exécuté.')
else:
    print('Aucun réentraînement nécessaire selon les seuils actuels.')
