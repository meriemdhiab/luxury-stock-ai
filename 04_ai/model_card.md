# Model card, prévision de demande

## Usage prévu

Aider un responsable approvisionnement à prioriser les produits à examiner. Le modèle ne déclenche pas automatiquement une commande.

## Données

Données synthétiques, agrégées par produit et semaine. Aucun attribut personnel.

## Modèle

Forêt aléatoire avec variables calendaires, produit, retards 1, 4 et 8 semaines et moyenne glissante sur 4 semaines.

## Évaluation

MAE et RMSE sur 12 semaines de test chronologiquement postérieures à l'entraînement. La baseline est une moyenne glissante sur 4 semaines.

## Limites

Le modèle ne connaît pas les promotions réelles, les événements externes, les ruptures fournisseurs ou les changements de prix. Les performances observées sur des données synthétiques ne garantissent pas les performances en production.

## Explicabilité et équité

Le projet fournit l'importance globale des variables, une règle métier explicite de réapprovisionnement et un rapport d'écarts par catégorie produit. Cette analyse ne remplace pas une étude de biais sur des données de personnes.
