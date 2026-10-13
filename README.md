# Luxury Stock AI

> Prévision de la demande et aide à la décision pour une marque fictive de maroquinerie de luxe.

Luxury Stock AI est un MVP complet d'architecture et de solution d'intelligence artificielle. Le projet transforme des données synthétiques de catalogue, ventes et stocks en prévisions de demande, détection de risques de rupture et recommandations de réapprovisionnement.

Le dépôt est structuré pour couvrir les quatre blocs d'une soutenance d'Architecte en Intelligence Artificielle : gouvernance, architecture, pipelines de données, puis construction et déploiement d'une solution IA.

## Fonctionnalités

- génération reproductible d'un jeu de données synthétique ;
- validation du schéma et des règles métier ;
- détection des doublons, dates invalides, valeurs manquantes, quantités négatives et références inconnues ;
- quarantaine des lignes rejetées ;
- stockage SQLite et scripts PostgreSQL ;
- création de variables retardées et de moyennes glissantes ;
- comparaison entre une baseline et un modèle de forêt aléatoire ;
- évaluation temporelle avec MAE et RMSE ;
- prévisions futures sur 12 semaines ;
- détection des risques de rupture ;
- recommandations de réapprovisionnement ;
- dashboard Streamlit ;
- tests unitaires, fonctionnels et de robustesse ;
- rapports JSON de qualité, validation, monitoring, dérive et explicabilité ;
- Docker Compose ;
- workflows GitHub Actions de CI et de réentraînement planifié.

## Résultats de référence

Le jeu fourni est généré avec une seed fixe afin de rendre les résultats reproductibles :

| Élément | Valeur |
|---|---:|
| Produits | 36 |
| Semaines historiques | 116 |
| Semaines d'entraînement | 104 |
| Semaines de test | 12 |
| Lignes de ventes | 4 176 |
| Lignes d'inventaire | 4 176 |
| MAE baseline | 7.2964 |
| MAE modèle candidat | 3.8742 |
| Amélioration de la MAE | 46.9 % |

Ces résultats sont obtenus sur des données synthétiques. Ils ne constituent pas une garantie de performance sur des données réelles.

## Architecture

```text
CSV synthétiques
    |
    v
Validation et contrôles qualité
    |
    v
Nettoyage et quarantaine
    |
    +----------------------+
    |                      |
    v                      v
SQLite / PostgreSQL    Rapports qualité
    |
    v
Variables temporelles et retardées
    |
    v
Baseline + modèle candidat
    |
    v
Evaluation temporelle
    |
    v
Prévisions et recommandations de stock
    |
    v
Dashboard Streamlit
```

Les choix d'architecture sont détaillés dans `02_architecture/architecture_decisions.md`.

## Installation locale

### Prérequis

- Python 3.11 ou version compatible ;
- Git ;
- Docker et Docker Compose, uniquement pour le déploiement conteneurisé ;
- PostgreSQL facultatif, SQLite étant fourni pour un démarrage immédiat.

### Installation

````bash
git clone <URL_DU_DEPOT>
cd luxury-stock-ai

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
````

Sous Windows PowerShell :

````powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
````

### Exécution complète

````bash
python scripts/generate_data.py
python 03_pipeline/src/run_pipeline.py
python 04_ai/src/train.py
python 04_ai/src/evaluate.py
python 04_ai/src/predict.py
python scripts/generate_reports.py
python scripts/check_drift.py
````

Ou avec les scripts de lancement :

````bash
# Linux ou macOS
./run_pipeline.sh

# Windows
run_pipeline.bat
````

### Tests

````bash
pytest -q
````

Les tests couvrent la validation de données, la quarantaine, la construction des variables, la séparation temporelle et la robustesse face à des données dégradées.

### Dashboard

Après l'exécution du pipeline et de la prédiction :

````bash
streamlit run app/streamlit_app.py
````

Le dashboard est accessible à l'adresse `http://localhost:8501`.

## Exécution avec Docker Compose

````bash
docker compose up --build
````

Le service `pipeline` génère les données, exécute les contrôles, entraîne le modèle et produit les rapports. Le service `app` démarre le dashboard Streamlit.

Pour arrêter les services :

````bash
docker compose down
````

Pour supprimer également le volume PostgreSQL local :

````bash
docker compose down -v
````

## Jeu de données

Les données sont synthétiques et ne contiennent aucune donnée personnelle.

- `data/raw/products.csv` : catalogue de 36 produits ;
- `data/raw/calendar.csv` : calendrier et partition TRAIN/TEST ;
- `data/raw/sales_weekly.csv` : ventes hebdomadaires ;
- `data/raw/inventory_weekly.csv` : niveaux de stock ;
- `data/raw/forecast_horizon.csv` : horizon futur de prévision ;
- `data/quality/sales_quality_issues.csv` : fichier volontairement dégradé pour démontrer les contrôles qualité.

La fixture qualité se lance avec :

````bash
python 03_pipeline/src/run_quality_fixture.py
````

Les lignes rejetées sont disponibles dans `data/processed/quality_demo_sales_quarantine.csv`.

