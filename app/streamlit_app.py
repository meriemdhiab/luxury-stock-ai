from __future__ import annotations

from pathlib import Path
import json

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(page_title="Luxury Stock AI", page_icon="📦", layout="wide")
st.title("Luxury Stock AI")
st.caption("Prévision de la demande et aide à la décision pour une marque fictive de maroquinerie de luxe")

forecast_path = ROOT / "04_ai/forecast_future.csv"
metrics_path = ROOT / "04_ai/metrics.json"
products_path = ROOT / "data/processed/products_clean.csv"


@st.cache_data
def load_forecast(forecast_mtime: float) -> pd.DataFrame:
    # forecast_mtime invalide le cache quand predict.py régénère les prévisions.
    forecast = pd.read_csv(forecast_path)
    products = pd.read_csv(products_path if products_path.exists() else ROOT / "data/raw/products.csv")
    return forecast.merge(products[["product_id", "product_name", "category", "collection"]], on="product_id", how="left")


if not forecast_path.exists():
    st.warning("Les prévisions ne sont pas encore disponibles. Exécutez le pipeline, l'entraînement et la prédiction.")
    st.code("python 03_pipeline/src/run_pipeline.py\npython 04_ai/src/train.py\npython 04_ai/src/evaluate.py\npython 04_ai/src/predict.py")
    st.stop()

forecast = load_forecast(forecast_path.stat().st_mtime)

with st.sidebar:
    st.header("Filtres")
    categories = sorted(forecast["category"].dropna().unique())
    category = st.selectbox("Catégorie", ["Toutes"] + categories)
    risk_only = st.checkbox("Afficher uniquement les risques de rupture")
    product_options = sorted(forecast["product_name"].dropna().unique())
    selected_products = st.multiselect("Produits", product_options)

view = forecast.copy()
if category != "Toutes":
    view = view[view["category"] == category]
if risk_only:
    view = view[view["risk_of_stockout"]]
if selected_products:
    view = view[view["product_name"].isin(selected_products)]

# Le risque et la recommandation sont calculés par produit : une ligne par produit pour les agréger.
per_product = view.drop_duplicates("product_id")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Produits analysés", int(per_product["product_id"].nunique()))
col2.metric("Produits à risque de rupture", int(per_product["risk_of_stockout"].sum()))
col3.metric("Unités prévues (12 semaines)", int(view["forecast_units"].sum()))
col4.metric("Unités à réapprovisionner", int(per_product["recommended_replenishment_units"].sum()))

st.subheader("Recommandations par produit")
st.dataframe(
    per_product[[
        "product_name", "category", "closing_stock_units", "lead_time_days", "minimum_stock_units",
        "reorder_point_units", "risk_of_stockout", "recommended_replenishment_units",
    ]].sort_values("recommended_replenishment_units", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Prévisions hebdomadaires")
chart = view.groupby("forecast_week_start", as_index=False)["forecast_units"].sum()
st.line_chart(chart.set_index("forecast_week_start"))
st.dataframe(
    view[["forecast_week_start", "product_name", "category", "forecast_units"]],
    use_container_width=True,
    hide_index=True,
)

if metrics_path.exists():
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    st.subheader("Performance du modèle")
    st.json(metrics)

st.info("Les recommandations sont une aide à la décision. Une validation humaine reste nécessaire avant toute décision d'achat.")
