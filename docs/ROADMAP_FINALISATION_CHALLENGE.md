# TERROVIA — Feuille de route de finalisation du Data Challenge

**Mise à jour : 20 novembre 2026**
**Dépôt publié :** `EgueRichnel2025/terrovia-TOGO`
**Branche :** `main`

Ce fichier est le point de reprise central du projet. À chaque session, le lire en premier, mettre les cases à jour après vérification des livrables et reprendre la première tâche inachevée.

## 1. État général

| Volet | État | Situation |
|---|---|---|
| Sujet et problématique | ✅ Réalisé | Diagnostic géospatial de la proximité des petites exploitations agricoles aux marchés et services au Togo. |
| Collecte et préparation initiales | ✅ Réalisées | Plusieurs couches agricoles et administratives traitées. |
| Contrôle qualité géospatial | ✅ Réalisé | Audits, réparations acceptées et quarantaines documentés. |
| Première analyse d'accessibilité | ✅ Réalisée | Distances euclidiennes vers sept familles d'équipements. |
| Dashboard Python | 🟠 À finaliser | Trois pages, filtres et indicateurs ; parcours jury, revue visuelle réelle et données reproductibles à vérifier. |
| Analyses agricoles complémentaires | 🔴 À faire | Densité agricole, couverture ZAAP/ZAPB, analyse approfondie du réseau coopératif. |
| Accessibilité routière | 🔴 Non réalisée | Graphe routier non validé ; aucun temps de trajet ou itinéraire ne doit être annoncé. Extension conditionnelle. |
| Recommandations territoriales | 🟠 Partiel | Note décisionnelle produite ; validations terrain et compléments à poursuivre. |
| Rapport final | 🟠 Partiel | Analyses et documentation existantes ; synthèse argumentée à produire. |
| PowerPoint | 🔴 À faire | Support de présentation à produire ; règles et nombre de diapositives à confirmer. |
| Dépôt Git local | ✅ Initialisé | Branche `main` avec huit commits initiaux et les commits de finalisation à venir. |
| Dépôt GitHub public | ✅ Publié | `origin/main` contient les huit commits initiaux ; les changements de finalisation restent à pousser après validation. |
| Paquet de soumission | 🔴 À faire | Formats et pièces exactes à confirmer dans la FAQ et le formulaire. |

## 2. Cadre du challenge : confirmé / à confirmer

Les communications publiques du Togo AI Lab consultées pour l'édition spéciale indiquent le choix libre du sujet, de la problématique et des données, ainsi que la réalisation d'un dashboard interactif avec Power BI ou Python. La date limite de candidature annoncée est le **23 novembre 2026**.

Les communications générales présentent quatre axes d'évaluation :
1. Pertinence du rapport.
2. Qualité du dashboard.
3. Interactivité du dashboard.
4. Ergonomie du dashboard.

**Important :** ne pas transposer automatiquement les anciennes règles d'autres éditions (par exemple un PowerPoint limité à 10 diapositives) à l'édition spéciale actuelle. Vérifier la FAQ et le formulaire courant avant de figer les livrables.

### Checklist réglementaire

- [ ] Confirmer les conditions d'éligibilité.
- [ ] Confirmer participation individuelle/équipe, nombre de membres et informations requises.
- [ ] Confirmer les restrictions sur les sources et données externes.
- [ ] Confirmer le format exact du rapport et du dashboard.
- [ ] Confirmer si PowerPoint est obligatoire, facultatif ou non demandé.
- [ ] Confirmer la limite de diapositives, taille des fichiers et formats.
- [ ] Confirmer si le jury doit recevoir un lien public, le code source, une vidéo ou des captures.
- [ ] Confirmer les modalités de dépôt et la preuve de soumission.

Sources publiques de travail :
- Annonce spéciale : https://fr.linkedin.com/posts/togo-ai-lab_mesptn-togoailab-datachallenge-activity-7528129929729851394-O6bm
- FAQ : https://fr.linkedin.com/posts/togo-ai-lab_data-challenge-activity-7525852432824848384-17pC
- Présentation générale des critères : https://fr.linkedin.com/posts/togo-ai-lab_mesptn-datachallenge-togoailab-activity-7490098615672164353-BJTF

Revalider ces informations sur le formulaire officiel au moment de la soumission.

## 3. Phases restantes

### Phase 0 — Créer le dépôt GitHub public et publier les commits

**Objectif :** rendre le code consultable et conserver un historique propre.

- [x] Créer un dépôt public `terrovia-TOGO` sous le compte `EgueRichnel2025`.
- [x] Choisir **Public**.
- [x] Ne pas demander à GitHub d'ajouter un README ou un .gitignore : les fichiers existaient déjà localement.
- [ ] Choisir explicitement une licence de code avant d'autoriser la réutilisation.
- [x] Ajouter/vérifier le dépôt distant sous le nom `origin`.
- [x] Pousser la branche `main` et son historique initial (8 commits).
- [x] Vérifier les huit commits, le README et l'exclusion des données brutes/détaillées.


Commandes après création du dépôt vide :