## Modélisation

La cible est `net_units_sold`, c'est-à-dire le nombre d'unités vendues nettes par produit et par semaine.

La baseline correspond à une moyenne glissante sur les quatre dernières semaines. Le modèle candidat est une forêt aléatoire utilisant notamment :

- l'identifiant numérique du produit ;
- l'index de semaine ;
- le mois et le trimestre ;
- l'indicateur de période de pointe ;
- les retards à une, quatre et huit semaines ;
- la moyenne glissante sur quatre semaines.

L'évaluation respecte l'ordre temporel : les 104 premières semaines servent à l'entraînement et les 12 dernières au test.

Les résultats sont écrits dans :

- `04_ai/metrics.json` ;
- `04_ai/predictions_test.csv` ;
- `04_ai/forecast_future.csv` ;
- `reports/evaluation_forecasting_report.json`.

## Rapports de preuve

Le dossier `reports/` contient des preuves techniques réutilisables dans le dossier de soutenance :

- `ai_data_report.json` : profil, volumes, split et hashes des sources ;
- `validation_report.json` : validation et lignes rejetées ;
- `transformation_report.json` : transformations et sorties ;
- `quality_report.json` : contrôles et tests ;
- `pipeline_report.json` : étapes d'exécution ;
- `evaluation_forecasting_report.json` : performances du modèle ;
- `bias_report.json` : écarts indicatifs par catégorie produit ;
- `explainability_report.json` : importance des variables et logique métier ;
- `chain_report.json` : traçabilité de bout en bout ;
- `engine_scalability_report.json` : benchmark local ;
- `monitoring_reference.json` : seuils de supervision ;
- `monitoring_report.json` : état des contrôles ;
- `drift_report.json` : dérive indicative mesurée par PSI.

## Gouvernance et sécurité

Le projet contient :

- `01_governance/plan_gouvernance.pdf` ;
- `01_governance/data_dictionary.xlsx` ;
- `01_governance/ai_risk_register.xlsx` ;
- `01_governance/controls.md` ;
- `01_governance/data_subject_rights.md` ;
- `02_architecture/security_controls.md` ;
- `02_architecture/backup_restore.md` ;
- `02_architecture/sql/004_roles.sql`.

Le MVP local utilise des données synthétiques. Le chiffrement TLS, le chiffrement au repos, la réplication PostgreSQL et le gestionnaire de secrets sont documentés comme contrôles nécessaires en production, mais ne sont pas prétendus actifs dans l'environnement local.

## Réentraînement et dérive

Pour calculer la dérive :

````bash
python scripts/check_drift.py
````

Pour déclencher le réentraînement si les seuils l'exigent :

````bash
python scripts/retrain_if_needed.py
````

Les workflows GitHub Actions sont disponibles dans `.github/workflows/` :

- `ci.yml` : génération, pipeline, modèle, rapports et tests sur chaque push ou pull request ;
- `retraining.yml` : exécution planifiée et lancement manuel du réentraînement.

## Structure du dépôt

```text
luxury-stock-ai/
├── .github/workflows/
├── 01_governance/
├── 02_architecture/
├── 03_pipeline/
├── 04_ai/
├── 04_deployment/
├── app/
├── data/
├── database/
├── docs/
├── presentations/
├── reports/
├── scripts/
├── videos/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pipeline.md
└── README.md
```

## Livrables de soutenance

### Bloc 1, gouvernance

- plan de gouvernance PDF ;
- dictionnaire de données ;
- cartographie de lignage ;
- registre des risques IA ;
- matrice de contrôles ;
- présentation du bloc 1.

### Bloc 2, architecture

- schéma d'architecture ;
- décisions techniques ;
- scripts SQL ;
- configuration Docker ;
- documentation de sauvegarde et sécurité ;
- présentation du bloc 2 ;
- script de vidéo de production.

### Bloc 3, pipeline

- schéma du pipeline ;
- code d'ingestion, validation et transformation ;
- tests ;
- rapport qualité ;
- monitoring ;
- présentation du bloc 3 ;
- script de vidéo de production.

### Bloc 4, solution IA

- code d'entraînement, évaluation et prédiction ;
- modèle et métriques ;
- prévisions de test et futures ;
- model card ;
- dashboard Streamlit ;
- Dockerfile et Docker Compose ;
- présentation du bloc 4 ;
- script de vidéo de démonstration.

Les fichiers vidéo eux-mêmes doivent être enregistrés depuis un environnement réel. Le dépôt contient les scripts de capture dans `videos/`.

## Limites connues

- les données sont synthétiques ;
- les facteurs externes, promotions et événements économiques ne sont pas intégrés ;
- le dashboard est un outil d'aide à la décision ;
- les recommandations ne déclenchent aucune commande automatiquement ;
- le monitoring temps réel et la haute disponibilité doivent être activés dans une infrastructure de production ;
- les métriques ne doivent pas être généralisées à un contexte réel sans nouvelle validation.

## Publication GitHub

Consulter `docs/github_publication_manifest.md` pour la liste des fichiers à publier et les fichiers générés à exclure.
