# Script vidéo, Bloc 3

Durée cible : 3 à 5 minutes.

1. Afficher le dépôt et les fichiers `data/raw`.
2. Ouvrir `03_pipeline/src/pipeline.py` et présenter les contrôles.
3. Lancer `python 03_pipeline/src/run_pipeline.py`.
4. Montrer les logs de traitement.
5. Ouvrir `data/processed/quality_report.json`.
6. Ouvrir `data/processed/sales_quarantine.csv` et montrer les anomalies isolées.
7. Vérifier `sales_clean.csv`.
8. Montrer la création de `database/luxury_stock_pipeline.sqlite`.
9. Exécuter une requête simple sur la vue d'entraînement.
10. Conclure sur la reproductibilité et la traçabilité.

Pour montrer des anomalies de manière reproductible, lancer `python 03_pipeline/src/run_quality_fixture.py` plutôt que de modifier les données principales.
