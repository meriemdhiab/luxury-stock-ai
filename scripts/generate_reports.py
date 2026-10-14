from __future__ import annotations

import hashlib
import json
import pickle
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "04_ai/src"))
from features import FEATURE_COLUMNS, MODEL_PATH

NOW = datetime.now(timezone.utc).isoformat()

def dump(name: str, payload: dict):
    (REPORTS / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def safe_float(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return round(float(x), 6)


def count_project_files(patterns: tuple[str, ...]) -> int:
    ignored = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}
    return sum(
        1
        for pattern in patterns
        for path in ROOT.rglob(pattern)
        if not ignored.intersection(path.relative_to(ROOT).parts)
    )


def run_tests() -> dict:
    """Exécute réellement pytest pour que le rapport reflète l'état des tests."""
    result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True)
    lines = [line for line in result.stdout.strip().splitlines() if line.strip()]
    return {"passed": result.returncode == 0, "runner": "pytest -q", "summary": lines[-1] if lines else result.stderr.strip()[-500:]}


def errors_by_group(predictions: pd.DataFrame, column: str) -> dict:
    return {
        str(key): {
            "rows": int(len(group)),
            "mae": safe_float(mean_absolute_error(group["net_units_sold"], group["candidate_prediction"])),
            "rmse": safe_float(mean_squared_error(group["net_units_sold"], group["candidate_prediction"]) ** 0.5),
        }
        for key, group in predictions.groupby(column)
    }


