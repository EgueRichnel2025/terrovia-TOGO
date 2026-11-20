# TERROVIA — Registre de provenance et de réutilisation des données

**État au : 19 novembre 2026**
**Statut : registre préliminaire — vérification des fiches individuelles encore nécessaire.**

## 1. Règles de traçabilité

Pour chaque ressource, conserver : intitulé exact, producteur, portail, URL de la fiche, URL ou identifiant de l'export, date de publication/mise à jour, date de téléchargement, format, CRS, nombre d'entités, empreinte SHA-256, licence et conditions de réutilisation.

Le téléchargement d'un fichier ne prouve pas à lui seul que sa redistribution est autorisée ni qu'il compte pour un éventuel quota de sources du challenge. Ne pas republier les données brutes avant validation des droits. Pour toute donnée Géodata réutilisée, respecter les CGU en vigueur et citer la source ainsi que sa dernière date de mise à jour.

## 2. Ressources agricoles archivées

Portail déclaré dans les notes de collecte : [Géodata Togo — Données](https://geodata.gouv.tg/donnees). Les exports locaux sont datés du 18 novembre 2026 et déclarent EPSG:4326. Les empreintes SHA-256 et les noms exacts des fichiers sont conservés dans data/raw/agriculture/README.md.

| Ressource | Entités | Géométrie | Fiche individuelle / identifiant | Producteur / licence |
|---|---:|---|---|---|
| ZAAPs - Formes | 144 | Polygon | À rattacher à la fiche exacte | À confirmer |
| Marchés | 1 078 | MultiPolygon | À rattacher à la fiche exacte | À confirmer |
| Coopératives - Agricoles | 6 859 | Point | À rattacher à la fiche exacte | À confirmer |
| ESOP | 12 | Point | À rattacher à la fiche exacte | À confirmer |
| Petites exploitations agricoles | 13 119 | MultiPolygon | À rattacher à la fiche exacte | À confirmer |
| Grandes exploitations agricoles - Champs | 601 | Polygon | À rattacher à la fiche exacte | À confirmer |
| Grandes exploitations agricoles - Établissements | 220 | Point | À rattacher à la fiche exacte | À confirmer |
| Plantations agricoles - Établissements | 2 911 | Point | À rattacher à la fiche exacte | À confirmer |
| Pépinières agricoles | 728 | Point | À rattacher à la fiche exacte | À confirmer |
| Pépinières agricoles - Autres | 210 | Polygon | À rattacher à la fiche exacte | À confirmer |
| Magasins d'intrants agricoles - Établissements | 463 | Point | À rattacher à la fiche exacte | À confirmer |

**Contrôle effectué le 19 novembre :** les 11 fichiers ont été relus en JSON. Ils contiennent les clés type, features, totalFeatures, numberMatched, numberReturned, timeStamp et crs. Le CRS déclaré dans chaque export est urn:ogc:def:crs:EPSG::4326. Les propriétés observées sont thématiques et administratives ; aucune URL de fiche, licence ou identité de producteur n'est embarquée dans ces exports.

### Réserve sur les ZAAP

La fiche consultée pour « ZAAPs et ZAPBs - Champs individuels » ne correspond pas à « ZAAPs - Formes ». La couche de formes locale semble provenir d'une vue intitulée mview_zaapzapb_formes_zaap_zapb et son attribut ne distingue pas explicitement ZAAP et ZAPB. Il faut retrouver la fiche exacte et confirmer le périmètre avant de présenter les 144 polygones comme autant de ZAAP.

## 3. Autres sources déjà présentes

| Ressource | Portail / producteur | État de traçabilité | Réserve |
|---|---|---|---|
| Limites administratives (communes, préfectures, régions) | Géodata Togo | Portail indiqué dans le README administratif ; fiches exactes et licence à rattacher | CSV WKT avec FID et géométrie, sans noms ni CRS explicite |
| Réseau routier | Géodata Togo | Jeu « Routes - Réseau routier » indiqué dans le README des routes | EPSG:4326 déclaré ; graphe non validé topologiquement |
| Population RGPH-5 2022 | Open Data Togo ; producteur statistique INSEED | Fiche et ressource CSV indiquées dans le README population | Métadonnée licence other-open, qui ne désigne pas une licence standard précise ; hiérarchie géographique ambiguë |
| Données sanitaires historiques | Géodata Togo | Conservées dans data/raw/health/ | Hors périmètre TERROVIA actuel ; ne pas supprimer |

## 4. Conditions Géodata — point de vigilance juridique

Les CGU officielles consultées le 19 novembre 2026 distinguent la visualisation/téléchargement, gratuits en principe, de la réutilisation du contenu, qui est indiquée comme soumise à une contrepartie financière. Elles prévoient une licence non exclusive pour le contenu et imposent notamment de citer la source et la dernière date de mise à jour, de ne pas altérer le contenu ni le dénaturer.

Référence : [Géodata Togo — Conditions générales d'utilisation](https://geodata.gouv.tg/).

**Décision provisoire :** ne pas considérer automatiquement les couches Géodata comme des données librement redistribuables ou comme admissibles à un quota « open data ». Vérifier les conditions applicables au concours et à la réutilisation dans le contexte du projet avant d'inclure les fichiers bruts dans l'archive finale. Cette note est une alerte de conformité, pas une interprétation juridique définitive.

## 5. Challenge — informations confirmées publiquement

Une publication du Togo AI Lab indique que cette édition laisse le choix du thème, de la problématique et des données, et demande un tableau de bord interactif réalisé avec Power BI ou Python. Une publication récente du Lab indique une clôture des candidatures au **23 novembre 2026**.

Références :
- [Annonce Open Data Challenge — Togo AI Lab](https://fr.linkedin.com/posts/togo-ai-lab_mesptn-togoailab-datachallenge-activity-7528129929729851394-O6bm)
- [FAQ / précisions du Data Challenge — Togo AI Lab](https://fr.linkedin.com/posts/togo-ai-lab_data-challenge-activity-7525852432824848384-17pC)

Le règlement détaillé, les consignes techniques et les éventuelles règles de quota, de taille de fichier ou de format de rapport ne sont pas présents dans le dossier Linux inspecté à cette date. Ne pas traiter ces modalités comme confirmées tant que les documents officiels n'ont pas été retrouvés ou consultés sur le portail.

## 6. Actions de vérification restantes

1. Associer chaque export agricole à sa fiche Géodata exacte et relever producteur, dernière mise à jour et conditions affichées.
2. Vérifier les conditions d'usage applicables aux données Open Data Togo et INSEED, en particulier la licence other-open du RGPH-5.
3. Retrouver et lire le règlement et les directives techniques de l'édition en cours.
4. Déterminer, à partir des règles officielles, ce qui compte comme source admissible et comment le quota éventuel est calculé.
5. Avant la diffusion, décider si l'archive contient les données brutes, des résultats dérivés, ou uniquement le code et les références de téléchargement selon les droits confirmés.


### Fiche individuelle retrouvée pendant la vérification web

- **Pépinières agricoles** : fiche Géodata identifiée, UUID `a76811ff-0a11-4843-b559-d329a6297cd7`, URL https://geodata.gouv.tg/donnees/a76811ff-0a11-4843-b559-d329a6297cd7.
- Cette fiche expose un dictionnaire avec des champs de contact et d'identification personnelle (nom/prénom, téléphone, courriel) dans le schéma général. Les colonnes correspondantes ne sont pas présentes dans l'export local contrôlé, mais cette couche ne doit pas être réexportée ou enrichie sans filtrage de ces champs.
- La correspondance entre cette fiche et l'export local de 728 points est cohérente avec le titre et le schéma observé, mais la date de mise à jour et les conditions propres à cette ressource restent à relever.
