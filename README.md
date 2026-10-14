# Luxury Stock AI

> **Prévision de la demande et aide à la décision pour une marque fictive de maroquinerie de luxe.**

Luxury Stock AI est un MVP complet d'architecture data et d'intelligence artificielle. Le projet transforme des données synthétiques de catalogue, de ventes et de stocks en prévisions de demande, indicateurs de couverture et recommandations de réapprovisionnement.

Le dépôt couvre une chaîne de bout en bout : gouvernance des données, architecture, pipeline de traitement, modèle de prévision, évaluation, monitoring et dashboard métier.

---

## Vue d'ensemble

| Élément | Description |
|---|---|
| **Problème métier** | Anticiper la demande et réduire les risques de rupture ou de surstock. |
| **Données** | Catalogue produits, ventes hebdomadaires, inventaire et calendrier. |
| **Modèle** | Baseline par moyenne glissante et modèle Random Forest. |
| **Stockage** | SQLite pour le démarrage local et PostgreSQL pour l'architecture cible. |
| **Interface** | Dashboard Streamlit avec filtres et recommandations. |
| **Déploiement** | Docker Compose. |
| **Qualité** | Tests, rapports JSON, quarantaine et détection de dérive. |

## Fonctionnalités principales

- génération reproductible de données synthétiques ;
- validation des schémas et des règles métier ;
- détection des doublons, dates invalides, valeurs manquantes, quantités négatives et références inconnues ;
- export des lignes rejetées dans une quarantaine ;
- stockage SQLite et scripts PostgreSQL ;
- création de variables retardées et de moyennes glissantes ;
- comparaison d'une baseline avec un modèle Random Forest ;
- évaluation temporelle avec MAE et RMSE ;
- prévisions de demande sur 12 semaines ;
- détection des couvertures de stock insuffisantes ;
- recommandations de réapprovisionnement ;
- dashboard Streamlit ;
- tests unitaires, fonctionnels et de robustesse ;
- rapports de qualité, validation, monitoring, dérive et explicabilité ;
- orchestration Docker Compose ;
- workflows GitHub Actions de qualité et de réentraînement.

## Résultats de référence

Le jeu de données est généré avec une seed fixe afin de rendre les résultats reproductibles.

| Indicateur | Valeur |
|---|---:|
| Produits | 36 |
| Semaines disponibles | 116 |
| Semaines d'entraînement | 104 |
| Semaines de test | 12 |
| Lignes de ventes | 4 176 |
| Lignes d'inventaire | 4 176 |
| MAE baseline | 7.2964 |
| MAE modèle candidat | 3.8742 |
| Amélioration de la MAE | 46.9 % |

> Les résultats sont obtenus sur des données synthétiques. Ils ne constituent pas une garantie de performance sur des données réelles.

## Architecture

```text
Sources CSV
    |
    v
Validation et contrôles qualité
    |
    v
Nettoyage et quarantaine
    |
    +-------------------------+
    |                         |
    v                         v
SQLite / PostgreSQL       Rapports qualité
    |
    v
Variables temporelles et retardées
    |
    v
Baseline + modèle candidat
    |
    v
Évaluation temporelle
    |
    v
Prévisions et recommandations de stock
    |
    v
Dashboard Streamlit
```

Les choix d'architecture sont détaillés dans [`02_architecture/architecture_decisions.md`](02_architecture/architecture_decisions.md).

## Installation locale

### Prérequis

- Python 3.11 recommandé pour l'exécution locale ;
- Git ;
- Docker Desktop et Docker Compose ;
- PostgreSQL facultatif, SQLite étant fourni pour un démarrage immédiat.

Docker est recommandé pour obtenir un environnement reproductible et éviter les différences de versions entre machines.

### Installation Python

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Sous Windows PowerShell :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Exécution complète

### Avec Python

```bash
python scripts/generate_data.py
python 03_pipeline/src/run_pipeline.py
python 04_ai/src/train.py
python 04_ai/src/evaluate.py
python 04_ai/src/predict.py
python scripts/generate_reports.py
python scripts/check_drift.py
```

### Avec Docker Compose

```bash
docker compose up --build
```

Le service `pipeline` génère les données, exécute les contrôles, entraîne le modèle et produit les prévisions. Le service `app` démarre le dashboard Streamlit.

Le dashboard est accessible à l'adresse :

```text
http://localhost:8501
```

Pour arrêter les services :

```bash
docker compose down
```

Pour supprimer également le volume PostgreSQL local :

```bash
docker compose down -v
```

## Tests

Avec un environnement Python compatible :

```bash
pytest -q
```

Avec Docker :

```bash
docker compose run --build --rm --no-deps pipeline pytest -q
```

Les tests couvrent :

- la validation des données ;
- la détection des anomalies ;
- la quarantaine ;
- la construction des variables ;
- la séparation temporelle ;
- la robustesse face à des données dégradées.

