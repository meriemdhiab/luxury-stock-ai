# Audit du référentiel d'évaluation

## Légende

- **Couvert** : une preuve est présente dans le dépôt.
- **Partiel** : le principe est documenté, mais la preuve opérationnelle doit être renforcée ou montrée à l'oral.
- **À faire** : élément non démontré par le MVP actuel.

## Synthèse

Le dépôt couvre les livrables obligatoires des quatre blocs et les principales preuves techniques. Les critères demandant une infrastructure de production complète, une haute disponibilité réelle, un monitoring temps réel ou une CI/CD réellement exécutée restent partiels tant que le dépôt n'est pas poussé sur GitHub et exécuté dans l'environnement de soutenance.

## Écarts corrigés dans cette version

- table des matières du plan de gouvernance ;
- références RGPD, CNIL, Loi Informatique et Libertés, ISO 27001, ANSSI et RGAA ;
- procédure d'exercice des droits ;
- contrôles de sécurité local versus production ;
- sauvegarde, RPO, RTO et reprise ;
- rôles PostgreSQL à privilèges séparés ;
- monitoring et niveaux d'alerte ;
- détection de dérive par PSI ;
- script de réentraînement conditionnel ;
- workflows GitHub Actions de CI et réentraînement planifié ;
- test de robustesse ;
- model card.

## Points à démontrer par Meriem

- exécuter Docker Compose sur sa machine ;
- pousser le dépôt sur GitHub et montrer les workflows CI ;
- enregistrer les trois vidéos réelles ;
- expliquer les limites du MVP et distinguer les contrôles locaux des contrôles de production ;
- respecter les temps de présentation ;
- répondre aux questions du jury et montrer les fichiers de preuve.

## Conclusion

Le projet est aligné sur la structure et les livrables du référentiel, mais il ne faut pas présenter les mécanismes de production comme déjà actifs lorsque le dépôt est seulement local. La formulation correcte est : « le MVP implémente et démontre les contrôles de base, tandis que les contrôles de production sont spécifiés et automatisables dans l'architecture cible ». 