```bash
cd "/media/richnel/Richnel_disque/Projet/terrovia-togo"
git remote add origin https://github.com/EgueRichnel2025/terrovia-togo.git
git push -u origin main
git remote -v
git status
git log --oneline -8
```

Si `origin` existe déjà, ne pas le recréer : vérifier d'abord `git remote -v`.

### Phase 1 — Confirmer les modalités et sécuriser les sources

**Objectif :** éviter une non-conformité ou une publication illicite de données.

- [ ] Lire intégralement la FAQ et le formulaire actuels.
- [ ] Consigner leurs réponses dans ce fichier.
- [ ] Vérifier producteur, provenance, licence, accès, modification et redistribution de chaque source.
- [ ] Confirmer les règles concernant les données externes et leur déclaration.
- [ ] Rechercher noms, contacts, téléphones, identifiants et coordonnées individuelles.
- [ ] Préparer au besoin des données publiques agrégées et non sensibles.
- [ ] Garder les sources brutes et exports détaillés hors du dépôt public tant que licence et confidentialité ne sont pas validées.

Une donnée téléchargeable n'est pas automatiquement redistribuable. Par défaut, le dépôt exclut `data/raw/`, `data/processed/` et les audits tabulaires détaillés.

### Phase 2 — Consolider les analyses agricoles

**Objectif :** approfondir les constats sans dépasser ce que les données permettent de démontrer.

#### 2.1 Densité agricole
- [ ] Définir l'indicateur : nombre d'exploitations par km², surface agricole par km² ou mesure mieux justifiée.
- [ ] Choisir une unité spatiale défendable (commune, grille régulière, etc.).
- [ ] Valider géométries, superficies, dénominateurs et unités.
- [ ] Ne pas appeler « densité » un simple effectif brut.
- [ ] Produire cartes et tableaux comparables.
- [ ] Documenter les biais de couverture et données manquantes.

#### 2.2 Couverture ZAAP/ZAPB
- [ ] Vérifier les définitions métier et la sémantique des couches.
- [ ] Déterminer si ZAAP et ZAPB sont distinguables.
- [ ] Si elles ne le sont pas, conserver une catégorie combinée et le signaler.
- [ ] Mesurer surfaces et parts couvertes seulement après validation des géométries.
- [ ] Étudier avec prudence proximité et inclusion des exploitations.
- [ ] Comparer les territoires seulement si les correspondances administratives sont validées.

#### 2.3 Réseau coopératif
- [ ] Décrire la distribution et la concentration territoriale des coopératives.
- [ ] Comparer les effectifs au nombre d'exploitations sans confondre quantité et couverture réelle.
- [ ] Examiner les territoires relativement peu dotés.
- [ ] Croiser ces résultats avec les distances calculées.
- [ ] Tenir compte de l'incomplétude possible de l'inventaire.

#### 2.4 Accessibilité routière — extension conditionnelle
- [ ] Auditer et corriger la topologie du réseau routier.
- [ ] Vérifier composantes connexes, intersections, discontinuités et points d'accrochage.
- [ ] Définir les règles de déplacement et coûts de parcours.
- [ ] Valider quelques trajets sur des références crédibles.
- [ ] Calculer distances réseau/temps seulement après validation.
- [ ] Documenter mode de transport, vitesse, saisonnalité et praticabilité.

**Décision :** si le réseau n'est pas validé à temps, ne pas bloquer la soumission. Conserver les distances euclidiennes comme première approximation de proximité potentielle et en expliquer les limites.

### Phase 3 — Construire les recommandations territoriales

- [ ] Retenir des constats robustes et reproductibles.
- [ ] Définir et justifier les critères de priorisation.
- [ ] Croiser concentration agricole, distances et couverture des équipements.
- [ ] Confronter les résultats aux limites des sources.
- [ ] Formuler des pistes d'investigation, collecte complémentaire ou planification.
- [ ] Pour chaque recommandation, donner constat, territoire, preuve, action proposée et limites.
- [ ] Ne pas présenter un classement exploratoire comme une décision officielle d'investissement.

### Phase 4 — Finaliser le dashboard pour le jury

- [ ] Faire comprendre la question, le périmètre et les résultats dès la page d'accueil.
- [ ] Organiser l'exploration par territoire et famille d'équipement.
- [ ] Afficher clairement unités, sources, dates et limites, en particulier « distance en ligne droite ».
- [ ] Tester filtres, cartes, graphiques, tableaux et exports.
- [ ] Faire tester le parcours par une personne qui ne connaît pas le projet.
- [ ] Vérifier visuellement ordinateur, tablette et vrai téléphone.
- [ ] Vérifier états vides, erreurs de données et instructions de lancement.
- [ ] N'ajouter que des indicateurs validés par les analyses précédentes.

### Phase 5 — Rédiger le rapport final

Le rapport doit construire une démonstration, pas répéter les graphiques du dashboard.

1. Contexte et intérêt de la question.
2. Problématique, objectifs et périmètre.
3. Sources et provenance des données.
4. Contrôle qualité et préparation.
5. Méthodologie et indicateurs.
6. Résultats nationaux.
7. Disparités régionales et communales.
8. Interprétation.
9. Recommandations et priorités d'investigation.
10. Limites, incertitudes et perspectives.

