# Documentation technique — TERROVIA

## 1. Architecture générale
TERROVIA sépare les sources, les traitements, les résultats et l'interface :

- data/raw/ : fichiers sources archivés et non modifiés ;
- data/processed/ : couches réparées, données préparées et indicateurs dérivés ;
- scripts/ : scripts Python d'audit, de réparation, d'analyse et de cartographie ;
- dashboard/ : application Streamlit ;
- tests/ : tests automatisés ;
- reports/ : rapports d'audit, résultats et figures ;
- docs/ : documentation, décisions et journal de travail.

Le tableau de bord lit les fichiers préparés depuis data/processed/accessibility/. Il ne lit pas directement les GeoJSON bruts agricoles.

## 2. Environnement logiciel
Le projet déclare Python >=3.13 et <3.14 dans pyproject.toml. Les dépendances principales comprennent GeoPandas, Shapely, PyProj, Pyogrio, Pandas, SciPy, NetworkX, Matplotlib, Plotly et Streamlit. Les outils de développement comprennent pytest et Ruff. uv.lock fixe les versions résolues.

Installation reproductible :

    uv sync

Lancer l'application :

    uv run streamlit run dashboard/app.py

## 3. Chaîne de traitement disponible
Les scripts sont conçus pour être exécutés depuis la racine du projet.

1. scripts/audit_agricultural_layers.py : audit des couches agricoles brutes et production d'un rapport d'audit.
2. scripts/repair_agricultural_geometries.py : réparation contrôlée des géométries agricoles ; les géométries acceptées et les cas mis en quarantaine sont écrits dans les données préparées, sans écraser les sources.
3. scripts/audit_territorial_consistency.py : contrôles de cohérence des géométries administratives et de leur relation spatiale avec les couches agricoles préparées.
4. scripts/analyze_potential_accessibility.py : calcul des distances euclidiennes depuis les points représentatifs des petites exploitations vers les géométries d'infrastructures les plus proches.
5. scripts/create_accessibility_maps.py : génération des cartes statiques et de la couche régionale enrichie utilisée par le dashboard.

Avant de relancer un script, lire son code et les chemins de sortie afin d'éviter d'écraser des résultats dont on souhaite conserver une version. Les noms et les sorties détaillées sont décrits dans les rapports et dans les scripts.

## 4. Fichiers consommés par le dashboard
Répertoire : data/processed/accessibility/

- small_farms_potential_accessibility.csv : une ligne par petite exploitation préparée, avec les attributs administratifs disponibles et les distances aux sept familles d'équipements.
- regional_accessibility_summary.csv : statistiques agrégées par région.
- overall_accessibility_summary.csv : statistiques nationales par indicateur.
- regions_accessibility.geojson : géométries régionales enrichies pour la carte.
- methodology.json : CRS métrique, type de distance, effectifs et limites analytiques.

Le tableau de bord échoue si les fichiers obligatoires sont absents ou si leurs colonnes attendues ont été renommées.

## 5. Organisation interne de l'application
Le point d'entrée est dashboard/app.py. L'application :
- définit les familles d'indicateurs et les colonnes de distance associées ;
- charge les fichiers préparés avec Pandas et JSON ;
- met en cache les données avec Streamlit ;
- applique les filtres région et équipement ;
- calcule les statistiques descriptives du périmètre filtré ;
- construit les graphiques avec Plotly ;
- prépare les classements et les fichiers CSV exportables.

Les références courtes EXP-* sont générées pour l'affichage. Elles ne constituent pas un identifiant officiel des exploitations.

## 6. Tests et contrôles
Commandes utiles :

    uv run ruff check dashboard scripts tests
    uv run ruff format --check dashboard scripts tests
    uv run python -m compileall -q dashboard scripts tests
    uv run pytest -q

Les tests du dashboard peuvent également être complétés par Streamlit AppTest pour vérifier le rendu logique des composants et les scénarios de filtres. Un test automatisé sans exception ne remplace pas une vérification visuelle dans un navigateur.

## 7. Données, sécurité et reproductibilité
- Ne jamais modifier les fichiers de data/raw/.
- Ne pas publier les identifiants ou attributs personnels qui pourraient apparaître dans une nouvelle version des sources.
- Documenter les transformations et les paramètres.
- Conserver les rapports et les manifests de réparation.
- Vérifier les licences et conditions de réutilisation avant de redistribuer les données.
- Ne pas annoncer de distance routière ou de temps de parcours tant qu'un graphe routier validé et un modèle de coût n'ont pas été construits.

## 8. Évolutions à considérer
- confirmer les CRS et les correspondances administratives ;
- qualifier la provenance et les licences couche par couche ;
- améliorer la validation des points représentatifs et des rattachements territoriaux ;
- reconstruire et valider la topologie du réseau routier avant toute analyse de plus courts chemins ;
- intégrer les contraintes de saisonnalité, de capacité ou d'ouverture seulement si des données fiables sont disponibles ;
- étudier un modèle d'optimisation uniquement après définition justifiée de la demande, des sites candidats, des seuils et des fonctions de service.

## 9. Parcours utilisateur du dashboard
L'application présente trois onglets :
- Vue d'ensemble : périmètre de l'analyse, comparaison des distances médianes des sept familles de services, tableau détaillé accessible sous le graphique et exemple d'interprétation sur les marchés.
- Explorer les territoires : filtres région/service/repère, trois indicateurs principaux, carte conservant le contexte national, comparaison régionale, classement communal et exports CSV. La distribution des distances et les 20 exploitations les plus éloignées sont dans des sections repliables.
- Méthode et limites : définitions en langage courant, étapes du calcul et limites scientifiques.

Les filtres sont regroupés dans l'onglet d'exploration plutôt que dans la barre latérale. La page d'accueil privilégie la compréhension du périmètre et du constat national ; les analyses détaillées sont disponibles à la demande.
