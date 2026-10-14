from pathlib import Path
import json
import logging
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import run_pipeline

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    report = run_pipeline(ROOT)
    print(json.dumps(report, ensure_ascii=False, indent=2))
