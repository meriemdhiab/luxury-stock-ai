from pathlib import Path
import json
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import clean_sales

if __name__ == "__main__":
    out_dir = ROOT / "data/processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    products = pd.read_csv(ROOT / "data/raw/products.csv")
    sales = pd.read_csv(ROOT / "data/quality/sales_quality_issues.csv")
    clean, quarantine, report = clean_sales(sales, products)
    clean.to_csv(out_dir / "quality_demo_sales_clean.csv", index=False)
    quarantine.to_csv(out_dir / "quality_demo_sales_quarantine.csv", index=False)
    (out_dir / "quality_demo_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
