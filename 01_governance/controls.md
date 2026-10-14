# Matrice de contrôles

Statut : **Actif** (preuve disponible), **À activer** (fichier fourni, à pousser et à exécuter), **Planifié** (preuve à produire). Les identifiants de risque renvoient à `ai_risk_register.xlsx`.

| ID | Domaine | Contrôle | Fréquence | Preuve | Responsable | Risques | Statut |
|---|---|---|---|---|---|---|---|
| C-01 | Qualité | Vérification des colonnes obligatoires | Chaque exécution | `validation_report.json` | Data engineer | R-02 | Actif |
| C-02 | Qualité | Dates valides et valeurs non négatives | Chaque exécution | `quality_report.json` | Data engineer | R-02 | Actif |
| C-03 | Qualité | Doublons et références inconnues | Chaque exécution | `sales_quarantine.csv` | Data engineer | R-02 | Actif |
| C-04 | Qualité | Contrôles d'intégrité SQL après chargement (6 critiques, 6 avertissements) | À chaque création de la base | Synthèse de `003_quality_checks.sql` dans le journal Docker | Data engineer | R-02 | Actif |
| C-05 | Traçabilité | Hash des sources et version du dataset | Chaque exécution | `ai_data_report.json` | Data owner | R-08 | Actif |
| C-06 | Traçabilité | Cohérence entre schéma SQL et dictionnaire de données | Chaque commit | `tests/test_data_dictionary.py` | Data owner | R-02 | Actif |
| C-07 | Sécurité | Aucun secret dans le dépôt : `.env` non versionné, scan gitleaks | Chaque push | `.gitignore`, `.env.example`, résultat de `secret-scan.yml` | Responsable sécurité | R-05 | À activer |
| C-08 | Sécurité | Revue des droits PostgreSQL : rôles de moindre privilège, droits PUBLIC retirés, port local | Chaque revue | `004_roles.sql`, `docker-compose.yml` | Responsable sécurité | R-09 | Actif |
| C-09 | Sécurité | Analyse des dépendances | Chaque push | Rapport pip-audit ou Dependabot | Responsable sécurité | R-13 | Planifié |
| C-10 | Modèle | Split temporel sans fuite | Chaque entraînement | `evaluation_forecasting_report.json`, contrôle Q03 | ML engineer | R-01 | Actif |
| C-11 | Modèle | Comparaison à une baseline | Chaque entraînement | Métriques MAE et RMSE | ML engineer | R-12 | Actif |
| C-12 | Modèle | Baseline saisonnière et rétro-test sur plusieurs fenêtres | Chaque entraînement | `evaluation_forecasting_report.json` | ML engineer | R-12 | Planifié |
| C-13 | Modèle | Suivi de la dérive et seuils d'alerte | À chaque nouveau batch | `monitoring_report.json`, `drift_report.json` | ML engineer | R-03 | Actif |
| C-14 | Modèle | Traitement des semaines en rupture dans l'entraînement | Chaque entraînement | `bias_report.json` | ML engineer | R-11, R-06 | Planifié |
| C-15 | Métier | Validation humaine avant réapprovisionnement | Chaque décision | Dashboard et procédure | Propriétaire métier | R-04 | Actif |
| C-16 | Conformité | Procédure d'exercice des droits et analyse d'impact avant toute donnée réelle | Avant toute donnée réelle | `data_subject_rights.md` | Data owner | R-10 | Actif |
| C-17 | Accessibilité | Contraste, libellés et alternative textuelle du dashboard | Avant soutenance et à chaque évolution | Captures et résultat d'un outil de contrôle | Responsable produit | R-04 | Actif |
| C-18 | Incident | Quarantaine et journalisation | À chaque anomalie | Logs et rapport | Data engineer | R-02, R-08 | Actif |
