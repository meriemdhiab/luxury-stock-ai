from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RETRAINING_STEPS = [
    "03_pipeline/src/run_pipeline.py",
    "04_ai/src/train.py",
    "04_ai/src/evaluate.py",
    "04_ai/src/predict.py",
    "scripts/generate_reports.py",
    "scripts/check_drift.py",
]


def run(script: str) -> None:
    print(">", script)
    subprocess.run([sys.executable, script], cwd=ROOT, check=True)


def should_retrain(root: Path = ROOT) -> bool:
    monitor_path = root / "reports/monitoring_report.json"
    drift_path = root / "reports/drift_report.json"
    if not monitor_path.exists() or not drift_path.exists():
        print("Rapports de monitoring absents, exécution du pipeline de référence.")
        return True
    monitoring = json.loads(monitor_path.read_text(encoding="utf-8"))
    drift = json.loads(drift_path.read_text(encoding="utf-8"))
    return monitoring.get("status") != "ok" or drift.get("status") in {"WARNING", "ALERT"}


def main() -> None:
    if not should_retrain():
        print("Aucun réentraînement nécessaire selon les seuils actuels.")
        return
    for script in RETRAINING_STEPS:
        run(script)
    print("Réentraînement exécuté.")


if __name__ == "__main__":
    main()
