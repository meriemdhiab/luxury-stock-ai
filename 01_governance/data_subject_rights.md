# Procédure d'exercice des droits

## Périmètre actuel

Le MVP utilise uniquement des données synthétiques agrégées et ne contient aucun identifiant de personne. Les mécanismes ci-dessous décrivent néanmoins la procédure à appliquer si des données réelles étaient introduites.

## Droits couverts

- accès ;
- rectification ;
- effacement ;
- limitation ;
- opposition ;
- portabilité lorsque applicable.

## Procédure

1. Recevoir la demande via le canal défini par le responsable de traitement.
2. Vérifier l'identité du demandeur sans conserver de justificatif inutile.
3. Rechercher les identifiants dans les sources, tables préparées, logs et sauvegardes.
4. Exporter, corriger ou supprimer les données concernées selon le droit exercé.
5. Propager l'action dans les vues dérivées et les modèles si nécessaire.
6. Journaliser la demande, la décision, la date et la personne responsable.
7. Répondre dans les délais réglementaires applicables.

## Contrôles techniques à prévoir en production

- identifiant de traitement permettant la traçabilité ;
- tables de correspondance séparées si une pseudonymisation est utilisée ;
- procédure de suppression des sauvegardes selon la politique de conservation ;
- revue par le DPO ou le responsable conformité ;
- test périodique de restauration et d'effacement.
