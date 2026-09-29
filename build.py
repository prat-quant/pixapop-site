"""Builds the Pixapop website (pixapop.fr) into docs/, served by GitHub Pages.

Usage: python3 build.py
Sources: this file (page texts), assets/ (styles, fonts, images), data/nouveau-cap-legal.json
(the legal texts of the Nouveau Cap app, exported by its repository: node scripts/build-legal.mjs).
Standard library only. Never edit docs/ by hand: it is rewritten on every build.
"""
import html
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
SITE = "https://www.pixapop.fr"
LEGAL = json.loads((ROOT / "data" / "nouveau-cap-legal.json").read_text(encoding="utf-8"))
PUB = LEGAL["publisher"]
PRICES = LEGAL["prices"]
EMAIL = PUB["email"]
PROJECT_EMAIL = "projet@pixapop.fr"  # new app projects, shown in the home contact block
APP_SITE = "https://nouveaucap.pixapop.fr/"  # the app's own website (waitlist, blog)
YEAR = date.today().year
esc = html.escape

# The logo: a 3 x 3 grid of pixels, one of them popping out.
LOGO = """<svg viewBox="0 0 30 30" aria-hidden="true">
<rect x="0" y="0" width="8" height="8" rx="2" fill="#FF4F8B"/><rect x="11" y="0" width="8" height="8" rx="2" fill="#FFC43A"/>
<rect x="0" y="11" width="8" height="8" rx="2" fill="#7C5CFF"/><rect x="11" y="11" width="8" height="8" rx="2" fill="#1E1535"/><rect x="22" y="11" width="8" height="8" rx="2" fill="#1FCB9C"/>
<rect x="0" y="22" width="8" height="8" rx="2" fill="#FF7A45"/><rect x="11" y="22" width="8" height="8" rx="2" fill="#FF4F8B"/><rect x="22" y="22" width="8" height="8" rx="2" fill="#FFC43A"/>
<rect x="23.5" y="-1.5" width="7" height="7" rx="2" fill="#1FCB9C" transform="rotate(18 27 2)"/></svg>"""

FAVICON = LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"')


def page(path, title, description, body, *, canonical=None, jsonld=None, noindex=False):
    """Writes one page. path is the URL path ('/', '/nouveau-cap/', ...)."""
    url = SITE + (canonical or path)
    head_ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    doc = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Pixapop">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta name="theme-color" content="#07060C">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/geist-sans-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/instrument-serif-latin-400-italic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/styles.css">
<script>document.documentElement.classList.add('js')</script>
{head_ld}
</head>
<body>
<div class="aurora" aria-hidden="true"><i></i><i></i><i></i></div>
<div class="grain" aria-hidden="true"></div>
<header class="top"><div class="wrap"><div class="bar glass">
  <a class="brand" href="/" aria-label="Pixapop, accueil">{LOGO}<span>pixapop</span></a>
  <nav class="nav" aria-label="Menu principal">
    <a href="/#savoir-faire" class="hide-sm">Savoir-faire</a>
    <a href="/nouveau-cap/">Nouveau Cap</a>
    <a href="/#contact" class="cta">Contact</a>
  </nav>
</div></div></header>
<main>
{body}
</main>
<footer><div class="wrap"><div class="row">
  <p>© {YEAR} Pixapop</p>
  <nav aria-label="Liens légaux">
    <a href="/mentions-legales/">Mentions légales</a>
    <a href="/nouveau-cap/confidentialite/">Confidentialité de Nouveau Cap</a>
    <a href="/nouveau-cap/conditions/">Conditions de Nouveau Cap</a>
  </nav>
</div></div></footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    target = OUT / path.strip("/") / "index.html" if path != "/404" else OUT / "404.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    return path


ARROW = '<svg class="arr" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17L17 7M9 7h8v8"/></svg>'


def phone(src, alt, cls=""):
    return f'<div class="phone glass {cls}"><img src="/assets/app/{src}.jpg" alt="{esc(alt)}" width="390" height="844" loading="eager" decoding="async"></div>'


MARQUEE = ["Apps iPhone et Android", "IA vraiment utile", "Design sur mesure", "Notifications", "Abonnements et paiements",
           "Thème clair et sombre", "Données protégées", "Publication sur les stores"]


