# Model card, prévision de demande

Version 1.0, 14 octobre 2026.

## Usage prévu

Aider un responsable approvisionnement à prioriser les produits à examiner. Le modèle ne déclenche pas automatiquement une commande : toute recommandation est validée par le métier.

## Données

Données synthétiques, agrégées par produit et semaine : 36 produits, 116 semaines, 4 176 lignes de ventes. Aucun attribut personnel. La cible est `net_units_sold` : il s'agit de ventes nettes et non de demande, donc les semaines en rupture (`stockout_flag`) sous-estiment la demande.

## Modèle

Forêt aléatoire (`random_state` fixé à 42) avec :

- le produit ;
- l'index de semaine, le mois et le trimestre ;
- l'indicateur de période de forte activité ;
- les retards à 1, 4 et 8 semaines ;
- la moyenne glissante sur 4 semaines.

Les prévisions futures sont récursives : chaque prévision alimente les retards de la semaine suivante.

## Évaluation

Séparation chronologique : les 104 premières semaines servent à l'entraînement, dont 8 de préchauffage pour calculer les retards (96 semaines d'entraînement effectives, 3 456 lignes), et les 12 dernières semaines au test (432 lignes).

L'évaluation est à **une semaine d'horizon** : les retards du test utilisent les valeurs observées. Elle ne mesure pas l'erreur d'une prévision récursive à 12 semaines.

| Modèle | MAE | RMSE |
|---|---|---|
| Baseline, moyenne glissante sur 4 semaines | 4.0498 | 5.1581 |
| Random Forest | 3.4985 | 4.5476 |

Amélioration de la MAE : 13,61 %. Source : `04_ai/metrics.json` et `reports/evaluation_forecasting_report.json`.

## Règle de réapprovisionnement

Le risque de rupture est calculé par produit. Il est activé lorsque le stock actuel ne couvre pas la demande prévue pendant le délai fournisseur (`lead_time_days`), augmentée du stock minimal (`minimum_stock_units`). La quantité recommandée vise ce seuil plus deux semaines de demande prévue, moins le stock actuel (jamais négative). Le seuil figure dans `forecast_future.csv`.

## Supervision

Dérive mesurée par PSI entre la période d'entraînement et la période de test : 0,0698 (seuils : avertissement 0,2, alerte 0,25). Un réentraînement est recommandé si la MAE dépasse de plus de 10 % la MAE de référence, si un seuil de monitoring est dépassé, si la dérive est durable, si une règle qualité critique est violée ou si de nouvelles données arrivent.

## Limites

- Le modèle ne connaît pas les promotions réelles, les événements externes, les ruptures fournisseurs ou les changements de prix.
- Les performances observées sur des données synthétiques ne garantissent pas les performances en production.
- L'évaluation porte sur une seule fenêtre de 12 semaines, à une semaine d'horizon, face à une baseline sans saisonnalité.
- L'index de semaine prend des valeurs jamais vues à l'entraînement pour les semaines futures, et une forêt aléatoire ne sait pas l'extrapoler.
- La règle de réapprovisionnement ne tient pas compte des commandes déjà en cours.

## Explicabilité et équité

Le projet fournit l'importance globale des variables (`reports/explainability_report.json`), une règle métier explicite de réapprovisionnement et un rapport d'écarts par catégorie produit (`reports/bias_report.json`). Cette analyse ne remplace pas une étude de biais sur des données de personnes.
