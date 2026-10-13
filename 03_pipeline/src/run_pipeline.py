from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import run_pipeline

if __name__ == "__main__":
    report = run_pipeline(ROOT)
    print(report)