## Données

Les données sont synthétiques et ne contiennent aucune donnée personnelle.

| Fichier | Description |
|---|---|
| `data/raw/products.csv` | Catalogue de 36 produits. |
| `data/raw/calendar.csv` | Calendrier hebdomadaire et partition TRAIN/TEST. |
| `data/raw/sales_weekly.csv` | Ventes agrégées par produit et par semaine. |
| `data/raw/inventory_weekly.csv` | Stock initial, entrées, stock final et couverture. |
| `data/raw/forecast_horizon.csv` | Horizon futur de prévision. |
| `data/quality/sales_quality_issues.csv` | Fixture volontairement dégradée pour tester les contrôles. |

Pour démontrer la gestion des anomalies :

```bash
python 03_pipeline/src/run_quality_fixture.py
```

Les lignes rejetées sont exportées dans :

```text
data/processed/quality_demo_sales_quarantine.csv
```

## Modélisation

La cible est `net_units_sold`, c'est-à-dire le nombre d'unités vendues nettes par produit et par semaine.

La baseline correspond à une moyenne glissante sur les quatre dernières semaines. Le modèle candidat est une forêt aléatoire utilisant notamment :

- le produit ;
- l'index de semaine ;
- le mois et le trimestre ;
- les périodes de forte activité ;
- les retards à une, quatre et huit semaines ;
- la moyenne glissante sur quatre semaines.

L'évaluation respecte l'ordre temporel : les 104 premières semaines servent à l'entraînement et les 12 dernières au test.

L'indicateur de risque est conservateur. Il est activé lorsque le stock disponible est inférieur à deux semaines de demande prévue. La recommandation de réapprovisionnement vise à atteindre cette couverture cible.

Les résultats sont écrits dans :

- `04_ai/metrics.json` ;
- `04_ai/predictions_test.csv` ;
- `04_ai/forecast_future.csv` ;
- `reports/evaluation_forecasting_report.json`.

## Rapports de preuve

Le dossier `reports/` rassemble les preuves techniques du projet :

| Rapport | Contenu |
|---|---|
| `ai_data_report.json` | Profil, volumes, partition et hashes des sources. |
| `validation_report.json` | Validation des sources et lignes rejetées. |
| `transformation_report.json` | Transformations et fichiers produits. |
| `quality_report.json` | Contrôles qualité et tests. |
| `pipeline_report.json` | Étapes d'exécution de la chaîne. |
| `evaluation_forecasting_report.json` | Performances de la baseline et du modèle candidat. |
| `bias_report.json` | Écarts indicatifs par catégorie produit. |
| `explainability_report.json` | Importance des variables et logique métier. |
| `chain_report.json` | Traçabilité de bout en bout. |
| `engine_scalability_report.json` | Benchmark local et stratégie de passage à l'échelle. |
| `monitoring_reference.json` | Seuils de supervision. |
| `monitoring_report.json` | État des contrôles et politique de réentraînement. |
| `drift_report.json` | Dérive indicative mesurée par PSI. |

## Gouvernance et sécurité

Les principaux livrables sont disponibles dans :

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

```bash
python scripts/check_drift.py
```

Pour déclencher le réentraînement si les seuils l'exigent :

```bash
python scripts/retrain_if_needed.py
```

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
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pipeline.md
└── README.md
```

## Livrables de certification

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
- documentation de sécurité et de sauvegarde ;
- présentation du bloc 2.

### Bloc 3, pipeline

- schéma du pipeline ;
- code d'ingestion, validation et transformation ;
- tests ;
- rapport qualité ;
- monitoring ;
- présentation du bloc 3.

### Bloc 4, solution IA

- code d'entraînement, d'évaluation et de prédiction ;
- modèle et métriques ;
- prévisions de test et prévisions futures ;
- model card ;
- dashboard Streamlit ;
- Dockerfile et Docker Compose ;
- présentation du bloc 4.

## Limites connues

- les données sont synthétiques ;
- les promotions, événements externes et contraintes fournisseurs ne sont pas intégrés ;
- le dashboard est un outil d'aide à la décision ;
- les recommandations ne déclenchent aucune commande automatiquement ;
- le monitoring temps réel et la haute disponibilité doivent être activés dans une infrastructure de production ;
- les métriques ne doivent pas être généralisées à un contexte réel sans nouvelle validation.

## Documentation complémentaire

- [`pipeline.md`](pipeline.md) : fonctionnement détaillé du pipeline ;
- [`docs/matrice_evaluation.md`](docs/matrice_evaluation.md) : correspondance entre critères et preuves ;
- [`docs/audit_referentiel.md`](docs/audit_referentiel.md) : audit du référentiel ;
- [`docs/oral_questions.md`](docs/oral_questions.md) : questions probables du jury ;
- [`presentations/`](presentations/) : supports de présentation par bloc.