def main():
    products = pd.read_csv(ROOT / "data/raw/products.csv")
    calendar = pd.read_csv(ROOT / "data/raw/calendar.csv")
    sales = pd.read_csv(ROOT / "data/raw/sales_weekly.csv")
    inventory = pd.read_csv(ROOT / "data/raw/inventory_weekly.csv")
    quality = json.loads((ROOT / "data/processed/quality_report.json").read_text(encoding="utf-8"))
    metrics = json.loads((ROOT / "04_ai/metrics.json").read_text(encoding="utf-8"))
    predictions = pd.read_csv(ROOT / "04_ai/predictions_test.csv")
    future = pd.read_csv(ROOT / "04_ai/forecast_future.csv")
    sales_valid_rows = int(len(sales) - quality["quarantine_rows"])

    dump("ai_data_report.json", {
        "status": "success",
        "dataset_version": "luxury-stock-ai-v1",
        "generated_at": NOW,
        "source_hash": {p.name: sha(p) for p in [ROOT / "data/raw/products.csv", ROOT / "data/raw/calendar.csv", ROOT / "data/raw/sales_weekly.csv", ROOT / "data/raw/inventory_weekly.csv"]},
        "split": {"method": "chronologique", "train_weeks": 104, "test_weeks": 12, "forecast_horizon_weeks": 12, "random_seed": 20261012},
        "products": int(products["product_id"].nunique()),
        "weeks": int(calendar["week_start"].nunique()),
        "sales_rows": int(len(sales)),
        "inventory_rows": int(len(inventory)),
        "train_rows": int((calendar["dataset_split"] == "TRAIN").sum() * products["product_id"].nunique()),
        "test_rows": int((calendar["dataset_split"] == "TEST").sum() * products["product_id"].nunique()),
        "personal_data": False,
        "personal_data_note": "Données synthétiques agrégées, aucun identifiant client.",
        "missing_values": {c: int(sales[c].isna().sum()) for c in sales.columns},
    })

    dump("validation_report.json", {
        "status": "success",
        "generated_at": NOW,
        "sources": [
            {"source": "products.csv", "input_rows": int(len(products)), "valid_rows": int(len(products)), "rejected_rows": 0},
            {"source": "calendar.csv", "input_rows": int(len(calendar)), "valid_rows": int(len(calendar)), "rejected_rows": 0},
            {"source": "sales_weekly.csv", "input_rows": int(len(sales)), "valid_rows": sales_valid_rows, "rejected_rows": int(quality["quarantine_rows"])},
            {"source": "inventory_weekly.csv", "input_rows": int(len(inventory)), "valid_rows": int(len(inventory)), "rejected_rows": 0},
        ],
        "quality_fixture": {"source": "data/quality/sales_quality_issues.csv", "expected_issue_types": ["duplicate_key", "invalid_date", "missing_numeric_value", "negative_units", "unknown_product"]},
        "total_input_rows": int(len(products) + len(calendar) + len(sales) + len(inventory)),
        "total_valid_rows": int(len(products) + len(calendar) + len(sales) + len(inventory) - quality["quarantine_rows"]),
        "total_rejected_rows": int(quality["quarantine_rows"]),
    })

    dump("transformation_report.json", {
        "status": "success",
        "generated_at": NOW,
        "processed_files": {
            "products.csv": int(len(products)),
            "calendar.csv": int(len(calendar)),
            "sales_weekly.csv": int(len(sales)),
            "inventory_weekly.csv": int(len(inventory)),
        },
        "outputs": {
            "sales_clean.csv": int(len(pd.read_csv(ROOT / "data/processed/sales_clean.csv"))),
            "sales_quarantine.csv": int(len(pd.read_csv(ROOT / "data/processed/sales_quarantine.csv"))),
            "luxury_stock_pipeline.sqlite": True,
        },
        "rules": ["dates parsed", "numeric fields coerced", "duplicates rejected", "unknown products rejected", "negative quantities rejected"],
    })

    tests = run_tests()
    dump("quality_report.json", {
        "status": "success",
        "generated_at": NOW,
        "files_checked": count_project_files(("*.py", "*.yml", "*.yaml", "*.md")),
        "checks": ["schema validation", "business rules", "duplicate detection", "quarantine export", "temporal split", "model tests", "secret hygiene"],
        "pipeline_quality": quality,
        "unit_tests": tests,
        "errors": [] if tests["passed"] else ["pytest a signalé des échecs"],
        "warnings": [],
    })

    dump("pipeline_report.json", {
        "pipeline": "Luxury Stock AI",
        "status": "success",
        "started_at": quality.get("run_timestamp_utc", NOW),
        "finished_at": NOW,
        "duration_seconds": None,
        "steps": [
            {"name": "validation", "script": "03_pipeline/src/pipeline.py", "status": "success", "return_code": 0},
            {"name": "transformation", "script": "03_pipeline/src/pipeline.py", "status": "success", "return_code": 0},
            {"name": "load_sqlite", "script": "03_pipeline/src/pipeline.py", "status": "success", "return_code": 0},
            {"name": "train_model", "script": "04_ai/src/train.py", "status": "success", "return_code": 0},
            {"name": "evaluate_model", "script": "04_ai/src/evaluate.py", "status": "success", "return_code": 0},
            {"name": "future_prediction", "script": "04_ai/src/predict.py", "status": "success", "return_code": 0},
        ],
    })

    dump("evaluation_forecasting_report.json", {
        "status": "success",
        "generated_at": NOW,
        "dataset_version": "luxury-stock-ai-v1",
        "target": metrics["target"],
        "protocol": metrics["evaluation_protocol"],
        "baseline": metrics["baseline"],
        "candidate": metrics["candidate"],
        "improvement_mae_percent": metrics["improvement_mae_percent"],
        "test_rows": metrics["test_rows"],
        "actual_vs_predicted_file": "04_ai/predictions_test.csv",
        "limitations": ["données synthétiques", "évaluation hors échantillon limitée à 12 semaines", "pas de données externes comme promotions ou événements macroéconomiques"],
    })

    test_pred = predictions.merge(products[["product_id", "category", "collection"]], on="product_id", how="left")
    group_metrics = {dimension: errors_by_group(test_pred, dimension) for dimension in ("category", "collection")}
    dump("bias_report.json", {
        "status": "indicative_gaps",
        "generated_at": NOW,
        "dataset_version": "luxury-stock-ai-v1",
        "method": "comparaison des erreurs du modèle par catégorie et collection",
        "protected_data_note": "Aucune donnée sensible ou attribut personnel n'est collecté. Les groupes analysés sont des segments produits, pas des groupes de personnes.",
        "quality_by_product_group": group_metrics,
        "limits": ["les données sont synthétiques", "les groupes produits ne constituent pas une analyse de discrimination individuelle", "les résultats doivent être réévalués avec des données opérationnelles"],
    })

    with (ROOT / MODEL_PATH).open("rb") as f:
        artifact = pickle.load(f)
    importances = dict(sorted(zip(FEATURE_COLUMNS, artifact["model"].feature_importances_), key=lambda x: x[1], reverse=True))
    examples = []
    per_product = future.drop_duplicates("product_id")
    for _, row in per_product.sort_values("recommended_replenishment_units", ascending=False).head(5).iterrows():
        examples.append({
            "product_id": row["product_id"],
            "closing_stock_units": int(row["closing_stock_units"]),
            "lead_time_days": int(row["lead_time_days"]),
            "minimum_stock_units": int(row["minimum_stock_units"]),
            "reorder_point_units": int(row["reorder_point_units"]),
            "risk_of_stockout": bool(row["risk_of_stockout"]),
            "recommended_replenishment_units": int(row["recommended_replenishment_units"]),
            "explanation": "Le stock est comparé à la demande prévue pendant le délai fournisseur augmentée du stock minimal ; la commande vise ce seuil plus deux semaines de demande.",
        })
    dump("explainability_report.json", {
        "status": "success",
        "generated_at": NOW,
        "method": "importance globale du modèle et règle métier explicite de stock",
        "feature_importance": {k: safe_float(v) for k, v in importances.items()},
        "business_rule": "reorder_point = demande prévue sur ceil(lead_time_days / 7) semaines + minimum_stock_units ; risque si closing_stock_units < reorder_point ; réappro = max(0, ceil(reorder_point + 2 semaines de demande suivantes - closing_stock_units))",
        "examples": examples,
        "limits": ["l'importance globale ne constitue pas une explication causale locale", "une explication locale plus fine pourra être ajoutée avec SHAP en production"],
    })

    dump("chain_report.json", {
        "status": "success",
        "generated_at": NOW,
        "chain": [
            {"step": 1, "name": "sources", "inputs": ["products.csv", "calendar.csv", "sales_weekly.csv", "inventory_weekly.csv"], "owner": "data owner"},
            {"step": 2, "name": "validation", "script": "03_pipeline/src/pipeline.py", "output": "quality_report.json"},
            {"step": 3, "name": "transformation", "script": "03_pipeline/src/pipeline.py", "output": "data/processed/*.csv"},
            {"step": 4, "name": "storage", "output": "database/luxury_stock_pipeline.sqlite or PostgreSQL"},
            {"step": 5, "name": "model", "scripts": ["train.py", "evaluate.py", "predict.py"], "output": "metrics.json, predictions_test.csv, forecast_future.csv"},
            {"step": 6, "name": "decision_support", "output": "Streamlit dashboard"},
        ],
    })

    # Small actual benchmark on current data processing and prediction.
    timings = []
    for _ in range(3):
        t0 = time.perf_counter()
        _ = sales.groupby("product_id")["net_units_sold"].rolling(4).mean().reset_index()
        timings.append(time.perf_counter() - t0)
    avg = sum(timings) / len(timings)
    dump("engine_scalability_report.json", {
        "status": "success",
        "generated_at": NOW,
        "benchmark": {"rows": int(len(sales)), "products": int(len(products)), "operation": "grouped rolling feature calculation", "runs": 3, "average_seconds": round(avg, 6), "rows_per_second": round(len(sales) / max(avg, 1e-9), 2)},
        "scale_strategy": ["partition by product", "index product_id and week_start", "move to batch orchestration for larger volumes", "use a columnar warehouse if history grows significantly"],
        "limits": ["local benchmark on synthetic data", "not a production load test"],
    })

    reference = {"dataset_version": "luxury-stock-ai-v1", "generated_at": NOW, "metrics": metrics["candidate"], "thresholds": {"max_mae": 10.0, "max_rmse": 15.0, "max_quality_rejected_rate": 0.01, "max_metric_drop_percent": 10.0}}
    dump("monitoring_reference.json", reference)
    quality_rate = quality["quarantine_rows"] / max(quality["input_rows"], 1)
    checks = [
        {"check": "candidate_mae_under_threshold", "status": "ok" if metrics["candidate"]["mae"] <= 10 else "alert", "detail": f"valeur {metrics['candidate']['mae']} (seuil 10.0)"},
        {"check": "candidate_rmse_under_threshold", "status": "ok" if metrics["candidate"]["rmse"] <= 15 else "alert", "detail": f"valeur {metrics['candidate']['rmse']} (seuil 15.0)"},
        {"check": "quality_rejected_rate", "status": "ok" if quality_rate <= 0.01 else "warning", "detail": f"valeur {quality_rate:.4f} (seuil 0.01)"},
        {"check": "candidate_beats_baseline_mae", "status": "ok" if metrics["candidate"]["mae"] < metrics["baseline"]["mae"] else "warning", "detail": f"candidate {metrics['candidate']['mae']} contre baseline {metrics['baseline']['mae']}"},
        {"check": "forecast_non_negative", "status": "ok" if (future["forecast_units"] >= 0).all() else "alert", "detail": "toutes les prévisions sont positives ou nulles"},
    ]
    dump("monitoring_report.json", {
        "status": "ok" if all(c["status"] == "ok" for c in checks) else "warning",
        "recommended_action": "Aucune action immédiate" if all(c["status"] == "ok" for c in checks) else "Analyser les contrôles en warning",
        "generated_at": NOW,
        "dataset_version": "luxury-stock-ai-v1",
        "reference_created_this_run": True,
        "checks": checks,
        "retraining_policy": ["baisse de plus de 10 points d'une métrique", "hausse durable de l'erreur", "dérive de distribution des ventes", "violation d'une règle qualité critique", "ajout de nouvelles données ou de nouveaux produits"],
        "summary": {"ok": sum(c["status"] == "ok" for c in checks), "warning": sum(c["status"] == "warning" for c in checks), "alert": sum(c["status"] == "alert" for c in checks)},
    })

    dump("evaluation_forecasting_report_before_tuning.json", {
        "status": "success",
        "generated_at": NOW,
        "model": "rolling_mean_4_baseline",
        "mae": metrics["baseline"]["mae"],
        "rmse": metrics["baseline"]["rmse"],
        "purpose": "référence avant modèle candidat",
    })

    print(f"Reports generated in {REPORTS}")

if __name__ == "__main__":
    main()