def home():
    words = "".join(f"<span>{esc(w)}</span>" for w in MARQUEE)
    body = f"""
<section class="hero" aria-labelledby="t">
  <canvas data-pixels aria-hidden="true"></canvas>
  <div class="wrap">
    <a class="pill rv" href="/nouveau-cap/" style="text-decoration:none"><b>Nouveau</b> Nouveau Cap arrive sur Google Play</a>
    <h1 id="t" class="rv" style="--d:80ms">Des apps pensées<br>pour les <span class="capsule"><em>humains</em></span></h1>
    <p class="lead rv" style="--d:160ms">Pixapop conçoit et développe des applications mobiles élégantes pour iPhone et Android, avec une intelligence artificielle utile et beaucoup d’attention pour les personnes qui les utilisent.</p>
    <div class="btns rv" style="--d:240ms;justify-content:center">
      <a class="btn btn-light" href="/nouveau-cap/">Découvrir Nouveau Cap {ARROW}</a>
      <a class="btn btn-glass" href="#contact">Parler de votre projet</a>
    </div>
    <div class="stage rv" style="--d:320ms" aria-hidden="true">
      {phone('finances', 'Écran Finances de Nouveau Cap', 'p2')}
      {phone('home', 'Écran d’accueil de Nouveau Cap', 'p1')}
      {phone('plan', 'Écran Plan 90 jours de Nouveau Cap', 'p3')}
    </div>
  </div>
</section>

<div class="marquee" aria-label="Ce que nous faisons"><div class="track">{words}{words}</div></div>

<section id="savoir-faire" aria-labelledby="t2"><div class="wrap">
  <div class="head rv"><span class="pill solo">Savoir-faire</span><h2 id="t2">Tout ce qu’il faut. <em>Rien de superflu.</em></h2>
    <p class="lead">De l’idée à la fiche du store, on s’occupe de tout ce qui fait une vraie app : le design, le code, le serveur, l’IA, les paiements et les textes légaux.</p></div>
  <div class="bento">
    <article class="glass lit b-wide rv">
      <div class="visual" aria-hidden="true"><div class="stack"><i></i><i></i><i></i></div></div>
      <h3>iPhone et Android, <em>d’un seul geste</em></h3>
      <p>Une seule base de code pour les deux systèmes, publiée sur Google Play et l’App Store, avec les notifications, les abonnements et les achats intégrés.</p>
    </article>
    <article class="glass lit b-tall rv" style="--d:80ms">
      <div class="visual" aria-hidden="true"><div class="orb"></div></div>
      <h3>Une IA <em>vraiment utile</em></h3>
      <p>Un assistant qui connaît le parcours de l’utilisateur, des textes rédigés en un geste, des analyses en quelques secondes. Avec des garde-fous : aucun chiffre inventé, un bouton pour signaler une réponse, des données protégées.</p>
    </article>
    <article class="glass lit b-half rv">
      <div class="visual" aria-hidden="true"><div class="panes"><i></i><i></i><i></i></div></div>
      <h3>Un design qui <em>donne envie</em></h3>
      <p>Verre dépoli, thème clair et sombre, écrans compris sans mode d’emploi, par tous les âges.</p>
    </article>
    <article class="glass lit b-third rv" style="--d:80ms">
      <span class="glyph" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3EE6C1" stroke-width="1.8" stroke-linejoin="round"><path d="M12 3l8 3v6c0 4.5-3.4 8.2-8 9-4.6-.8-8-4.5-8-9V6z"/><path d="M9 12l2 2 4-4" stroke-linecap="round"/></svg></span>
      <h3>Données <em>protégées</em></h3>
      <p>Serveurs en Europe, consentement explicite, effacement en un geste.</p>
    </article>
    <article class="glass lit b-third rv" style="--d:140ms">
      <span class="glyph" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFC857" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="6" width="18" height="13" rx="3"/><path d="M3 10h18M7 15h4"/></svg></span>
      <h3>Paiements <em>intégrés</em></h3>
      <p>Abonnements, essais gratuits et achats à l’unité, gérés par les stores.</p>
    </article>
  </div>
</div></section>

<section aria-labelledby="t3"><div class="wrap">
  <article class="case glass rv">
    <div class="glow" aria-hidden="true"></div>
    <div class="copy">
      <span class="pill solo">Étude de cas</span>
      <h2 id="t3">Nouveau Cap, <em>le copilote de la reconversion</em></h2>
      <p class="lead">Pour les cadres de plus de 40 ans qui veulent changer de métier : un plan de 90 jours, les finances sous contrôle, un CV et un profil LinkedIn réécrits, et un Copilote IA qui connaît leur parcours.</p>
      <div class="chips"><span>Copilote IA</span><span>Plan 90 jours</span><span>Runway financier</span><span>CV PDF et Word</span><span>Notifications</span><span>Abonnements</span></div>
      <div class="btns"><a class="btn btn-light" href="/nouveau-cap/">Voir l’app {ARROW}</a><a class="btn btn-glass" href="{APP_SITE}">Le site de Nouveau Cap</a></div>
    </div>
    <div class="phones" data-tilt aria-hidden="true">
      {phone('pistes', 'Écran Pistes de Nouveau Cap', 'b')}
      {phone('home', 'Écran d’accueil de Nouveau Cap', 'a')}
      {phone('finances', 'Écran Finances de Nouveau Cap', 'c')}
    </div>
  </article>
</div></section>

<section aria-labelledby="t4">
  <svg class="ribbon" viewBox="0 0 1440 260" preserveAspectRatio="none" aria-hidden="true">
    <defs><linearGradient id="rg" x1="0" x2="1"><stop offset="0" stop-color="#8B6CFF" stop-opacity="0"/><stop offset=".35" stop-color="#8B6CFF"/><stop offset=".6" stop-color="#FF4F8B"/><stop offset="1" stop-color="#FFC857" stop-opacity="0"/></linearGradient>
    <filter id="rb"><feGaussianBlur stdDeviation="2"/></filter></defs>
    <path d="M0 190 C 300 40, 560 250, 820 120 S 1240 60, 1440 150" stroke="url(#rg)" filter="url(#rb)"/>
    <path d="M0 210 C 320 80, 600 260, 860 150 S 1260 100, 1440 180" stroke="url(#rg)" opacity=".5"/>
  </svg>
  <div class="wrap">
    <div class="head center rv"><span class="pill solo">Méthode</span><h2 id="t4">Vous rêvez l’app. <em>On la construit.</em></h2></div>
    <ol class="steps" aria-label="Les quatre étapes">
      <li class="glass lit rv"><span class="num" aria-hidden="true">01</span><h3>Écouter</h3><p>On part de votre idée et des personnes à qui l’app doit rendre service.</p></li>
      <li class="glass lit rv" style="--d:80ms"><span class="num" aria-hidden="true">02</span><h3>Prototyper</h3><p>Un premier parcours à tester sur votre téléphone, pour décider sur du concret.</p></li>
      <li class="glass lit rv" style="--d:160ms"><span class="num" aria-hidden="true">03</span><h3>Construire</h3><p>L’app, le serveur, les paiements, les notifications, les textes légaux et la fiche du store.</p></li>
      <li class="glass lit rv" style="--d:240ms"><span class="num" aria-hidden="true">04</span><h3>Faire grandir</h3><p>Les retours des utilisateurs, les mises à jour, le référencement de l’app.</p></li>
    </ol>
  </div>
</section>

<section id="contact" aria-labelledby="t5"><div class="wrap">
  <div class="contact glass rv">
    <span class="pill solo">Contact</span>
    <h2 id="t5">Une idée d’app&nbsp;? <em>Parlons-en.</em></h2>
    <p class="lead">Décrivez votre projet en quelques lignes : à qui il s’adresse, ce qu’il doit changer pour eux. On vous répond personnellement.</p>
    <a class="mail" href="mailto:{PROJECT_EMAIL}?subject=Projet%20d%E2%80%99application">{PROJECT_EMAIL}</a>
    <div class="glowline" aria-hidden="true"></div>
  </div>
</div></section>
"""
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": "Pixapop", "url": SITE, "email": EMAIL,
          "logo": SITE + "/favicon.svg", "legalName": f"{PUB['name']}, entrepreneur individuel",
          "address": {"@type": "PostalAddress", "streetAddress": "4775 RD 2085", "postalCode": "06330", "addressLocality": "Roquefort-les-Pins", "addressCountry": "FR"}}
    return page("/", "Pixapop · Agence de création d’applications mobiles",
                "Pixapop conçoit et développe des applications mobiles élégantes pour iPhone et Android, avec une IA utile. Première app : Nouveau Cap, pour réussir sa reconversion après 40 ans.",
                body, jsonld=ld)


