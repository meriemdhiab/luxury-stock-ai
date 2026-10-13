# Pipeline détaillé

## Étapes

1. Génération ou réception des données sources.
2. Validation des schémas et règles métier.
3. Nettoyage, dédoublonnage et quarantaine.
4. Chargement dans SQLite ou PostgreSQL.
5. Création des variables retardées.
6. Entraînement de la baseline et du modèle candidat.
7. Évaluation temporelle.
8. Prévisions futures.
9. Calcul des risques de rupture et recommandations.
10. Génération des rapports et restitution Streamlit.

## Commandes principales

```bash
python scripts/generate_data.py
python 03_pipeline/src/run_pipeline.py
python 04_ai/src/train.py
python 04_ai/src/evaluate.py
python 04_ai/src/predict.py
python scripts/generate_reports.py
streamlit run app/streamlit_app.py
```

## Démonstration qualité

```bash
python 03_pipeline/src/run_quality_fixture.py
```
