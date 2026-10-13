# Déploiement

Le déploiement local repose sur Docker Compose. Le service `pipeline` génère les données, exécute les contrôles, entraîne le modèle et produit les prévisions. Le service `app` lance Streamlit.

```bash
docker compose up --build
```

La preuve vidéo doit montrer :

1. le démarrage des services ;
2. l'absence d'erreur bloquante dans les logs ;
3. l'apparition de `metrics.json` et `forecast_future.csv` ;
4. l'ouverture du dashboard sur `http://localhost:8501` ;
5. une filtration par catégorie et l'affichage d'un risque de rupture.
