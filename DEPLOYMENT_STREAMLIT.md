# Déployer TERROVIA sur Streamlit Community Cloud

## Configuration du dépôt

- Dépôt : `EgueRichnel2025/terrovia-TOGO`
- Branche : `main`
- Fichier principal : `dashboard/app.py`
- Version Python : `3.13`
- Dépendances cloud : `requirements.txt`

Le déploiement sélectionne automatiquement `data/public/accessibility` lorsque les fichiers détaillés privés ne sont pas présents. Le site hébergé présente donc uniquement les agrégats et les profils régionaux.

## Étapes

1. Ouvrir https://share.streamlit.io et se connecter avec GitHub.
2. Autoriser Streamlit Community Cloud à accéder au dépôt.
3. Créer une application depuis `EgueRichnel2025/terrovia-TOGO`.
4. Choisir la branche `main` et le fichier `dashboard/app.py`.
5. Dans les paramètres avancés, sélectionner Python `3.13`.
6. Déployer, puis vérifier les quatre pages et les journaux de l'application.

Aucun secret ou fichier `.env` n'est nécessaire à cette application.
