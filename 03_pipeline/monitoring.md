# Monitoring et alertes du pipeline

## Métriques suivies

- durée d'exécution ;
- nombre de lignes entrantes et sortantes ;
- taux de rejet ;
- nombre de doublons ;
- nombre de références inconnues ;
- taux de valeurs manquantes ;
- erreur du modèle ;
- dérive de distribution ;
- statut du chargement en base.

## Niveaux d'alerte

- **OK** : traitement terminé et métriques sous les seuils ;
- **WARNING** : dégradation à analyser ;
- **ALERT** : traitement bloqué, métrique critique dépassée ou dérive importante.

## Production

Dans un environnement réel, `monitoring_report.json` serait envoyé vers un outil d'alerting tel que Prometheus/Grafana, CloudWatch ou un système équivalent. Le MVP fournit le contrat de métriques et le rapport exploitable, mais pas un serveur de monitoring temps réel.
