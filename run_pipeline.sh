#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python scripts/generate_data.py
python 03_pipeline/src/run_pipeline.py
python 04_ai/src/train.py
python 04_ai/src/evaluate.py
python 04_ai/src/predict.py
python scripts/generate_reports.py
python scripts/check_drift.py
