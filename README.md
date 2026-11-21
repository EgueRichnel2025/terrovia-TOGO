# TERROVIA

**Relier les territoires agricoles aux opportunités.**

TERROVIA est un diagnostic géospatial de l'accessibilité potentielle des petites exploitations agricoles togolaises aux marchés et aux services de production.

Le projet transforme des données géographiques en indicateurs territoriaux, cartes et outils d'exploration pour faire ressortir des disparités et éclairer les investigations de planification.

> Périmètre scientifique actuel : les résultats mesurent des distances euclidiennes (en ligne droite), pas des distances routières ou des temps de trajet. Ils décrivent la proximité des infrastructures recensées, pas l'accès effectif des producteurs.

## Question étudiée

Comment la proximité géographique des petites exploitations agricoles aux marchés et aux services de production varie-t-elle selon les territoires au Togo, et quelles zones méritent une attention plus approfondie ?

## Résultats disponibles

- 13 076 petites exploitations intégrées au calcul exploratoire.
- Sept familles d'équipements analysées séparément.
- Statistiques nationales et régionales : médianes, percentiles et parts au-delà de seuils descriptifs.
- Comparaisons territoriales et exploration interactive.
- Audits géométriques et de cohérence territoriale documentés.

Les seuils de 5 km et 10 km sont des repères descriptifs, pas des normes officielles. Les catégories d'équipements n'ont pas toutes la même fonction et ne doivent pas être classées comme si elles étaient interchangeables.

## Tableau de bord

Application Python construite avec Streamlit.

Prérequis : Python 3.13 et uv.

Installation et lancement depuis la racine :

    uv sync
    uv run python scripts/prepare_streamlit_french.py
    uv run streamlit run dashboard/app.py

Les données préparées nécessaires au dashboard sont des fichiers locaux sous data/processed/. Elles ne sont pas incluses dans ce dépôt public. Leur provenance, leurs licences et leurs conditions d'accès doivent être vérifiées avant utilisation.

## Vérifications

    uv run ruff check dashboard scripts tests
    uv run ruff format --check dashboard scripts tests
    uv run python -m compileall -q dashboard scripts tests
    uv run pytest -q

## Documentation

- Guide utilisateur : docs/USER_GUIDE.md
- Méthodologie et limites : docs/METHODOLOGY.md
- Documentation technique : docs/TECHNICAL_DOCUMENTATION.md
- Dictionnaire des données : docs/DATA_DICTIONARY.md
- État de préparation au Data Challenge : docs/CHALLENGE_READINESS.md
- Feuille de route de finalisation : docs/ROADMAP_FINALISATION_CHALLENGE.md
- Politique de publication : docs/PUBLICATION_POLICY.md
- Analyse exploratoire : reports/ANALYSE_ACCESSIBILITE_POTENTIELLE_2026-11-20.md
- Note décisionnelle territoriale : reports/NOTE_DECISIONNELLE_TERRITORIALE_2026-11-20.md
- Registre de provenance : reports/REGISTRE_PROVENANCE_DONNEES.md

## Structure

    dashboard/      Application Streamlit
    scripts/        Audits, préparation et analyse géospatiale
    tests/          Tests automatisés
    docs/           Guides et documentation méthodologique
    reports/        Analyses agrégées et figures sélectionnées
    data/raw/       Sources locales — non versionnées
    data/processed/ Dérivés locaux — non versionnés

## Limites connues

- Distances calculées en EPSG:32631 depuis un point représentatif intérieur vers la géométrie la plus proche.
- Réseau routier non validé topologiquement ; aucune accessibilité routière ni durée de parcours n'est produite.
- Capacité, horaires, prix, état et fonctionnement des infrastructures non modélisés exhaustivement.
- Couche source ZAAP/ZAPB ne permettant pas encore de distinguer les deux catégories.
- Correspondances entre FID administratifs et noms régionaux encore candidates.
- Licences et conditions de redistribution à confirmer avant toute diffusion des données sources.

## Publication des données

Ce dépôt public ne distribue ni les données brutes ni les fichiers dérivés détaillés. Certaines sources comportent des identifiants, coordonnées ou informations de contact. Lire docs/PUBLICATION_POLICY.md avant d'ajouter tout jeu de données.

## Statut

Projet de recherche exploratoire en cours. Les résultats ne constituent pas une mesure officielle de l'accès aux services agricoles et ne doivent pas être interprétés comme une recommandation d'investissement sans analyses complémentaires.
