# Sauvegarde, disponibilité et reprise

## Objectif

Garantir qu'une panne du conteneur ou du stockage ne supprime pas les données préparées et les rapports du projet.

## Stratégie cible

- sauvegarde quotidienne de PostgreSQL ;
- conservation courte des sauvegardes opérationnelles et conservation longue des versions certifiantes ;
- stockage des sauvegardes sur un espace séparé et chiffré ;
- test de restauration mensuel ;
- healthcheck PostgreSQL et redémarrage automatique du service ;
- RPO cible : 24 heures ;
- RTO cible : 4 heures pour l'environnement pilote.

## Démonstration locale

Le projet fournit une base SQLite de secours et des scripts PostgreSQL. Cela démontre la reproductibilité mais ne remplace pas une réplication haute disponibilité en production.

## Commandes indicatives

```bash
./scripts/backup_postgres.sh
./scripts/restore_postgres.sh backups/luxury_stock_latest.dump
```
