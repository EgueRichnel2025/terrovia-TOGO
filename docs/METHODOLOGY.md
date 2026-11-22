# Méthodologie et limites — TERROVIA

## 1. Question étudiée
Dans quelle mesure la répartition spatiale des petites exploitations agricoles et des infrastructures recensées est-elle associée à des différences de proximité géographique aux marchés et aux services de production au Togo ?

L'analyse actuelle constitue une première mesure d'accessibilité potentielle. Elle ne mesure pas l'accès effectif ni la performance économique des exploitations.

## 2. Unité d'analyse
L'unité de demande utilisée est une petite exploitation agricole représentée par une entité surfacique dans la source. Après préparation géométrique et contrôles, 13 076 exploitations sont incluses dans le calcul.

Chaque polygone est représenté par un point intérieur représentatif. Ce point est une approximation géométrique : il ne représente pas nécessairement l'entrée de la parcelle, l'habitation, le lieu de stockage ou le point d'accès routier.

## 3. Infrastructures comparées
Les distances sont calculées séparément vers les géométries cartographiées des catégories suivantes :
- marchés ;
- magasins d'intrants ;
- coopératives agricoles ;
- ESOP ;
- pépinières ponctuelles ;
- pépinières surfaciques ;
- couche combinée ZAAP/ZAPB.

Les catégories sont conservées séparément car leurs fonctions ne sont pas équivalentes. Les couches de pépinières ponctuelles et surfaciques sont également distinctes.

## 4. Mesure de distance
Les géométries sont traitées dans le système projeté métrique EPSG:32631. Pour chaque exploitation et chaque famille d'équipements, la distance euclidienne minimale est calculée entre le point représentatif de l'exploitation et la géométrie de l'équipement le plus proche.

Formellement, pour une exploitation i et une catégorie d'équipements S :

    d(i,S) = min distance_euclidienne(p_i, g_j), pour g_j appartenant à S

Pour les marchés surfaciques, la distance est mesurée vers le polygone du marché, et non vers son centroïde. Pour les couches ponctuelles, elle est mesurée vers le point cartographié.

Cette mesure décrit une proximité géométrique en ligne droite. Elle ne correspond pas à une distance de déplacement réelle.

## 5. Indicateurs descriptifs
Les indicateurs utilisés comprennent :
- effectif d'exploitations analysées ;
- moyenne et médiane des distances ;
- percentiles (P75, P90, P95 selon les tableaux) ;
- distance maximale ;
- nombre et part des observations au-delà de 5 km et 10 km ;
- agrégats régionaux et communaux.

Le seuil de 5 km et celui de 10 km sont utilisés comme repères exploratoires pour décrire la distribution. Ils ne sont pas présentés comme des normes nationales, des seuils réglementaires ou des distances acceptables universelles.

Dans l'interface, le seuil initial proposé pour une famille d'équipements correspond à son P75 national. Ce choix facilite l'exploration de la distribution propre à chaque catégorie ; il ne traduit pas une norme de service.

## 6. Résultats de référence du 20 novembre 2026
Pour les 13 076 petites exploitations préparées :
- marchés : médiane 2,34 km ; P90 5,47 km ;
- magasins d'intrants : médiane 5,51 km ; P90 14,71 km ;
- coopératives : médiane 0,72 km ; P90 2,18 km ;
- ESOP : médiane 34,71 km ; P90 57,09 km ;
- pépinières ponctuelles : médiane 5,93 km ; P90 17,48 km ;
- pépinières surfaciques : médiane 13,28 km ; P90 125,63 km ;
- ZAAP/ZAPB : médiane 6,98 km ; P90 14,92 km.

Ces valeurs décrivent uniquement les couches et les entités incluses dans le traitement. Elles ne prouvent pas que les services sont disponibles, opérationnels ou accessibles aux producteurs.

## 7. Limites et biais connus
1. **Réseau de transport non modélisé :** aucune distance routière ni durée de trajet n'est calculée.
2. **Qualité du réseau :** le graphe routier brut présente des problèmes de connectivité topologique ; il doit être noded/snapped et validé avant tout calcul de plus court chemin.
3. **État des routes :** revêtement, praticabilité, saisonnalité, ponts, barrières et modes de transport ne sont pas modélisés.
4. **Fonctionnement des services :** capacité, horaires, prix, qualité, disponibilité et statut opérationnel ne sont pas connus de manière exhaustive.
5. **Exhaustivité :** les points et polygones cartographiés ne garantissent pas l'inventaire complet des services et exploitations existants.
6. **Représentation des exploitations :** un point intérieur représentatif ne correspond pas nécessairement au lieu réel d'accès.
7. **Données manquantes :** plusieurs attributs descriptifs contiennent des codes de non-réponse ; les localités manquantes réduisent les possibilités d'interprétation nominative.
8. **ZAAP/ZAPB :** la couche source ne permet pas de distinguer sûrement les deux catégories.
9. **Limites administratives :** les CSV WKT ne déclarent pas de CRS ; les correspondances FID-région sont candidates et doivent être confirmées par une nomenclature officielle.
10. **Seuils :** 5 km, 10 km et P75 sont descriptifs et exploratoires, pas normatifs.

## 8. Interprétation responsable
Une distance faible indique une proximité géométrique d'une infrastructure cartographiée. Elle ne prouve pas que l'exploitant utilise cette infrastructure, peut y accéder, y trouve le service requis ou peut s'y rendre à un coût acceptable.

Une distance élevée signale un cas à examiner, pas automatiquement une absence de service ou une situation d'enclavement. Les résultats doivent être confrontés à la qualité des données, à la topologie routière, aux conditions de mobilité et à des informations de terrain si elles deviennent disponibles.

## 9. Extensions méthodologiques conditionnelles
Une analyse réseau pourra être envisagée après validation de la topologie, de l'accrochage des exploitations et des équipements, des composantes connexes et des coûts de déplacement. Un indice composite ou un problème de localisation-allocation ne devra être construit qu'après justification des variables, des poids, des unités de demande, des sites candidats et des seuils de service.


## 10. Profils exploratoires par apprentissage non supervisé

Une segmentation K-Means a été entraînée sur les sept distances euclidiennes disponibles pour les 13 076 exploitations. Les variables sont transformées par `log1p`, puis mises à l'échelle avec `RobustScaler`. Les modèles de 2 à 8 groupes sont comparés par silhouette, Davies-Bouldin, Calinski-Harabasz, taille minimale des groupes et stabilité entre initialisations (indice ARI).

Le modèle retenu comporte trois profils. La silhouette observée est de 0,164 et la stabilité ARI moyenne de 0,991. La stabilité indique que l'algorithme retrouve des groupes similaires selon les initialisations ; la silhouette modérée indique toutefois un chevauchement entre les groupes. La segmentation doit donc être considérée comme exploratoire, et non comme une typologie naturelle ou définitive.

Les profils sont décrits par leurs distributions de distances et leur composition régionale. Leur numérotation facilite la lecture ; elle ne constitue ni un indice composite, ni un classement de performance ou d'investissement. Les affectations individuelles et le modèle entraîné sont conservés dans les fichiers locaux non versionnés. Seuls les agrégats sont publiés.

Cette extension ne dispose d'aucune variable cible ni vérité terrain. Aucune précision prédictive ne peut être calculée ou annoncée. Elle ne mesure ni distance routière, ni durée, ni coût, ni disponibilité, ni utilisation effective des services.