def nouveau_cap():
    p = PRICES
    features = [
        ("Faire <em>le point</em>", ["Votre runway : combien de mois vous pouvez tenir pendant la transition", "Le comparateur de pistes de métier", "Un plan de départ construit sur votre situation"]),
        ("Avancer <em>chaque semaine</em>", ["Un plan d’action de 90 jours, en étapes concrètes", "Des fiches « Comment faire » avec méthode et scripts", "Des tests de pistes sur le terrain, avec un verdict", "Le feu vert financier et des sessions Focus"]),
        ("Votre CV <em>et LinkedIn</em>", ["Le score de votre CV et vos corrections prioritaires", "L’analyse d’une annonce : ce que le recruteur attend", "La réécriture par l’IA, sans jamais inventer de chiffre", "Créer son CV : PDF et Word adaptés à chaque annonce"]),
        ("Le Copilote <em>IA</em>", ["Vos questions à tout moment, par un assistant qui connaît votre parcours", "Des actions à ajouter à votre plan en un geste", "Avec Premium : un bilan de progression toutes les deux semaines", "Un module VAE : diagnostic, dossier et entraînement au jury"]),
    ]
    feats = "".join(f'<article class="glass lit rv" style="--d:{k * 70}ms"><h3>{t}</h3><ul>{"".join(f"<li>{esc(x)}</li>" for x in items)}</ul></article>' for k, (t, items) in enumerate(features))
    shots = [("home", "Accueil : le mot du Copilote et le bilan"), ("finances", "Finances : votre runway en mois"), ("pistes", "Pistes : comparer les métiers visés"), ("plan", "Plan 90 jours : les étapes de la semaine")]
    gallery = "".join(phone(f, alt) for f, alt in shots)
    body = f"""
<section class="apphero" aria-labelledby="t" style="padding-bottom:40px"><div class="wrap">
  <div class="top-row rv">
    <img class="appicon" src="/assets/nouveau-cap-icon.png" alt="Icône de Nouveau Cap : une boussole qui pointe vers le nord" width="128" height="128">
    <div style="display:grid;gap:14px;justify-items:start">
      <span class="pill"><b>Bientôt</b> Sur Google Play</span>
      <h1 id="t">Nouveau Cap</h1>
    </div>
  </div>
  <p class="lead rv" style="--d:100ms;margin-top:28px;font-size:clamp(19px,2vw,24px)">Vous avez plus de 40 ans, une carrière solide, et l’envie de changer de métier. Nouveau Cap vous aide à passer de l’idée au projet, puis du projet au nouveau poste, <em style="color:var(--text)">avec une méthode claire et un Copilote IA qui connaît votre parcours.</em></p>
  <div class="btns rv" style="--d:150ms;margin-top:28px"><a class="btn btn-light" href="{APP_SITE}">Le site de Nouveau Cap {ARROW}</a><a class="btn btn-glass" href="{APP_SITE}#liste">Être prévenu du lancement</a></div>
  <div class="gallery rv" style="--d:200ms" aria-label="Captures d’écran de l’app">{gallery}</div>
</div></section>

<section aria-labelledby="f" style="padding-top:40px"><div class="wrap">
  <div class="head rv"><span class="pill solo">L’app</span><h2 id="f">Tout pour changer de cap, <em>pas à pas.</em></h2></div>
  <div class="features">{feats}</div>
</div></section>

<section aria-labelledby="o"><div class="wrap">
  <div class="head rv"><span class="pill solo">Offres</span><h2 id="o">Simple, <em>sans engagement.</em></h2><p class="lead">Résiliable à tout moment dans Google Play.</p></div>
  <div class="plans">
    <article class="glass lit rv"><h3>Gratuit</h3><p class="price">0 €</p><p>Faire le point par vous-même, sans IA : runway, comparateur de pistes, plan de départ, exemples de ce que fait le Copilote.</p></article>
    <article class="glass lit rv" style="--d:70ms"><h3>Pilote</h3><p class="price">{esc(p['pilote'])} <small>/ mois</small></p><p>La méthode guidée pour avancer chaque semaine : plan de 90 jours, fiches, tests de pistes, Mon CV, le Copilote IA (10 messages par jour).</p></article>
    <article class="glass lit best rv" style="--d:140ms"><h3>Premium <em class="grad">recommandé</em></h3><p class="price">{esc(p['premium'])} <small>/ mois</small></p><p>Le suivi rapproché : bilan toutes les deux semaines, Copilote et fonctions IA sans limite, Créer son CV inclus. {p['trialDays']} jours d’essai gratuit pour un premier abonnement.</p></article>
    <article class="glass lit rv" style="--d:210ms"><h3>Créer son CV</h3><p class="price">{esc(p['cvBuilder'])}</p><p>Achat unique, sans abonnement : votre CV rédigé par l’IA à partir de vos réponses, adapté à chaque annonce.</p></article>
  </div>
  <p class="note rv" style="margin-top:16px">Prix toutes taxes comprises. Le prix qui s’applique est celui affiché par Google Play au moment de l’achat.</p>
</div></section>

<section aria-labelledby="d"><div class="wrap"><div style="max-width:780px">
  <div class="head rv"><span class="pill solo">Vos données</span><h2 id="d">Votre projet <em>vous appartient.</em></h2></div>
  <p class="lead rv">Votre profil, votre plan et vos CV restent sur votre téléphone. Notre serveur est hébergé à Paris. Rien n’est envoyé à l’IA sans votre accord, pas de publicité, pas de mesure d’audience, et vous pouvez tout effacer depuis l’app.</p>
  <div class="links rv" style="margin-top:26px">
    <a href="/nouveau-cap/confidentialite/">Politique de confidentialité</a>
    <a href="/nouveau-cap/conditions/">Conditions générales</a>
    <a href="/nouveau-cap/suppression-donnees/">Supprimer vos données</a>
    <a href="/nouveau-cap/mentions-legales/">Mentions légales de l’app</a>
  </div>
  <p class="note rv" style="margin-top:22px">Nouveau Cap est un outil d’aide à la décision et d’organisation. Il ne remplace ni un conseil juridique ou financier, ni un accompagnement professionnel, et ne délivre pas de diplôme.</p>
</div></div></section>
"""
    ld = {"@context": "https://schema.org", "@type": "MobileApplication", "name": "Nouveau Cap", "operatingSystem": "Android",
          "applicationCategory": "BusinessApplication", "inLanguage": "fr", "url": APP_SITE, "sameAs": [SITE + "/nouveau-cap/"],
          "publisher": {"@type": "Organization", "name": "Pixapop", "url": SITE},
          "offers": [{"@type": "Offer", "name": "Gratuit", "price": "0", "priceCurrency": "EUR"},
                     {"@type": "Offer", "name": "Pilote", "price": p["pilote"].replace(" €", "").replace(",", "."), "priceCurrency": "EUR"},
                     {"@type": "Offer", "name": "Premium", "price": p["premium"].replace(" €", "").replace(",", "."), "priceCurrency": "EUR"}]}
    return page("/nouveau-cap/", "Nouveau Cap · Réussir sa reconversion après 40 ans",
                "Nouveau Cap, l’app de reconversion professionnelle après 40 ans : plan de 90 jours, CV et LinkedIn repensés, Copilote IA. Par Pixapop.",
                body, jsonld=ld)


