# Profils de proximité géographique — TERROVIA

Date d'entraînement : 2026-11-22

## Objectif

Un modèle K-Means non supervisé a été entraîné sur les sept distances séparant les
13 076 petites exploitations préparées des familles d'équipements cartographiées.
L'objectif est d'identifier des profils de proximité similaires, et non de prédire
l'accès réel aux services.

## Préparation des variables

Les sept distances en kilomètres sont transformées par `log1p`, puis mises à
l'échelle avec `RobustScaler`. Cette préparation limite l'influence de distributions
très asymétriques et des écarts de dispersion entre les familles d'équipements.

## Comparaison des modèles

|   Profils |   Silhouette |   Davies-Bouldin |   Calinski-Harabasz |   Part minimale (%) |   Stabilité ARI moyenne |   Inertie |
|----------:|-------------:|-----------------:|--------------------:|--------------------:|------------------------:|----------:|
|     2.000 |        0.146 |            2.318 |            2208.660 |              44.501 |                   0.996 | 42154.222 |
|     3.000 |        0.164 |            1.913 |            2300.244 |              27.210 |                   0.991 | 36448.921 |
|     4.000 |        0.159 |            1.762 |            2245.158 |              16.381 |                   0.995 | 32519.497 |
|     5.000 |        0.158 |            1.701 |            2146.516 |              12.634 |                   0.992 | 29739.965 |
|     6.000 |        0.160 |            1.675 |            2005.666 |              12.359 |                   0.994 | 27882.148 |
|     7.000 |        0.159 |            1.649 |            1866.827 |              10.653 |                   0.958 | 26534.153 |
|     8.000 |        0.158 |            1.617 |            1764.686 |               7.923 |                   0.991 | 25330.919 |

La silhouette mesure la cohésion et la séparation des groupes (plus elle est élevée,
mieux c'est). L'indice de Davies-Bouldin est préférable lorsqu'il est plus faible ;
l'indice de Calinski-Harabasz lorsqu'il est plus élevé. La stabilité est évaluée par
l'indice ARI entre plusieurs initialisations. Ces critères décrivent la structure des
données, pas une précision prédictive.

## Modèle retenu

- Algorithme : K-Means.
- Nombre de profils : 3.
- Silhouette : 0.164.
- Davies-Bouldin : 1.913.
- Calinski-Harabasz : 2300.2.
- Stabilité ARI moyenne : 0.991.
- Taille du plus petit profil : 27.21 %.
- Appréciation : **Structure exploratoire modérée**.

## Résumé des profils

|   Numéro | Profil   |   Exploitations |   Part nationale (%) |   Marchés · médiane (km) |   Marchés · P90 (km) |   Magasins d'intrants · médiane (km) |   Magasins d'intrants · P90 (km) |   Coopératives · médiane (km) |   Coopératives · P90 (km) |   ESOP · médiane (km) |   ESOP · P90 (km) |   Pépinières ponctuelles · médiane (km) |   Pépinières ponctuelles · P90 (km) |   Pépinières surfaciques · médiane (km) |   Pépinières surfaciques · P90 (km) |   ZAAP / ZAPB · médiane (km) |   ZAAP / ZAPB · P90 (km) |
|---------:|:---------|----------------:|---------------------:|-------------------------:|---------------------:|-------------------------------------:|---------------------------------:|------------------------------:|--------------------------:|----------------------:|------------------:|----------------------------------------:|------------------------------------:|----------------------------------------:|------------------------------------:|-----------------------------:|-------------------------:|
|        1 | Profil 1 |            3558 |                27.21 |                     1.79 |                 4.03 |                                 3.75 |                             8.46 |                          0.57 |                      1.62 |                 15.35 |             27.55 |                                    4.28 |                               11.99 |                                   25.41 |                              127.47 |                         6.58 |                    13.37 |
|        2 | Profil 2 |            5368 |                41.05 |                     2.71 |                 5.71 |                                 4.25 |                             8.72 |                          0.76 |                      2.21 |                 40.02 |             56.60 |                                    8.67 |                               28.35 |                                    6.35 |                               19.96 |                         9.96 |                    17.79 |
|        3 | Profil 3 |            4150 |                31.74 |                     2.42 |                 6.20 |                                11.28 |                            26.20 |                          0.82 |                      2.56 |                 41.29 |             59.37 |                                    4.26 |                               10.68 |                                   61.64 |                              134.64 |                         4.22 |                     9.62 |

Les numéros de profil sont ordonnés selon les médianes relatives des distances afin
de faciliter la lecture. Ils ne constituent ni score synthétique, ni classement de
performance ou d'investissement.

## Répartition régionale

Part de chaque profil au sein de chaque région (en %) :

| region_nom_bdd   |   Profil 1 |   Profil 2 |   Profil 3 |
|:-----------------|-----------:|-----------:|-----------:|
| Centrale         |        2.6 |       77.4 |       20.1 |
| Kara             |       36.4 |       57.2 |        6.5 |
| Maritime         |       13.9 |       59.9 |       26.2 |
| Plateaux         |       40.2 |       56.0 |        3.8 |
| Savanes          |       38.5 |        4.4 |       57.1 |

Cette répartition décrit la composition des groupes dans les données préparées.
Elle ne mesure pas la qualité des services ni l'accès effectif.

## Limites d'interprétation

- Il n'existe pas de variable cible ni d'étiquettes de référence : aucune précision
  supervisée ne peut être annoncée.
- Les groupes sont exploratoires et dépendent des données cartographiées.
- Les distances sont euclidiennes, en ligne droite, et ne représentent pas un trajet.
- Le modèle ne connaît ni l'état des routes, ni les horaires, les prix, les stocks,
  la capacité, le statut opérationnel ou l'utilisation réelle des équipements.
- La présence d'un groupe dans une région ne suffit pas à conclure à une privation
  d'accès ou à justifier une implantation.

## Protection des données

Seules des synthèses par profil et région figurent dans ce rapport. Les affectations
individuelles et le fichier du modèle sont conservés dans `data/processed/`, exclu
du dépôt public.