- [ ] Rédiger les sections avec des résultats reproductibles.
- [ ] Donner effectifs, unités et dates de référence.
- [ ] Distinguer faits, interprétations et hypothèses.
- [ ] Citer sources et conditions d'utilisation.
- [ ] Vérifier la cohérence rapport/dashboard/données.
- [ ] Supprimer toute conclusion non soutenue.

### Phase 6 — Produire le PowerPoint / support oral

- [ ] Confirmer si le PowerPoint est exigé et la limite de diapositives.
- [ ] Raconter problème, données, méthode, résultats, disparités, recommandations et limites.
- [ ] Utiliser des cartes et graphiques lisibles, sans recopier le dashboard écran par écran.
- [ ] Ajouter références et précautions.
- [ ] Synchroniser tous les chiffres avec le rapport et le dashboard.
- [ ] Exporter et vérifier le PDF si demandé.
- [ ] Préparer et chronométrer une démonstration orale.

### Phase 7 — Reproductibilité et contrôle qualité final

- [ ] Vérifier une installation propre depuis `uv.lock`.
- [ ] Exécuter Ruff, formatage, compilation et tests.
- [ ] Vérifier la chaîne de préparation depuis les sources locales autorisées.
- [ ] Vérifier qu'aucun chemin absolu propre au PC n'est requis.
- [ ] Vérifier tous les chiffres du rapport et du dashboard.
- [ ] Contrôler références, liens et noms de fichiers.
- [ ] Auditer le dépôt public : secrets, données personnelles, données non autorisées et fichiers volumineux.
- [ ] Vérifier statut Git et historique.

### Phase 8 — Préparer et soumettre le dossier

- [ ] Remplir les informations du formulaire.
- [ ] Préparer exactement les pièces demandées.
- [ ] Joindre le rapport final.
- [ ] Joindre le dashboard, son lien ou ses fichiers sources selon le règlement.
- [ ] Joindre le PowerPoint uniquement selon les consignes confirmées.
- [ ] Ajouter le lien GitHub si demandé ou utile.
- [ ] Vérifier chaque fichier après téléchargement.
- [ ] Conserver la preuve de soumission et les versions exactes envoyées.

## 4. Stratégie de commits

Objectif : un historique riche, lisible et professionnel. Les commits doivent être petits, atomiques et correspondre à de vrais changements, jamais artificiels.

- [ ] Un commit par audit ou correction analytique autonome.
- [ ] Un commit par indicateur nouveau, calculé et testé.
- [ ] Un commit par amélioration isolée du dashboard.
- [ ] Un commit par section substantielle du rapport.
- [ ] Un commit par livrable finalisé.
- [ ] Avant commit : revoir `git diff`, lancer les vérifications pertinentes et `git diff --cached --check`.
- [ ] Après commit : contrôler `git status` et `git log --oneline`.

Préfixes : `data:`, `feat:`, `fix:`, `docs:`, `test:`, `ci:`, `chore:`.

## 5. Précautions scientifiques à conserver partout

- Les distances actuelles sont euclidiennes, en EPSG:32631, depuis un point représentatif intérieur vers la géométrie la plus proche.
- Elles ne sont ni des distances routières ni des temps de trajet.
- Les seuils de 5 km et 10 km sont descriptifs, pas des normes officielles.
- La présence d'un équipement ne garantit ni fonctionnement, capacité, prix, horaires, qualité ou utilisation.
- La couche ZAAP/ZAPB ne permet pas encore de séparer sûrement les catégories.
- Les correspondances FID/noms régionaux sont candidates tant qu'une référence officielle ne les confirme pas.
- L'exhaustivité des inventaires d'exploitations et d'équipements n'est pas garantie.

## 6. État Git connu au 20 novembre 2026

Huit commits locaux initiaux ont été créés avant les travaux de finalisation :

1. `b8fd87a` — chore: initialize TERROVIA public project structure
2. `c3e5fc0` — feat: add interactive geospatial accessibility dashboard
3. `99fc81e` — feat: add geospatial audit and accessibility pipelines
4. `89fc318` — test: cover dashboard data and helper logic
5. `9ee1ab7` — docs: publish methodology and aggregated accessibility findings
6. `1d9ca92` — ci: automate lint formatting compilation and tests
7. `d65da78` — chore: exclude internal notes and preserve empty data directory
8. `2dc4081` — docs: add challenge finalization roadmap

Le dépôt public `EgueRichnel2025/terrovia-TOGO` est créé ; les huit commits initiaux ont été poussés sur `main` et vérifiés synchronisés.

## 7. Prochaine action immédiate

1. Confirmer les consignes exactes du formulaire officiel de cette édition.
2. Consolider les résultats territoriaux et les recommandations à partir des données déjà calculées.
3. Finaliser rapport et dashboard en traitant la dépendance aux données locales non publiées.
4. Produire les pièces strictement demandées, puis vérifier et pousser chaque changement.

**Règle de reprise :** ne jamais déclarer une phase terminée sur la seule base d'une intention. Exiger un livrable et sa vérification.
