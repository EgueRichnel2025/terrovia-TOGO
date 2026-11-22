# TERROVIA — État de préparation au Data Challenge

Dernière revue : 22 novembre 2026.

## Cadre confirmé pour l'édition spéciale

Les communications publiques du Togo AI Lab indiquent que cette édition spéciale laisse aux participants le choix de la thématique, de la problématique et des données à exploiter. La mission annoncée est de produire des analyses pertinentes au moyen d'un tableau de bord interactif réalisé avec Power BI ou Python. La date limite de candidature annoncée est le 23 novembre 2026.

Les communications générales du Togo AI Lab décrivent quatre axes d'évaluation :
1. Pertinence du rapport.
2. Qualité du dashboard.
3. Interactivité du dashboard.
4. Ergonomie du dashboard.

Prudence : l'annonce publique de l'édition spéciale ne détaille pas à elle seule le format exact du paquet final, les contraintes de taille, les règles d'équipe, ni le caractère obligatoire d'un PowerPoint. Les formats annoncés dans des défis précédents (par exemple 10 diapositives maximum) ne doivent pas être transposés automatiquement à cette édition. Confirmer ces points dans la FAQ et le formulaire en cours.

## État du projet

| Élément | État | Commentaire |
|---|---|---|
| Thématique et problématique librement choisies | FAIT | Diagnostic géospatial de l'accessibilité potentielle des exploitations agricoles aux marchés et services au Togo. |
| Données réelles et documentées | PARTIEL | Couches agricoles et administratives exploitées ; provenance et licences à confirmer avant redistribution. |
| Contrôle qualité des données | FAIT / À CONSOLIDER | Audits géométriques, cohérence territoriale, réparations et quarantaine documentés. |
| Analyse exploratoire | FAIT | Distances euclidiennes, statistiques nationales et régionales réalisées. |
| Modèle exploratoire | FAIT / À INTERPRÉTER AVEC PRUDENCE | K-Means sur sept distances, trois profils, stabilité ARI 0,991 et silhouette modérée de 0,164. Aucun objectif prédictif ni vérité terrain. |
| Dashboard Python interactif | FAIT / À FINALISER | Streamlit avec synthèse, exploration, profils du modèle et méthode ; revue visuelle finale et parcours jury à effectuer. |
| Pertinence du rapport | PARTIEL | Analyse exploratoire, méthodologie et note décisionnelle disponibles ; rapport final consolidé à produire. |
| Interactivité | FAIT / À AMÉLIORER | Filtres territoriaux et par service, comparaisons, tableaux et exports. |
| Ergonomie | PARTIEL | Navigation et responsive renforcés ; revue visuelle et tests utilisateurs à effectuer. |
| Recommandations concrètes | PARTIEL | Une note décisionnelle propose des priorités d'investigation ; validation terrain et enrichissement à poursuivre. |
| PowerPoint | À FAIRE / À CONFIRMER | À produire comme support de synthèse ; caractère obligatoire et limite de slides à confirmer. |
| Paquet de soumission | À FAIRE | Préparer et vérifier les fichiers exacts exigés par le formulaire. |
| Dépôt Git public | PUBLIÉ | Dépôt public disponible ; données détaillées exclues. |

## Extensions analytiques utiles — pas des exigences officielles explicites

| Axe | État | Travail restant |
|---|---|---|
| Densité agricole | À FAIRE | Construire des densités par surface et/ou population agricole, après validation des dénominateurs et unités spatiales. |
| Couverture ZAAP/ZAPB | PARTIEL | Couche combinée disponible ; distinguer ZAAP et ZAPB et mesurer couverture/surfaces après validation sémantique. |
| Réseau coopératif | PARTIEL | Proximité mesurée ; analyser distribution, concentration et couverture territoriale. |
| Profils de proximité K-Means | FAIT | Trois groupes exploratoires entraînés et évalués ; séparation modérée, à confronter à des données terrain. |
| Accessibilité routière réelle | NON FAIT | Graphe routier non validé topologiquement ; aucune distance réseau ni durée de trajet. |
| Recommandations territoriales | À FAIRE | Hiérarchiser les zones à examiner avec justification, faisabilité et limites. |

## Plan de finalisation

1. Confirmer dans la FAQ et le formulaire les règles exactes : éligibilité, individuel/équipe, sources externes, formats, taille et procédure.
2. Consolider les analyses prioritaires sans surinterpréter les données.
3. Produire une synthèse décisionnelle et des recommandations prudentes.
4. Finaliser le parcours du dashboard pour le jury.
5. Produire un PowerPoint court si utile et conforme aux règles confirmées.
6. Effectuer les revues scientifique, visuelle, responsive et de reproductibilité.
7. Préparer le paquet de soumission et contrôler licences et données personnelles.

## Contrôles techniques du 22 novembre 2026

- `uv run python -m pytest -q` : 12 tests réussis, dont quatre tests dédiés au modèle.
- Ruff : contrôle et formatage vérifiés.
- Compilation Python : réussie.
- Modèle : K-Means, trois profils, silhouette 0,164, Davies-Bouldin 1,913, Calinski-Harabasz 2300,2, ARI moyen 0,991.
- Rapports agrégés et tableau de bord enrichis ; affectations individuelles et modèle sérialisé exclus de Git.
- Dépôt : synchronisation GitHub à effectuer après validation finale.
- Limite majeure : les données de `data/raw/` et `data/processed/` sont exclues du dépôt public ; le dashboard nécessite ces fichiers locaux et ne peut pas être lancé par un clone seul. Une solution de démonstration/diffusion conforme aux licences reste à définir.

## Sources publiques

- Annonce de l'édition spéciale et date limite : https://fr.linkedin.com/posts/togo-ai-lab_mesptn-togoailab-datachallenge-activity-7528129929729851394-O6bm
- FAQ de l'édition spéciale : https://fr.linkedin.com/posts/togo-ai-lab_data-challenge-activity-7525852432824848384-17pC
- Présentation générale du format et des axes d'évaluation : https://fr.linkedin.com/posts/togo-ai-lab_mesptn-datachallenge-togoailab-activity-7490098615672164353-BJTF

Les pages et formulaires peuvent être mis à jour. Vérifier les instructions affichées au moment de la soumission.
