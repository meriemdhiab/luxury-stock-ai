# Architecture et décisions techniques

## ADR-001, architecture modulaire locale

### Décision

Retenir une architecture locale, modulaire et conteneurisée composée de fichiers CSV, d'un pipeline Python, de PostgreSQL, d'un modèle scikit-learn et d'une application Streamlit.

### Raisons

- le volume synthétique est faible et ne justifie pas une architecture distribuée ;
- Docker Compose permet une démonstration reproductible ;
- PostgreSQL représente un stockage relationnel réaliste ;
- Python et scikit-learn sont adaptés à un MVP de prévision ;
- Streamlit permet une restitution métier rapide et compréhensible ;
- chaque composant est remplaçable sans réécrire l'ensemble.

## ADR-002, granularité hebdomadaire

La granularité hebdomadaire réduit le bruit, simplifie la visualisation et permet de conserver 116 périodes dans un délai court. Le passage au jour serait envisageable en production si la fréquence des décisions le justifie.

## ADR-003, séparation temporelle

Les 104 premières semaines servent à l'entraînement et les 12 dernières au test. La date est respectée dans la construction des variables. Cette séparation reflète le contexte réel d'une prévision future et évite d'utiliser des observations futures pour entraîner le modèle.

## ADR-004, baseline et modèle candidat

La baseline est une moyenne glissante des quatre dernières semaines. Le modèle candidat est une forêt aléatoire utilisant des variables retardées et calendaires. Le candidat n'est retenu que si ses résultats sont meilleurs ou mieux justifiés que la baseline.

## ADR-005, validation humaine

La recommandation de réapprovisionnement n'est pas une commande automatique. Elle fournit un signal explicable à un responsable métier. Cette décision réduit le risque d'une automatisation inappropriée et rend la solution compatible avec une phase pilote.

## Limites

- les données sont synthétiques ;
- la demande n'intègre pas tous les facteurs externes ;
- les prévisions ne remplacent pas un système de planification complet ;
- le monitoring du modèle est démontré au niveau MVP, avec une extension possible vers un outil dédié.
