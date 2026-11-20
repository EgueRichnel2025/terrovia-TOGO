# Politique de publication — dépôt public TERROVIA

Le dépôt public contient le code, la documentation méthodologique et des résultats agrégés sélectionnés. Il ne constitue pas un miroir des dossiers de travail locaux.

## Exclusions obligatoires

- data/raw : sources originales non redistribuées.
- data/processed : exports dérivés pouvant contenir coordonnées, identifiants, noms, adresses, téléphones ou attributs issus des sources.
- reports/audits/*.csv : tables détaillées d'audit non publiées car certaines contiennent des attributs et coordonnées au niveau individuel.
- Secrets, fichiers .env, identifiants, sauvegardes locales et caches.
- Notes de passation internes et journaux de travail sans intérêt pour les utilisateurs publics.

## Avant toute publication de données

1. Vérifier la licence exacte et les conditions de redistribution de chaque source.
2. Vérifier les données personnelles et les coordonnées fines.
3. Vérifier les identifiants et les possibilités de ré-identification.
4. Privilégier les statistiques agrégées et les cartes à une échelle adaptée.
5. Documenter les transformations et limites.
6. Ne pas considérer qu'une donnée téléchargeable est automatiquement redistribuable.

## Licence du code

Aucune licence open source n'est appliquée automatiquement. La visibilité publique d'un dépôt GitHub ne vaut pas octroi d'une licence de réutilisation. Une licence de code devra être choisie explicitement par le propriétaire avant publication.
