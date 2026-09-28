# pixapop.fr

Site de Pixapop, agence de création d'applications mobiles (nom commercial de Cyril Gayet, EI).
Hébergé gratuitement par GitHub Pages, à partir du dossier `docs/` de la branche `main`.

## Mettre à jour

1. Modifier les textes dans `build.py`, le style dans `assets/styles.css`.
2. Textes légaux de Nouveau Cap : dans le dépôt `nouveau-cap`, lancer `node scripts/build-legal.mjs`,
   puis copier `docs/legal/nouveau-cap-legal.json` dans `data/`.
3. Lancer `python3 build.py` (Python 3, aucune dépendance) : le dossier `docs/` est réécrit.
4. Vérifier en local : `cd docs && python3 -m http.server 8777`, puis ouvrir http://localhost:8777.
5. Enregistrer et envoyer (`git add -A && git commit && git push`) : le site se met à jour en une minute.

Ne jamais modifier `docs/` à la main.

## Liste d'attente

Le formulaire « Prévenez-moi au lancement » (page Nouveau Cap) envoie l'adresse à la fonction
`liste-attente` du projet Supabase « pixapop-marketing » (source et règles dans le dépôt AIOS,
`projects/nouveau-cap-marketing/supabase/`). Page de désinscription : `/nouveau-cap/desinscription/`
(non indexée, désinscription au clic). Texte de confidentialité : mentions légales du site.

## Choix

- Aucun cookie, aucune mesure d'audience, aucune ressource tierce chargée à l'affichage (seul le formulaire de liste d'attente envoie des données, quand on le valide) : les polices (Unbounded, Figtree,
  licence SIL OFL 1.1) sont dans `assets/fonts/`. Pas de bandeau cookies nécessaire.
- Adresses publiques de Nouveau Cap pour Google Play : `/nouveau-cap/confidentialite/` et
  `/nouveau-cap/suppression-donnees/`.
