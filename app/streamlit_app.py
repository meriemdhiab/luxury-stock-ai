from __future__ import annotations

from pathlib import Path
import json
import sqlite3

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(page_title="Luxury Stock AI", page_icon="📦", layout="wide")
st.title("Luxury Stock AI")
st.caption("Prévision de la demande et aide à la décision pour une marque fictive de maroquinerie de luxe")

forecast_path = ROOT / "04_ai/forecast_future.csv"
metrics_path = ROOT / "04_ai/metrics.json"
db_path = ROOT / "database/luxury_stock_pipeline.sqlite"

if not forecast_path.exists():
    st.warning("Les prévisions ne sont pas encore disponibles. Exécutez le pipeline, l'entraînement et la prédiction.")
    st.code("python 03_pipeline/src/run_pipeline.py\npython 04_ai/src/train.py\npython 04_ai/src/evaluate.py\npython 04_ai/src/predict.py")
    st.stop()

forecast = pd.read_csv(forecast_path)
products_path = ROOT / "data/processed/products_clean.csv"
products = pd.read_csv(products_path) if products_path.exists() else pd.read_csv(ROOT / "data/raw/products.csv")
forecast = forecast.merge(products[["product_id", "product_name", "category", "collection"]], on="product_id", how="left")

with st.sidebar:
    st.header("Filtres")
    categories = sorted(forecast["category"].dropna().unique())
    category = st.selectbox("Catégorie", ["Toutes"] + categories)
    risk_only = st.checkbox("Afficher uniquement les risques de rupture")
    product_options = sorted(forecast["product_name"].dropna().unique())
    selected_products = st.multiselect("Produits", product_options)

view = forecast.copy()
if category != "Toutes": view = view[view["category"] == category]
if risk_only: view = view[view["risk_of_stockout"]]
if selected_products: view = view[view["product_name"].isin(selected_products)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Produits analysés", int(view["product_id"].nunique()))
col2.metric("Risques de rupture", int(view["risk_of_stockout"].sum()))
col3.metric("Unités prévues", int(view["forecast_units"].sum()))
col4.metric("Unités à réapprovisionner", int(view["recommended_replenishment_units"].sum()))

st.subheader("Prévisions et stock")
st.dataframe(view[["forecast_week_start", "product_name", "category", "forecast_units", "closing_stock_units", "risk_of_stockout", "recommended_replenishment_units"]], use_container_width=True)

chart = view.groupby("forecast_week_start", as_index=False).agg(forecast_units=("forecast_units", "sum"), replenishment=("recommended_replenishment_units", "sum"))
st.line_chart(chart.set_index("forecast_week_start"))

if metrics_path.exists():
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    st.subheader("Performance du modèle")
    st.json(metrics)

st.info("Les recommandations sont une aide à la décision. Une validation humaine reste nécessaire avant toute décision d'achat.")
