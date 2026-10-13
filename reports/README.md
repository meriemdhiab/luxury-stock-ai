# Rapports de preuve

Ce dossier rassemble les rapports JSON générés automatiquement, sur le modèle d'un dossier de preuves d'un projet data/IA professionnel.

## Rapports disponibles

- `ai_data_report.json` : profil du jeu de données, split et hashes sources.
- `validation_report.json` : lignes valides et rejetées par source.
- `transformation_report.json` : sorties nettoyées et règles appliquées.
- `quality_report.json` : contrôles de qualité, tests et avertissements.
- `pipeline_report.json` : chaîne d'exécution et statut des étapes.
- `evaluation_forecasting_report.json` : comparaison baseline/modèle candidat.
- `evaluation_forecasting_report_before_tuning.json` : résultats de la baseline.
- `bias_report.json` : écarts indicatifs par segment produit, sans données sensibles.
- `explainability_report.json` : importance des variables et exemples de décisions.
- `chain_report.json` : traçabilité sources, transformations, modèle et application.
- `engine_scalability_report.json` : benchmark local et stratégie de passage à l'échelle.
- `monitoring_reference.json` : référence de suivi du modèle.
- `monitoring_report.json` : contrôles de supervision et politique de réentraînement.
- `drift_report.json` : détection indicative de dérive par PSI entre TRAIN et TEST.

## Régénération

Depuis la racine du projet :

```bash
python 03_pipeline/src/run_pipeline.py
python 04_ai/src/train.py
python 04_ai/src/evaluate.py
python 04_ai/src/predict.py
python scripts/generate_reports.py
```

Les rapports reflètent les métriques réellement produites par cette exécution. Ils ne doivent pas être modifiés manuellement pour embellir un résultat.
