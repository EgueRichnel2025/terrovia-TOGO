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
Le projet déclare Python >=3.13 et <3.14 dans pyproject.toml. Les dépendances principales comprennent GeoPandas, Shapely, PyProj, Pyogrio, Pandas, SciPy, NetworkX, Matplotlib, Plotly, Streamlit et scikit-learn. Tabulate sert à générer les tableaux Markdown des rapports. Les outils de développement comprennent pytest et Ruff. uv.lock fixe les versions résolues.

Installation reproductible :

    uv sync

Lancer l'application :

    uv run python scripts/prepare_streamlit_french.py
    uv run python scripts/train_accessibility_profiles.py
    uv run streamlit run dashboard/app.py

## 3. Chaîne de traitement disponible
Les scripts sont conçus pour être exécutés depuis la racine du projet.

1. scripts/audit_agricultural_layers.py : audit des couches agricoles brutes et production d'un rapport d'audit.
2. scripts/repair_agricultural_geometries.py : réparation contrôlée des géométries agricoles ; les géométries acceptées et les cas mis en quarantaine sont écrits dans les données préparées, sans écraser les sources.
3. scripts/audit_territorial_consistency.py : contrôles de cohérence des géométries administratives et de leur relation spatiale avec les couches agricoles préparées.
4. scripts/analyze_potential_accessibility.py : calcul des distances euclidiennes depuis les points représentatifs des petites exploitations vers les géométries d'infrastructures les plus proches.
5. scripts/create_accessibility_maps.py : génération des cartes statiques et de la couche régionale enrichie utilisée par le dashboard.
6. scripts/train_accessibility_profiles.py : entraînement reproductible d'un K-Means non supervisé sur les sept distances, comparaison de 2 à 8 profils, évaluation de stabilité et export d'agrégats nationaux et régionaux. Le modèle, les affectations individuelles et les résultats détaillés restent dans data/processed/accessibility/model/ (données locales non versionnées).

Avant de relancer un script, lire son code et les chemins de sortie afin d'éviter d'écraser des résultats dont on souhaite conserver une version. Les noms et les sorties détaillées sont décrits dans les rapports et dans les scripts.

## 4. Fichiers consommés par le dashboard
Répertoire : data/processed/accessibility/

- small_farms_potential_accessibility.csv : une ligne par petite exploitation préparée, avec les attributs administratifs disponibles et les distances aux sept familles d'équipements.
- regional_accessibility_summary.csv : statistiques agrégées par région.
- overall_accessibility_summary.csv : statistiques nationales par indicateur.
- regions_accessibility.geojson : géométries régionales enrichies pour la carte.
- methodology.json : CRS métrique, type de distance, effectifs et limites analytiques.
- model/profils_accessibilite.csv : médianes et P90 par profil, sans identifiant individuel.
- model/repartition_regionale_profils.csv : répartition agrégée des profils dans les régions.
- model/metadonnees_modele.json : algorithme, variables, paramètres et métriques d'évaluation.

Le tableau de bord échoue si les fichiers obligatoires sont absents ou si leurs colonnes attendues ont été renommées.

## 5. Organisation interne de l'application
Le point d'entrée est dashboard/app.py. L'application :
- définit les familles d'indicateurs et les colonnes de distance associées ;
- charge les fichiers préparés avec Pandas et JSON ;
- met en cache les données avec Streamlit ;
- applique les filtres région et équipement ;
- calcule les statistiques descriptives du périmètre filtré ;
- construit les graphiques avec Plotly ;
- prépare les classements et les fichiers CSV exportables ;
- affiche les profils K-Means à partir des seuls agrégats publiables.

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
L'application présente quatre pages :
- Vue d'ensemble : périmètre de l'analyse, comparaison des distances médianes des sept familles de services, tableau détaillé accessible sous le graphique et exemple d'interprétation sur les marchés.
- Explorer les territoires : filtres région/service/repère, trois indicateurs principaux, carte conservant le contexte national, comparaison régionale, classement communal et exports CSV. La distribution des distances et les 20 exploitations les plus éloignées sont dans des sections repliables.
- Profils d'accessibilité : comparaison des trois groupes exploratoires, signatures de distance et répartition régionale.
- Méthode et limites : définitions en langage courant, étapes du calcul et limites scientifiques.

Les filtres sont regroupés dans l'onglet d'exploration plutôt que dans la barre latérale. La page d'accueil privilégie la compréhension du périmètre et du constat national ; les analyses détaillées sont disponibles à la demande.


## 10. Modèle de profils de proximité

Le script `scripts/train_accessibility_profiles.py` charge uniquement les sept colonnes de distance, la région et la référence technique locale de l'exploitation. Les distances sont transformées par `log1p` et mises à l'échelle par `RobustScaler`. Les candidats K-Means (K=2 à 8) sont comparés avec silhouette, Davies-Bouldin, Calinski-Harabasz, part minimale de chaque groupe et stabilité ARI sur plusieurs initialisations. Les critères de sélection exigent au moins 1 % d'observations dans chaque groupe et un ARI moyen d'au moins 0,70.

Le modèle retenu sur les données du 22 novembre 2026 comporte trois profils, une silhouette de 0,164 et un ARI moyen de 0,991. Les résultats sont stables entre initialisations mais leur séparation reste modérée. Le rapport `reports/PROFILS_ACCESSIBILITE_MODELE_2026-11-22.md` présente les métriques et les profils agrégés.

Les fichiers d'affectation par exploitation et le modèle sérialisé ne doivent pas être ajoutés au dépôt public. La page du tableau de bord consomme uniquement les synthèses par profil et par région.
