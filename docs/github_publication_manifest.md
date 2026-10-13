# Manifest de publication GitHub

## À publier

### Racine

- `README.md`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`
- `Makefile`
- `pipeline.md`
- `run_pipeline.sh`
- `run_pipeline.bat`
- `.gitignore`
- `.dockerignore`
- `.env.example`

### Gouvernance

Publier tout le dossier `01_governance/` :

- plan de gouvernance Markdown et PDF ;
- dictionnaire de données ;
- registre des risques IA ;
- matrice de contrôles ;
- cartographie de lignage ;
- procédure des droits des personnes.

### Architecture

Publier tout le dossier `02_architecture/` :

- schéma ;
- décisions techniques ;
- contrôles de sécurité ;
- sauvegarde et restauration ;
- scripts SQL ;
- script vidéo.

### Pipeline

Publier tout le dossier `03_pipeline/` :

- code source ;
- tests ;
- configuration ;
- documentation ;
- diagramme ;
- script vidéo.

### IA et application

Publier :

- `04_ai/src/` ;
- `04_ai/tests/` ;
- `04_ai/model_card.md` ;
- `04_ai/metrics.json` ;
- `04_ai/predictions_test.csv` ;
- `04_ai/forecast_future.csv` ;
- `04_ai/video_script.md` ;
- `04_deployment/` ;
- `app/`.

Le modèle binaire peut être régénéré avec `python 04_ai/src/train.py`. Il n'est pas nécessaire de publier `04_ai/models/candidate_model.pkl`.

### Données

Publier :

- `data/raw/` ;
- `data/quality/` ;
- `data/README.md`.

Les données sont synthétiques et adaptées à une publication publique.

### Rapports

Publier tout le dossier `reports/`, notamment :

- rapports JSON ;
- graphiques PNG ;
- `reports/README.md`.

Ces rapports servent de preuves reproductibles pour la soutenance.

### Documentation et présentations

Publier :

- `docs/` ;
- `presentations/` ;
- `videos/README.md`.

## À ne pas publier

Ne pas publier :

- `.env` contenant des secrets ;
- mots de passe, tokens ou clés API ;
- `__pycache__/` ;
- `.pytest_cache/` ;
- `logs/` ;
- fichiers MP4 lourds si l'école dispose d'un espace de dépôt séparé ;
- données personnelles réelles ;
- exports contenant des informations confidentielles ;
- `data/processed/` si elle est entièrement régénérable ;
- `database/luxury_stock_pipeline.sqlite` si elle est entièrement régénérable ;
- `04_ai/models/candidate_model.pkl` si la taille du dépôt doit rester réduite.

## Commandes Git recommandées

Depuis le dossier du projet :

````bash
git init
git add .
git status
git commit -m "Initialiser Luxury Stock AI"
git branch -M main
git remote add origin https://github.com/<TON_COMPTE>/luxury-stock-ai.git
git push -u origin main
````

Avant le premier commit, vérifier :

````bash
git status
find . -name '.env' -o -name '*.pem' -o -name '*secret*'
````

## Après publication

1. Vérifier que le workflow `ci.yml` passe au vert.
2. Vérifier que les fichiers CSV et JSON sont visibles sur GitHub.
3. Ouvrir le README depuis la page principale du dépôt.
4. Tester un clone propre du dépôt.
5. Enregistrer les vidéos depuis ce clone propre.
6. Ajouter les liens des vidéos uniquement dans l'espace demandé par l'école.
