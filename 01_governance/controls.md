# Matrice de contrôles

| Domaine | Contrôle | Fréquence | Preuve | Responsable |
|---|---|---|---|---|
| Qualité | Vérification des colonnes obligatoires | Chaque exécution | `validation_report.json` | Data engineer |
| Qualité | Dates valides et valeurs non négatives | Chaque exécution | `quality_report.json` | Data engineer |
| Qualité | Doublons et références inconnues | Chaque exécution | `sales_quarantine.csv` | Data engineer |
| Traçabilité | Hash des sources et version du dataset | Chaque exécution | `ai_data_report.json` | Data owner |
| Sécurité | Aucun secret réel dans le dépôt | Chaque revue | `.env.example`, revue Git | Responsable sécurité |
| Modèle | Split temporel sans fuite | Chaque entraînement | `evaluation_forecasting_report.json` | ML engineer |
| Modèle | Comparaison à une baseline | Chaque entraînement | métriques MAE/RMSE | ML engineer |
| Modèle | Suivi de la dérive et seuils d'alerte | À chaque nouveau batch | `monitoring_report.json` | ML engineer |
| Métier | Validation humaine avant réapprovisionnement | Chaque décision | dashboard et procédure | Propriétaire métier |
| Accessibilité | Contraste, libellés et alternative textuelle | Avant soutenance | revue dashboard | Responsable produit |
| Incident | Quarantaine et journalisation | À chaque anomalie | logs et rapport | Data engineer |
