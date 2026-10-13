# Questions probables du jury

## Architecture

- Pourquoi PostgreSQL plutôt qu'un simple fichier CSV ?
- Pourquoi ne pas utiliser une architecture cloud ou distribuée ?
- Comment ferais-tu évoluer la solution avec dix fois plus de données ?
- Comment gères-tu les secrets et les accès ?

## Données et pipeline

- Comment détectes-tu une donnée incorrecte ?
- Que se passe-t-il si un fichier contient une date invalide ?
- Comment évites-tu les doublons ?
- Comment garantis-tu la reproductibilité ?
- Où sont conservées les lignes rejetées ?

## Modèle

- Pourquoi cette baseline ?
- Pourquoi une forêt aléatoire ?
- Pourquoi une séparation temporelle ?
- Comment évites-tu la fuite de données ?
- Que signifie une erreur MAE de telle valeur pour le métier ?
- Comment détecterais-tu une dérive du modèle ?

## Métier, conformité et éthique

- Les données sont-elles personnelles ?
- Quelle est la base légale du traitement si des clients réels étaient ajoutés ?
- Comment un utilisateur peut-il comprendre une recommandation ?
- Pourquoi la solution ne passe-t-elle pas directement une commande ?
- Quels biais peuvent exister dans les ventes historiques ?

## Déploiement

- Comment reproduire le projet sur une autre machine ?
- Que se passe-t-il si PostgreSQL est indisponible ?
- Comment ajouter une nouvelle version du modèle ?
- Quels tests sont exécutés avant un déploiement ?
