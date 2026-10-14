# Procédure d'exercice des droits

## Périmètre actuel

Le MVP utilise uniquement des données synthétiques agrégées et ne contient aucun identifiant de personne : aucune des 46 colonnes du dictionnaire n'est une donnée personnelle. Les mécanismes ci-dessous décrivent néanmoins la procédure à appliquer si des données réelles étaient introduites (risque R-10).

## Droits couverts

- accès ;
- rectification ;
- effacement ;
- limitation ;
- opposition ;
- portabilité lorsque applicable.

## Procédure

1. Recevoir la demande via le canal défini par le responsable de traitement et en enregistrer la date de réception.
2. Vérifier l'identité du demandeur sans conserver de justificatif inutile.
3. Rechercher les identifiants dans les sources, tables préparées, logs et sauvegardes.
4. Exporter, corriger ou supprimer les données concernées selon le droit exercé, avec le rôle de maintenance `luxury_stock_maintainer` accordé temporairement à un compte nommé.
5. Propager l'action dans les vues dérivées, les prévisions et les modèles si nécessaire.
6. Journaliser la demande, la décision, la date et la personne responsable dans un registre des demandes.
7. Répondre sans retard injustifié et au plus tard dans un mois à compter de la réception (article 12 du RGPD). Ce délai peut être prolongé de deux mois selon la complexité ou le nombre de demandes, à condition d'en informer le demandeur dans le premier mois avec les motifs du report.

## Registre des demandes

Chaque demande est consignée avec : date de réception, droit exercé, vérification d'identité effectuée, périmètre recherché, décision, actions réalisées, date de réponse, personne responsable.

## Contrôles techniques à prévoir en production

- identifiant de traitement permettant la traçabilité ;
- tables de correspondance séparées si une pseudonymisation est utilisée ;
- procédure de suppression des sauvegardes selon la politique de conservation ;
- revue par le DPO ou le responsable conformité ;
- test périodique de restauration et d'effacement.
