# Pipeline de données

Le pipeline lit les fichiers bruts, vérifie le schéma et les règles métier, place les lignes non conformes en quarantaine, écrit les fichiers nettoyés et crée une base SQLite dédiée.

## Contrôles

- colonnes obligatoires ;
- dates valides ;
- valeurs numériques présentes ;
- quantités non négatives ;
- produits existants dans le catalogue ;
- absence de doublons sur `(week_start, product_id)`.

## Exécution

```bash
python 03_pipeline/src/run_pipeline.py
cat data/processed/quality_report.json
```

Le pipeline ne masque pas une anomalie : elle est comptée, documentée et exportée dans `data/processed/sales_quarantine.csv`.

## Démonstration des anomalies

Le jeu principal est propre pour l'entraînement. Pour montrer les contrôles en vidéo, utilisez la fixture volontairement dégradée :

```bash
python 03_pipeline/src/run_quality_fixture.py
cat data/processed/quality_demo_report.json
cat data/processed/quality_demo_sales_quarantine.csv
```
