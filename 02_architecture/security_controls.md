# Contrôles de sécurité de l'architecture

## Niveau MVP local

- aucun secret réel dans le dépôt ;
- variables d'environnement dans `.env.example` ;
- données synthétiques sans information personnelle ;
- volumes Docker séparés ;
- contrôle des entrées dans le pipeline ;
- accès au dashboard limité à l'environnement local.

## Niveau cible de production

- chiffrement en transit avec TLS ;
- chiffrement au repos du stockage et des sauvegardes ;
- gestionnaire de secrets, jamais de secret dans Git ;
- comptes distincts pour ingestion, lecture et maintenance ;
- principe du moindre privilège ;
- rotation périodique des secrets ;
- journalisation des accès et des erreurs ;
- sauvegardes chiffrées et test de restauration ;
- limitation réseau du serveur PostgreSQL ;
- revue des dépendances et des images Docker.

## Limitation explicitement assumée

Le chiffrement TLS, la réplication PostgreSQL et le gestionnaire de secrets ne sont pas simulés dans le MVP local. Ils sont décrits comme mesures de production et devront être activés lors d'un déploiement réel.
