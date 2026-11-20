# TERROVIA — Note décisionnelle territoriale

**Date de référence :** 20 novembre 2026
**Périmètre :** 13 076 petites exploitations agricoles cartographiées et préparées.
**Objet :** transformer les résultats de proximité géographique en pistes d'investigation territoriale.

> **Précaution de lecture.** Les distances sont euclidiennes, calculées en EPSG:32631 depuis un point représentatif intérieur de chaque exploitation vers la géométrie cartographiée la plus proche. Elles ne sont ni des distances routières ni des temps de trajet. Les seuils de 5 km et 10 km sont des repères descriptifs, pas des normes d'accessibilité.

## 1. Ce que les résultats permettent de dire

Les résultats mettent en évidence des profils différents selon les familles d'équipements. Il n'existe donc pas un classement unique des régions qui résumerait toutes les dimensions de l'accès aux services agricoles.

| Famille cartographiée | Médiane nationale | P90 national | Exploitations à plus de 10 km |
|---|---:|---:|---:|
| Marchés | 2,34 km | 5,47 km | 0,69 % |
| Magasins d'intrants | 5,51 km | 14,71 km | 23,14 % |
| Coopératives | 0,72 km | 2,18 km | 0,02 % |
| ESOP | 34,71 km | 57,09 km | 93,59 % |
| Pépinières ponctuelles | 5,93 km | 17,48 km | 26,73 % |
| Pépinières surfaciques | 13,28 km | 125,63 km | 59,31 % |
| Couche combinée ZAAP/ZAPB | 6,98 km | 14,92 km | 29,83 % |

Les fonctions des équipements ne sont pas interchangeables. La distance à une coopérative ne peut pas être assimilée à la distance à un marché, à un magasin d'intrants ou à une ESOP.

## 2. Signaux territoriaux à examiner en priorité

### A. Plateaux — signal relatif pour la proximité des marchés

- 1 453 exploitations dans le périmètre analysé.
- Médiane aux marchés : **3,42 km**, la plus élevée des cinq régions.
- P90 : **6,81 km**.
- **26,08 %** des exploitations se situent à plus de 5 km d'un marché cartographié, contre 12,73 % au niveau national.

**Piste d'action :** vérifier sur le terrain et avec les acteurs locaux les localités présentant les distances les plus élevées, puis confronter ces cas aux itinéraires réellement praticables et aux marchés effectivement fréquentés. Ce résultat justifie une investigation, pas une décision automatique de création de marché.

### B. Savanes — signal relatif pour la proximité des magasins d'intrants

- 4 389 exploitations dans le périmètre analysé.
- Médiane aux magasins d'intrants : **8,54 km**, contre 5,51 km au niveau national.
- P90 : **25,47 km**.
- **43,27 %** des exploitations sont à plus de 10 km d'un magasin cartographié, contre 23,14 % au niveau national.

**Piste d'action :** vérifier la présence, l'activité, les stocks, les horaires et les conditions d'accès des magasins recensés dans les communes concernées. Une enquête sur les circuits d'approvisionnement pourrait déterminer si le signal géométrique correspond à une difficulté vécue par les producteurs.

### C. Savanes — anomalie de couverture à vérifier pour les pépinières surfaciques

La médiane calculée pour cette couche atteint **116,29 km** dans les Savanes, avec un P90 de 138,33 km. Cette valeur est très supérieure aux autres régions et à la médiane nationale de 13,28 km.

**Interprétation prudente :** ce résultat peut refléter une faible couverture de la couche dans cette région, un inventaire incomplet ou une anomalie de géolocalisation. Il ne démontre pas à lui seul l'absence de pépinières. Il faut vérifier visuellement la distribution des 209 polygones et confronter la couche à une source locale avant toute conclusion opérationnelle.

### D. Centrale — signal à examiner pour la proximité des ESOP