def legal_page(path, title, description, intro, sections, crumbs):
    blocks = "".join(f"<h2>{esc(s['title'])}</h2>" + "".join(f"<p>{esc(l)}</p>" for l in s["lines"]) for s in sections)
    updated = date.fromisoformat(LEGAL["updated"])
    months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    body = f"""
<div class="wrap narrow legal">
  <p class="crumbs">{crumbs}</p>
  <div class="paper glass">
    <h1>{esc(title)}</h1>
    <p class="note">Mis à jour le {updated.day} {months[updated.month - 1]} {updated.year}.</p>
    {intro}
    {blocks}
  </div>
</div>"""
    return page(path, f"{title} · Nouveau Cap" if path.startswith("/nouveau-cap/") else f"{title} · Pixapop", description, body)


APP_CRUMBS = '<a href="/">Pixapop</a> › <a href="/nouveau-cap/">Nouveau Cap</a>'


def legal_pages():
    out = [
        legal_page("/nouveau-cap/confidentialite/", "Politique de confidentialité", "Politique de confidentialité de l’application Nouveau Cap : données sur le téléphone, sur le serveur, IA, notifications, paiements, durées et droits.",
                   "", LEGAL["privacy"], APP_CRUMBS),
        legal_page("/nouveau-cap/conditions/", "Conditions générales d’utilisation et de vente", "Conditions générales d’utilisation et de vente de l’application Nouveau Cap : offres, prix, abonnements, résiliation, essai gratuit.",
                   "", LEGAL["terms"], APP_CRUMBS),
        legal_page("/nouveau-cap/mentions-legales/", "Mentions légales de l’application", "Mentions légales de l’application Nouveau Cap : éditeur, hébergement, intelligence artificielle.",
                   "", LEGAL["notice"], APP_CRUMBS),
    ]
    deletion = [
        {"title": "Dans l’application", "lines": [
            "Réglages, « Confidentialité et données », puis « Effacer mes données ». Vos données sont effacées sur votre téléphone et sur notre serveur, immédiatement.",
            "Pour effacer seulement la mémoire du Copilote : même écran, « Effacer la mémoire du Copilote ».",
            "Vos achats ne sont pas supprimés : ils restent liés à votre compte Google et se restaurent avec « Restaurer mes achats »."]},
        {"title": "Sans l’application", "lines": [
            f"Écrivez-nous {LEGAL['contact']} en indiquant l’appareil utilisé : nous effaçons vos données sous un mois.",
            "Les compteurs d’utilisation, qui ne sont plus liés à vous après l’effacement, sont supprimés au plus tard 12 mois après leur création. L’historique des achats est conservé le temps exigé par les obligations comptables."]},
    ]
    out.append(legal_page("/nouveau-cap/suppression-donnees/", "Supprimer vos données", "Comment supprimer vos données de l’application Nouveau Cap, avec ou sans l’application.",
                          "", deletion, APP_CRUMBS))
    site_notice = [
        {"title": "Éditeur du site", "lines": [
            f"Pixapop, nom commercial de {PUB['name']}, entrepreneur individuel (EI).",
            f"Adresse : {PUB['address']}.", f"SIRET : {PUB['siret']}.",
            f"Directeur de la publication : {PUB['director']}.", f"Contact : {EMAIL}."]},
        {"title": "Hébergement", "lines": ["GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis (service GitHub Pages)."]},
        {"title": "Données personnelles et cookies", "lines": [
            "Ce site ne dépose aucun cookie, n’utilise aucun outil de mesure d’audience et ne charge aucune ressource d’un site tiers : les polices de caractères sont hébergées sur le site lui-même.",
            "L’hébergeur peut conserver temporairement l’adresse IP des visiteurs pour la sécurité du service. Si vous nous écrivez, votre message sert uniquement à vous répondre.",
            "Les données de l’application Nouveau Cap sont décrites dans sa politique de confidentialité."]},
        {"title": "Propriété intellectuelle", "lines": [
            "Les textes, images et logos de ce site appartiennent à Pixapop, sauf mention contraire. Toute reproduction sans autorisation est interdite.",
            "Polices Geist et Instrument Serif, sous licence SIL Open Font License 1.1."]},
    ]
    out.append(legal_page("/mentions-legales/", "Mentions légales", "Mentions légales du site pixapop.fr : éditeur, hébergement, données personnelles.",
                          "", site_notice, '<a href="/">Pixapop</a>'))
    return out


def not_found():
    body = f"""<section class="hero" style="min-height:90svh;align-items:center"><canvas data-pixels aria-hidden="true"></canvas>
<div class="wrap"><span class="pill solo">Erreur 404</span><h1>Ce pixel <em>s’est perdu.</em></h1>
<p class="lead">La page demandée n’existe pas ou a changé d’adresse.</p>
<div class="btns" style="justify-content:center"><a class="btn btn-light" href="/">Revenir à l’accueil {ARROW}</a></div></div></section>"""
    page("/404", "Page introuvable · Pixapop", "Cette page n’existe pas.", body, canonical="/", noindex=True)



def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    (OUT / "CNAME").write_text("www.pixapop.fr\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    paths = [home(), nouveau_cap(), *legal_pages()]
    not_found()
    today = date.today().isoformat()
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>\n" for p in paths)
        + "</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"{len(paths) + 1} pages written to docs/")


if __name__ == "__main__":
    main()
