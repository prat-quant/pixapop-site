# CLAUDE.md : site pixapop.fr

Site de **Pixapop**, l'agence de création d'apps mobiles de Cyril Gayet (entrepreneur individuel,
nom commercial Pixapop). En ligne sur https://www.pixapop.fr. Comment le construire : `README.md`.

## Règles pour chaque session

- **Avant toute modification** : récupérer la dernière version de `main` de ce dépôt et d'AIOS
  (`prat-quant/aios`, à ajouter à la session s'il n'y est pas), puis lire
  `docs/JOURNAL-MISES-A-JOUR.md` d'AIOS (entrées récentes, celles du site, tâches « À répercuter »,
  tableau des dépendances). Après : y ajouter une entrée et l'envoyer sur `main` d'AIOS. Les autres
  conversations (App, Marketing) modifient parfois le site : ce journal est la seule façon de le
  savoir.
- Écrire à Cyril **en français uniquement**, y compris les courtes phrases d'avancement. Il n'est
  pas développeur : simplement, une étape à la fois quand c'est lui qui agit. Pas de tiret cadratin.
- Méthode : `.claude/rules/working-method.md` du dépôt AIOS (plan d'abord, un chantier à la fois,
  tests avant chaque envoi, honnêteté sur ce qui n'est pas testé, journal tenu dans AIOS
  `memory/logs/`).
- Cyril autorise Claude à publier **directement sur `main`** (accord du 28/09/2026) : c'est `main`
  qui est en ligne, une minute après l'envoi.
- Ne jamais modifier `docs/` à la main : tout passe par `build.py`, puis `python3 build.py`.

## Ce que Cyril a validé (ne pas changer sans lui)

- Design validé le 28/09/2026 (« le design est top, je valide complètement ») : agence créative,
  fond sombre, effet de verre dépoli (« liquid glass »), titres en Geist avec des mots en
  Instrument Serif italique, pixels lumineux animés dans l'en-tête, vraies captures de Nouveau Cap
  dans des téléphones, micro-animations mesurées, respect du mode « moins d'animations ».
  Couleurs de l'agence distinctes du bleu de Nouveau Cap.
- Les contenus restent visibles même sans animation (l'animation d'apparition ne masque un bloc que
  si le navigateur confirme qu'il est hors de l'écran).
- Bloc Contact de l'accueil : **projet@pixapop.fr**, lien cliquable qui ouvre la messagerie avec
  l'objet « Projet d'application ». Contact légal et support : **contact@pixapop.fr**.
- Bas de page : seulement « © 2026 Pixapop » (le nom de Cyril reste dans les mentions légales,
  où la loi l'impose).
- Aucun cookie, aucune mesure d'audience, aucune ressource tierce. Ajouter un compteur de visites
  (sans cookies) seulement avec l'accord de Cyril, en mettant à jour la page de confidentialité.

## Pages

- `/` accueil de l'agence ; `/nouveau-cap/` page de l'app ; `/mentions-legales/` de l'agence
  (hébergeur GitHub) ; pages légales de Nouveau Cap : `/nouveau-cap/confidentialite/`,
  `/conditions/`, `/suppression-donnees/`, `/mentions-legales/` ; page 404.
- Les textes légaux de Nouveau Cap ne s'écrivent pas ici : ils viennent du dépôt `nouveau-cap`
  (`src/lib/legal.ts`, puis `node scripts/build-legal.mjs`, puis copie de
  `docs/legal/nouveau-cap-legal.json` dans `data/`). Ces adresses sont déclarées à Google Play : ne
  jamais les déplacer.

## Hébergement et domaine

- GitHub Pages, branche `main`, dossier `docs/`, domaine personnalisé `www.pixapop.fr` (`docs/CNAME`).
- pixapop.fr est acheté chez SiteGround ; ses DNS sont chez **o2switch** (éditeur de zone du
  cPanel) : `www` en CNAME vers `prat-quant.github.io`, quatre lignes A de `pixapop.fr` vers
  185.199.108 à 111.153. Ne jamais toucher aux lignes de messagerie (MX, mail, webmail,
  autodiscover...) ni à la ligne TXT `google-site-verification` (elle valide le site pour Google
  Play).
- Au 28/09/2026 : certificat HTTPS en cours chez GitHub ; Cyril doit cocher « Enforce HTTPS » dans
  les réglages Pages dès que possible.

## Tester avant chaque envoi

- `python3 build.py`, puis servir `docs/` en local et vérifier chaque page dans un vrai navigateur
  (Playwright) à 360 et 1280 px : aucune erreur, aucun débordement horizontal, aucun contenu masqué,
  aucun texte cassé (`undefined`, `{...}`), aucun tiret cadratin, lien projet@pixapop.fr correct.
- L'environnement cloud ne peut pas ouvrir pixapop.fr : c'est Cyril qui vérifie le site en ligne.

## À venir

- Lien vers la fiche Google Play de Nouveau Cap dès la publication de l'app.
- Le blog et la liste d'attente de Nouveau Cap vivent sur le site de l'app,
  https://nouveaucap.pixapop.fr (dépôt `prat-quant/nouveaucap-site`), décision de Cyril du 29/09/2026 :
  **aucun formulaire sur pixapop.fr**. Ce site renvoie vers le site de l'app (page `/nouveau-cap/` et
  étude de cas de l'accueil).
- Une page par nouvelle app de Pixapop, sur le même modèle que `/nouveau-cap/`.