La médiane aux 12 ESOP cartographiées est de **52,67 km** dans la région Centrale et de 34,71 km au niveau national. Le nombre total d'ESOP étant limité à 12, cette mesure décrit uniquement la proximité des entités recensées et demeure sensible à l'exhaustivité de l'inventaire.

**Piste d'action :** vérifier la liste et le statut des ESOP, leurs zones d'intervention et les filières qu'elles desservent. La distance seule ne renseigne ni sur les services proposés ni sur les relations commerciales avec les exploitations.

### E. Marchés — profil national relativement plus favorable, mais hétérogène

À l'échelle nationale, la médiane est de 2,34 km et 12,73 % des exploitations dépassent 5 km. Les Savanes présentent toutefois la plus forte part au-delà de 10 km (1,62 %), tandis que les Plateaux affichent la plus forte part au-delà de 5 km (26,08 %).

**Piste d'action :** examiner séparément les communes et localités les plus éloignées plutôt que de s'appuyer uniquement sur une moyenne ou une médiane régionale.

## 3. Ce que les résultats ne permettent pas de conclure

- Ils ne mesurent pas les itinéraires, les temps, les coûts ou la saisonnalité des déplacements.
- Ils ne prouvent pas que les infrastructures sont ouvertes, actives, approvisionnées, abordables ou accessibles à tous.
- Ils ne garantissent pas que les inventaires sont exhaustifs.
- Les 12 ESOP et les 209 pépinières surfaciques constituent des effectifs limités ; les résultats associés doivent être lus avec prudence.
- La couche ZAAP/ZAPB reste combinée : les deux catégories ne sont pas distinguées de manière fiable.
- Les noms régionaux proviennent des attributs des couches agricoles ; les correspondances administratives candidates doivent être confirmées avant une interprétation officielle.
- Les résultats décrivent les 13 076 entités préparées, pas nécessairement l'ensemble des exploitations agricoles du Togo.

## 4. Recommandations transversales

1. **Valider les inventaires** : faire confirmer par les services compétents et les organisations locales l'existence, la localisation et le statut opérationnel des équipements.
2. **Prioriser les vérifications de terrain** : commencer par les communes présentant des P90 et des parts au-delà des repères élevés, en conservant les effectifs de chaque groupe.
3. **Compléter l'information sur les services** : ajouter, si des sources fiables existent, capacité, horaires, filières desservies, disponibilité des intrants et conditions d'accès.
4. **Améliorer la mesure de mobilité** : construire ultérieurement une analyse de réseau seulement après validation topologique, points d'accrochage, modes de déplacement et coûts de parcours.
5. **Éviter un indice composite prématuré** : ne pas agréger des catégories de services différentes avec des poids arbitraires.

## 5. Ordre de travail recommandé pour les décideurs

| Priorité d'investigation | Territoire / dimension | Justification issue des données | Vérification nécessaire |
|---|---|---|---|
| 1 | Savanes — magasins d'intrants | 43,27 % à plus de 10 km ; P90 25,47 km | Statut, stock, accès réel et circuits d'approvisionnement |
| 2 | Plateaux — marchés | Médiane 3,42 km ; 26,08 % à plus de 5 km | Itinéraires, marchés fréquentés et localités concernées |
| 3 | Savanes — pépinières surfaciques | Médiane 116,29 km, valeur atypique | Couverture, géolocalisation et exhaustivité de la couche |
| 4 | Centrale — ESOP | Médiane 52,67 km ; inventaire national de 12 entités | Liste exhaustive, filières et zones de service |

Cet ordre est une proposition d'investigation fondée sur les signaux observés. Il ne constitue pas un classement officiel des besoins ni une recommandation d'investissement.

## 6. Références internes pour reproduction

- `reports/ANALYSE_ACCESSIBILITE_POTENTIELLE_2026-11-20.md`
- `docs/METHODOLOGY.md`
- `data/processed/accessibility/overall_accessibility_summary.csv` (données locales non versionnées)
- `data/processed/accessibility/regional_accessibility_summary.csv` (données locales non versionnées)
- `scripts/analyze_potential_accessibility.py`
