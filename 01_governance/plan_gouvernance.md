# Plan de gouvernance des données et de l'IA

## Table des matières

1. Objet et périmètre
2. Données et provenance
3. Principes de gouvernance
4. Dictionnaire et qualité
5. Rôles et responsabilités
6. Architecture et accès
7. Risques IA et contrôles
8. RGPD et conformité
9. Incidents et violations
10. Supervision et amélioration continue
11. Limites et références

## 1. Objet et périmètre

Luxury Stock AI est un système d'aide à la décision pour une marque fictive de maroquinerie de luxe. Il utilise des données synthétiques et agrégées de catalogue, ventes et stocks afin de prévoir la demande et d'identifier les risques de rupture ou de surstock.

Le périmètre couvre la collecte, la validation, la transformation, le stockage, la modélisation, l'évaluation, la restitution et la supervision. La solution ne prend pas automatiquement de décision d'achat et ne traite aucune donnée client réelle.

## 2. Principes de gouvernance

- **Finalité** : améliorer la planification du stock et prioriser les analyses.
- **Minimisation** : ne conserver que les variables nécessaires à la prévision.
- **Qualité** : contrôler les types, dates, valeurs, références et doublons.
- **Traçabilité** : conserver la provenance, les règles de transformation et les lignes rejetées.
- **Sécurité** : limiter les accès, ne pas versionner de secret et séparer les environnements.
- **Explicabilité** : documenter les variables, la baseline, les métriques et la règle de réapprovisionnement.
- **Validation humaine** : aucune recommandation ne devient automatiquement une commande.
- **Accessibilité** : concevoir le dashboard avec des libellés lisibles, des contrastes suffisants et une alternative textuelle aux graphiques.

## 3. Données et provenance

Les fichiers sont synthétiques et générés par `scripts/generate_data.py` avec une seed documentée. Les sources sont :

- `products.csv`, catalogue produit ;
- `calendar.csv`, calendrier et split temporel ;
- `sales_weekly.csv`, ventes agrégées par produit et semaine ;
- `inventory_weekly.csv`, niveaux de stock et indicateurs ;
- `forecast_horizon.csv`, période future à prévoir.

Aucun nom, email, identifiant client, adresse, donnée biométrique ou donnée de paiement n'est utilisé. Si le projet devait intégrer des données réelles, une analyse complémentaire serait nécessaire avant traitement.

## 4. Dictionnaire et qualité

Le dictionnaire de données fourni dans `data_dictionary.xlsx` définit chaque champ, son type, sa finalité, sa contrainte et sa règle de qualité.

Les contrôles portent sur :

- la présence des colonnes obligatoires ;
- le parsing des dates ;
- les valeurs numériques manquantes ;
- les quantités négatives ;
- les références produit inconnues ;
- les doublons sur `(week_start, product_id)` ;
- la cohérence entre périodes d'entraînement et de test.

Les lignes non conformes sont exportées dans `data/processed/sales_quarantine.csv` avec une raison de rejet. Elles ne sont pas supprimées silencieusement.

## 5. Rôles et responsabilités

| Rôle | Responsabilités |
|---|---|
| Propriétaire métier | Définit les besoins, valide les règles de stock et accepte les limites. |
| Data owner | Garantit la définition, la provenance et la qualité des données sources. |
| Data engineer | Développe les contrôles, transformations, chargements et logs. |
| ML engineer | Entraîne, évalue, versionne et supervise le modèle. |
| Responsable sécurité | Revoit les secrets, droits, dépendances et mesures de protection. |
| Utilisateur métier | Interprète les alertes et garde la décision finale. |

## 6. Architecture et accès

Les données brutes sont en lecture contrôlée. Les données nettoyées sont écrites dans PostgreSQL ou SQLite. Le modèle et les rapports sont générés par des scripts versionnés. Les secrets sont injectés par variables d'environnement et ne sont jamais committés.

Les accès recommandés sont :

- lecture des données brutes pour le pipeline ;
- écriture dans les tables nettoyées pour le service d'ingestion ;
- lecture des résultats pour le dashboard ;
- accès de maintenance limité aux responsables techniques.

## 7. Risques IA et contrôles

Le registre détaillé figure dans `ai_risk_register.xlsx`. Les principaux risques sont :

- fuite de données pendant l'évaluation ;
- erreurs de prévision ;
- dérive de la demande ;
- surconfiance dans une recommandation ;
- biais de disponibilité entre catégories ;
- rupture de traçabilité ;
- défaut de sécurité ou exposition de secrets.

Les contrôles incluent une séparation temporelle, une comparaison à une baseline, des tests, des métriques, des seuils de monitoring, une validation humaine et une procédure de réentraînement.

## 8. RGPD et conformité

Le MVP ne traite pas de données personnelles. Cette conclusion est limitée au périmètre synthétique fourni. Si des ventes associées à des personnes étaient ajoutées, il faudrait déterminer la base légale, documenter le registre des traitements, limiter la conservation, gérer les droits des personnes, sécuriser les accès et réaliser une analyse d'impact si nécessaire.

Le projet reprend les principes de minimisation, sécurité, traçabilité et responsabilité. Les références et limites sont conservées dans la documentation plutôt que présentées comme une certification juridique.

## 9. Incidents et violations

En cas d'anomalie de données :

1. le pipeline arrête ou isole la ligne concernée ;
2. la raison est enregistrée ;
3. l'équipe technique analyse l'impact ;
4. le propriétaire métier valide la reprise ;
5. le rapport est conservé avec la version des données.

En cas d'exposition d'un secret : révocation immédiate, remplacement, analyse des logs et revue du dépôt. En cas de données personnelles réelles, l'organisation compétente doit évaluer les obligations de notification.

## 10. Supervision et amélioration continue

Les rapports JSON du dossier `reports/` constituent les preuves de contrôle : qualité, transformation, pipeline, évaluation, explicabilité, monitoring, biais indicatif et scalabilité.

Un réentraînement est recommandé si :

- la métrique principale baisse de plus de 10 points par rapport à la référence ;
- l'erreur dépasse les seuils définis ;
- la distribution des ventes dérive durablement ;
- une règle qualité critique est violée ;
- de nouvelles données ou catégories sont ajoutées.

## 11. Limites et références

Le jeu est synthétique, les facteurs externes ne sont pas représentés et le modèle ne remplace pas un système de planification industriel. La solution est conçue comme un MVP démontrable, reproductible et extensible.

### Références à consulter

- RGPD, Règlement (UE) 2016/679 : https://eur-lex.europa.eu/eli/reg/2016/679/oj
- CNIL, principes de protection des données : https://www.cnil.fr/
- Loi Informatique et Libertés : https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000886460/
- ISO/IEC 27001, système de management de la sécurité de l'information : https://www.iso.org/isoiec-27001-information-security.html
- ANSSI, recommandations de sécurité : https://cyber.gouv.fr/
- Référentiel général d'accessibilité pour les administrations, RGAA : https://accessibilite.numerique.gouv.fr/rgaa/

Ces références servent à justifier les principes retenus. Elles ne constituent pas une certification juridique, ISO ou ANSSI du MVP.
