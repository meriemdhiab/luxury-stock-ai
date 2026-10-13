# Matrice de traçabilité des preuves

| Bloc | Attente | Preuve principale | Preuve secondaire |
|---|---|---|---|
| 1 | Réglementation et risques | `plan_gouvernance.pdf` | `ai_risk_register.xlsx` |
| 1 | Parties prenantes et responsabilités | `controls.md` | présentation bloc 1 |
| 1 | Qualité et traçabilité | `data_dictionary.xlsx`, `data_lineage.png` | `quality_report.json` |
| 1 | Documentation compréhensible | plan PDF | slides |
| 2 | Adéquation de l'architecture | `architecture.png` | décisions techniques |
| 2 | Scalabilité et disponibilité | schéma et ADR | configuration Docker |
| 2 | Sécurité et accès | contrôles + schéma SQL | `.env.example` |
| 2 | Qualité du code | dépôt `scripts/` | README |
| 3 | Performance et gestion des erreurs | `quality_report.json` | logs et tests |
| 3 | Automatisation | pipeline Python | Docker Compose |
| 3 | Monitoring et métriques | logs, rapports | dashboard |
| 3 | RGPD et traçabilité | plan de gouvernance | quarantaine |
| 4 | Performance du modèle | `metrics.json` | `predictions_test.csv` |
| 4 | Robustesse et limites | tests + documentation | présentation |
| 4 | Réentraînement et dérive | procédure documentée | roadmap |
| 4 | CI/CD et déploiement | Docker Compose | script vidéo |
| 4 | Code, tests et Git | dépôt et pytest | README |
| 4 | Communication | présentation et dashboard | script oral |
