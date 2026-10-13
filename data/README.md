# Données Luxury Stock AI

Jeu de données synthétique reproductible, généré avec la graine `20261012`. Il ne contient aucune donnée personnelle.

## Fichiers

- `raw/products.csv` : catalogue produit, 36 produits.
- `raw/calendar.csv` : 116 semaines, 104 semaines TRAIN et 12 semaines TEST.
- `raw/sales_weekly.csv` : ventes hebdomadaires par produit.
- `raw/inventory_weekly.csv` : état hebdomadaire des stocks.
- `raw/forecast_horizon.csv` : 12 semaines après la dernière date observée, pour générer des prévisions futures.
- `quality/sales_quality_issues.csv` : fixture volontairement dégradée pour tester les contrôles qualité.

## Principe d'évaluation

Les 104 premières semaines doivent être utilisées pour l'entraînement et les 12 dernières pour l'évaluation temporelle. Il ne faut pas utiliser les semaines TEST pour construire les variables d'entraînement.

## Régénération

Depuis le dossier `luxury-stock-ai` :

```bash
python scripts/generate_data.py
```

La base SQLite est fournie pour un démarrage immédiat. Les scripts SQL du dossier `02_architecture/sql` permettent de charger les mêmes données dans PostgreSQL.
