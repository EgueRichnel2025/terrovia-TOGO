# Guide utilisateur — Tableau de bord TERROVIA

## À quoi sert TERROVIA ?
TERROVIA étudie la proximité géographique entre les petites exploitations agricoles recensées au Togo et sept familles de services ou d'équipements : marchés, magasins d'intrants, coopératives, ESOP, pépinières ponctuelles, pépinières surfaciques et couche combinée ZAAP/ZAPB.

L'objectif est de comparer les distances entre territoires et de repérer les situations qui méritent une vérification plus approfondie. Le tableau de bord ne mesure pas l'accès réel aux services.

## Lancer l'application
Depuis la racine du projet :

    uv sync
    uv run python scripts/prepare_streamlit_french.py
    uv run python scripts/train_accessibility_profiles.py
    uv run streamlit run dashboard/app.py

Ouvrir l'adresse locale indiquée dans le terminal, généralement http://localhost:8501. Laisser le terminal ouvert pendant l'utilisation. Pour arrêter l'application, revenir au terminal et faire Ctrl+C.

## Le parcours dans le tableau de bord

L'application comporte quatre pages accessibles depuis le menu de navigation latéral. Le parcours conseillé va de la synthèse générale vers l'exploration et les profils, puis vers les explications méthodologiques.

### 1. Vue d'ensemble
C'est la page d'accueil. Elle donne immédiatement le périmètre de l'analyse :
- le nombre de petites exploitations intégrées aux calculs ;
- le nombre de régions présentes dans les données ;
- les sept familles de services étudiées.

Le graphique compare les distances médianes vers les équipements recensés. Le tableau détaillé (à ouvrir sous le graphique) donne aussi le P90 et le nombre d'équipements inventoriés pour chaque famille. Les catégories ne rendent pas toutes le même service : leur classement ne représente donc ni une hiérarchie de qualité ni une hiérarchie d'importance.

Un exemple consacré aux marchés montre comment interpréter une différence entre régions. Il signale une piste à examiner, pas une preuve d'enclavement. Le nombre d'exploitations par région est accessible dans une section repliable ; il s'agit d'effectifs présents dans le fichier analysé, et non d'une densité agricole.

### 2. Explorer les territoires
Cet onglet sert à examiner un territoire et un service précis. Les filtres sont réunis au même endroit :

1. **Région :** choisissez une région ou conservez « Toutes les régions ».
2. **Service à examiner :** sélectionnez une seule famille d'équipements.
3. **Repère de distance :** déplacez le curseur pour compter les exploitations dont la distance dépasse ce repère.

Le curseur commence au 75e percentile (P75) national de la catégorie choisie. C'est un point de départ statistique, pas une norme officielle. Vous pouvez le modifier.

Les trois cartes d'indicateurs affichent :
- la distance médiane ;
- la distance sous laquelle se trouvent 90 % des distances (P90) ;
- la part des exploitations au-delà du repère, avec leur nombre.

Le nombre d'exploitations concernées par le filtre est indiqué au-dessus des indicateurs. La carte conserve les cinq régions pour garder le contexte national. Le tableau repliable permet de comparer les médianes et les P90 régionaux.

Le classement communal aide à repérer les communes qui méritent une vérification. Il ne retient que les groupes comptant au moins 10 exploitations dans la sélection afin d'éviter de classer des effectifs trop faibles. La distribution des distances et les 20 exploitations les plus éloignées sont disponibles dans des sections repliables afin de ne pas surcharger la lecture initiale.

Les boutons de téléchargement exportent le classement communal et les observations filtrées au format CSV. Les fichiers correspondent à la sélection active. Les références EXP-* sont des références d'affichage générées par le tableau de bord ; elles ne remplacent pas les identifiants officiels.

### 3. Profils d'accessibilité
Cette page présente les trois groupes exploratoires obtenus par K-Means à partir des sept distances. Elle permet de comparer leur poids dans l'ensemble des exploitations, leurs distances médianes par famille de services et leur répartition dans les cinq régions.

La silhouette du modèle retenu est de 0,164 : la séparation des groupes est modérée et certains profils se recouvrent. La stabilité ARI moyenne entre initialisations est de 0,991. Cette stabilité signifie que l'algorithme retrouve des groupes proches lorsqu'il est relancé ; elle ne valide pas à elle seule une typologie réelle.

Les profils ne sont pas des notes de performance. Ils ne disent pas si une exploitation accède réellement à un service et ne doivent pas être utilisés seuls pour décider d'un investissement.

### 4. Méthode et limites
Cet onglet explique comment les chiffres sont calculés et comment les interpréter :
- **Médiane :** la moitié des exploitations a une distance inférieure ou égale à cette valeur.
- **P90 :** neuf exploitations sur dix ont une distance inférieure ou égale à cette valeur.
- **Part au-delà du repère :** proportion des exploitations dont la distance dépasse le curseur.
- **Équipements recensés :** nombre d'entités présentes dans la couche cartographique ; cela ne garantit pas leur fonctionnement.

Il décrit également les étapes du calcul, le système de coordonnées utilisé et les limites à prendre en compte.

## Limites à garder en tête
Les distances sont calculées en ligne droite dans le système projeté métrique EPSG:32631, depuis un point intérieur représentatif de chaque exploitation vers la géométrie cartographiée la plus proche.

Elles ne correspondent pas à des distances routières ou à des temps de trajet. Le calcul ne prend pas en compte l'état des routes, les pistes saisonnières, les obstacles, le mode de transport, les coûts, les horaires, la capacité ou le fonctionnement réel des équipements.

Les 5 km, 10 km et le P75 sont des repères descriptifs exploratoires, pas des normes nationales. Les profils K-Means sont eux aussi exploratoires et fondés uniquement sur les distances cartographiques. Une distance élevée signale un cas à examiner ; elle ne prouve pas qu'une exploitation est privée d'un service.

La couche source ZAAP/ZAPB ne distingue pas les deux catégories. Certaines correspondances administratives restent à confirmer. L'inventaire des équipements peut être incomplet.

## Dépannage
- **La page ne s'ouvre pas :** vérifier que le serveur Streamlit fonctionne toujours dans le terminal et utiliser l'adresse qu'il affiche.
- **Un fichier est introuvable :** vérifier que les sorties préparées de data/processed/accessibility/ sont présentes.
- **Les résultats semblent inattendus :** vérifier la région, le service et le repère de distance ; consulter l'onglet « Méthode et limites ».
- **L'affichage semble ancien :** actualiser le navigateur avec Ctrl+F5.

Pour les détails scientifiques et les sources, consulter docs/METHODOLOGY.md, docs/DATA_DICTIONARY.md et les rapports du dossier reports/.
