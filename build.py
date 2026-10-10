"""Builds the Pixapop website (pixapop.fr) into docs/, served by GitHub Pages.

Usage: python3 build.py
Sources: this file (page texts), assets/ (styles, fonts, images), data/nouveau-cap-legal.json
(the legal texts of the Nouveau Cap app, exported by its repository: node scripts/build-legal.mjs).
Standard library only. Never edit docs/ by hand: it is rewritten on every build.
"""
import html
import json
import re
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
YOUTUBE = "https://www.youtube.com/channel/UCwgrPyMgV04sl71rjCPfBGQ"  # the Pixapop YouTube channel (Cyril, 30/09/2026)
YEAR = date.today().year
esc = html.escape

# The logo: a 3 x 3 grid of pixels, one of them popping out.
LOGO = """<svg viewBox="0 0 30 30" aria-hidden="true">
<rect x="0" y="0" width="8" height="8" rx="2" fill="#FF4F8B"/><rect x="11" y="0" width="8" height="8" rx="2" fill="#FFC43A"/>
<rect x="0" y="11" width="8" height="8" rx="2" fill="#7C5CFF"/><rect class="ink" x="11" y="11" width="8" height="8" rx="2" fill="#1E1535"/><rect x="22" y="11" width="8" height="8" rx="2" fill="#1FCB9C"/>
<rect x="0" y="22" width="8" height="8" rx="2" fill="#FF7A45"/><rect x="11" y="22" width="8" height="8" rx="2" fill="#FF4F8B"/><rect x="22" y="22" width="8" height="8" rx="2" fill="#FFC43A"/>
<rect x="23.5" y="-1.5" width="7" height="7" rx="2" fill="#1FCB9C" transform="rotate(18 27 2)"/></svg>"""

FAVICON = LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"')


STUDIO_SITE = "https://studio.pixapop.fr/"  # the product's own site (beta sign-up until 9 November 2026, then the trial)
TRY = STUDIO_SITE  # « Essayer gratuitement » (Cyril, 10/10/2026)

NAV = [("/studio/", "Studio"), ("/pilot/", "Pilot"), ("/sur-mesure/", "Sites et applications"), ("/a-propos/", "À propos"), ("/contact/", "Contact")]

SUN = '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
MOON = '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>'
BURGER = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
ARROW = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def icon(name):
    paths = {
        "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
        "price": '<path d="M20 12l-8 8-9-9V3h8z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
        "loop": '<path d="M4 12a8 8 0 0 1 14-5.3L20 9M20 4v5h-5M20 12a8 8 0 0 1-14 5.3L4 15M4 20v-5h5"/>',
        "studio": '<rect x="3" y="4" width="18" height="14" rx="3"/><path d="M8 20h8M7 9h6M7 13h10"/>',
        "pilot": '<path d="M12 3v3M12 18v3M3 12h3M18 12h3"/><circle cx="12" cy="12" r="5"/><path d="M12 9v3l2 1"/>',
        "hand": '<path d="M7 11V6a2 2 0 0 1 4 0v5M11 10V5a2 2 0 0 1 4 0v6M15 10a2 2 0 0 1 4 0v3a7 7 0 0 1-7 7h-1a6 6 0 0 1-5.2-3l-2-3.5a1.8 1.8 0 0 1 3.1-1.8L7 14"/>',
        "site": '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M3 9h18M7 6.5h.01M10 6.5h.01"/>',
        "phone": '<rect x="7" y="2.5" width="10" height="19" rx="3"/><path d="M11 18h2"/>',
        "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
        "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8.2-8 9-4.6-.8-8-4.5-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "chat": '<path d="M5 18l-1.5 3.5L8 20h8a5 5 0 0 0 5-5V9a5 5 0 0 0-5-5H8a5 5 0 0 0-5 5v6a5 5 0 0 0 2 3z"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3.5 7l8.5 6 8.5-6"/>',
    }
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


def page(path, title, description, body, *, canonical=None, jsonld=None, noindex=False, body_class=""):
    """Writes one page. path is the URL path ('/', '/studio/', ...)."""
    url = SITE + (canonical or path)
    head_ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{href}"{cur if path == href else ""}>{esc(label)}</a>' for href, label in NAV)
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
<meta name="theme-color" content="#F8F8FC">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/geist-sans-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/instrument-serif-latin-400-italic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/styles.css">
<script>document.documentElement.classList.add('js');try{{if(localStorage.getItem('pxp_theme')==='dark')document.documentElement.setAttribute('data-theme','dark')}}catch(e){{}}</script>
{head_ld}
</head>
<body class="{body_class}">
<header class="top"><div class="wrap bar">
  <a class="brand" href="/" aria-label="Pixapop, accueil">{LOGO}<span>pixapop</span></a>
  <nav class="nav" aria-label="Menu principal">{nav}</nav>
  <button class="menu-btn" type="button" data-menu aria-expanded="false" aria-label="Ouvrir le menu">{BURGER}</button>
  <button class="theme" type="button" data-theme-toggle aria-pressed="false" aria-label="Passer en thème sombre ou clair">{SUN}{MOON}</button>
  <a class="btn primary small try" href="{TRY}">Essayer gratuitement</a>
</div></header>
<main>
{body}
</main>
<footer><div class="wrap">
  <div class="foot">
    <div><a class="brand" href="/" aria-label="Pixapop, accueil">{LOGO}<span>pixapop</span></a>
      <p>Pixapop aide les entrepreneurs solo et les petites entreprises à trouver des clients et à vendre au bon prix.</p></div>
    <div><b>Nos outils</b><a href="/studio/">Pixapop Studio</a><a href="/pilot/">Pixapop Pilot</a><a href="/sur-mesure/">Sites et applications</a><a href="/nouveau-cap/">Nouveau Cap</a></div>
    <div><b>Pixapop</b><a href="/a-propos/">À propos</a><a href="/contact/">Contact</a><a href="{YOUTUBE}" rel="me">YouTube</a></div>
    <div><b>Informations</b><a href="/mentions-legales/">Mentions légales</a><a href="/confidentialite/">Confidentialité</a><button type="button" class="linkish" data-consent-open>Cookies</button>
      <a href="/nouveau-cap/confidentialite/">Confidentialité de Nouveau Cap</a><a href="/nouveau-cap/conditions/">Conditions de Nouveau Cap</a></div>
  </div>
  <p class="copy">© {YEAR} Pixapop</p>
  <p class="note-etoile">* Publication sur les réseaux sociaux : nécessite un compte Metricool relié à Studio.</p>
</div></footer>
<script src="/assets/site.js" defer></script>
<script src="/assets/consent.js" defer></script>
</body>
</html>
"""
    doc = typo_fr(doc)
    target = OUT / path.strip("/") / "index.html" if path != "/404" else OUT / "404.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    return path


def typo_fr(doc):
    """French typography on the visible text: a non-breaking space before : ; ! ? and inside « » (skips scripts and tags)."""
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)", doc, flags=re.S)
    for i in range(0, len(parts), 2):
        s = parts[i]
        s = re.sub(r" ([:;!?])(?=\s|$|<|&)", "\u00a0\\1", s)
        s = re.sub(r"« ", "«\u00a0", s)
        s = re.sub(r" »", "\u00a0»", s)
        parts[i] = s
    return "".join(parts)


def shot(src, alt, eager=False):
    return (f'<div class="frame"><div class="frame-bar" aria-hidden="true"><i></i><i></i><i></i></div>'
            f'<img src="/assets/visite/{src}.jpg" alt="{esc(alt)}" width="1440" height="900" loading="{"eager" if eager else "lazy"}" decoding="async"></div>')


STORE = [("01_home", "Un copilote pour votre reconversion : l’accueil de Nouveau Cap"), ("02_financer", "Financez votre reconversion : le calendrier des démarches"),
         ("03_idees", "Des idées de métier pour vous, proposées par le Copilote"), ("04_finances", "Sachez combien de temps vous pouvez tenir : le runway"),
         ("05_pistes", "Comparez vos pistes de métier"), ("06_cv", "Un CV qui parle votre nouveau métier : le score et les critères"),
         ("07_creer", "Un CV prêt à envoyer, rédigé par l’IA"), ("08_vae", "Transformez votre expérience en diplôme : le module VAE")]


def deck(keys, label):
    """The Nouveau Cap store visuals (light theme) laid out like a fanned hand of cards (Cyril, 10/10)."""
    items = [x for x in STORE if x[0] in keys]
    n = len(items)
    cards = "".join(
        f'<figure class="dk" style="--o:{k - (n - 1) / 2:g};--a:{abs(k - (n - 1) / 2):g}"><img src="/assets/app/store/light-{f}.webp" alt="{esc(alt)}" width="540" height="960" loading="lazy" decoding="async"></figure>'
        for k, (f, alt) in enumerate(items))
    return f'<div class="deck" role="group" aria-label="{esc(label)}">{cards}</div>'


def phone(src, alt):
    return f'<div class="phone"><img src="/assets/app/{src}.jpg" alt="{esc(alt)}" width="390" height="844" loading="lazy" decoding="async"></div>'


def faq_block(items):
    return "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in items)


def cta_band(title_html, lead, second=None):
    second = second or ('<a class="btn ghost" href="/contact/">Nous écrire</a>')
    return f"""<section><div class="wrap"><div class="cta-band rv">
  <h2>{title_html}</h2>{f'<p class="lead">{esc(lead)}</p>' if lead else ''}
  <div class="btns" style="justify-content:center"><a class="btn primary" href="{TRY}">Essayer gratuitement {ARROW}</a>{second}</div>
</div></div></section>"""


HOME_FAQ = [
    ("Faut-il savoir utiliser l’IA ?", "Non. Vous parlez de votre activité, Studio prépare le reste."),
    ("Est-ce que quelque chose part sans mon accord ?", "Non. Tout attend votre validation."),
    ("Combien de temps faut-il y passer ?", "Le temps de relire et de valider. La semaine ou le mois est prêt d’avance."),
    ("ChatGPT ne fait-il pas déjà la même chose ?", "ChatGPT écrit un texte quand vous le lui demandez. Studio tient votre marketing à jour, publie* et mesure."),
    ("Mes textes vont-ils ressembler à ceux de tout le monde ?", "Non. Studio écrit avec vos mots, et retient vos corrections."),
    ("Combien ça coûte ?", "Les tarifs seront annoncés le 9 novembre 2026, à l’ouverture de la bêta."),
    ("Où sont mes données ?", "En France, à Paris. Jamais revendues."),
]


def home():
    pains = ["Je gère TOUT par moi-même.", "On est invisibles.", "Suis-je trop cher ?", "J’ai l’impression que je ne vais pas y arriver"]
    pain_html = "".join(f'<article class="card pain rv" style="--d:{(k % 4) * 60}ms"><q>{esc(q)}</q></article>' for k, q in enumerate(pains))
    body = f"""
<section class="hero"><div class="wrap center">
  <p class="eyebrow rv">Solopreneur <span class="amp" aria-hidden="true">&amp;</span><span class="sr-only"> et </span> PME</p>
  <h1 class="rv h1-accueil" style="--d:60ms"><span class="h1-l">Accompagner les entrepreneurs</span> <span class="h1-l"><em>est notre métier.</em></span></h1>
  <p class="lead lead-accueil rv" style="--d:120ms"><span>Studio pour votre marketing, Pilot pour piloter votre entreprise.</span> <span>Vous décidez, on fait le reste.</span></p>
  <div class="btns rv" style="--d:180ms"><a class="btn primary" href="{TRY}">Essayer Studio gratuitement {ARROW}</a><a class="btn ghost" href="/studio/">Voir Studio en huit écrans</a></div>
  <p class="note rv" style="--d:210ms;margin-top:14px">Bêta le lundi 9 novembre 2026.</p>
  <div class="hero-shot rv" style="--d:240ms">
    {shot("8-aujourdhui", "Pixapop Studio, l’écran Aujourd’hui (exemple)", True)}
    <span class="float f1" aria-hidden="true"><i style="background:#2BB5A0"></i>Votre article est en ligne</span>
    <span class="float f2 rot r1" aria-hidden="true"><i style="background:#E0559A"></i>Un nouveau contact est arrivé</span>
    <span class="float f2 rot r2" aria-hidden="true"><i style="background:#8B6CFF"></i>Vous avez un nouveau client</span>
    <span class="float f2 rot r3" aria-hidden="true"><i style="background:#2BB5A0"></i>Vous venez de faire une nouvelle vente</span>
    <span class="float f2 rot r4" aria-hidden="true"><i style="background:#F2A541"></i>100 nouveaux contacts aujourd’hui</span>
    <span class="float f2 rot r5" aria-hidden="true"><i style="background:#5B8DEF"></i>Votre devis vient d’être accepté</span>
    <span class="float f2 rot r6" aria-hidden="true"><i style="background:#8B6CFF"></i>3 rendez-vous pris cette semaine</span>
    <span class="float f2 rot r7" aria-hidden="true"><i style="background:#FFC43A"></i>Nouvel avis 5 étoiles sur Google</span>
    <span class="float f3" aria-hidden="true"><i style="background:#F2A541"></i>Stratégie ajustée d’après vos résultats</span>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="head center rv"><h2>Puis le reste <em>est arrivé.</em></h2>
    <p class="lead">Le post du dimanche soir. Le devis tapé à 23 h. Le client parti chez le moins cher. Et votre métier attend.</p></div>
  <div class="grid g4 pains">{pain_html}</div>
  <p class="note center rv" style="margin-top:14px">Phrases d’entrepreneurs relevées sur des forums.</p>
  <p class="lead center rv" style="margin:34px auto 0">Le plan n’était pas mauvais. Il lui manquait quelqu’un pour le reste.</p>
</div></section>

<section><div class="wrap narrow center">
  <h2 class="rv h2-lignes"><span>Le reste n’est pas votre métier.</span> <em>Il prend pourtant vos soirées.</em></h2>
  <blockquote class="villain rv">« J’ai créé ma boîte par amour du métier. Et j’ai découvert que, dans le bâtiment, ce n’est pas le travail bien fait qui gagne. C’est le devis le moins cher. »</blockquote>
  <p class="note center rv villain-by"><b>Julien, maçon</b><span>Sur le forum Entreprendre en France</span></p>
  <p class="rv villain-after">Le client ne choisit pas le meilleur artisan. <b>Il choisit celui en qui il a confiance.</b></p>
</div></section>

<section class="alt"><div class="wrap story">
  <h2 class="rv">Nous avons vécu <em>le même plan.</em></h2>
  <div class="rv" style="--d:80ms"><p class="lead">Dix ans seul aux commandes de trois entreprises. Le travail était bon, les clients contents. Le marketing passait toujours après. Alors nous avons construit les outils qui font le reste.</p>
    <p class="note">Cyril Gayet, créateur de Pixapop</p>
    <a class="btn ghost" href="/a-propos/">Lire notre histoire {ARROW}</a></div>
</div></section>

<section><div class="wrap">
  <div class="head rv"><span class="tag beta">Bêta le 9 novembre 2026</span><h2 style="margin-top:14px">Voilà Pixapop Studio. <em>Votre marketing, prêt avant vous.</em></h2></div>
  <ol class="steps">
    <li class="card rv"><h3>Vous racontez</h3><p>Votre activité, avec vos mots. Studio écrit votre stratégie : quoi dire, et à qui.</p></li>
    <li class="card rv" style="--d:70ms"><h3>Tout est prêt</h3><p>Chaque semaine, vos posts, articles, pages et e-mails sont prêts, avec vos mots.</p></li>
    <li class="card rv" style="--d:140ms"><h3>Vous validez</h3><p>Studio publie* à l’heure, puis vous montre ce qui a marché et quoi changer.</p></li>
  </ol>
  <p class="lead rv" style="margin-top:26px">Studio fait déjà le marketing de Pixapop et de l’application Nouveau Cap.</p>
  <div class="btns rv" style="margin-top:18px"><a class="btn ghost" href="/studio/">Voir Studio en huit écrans {ARROW}</a></div>
  <p class="relance rv">Et ce n’est que le premier outil.</p>
</div></section>

<section class="alt"><div class="wrap">
  <div class="grid g2">
    <article class="card rv"><span class="tag soon">Pixapop Pilot, bientôt</span><h3 style="margin-top:12px">Ensuite, vos clients et vos devis.</h3>
      <p>Chaque contact arrive avec son histoire. Après le rendez-vous, son devis est prêt, à partir de vos tarifs. Jamais un prix inventé.</p>
      <a class="more" href="/pilot/">Être prévenu à l’ouverture de Pilot {ARROW}</a></article>
    <article class="card rv" style="--d:80ms"><div class="ico i4">{icon("site")}</div><h3>Votre site ramène des demandes.</h3>
      <p>Sur mesure, au prix fixé dans le devis avant de commencer.</p>
      <a class="more" href="/sur-mesure/">Demander un devis de site {ARROW}</a></article>
  </div>
</div></section>

<section><div class="wrap narrow center">
  <h2 class="rv">Lundi, 8 h. <em>Votre semaine est prête.</em></h2>
  <p class="lead rv">Vous validez. Vous retournez à votre métier.</p>
  <p class="note rv" style="margin-top:22px">Sans ça, le meilleur du métier reste celui qu’on ne trouve pas. Et le devis le moins cher continue de gagner.</p>
</div></section>

<section class="alt"><div class="wrap">
  <div class="grid g4">
    <article class="card rv"><div class="ico i1">{icon("shield")}</div><h3>Rien ne part sans votre accord</h3><p>Tout attend votre validation.</p></article>
    <article class="card rv" style="--d:60ms"><div class="ico i2">{icon("chat")}</div><h3>Avec vos mots</h3><p>Studio écrit comme vous et retient vos corrections.</p></article>
    <article class="card rv" style="--d:120ms"><div class="ico i3">{icon("clock")}</div><h3>Aucune compétence en IA</h3><p>Vous parlez de votre activité, Studio prépare le reste.</p></article>
    <article class="card rv" style="--d:180ms"><div class="ico i4">{icon("heart")}</div><h3>Vos données en France</h3><p>À Paris. Jamais revendues.</p></article>
  </div>
  <p class="note center rv" style="margin-top:22px">Seul au marketing dans une équipe de quinze ? <a href="/contact/">Parlons-en</a>.</p>
</div></section>

<section><div class="wrap narrow">
  <div class="head center rv"><h2>Vos <em>questions</em></h2></div>
  <div class="faq rv">{faq_block(HOME_FAQ)}</div>
</div></section>
{cta_band("Le plan de départ <em>tient toujours.</em>", "")}
"""
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": "Pixapop", "url": SITE, "email": EMAIL,
          "description": "Pixapop aide les entrepreneurs solo et les petites entreprises à trouver des clients et à vendre au bon prix : Pixapop Studio (marketing préparé, validé par vous), Pixapop Pilot (CRM et devis, à venir), sites et applications sur mesure.",
          "logo": SITE + "/favicon.svg", "sameAs": [YOUTUBE], "legalName": f"{PUB['name']}, entrepreneur individuel",
          "address": {"@type": "PostalAddress", "streetAddress": "4775 RD 2085", "postalCode": "06330", "addressLocality": "Roquefort-les-Pins", "addressCountry": "FR"}}
    return page("/", "Pixapop · Accompagner les entrepreneurs est notre métier",
                "Avec Pixapop Studio, votre marketing est toujours à jour : posts, articles, pages, e-mails et réseaux préparés d’avance d’après votre métier. Vous relisez et vous validez. Pour les solopreneurs et les petites entreprises.",
                body, jsonld=ld)


def offer_designer_mock():
    return """<div class="mock" role="img" aria-label="Aperçu du designer d’offres de Pixapop Studio, en cours de conception">
  <div class="mock-head"><b>Vos offres</b><span class="mock-chip o">Forfait premium</span></div>
  <div class="mock-body">
    <div class="mock-row"><span><b>Séance découverte</b><small>Pour un premier contact, sans engagement</small></span><span class="mock-price">Offre d’appel</span></div>
    <div class="mock-row"><span><b>Accompagnement trois mois</b><small>Votre offre principale, la plus demandée</small></span><span class="mock-price">Offre principale</span></div>
    <div class="mock-row"><span><b>Suivi à l’année</b><small>Pour vos meilleurs clients</small></span><span class="mock-price">Offre haute</span></div>
    <div><small class="muted">Votre prix, comparé aux vraies données de votre métier</small><div class="mock-bar" style="margin-top:8px"><i style="width:68%"></i></div>
      <div style="display:flex;justify-content:space-between;font-size:12.5px;color:var(--muted);margin-top:6px"><span>Trop bas</span><span>Juste</span><span>Haut de gamme</span></div></div>
  </div>
  <div class="mock-label">Aperçu, en cours de conception</div>
</div>"""


def studio():
    steps = [
        ("1-strategie", "Stratégie", "Vous savez quoi dire, et à qui.", "Racontez votre activité. Studio écrit votre stratégie.", "une direction claire."),
        (None, "Offres et prix", "Votre juste prix.", "Offre d’appel, offre principale, offre haute, comparées à votre marché. Forfait premium, en conception.", "vous ne vous bradez plus."),
        ("3-mois", "Un mois en un clic", "Fini la page blanche.", "Un clic, et votre mois de contenus est prêt, dans votre ton.", "des heures retrouvées."),
        ("4-calendrier", "Calendrier éditorial", "Vous validez. Studio publie*.", "Chaque contenu part à l’heure, même le samedi.", "une présence régulière."),
        ("5-tunnels", "Pages et tunnels de vente", "Vos visiteurs deviennent des contacts.", "Une page, un formulaire, des e-mails : Studio crée tout.", "des contacts pendant que vous travaillez."),
        ("6-audit", "Audit Google et IA", "Vu par Google et par ChatGPT.", "Studio vérifie votre site et vous dit quoi corriger d’abord.", "vous savez par où commencer."),
        ("7-analytics", "Analytics", "Vous savez ce qui marche.", "Vos chiffres chaque semaine, et quoi changer. Vous acceptez, Studio applique.", "des décisions sur du concret."),
        ("8-aujourdhui", "Aujourd’hui", "Tout au même endroit.", "Ce qui attend votre accord, et le temps que ça prend.", "votre temps pour vos clients."),
    ]
    html_steps = ""
    for k, (img, kick, title, text, gain) in enumerate(steps):
        visual = offer_designer_mock() if img is None else shot(img, f"Pixapop Studio : {title}")
        html_steps += (f'<div class="step" role="group" aria-label="Étape {k + 1} sur {len(steps)}"><div><span class="k">Étape {k + 1} · {esc(kick)}</span><h3>{esc(title)}</h3><p>{esc(text)}</p>'
                       f'<p class="gain"><span><b>Ce que vous y gagnez :</b> {esc(gain)}</span></p></div><div>{visual}</div></div>')
    vid = lambda f, w, h, label, cls: (f'<video class="{cls}" controls preload="none" playsinline width="{w}" height="{h}" poster="/assets/studio/video/presentation-{f}.jpg" aria-label="{esc(label)}">'
                                       f'<source src="/assets/studio/video/presentation-{f}.mp4" type="video/mp4">'
                                       f'<track kind="subtitles" srclang="fr" label="Français" src="/assets/studio/video/presentation-{f}.vtt" default></video>')
    body = f"""
<section class="hero"><div class="wrap center">
  <p class="eyebrow rv">Pixapop Studio</p>
  <h1 class="rv" style="--d:60ms">Votre marketing tourne. <em>Vous validez.</em></h1>
  <p class="lead rv" style="--d:120ms">Stratégie, posts, articles, pages, e-mails : prêts d’avance, publiés* à l’heure, meilleurs chaque semaine.</p>
  <div class="btns rv" style="--d:180ms"><a class="btn primary" href="{TRY}">Essayer gratuitement {ARROW}</a><a class="btn ghost" href="#visite" data-tour-start>Lancer la visite</a></div>
  <p class="note rv" style="--d:220ms;margin-top:14px">Rien n’est publié sans votre accord. Bêta le lundi 9 novembre 2026.</p>
</div></section>

<section class="alt" id="visite" style="scroll-margin-top:80px"><div class="wrap">
  <div class="head rv"><p class="eyebrow">La visite</p><h2>Huit écrans. <em>Votre marketing tourne.</em></h2></div>
  <div class="tour" data-tour tabindex="-1">
    <div class="tour-top"><div class="tour-progress" aria-hidden="true"><i></i></div><span class="tour-count" aria-live="polite"></span></div>
    {html_steps}
    <div class="tour-nav"><button class="btn ghost" type="button" data-prev>Étape précédente</button><div class="tour-dots" aria-label="Choisir une étape"></div><button class="btn primary" type="button" data-next>Étape suivante</button></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="head rv"><p class="eyebrow">En vidéo</p><h2>Studio <em>en une minute.</em></h2></div>
  <div class="vid-one rv">{vid("16x9", 1280, 720, "Présentation de Pixapop Studio, faite avec Studio Vidéo", "v169")}
    <p class="vid-proof">Cette vidéo a été faite par Pixapop Studio, en un clic, avec Studio Vidéo.</p>
    <p class="vid-prompt"><span>Le prompt</span>« Crée-moi une présentation vidéo de Pixapop Studio en motion. »</p></div>
</div></section>
{cta_band("Essayez Studio <em>sur votre activité.</em>", "Rien ne part sans votre accord.", '<a class="btn ghost" href="' + STUDIO_SITE + '">Le site de Pixapop Studio</a>')}
"""
    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Pixapop Studio", "operatingSystem": "Web",
          "applicationCategory": "BusinessApplication", "inLanguage": "fr", "url": STUDIO_SITE,
          "publisher": {"@type": "Organization", "name": "Pixapop", "url": SITE}}
    return page("/studio/", "Pixapop Studio · Votre marketing préparé, vous validez",
                "Pixapop Studio écrit votre stratégie, votre calendrier éditorial, vos posts, articles, pages et tunnels de vente, publie quand vous validez et mesure ce qui marche. Pour les entrepreneurs solo et les petites entreprises.",
                body, jsonld=ld)


def pilot():
    body = f"""
<section class="hero"><div class="wrap center">
  <p class="eyebrow rv">Pixapop Pilot · en cours de développement</p>
  <h1 class="rv" style="--d:60ms">Vos clients. Vos devis. <em>Au même endroit.</em></h1>
  <p class="lead rv" style="--d:120ms">Le CRM relié à votre marketing. En cours de développement.</p>
  <div class="btns rv" style="--d:180ms"><a class="btn pilot" href="/contact/">Être prévenu {ARROW}</a><a class="btn ghost" href="/studio/">Découvrir Studio</a></div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="head rv"><p class="eyebrow">En cours de conception</p><h2>Ce que Pilot <em>change pour vous.</em></h2>
    <p class="lead">Maquettes : ce qui sortira pourra changer.</p></div>
  <div class="grid g2">
    <div class="rv"><h3>Vous savez où en est chaque contact.</h3><p class="muted">D’où il vient. Où il en est. Quoi faire ensuite.</p>
      <div class="mock pilotmock"><div class="mock-head"><b>Vos contacts</b><span class="tag mock">Maquette</span></div><div class="mock-body">
        <div class="mock-row"><span><b>Camille R.</b><small>Venue par votre article sur le blog</small></span><span class="mock-chip b">À rappeler</span></div>
        <div class="mock-row"><span><b>Julien M.</b><small>A demandé votre guide</small></span><span class="mock-chip o">Devis envoyé</span></div>
        <div class="mock-row"><span><b>Sarah L.</b><small>Recommandée par une cliente</small></span><span class="mock-chip g">Cliente</span></div>
      </div><div class="mock-label">Aperçu, en cours de conception</div></div></div>
    <div class="rv" style="--d:80ms"><h3>Un devis au juste prix, en un clic.</h3><p class="muted">Préparé depuis votre rendez-vous, à partir de vos tarifs. Jamais un prix inventé.</p>
      <div class="mock pilotmock"><div class="mock-head"><b>Proposition pour Julien M.</b><span class="tag mock">Maquette</span></div><div class="mock-body">
        <div class="mock-row"><span><b>D’après votre rendez-vous de mardi</b><small>Besoins repris, offre proposée, délais</small></span><span class="mock-chip b">Prête à relire</span></div>
        <div><small class="muted">Votre prix, comparé aux prix de votre métier</small><div class="mock-bar" style="margin-top:8px"><i style="width:62%"></i></div></div>
      </div><div class="mock-label">Aperçu, en cours de conception</div></div></div>
  </div>
  <div class="grid g2" style="margin-top:28px">
    <div class="rv"><h3>La prospection tourne pour vous.</h3><p class="muted">Des contacts qui ressemblent à vos meilleurs clients. Chaque e-mail validé par vous.</p>
      <div class="mock pilotmock"><div class="mock-head"><b>Campagne de rentrée</b><span class="tag mock">Maquette</span></div><div class="mock-body">
        <div class="mock-row"><span><b>Cible</b><small>Les profils qui ressemblent à vos meilleurs clients</small></span><span class="mock-chip g">Prête</span></div>
        <div class="mock-row"><span><b>Trois e-mails, sur deux semaines</b><small>Écrits dans votre ton, à valider</small></span><span class="mock-chip b">À relire</span></div>
      </div><div class="mock-label">Aperçu, en cours de conception</div></div></div>
    <div class="card rv" style="--d:80ms;align-self:start"><div class="ico i3">{icon("pilot")}</div><h3>Relié à Studio</h3>
      <p>Un contact venu d’un article arrive avec son historique.</p>
      <ul class="checks"><li>Chaque envoi validé par vous</li><li>Vos devis partent de vos tarifs</li><li>Vos données hébergées en France</li></ul></div>
  </div>
</div></section>
{cta_band("Pilot arrive. <em>Soyez prévenu.</em>", "Écrivez-nous.", '<a class="btn ghost" href="/contact/">Être prévenu</a>')}
"""
    return page("/pilot/", "Pixapop Pilot · CRM pour TPE et PME, devis et prospection (bientôt)",
                "Pixapop Pilot, CRM en cours de développement pour les entrepreneurs solo, les TPE et les PME : vos contacts, vos devis au bon prix et la prospection par e-mail, reliés à votre marketing.",
                body, body_class="pilot-page")


def sur_mesure():
    site_feats = ["Pages de vente", "Tunnels de vente", "Lettres d’information", "Formulaires de contact", "Pages d’inscription", "Prise de rendez-vous", "Référencement Google et IA", "Rapide sur téléphone"]
    feats = "".join(f"<span>{esc(f)}</span>" for f in site_feats)
    body = f"""
<section class="hero"><div class="wrap center">
  <p class="eyebrow rv">Sites et applications sur mesure</p>
  <h1 class="rv" style="--d:60ms">Un site qui vous ramène <em>des demandes.</em></h1>
  <p class="lead rv" style="--d:120ms">Sites, pages de vente, tunnels, applications. Au prix d’un freelance.</p>
  <div class="btns rv" style="--d:180ms"><a class="btn primary" href="/contact/">Demander un devis {ARROW}</a><a class="btn ghost" href="#applications">Voir une application</a></div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="grid g2" style="align-items:center">
    <div class="rv"><p class="eyebrow">Sites internet</p><h2>Fait pour <em>vos clients à vous.</em></h2>
      <p class="lead">Le plombier, la coach, la boutique : chacun ses clients, chacun son site.</p>
      <div class="features">{feats}</div></div>
    <div class="card rv" style="--d:80ms"><div class="ico i2">{icon("price")}</div><h3>Combien coûte un site internet ?</h3>
      <p>Un prix fixe, dans le devis, avant de commencer. Au tarif d’un freelance, souvent moins avec nos outils.</p>
      <a class="more" href="/contact/">Demander un devis {ARROW}</a></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="head rv"><p class="eyebrow">Comment ça se passe</p><h2>De l’idée <em>au site en ligne.</em></h2></div>
  <ol class="steps">
    <li class="card rv"><h3>Écouter</h3><p>Votre métier, vos clients.</p></li>
    <li class="card rv" style="--d:70ms"><h3>Dessiner</h3><p>Une maquette sur votre téléphone.</p></li>
    <li class="card rv" style="--d:140ms"><h3>Construire</h3><p>Pages, formulaires, tunnels, e-mails.</p></li>
    <li class="card rv" style="--d:210ms"><h3>Faire grandir</h3><p>Studio fait venir du monde.</p></li>
  </ol>
</div></section>

<section class="alt" id="applications" style="scroll-margin-top:80px"><div class="wrap case">
  <div class="rv"><p class="eyebrow">Applications mobiles</p><h2>Nouveau Cap, <em>une application conçue, développée et publiée par Pixapop.</em></h2>
    <p class="lead">Pour les plus de 40 ans qui changent de métier. De l’idée au store.</p>
    <ul class="checks"><li>Conception : le parcours, les écrans, les textes</li><li>Développement : l’application, le serveur, l’IA, les abonnements</li><li>Publication sur Google Play, avec les pages légales et la fiche du store</li></ul>
    <div class="btns" style="margin-top:24px"><a class="btn ghost" href="/nouveau-cap/">Voir Nouveau Cap {ARROW}</a><a class="btn primary" href="/contact/">Parler de votre application</a></div></div>
  <div class="rv deck-side" style="--d:100ms">{deck(["03_idees", "05_pistes", "01_home", "04_finances", "06_cv"], "Écrans de Nouveau Cap")}</div>
</div></section>
{cta_band("Votre site, <em>parlons-en.</em>", "Quelques lignes suffisent.", '<a class="btn ghost" href="/contact/">Nous écrire</a>')}
"""
    return page("/sur-mesure/", "Création de site internet pour artisans et indépendants · Pixapop",
                "Création de site internet et d’applications pour votre métier : site vitrine, pages de vente, tunnels, formulaires. Prix fixé dans un devis, au tarif d’un freelance. Exemple : Nouveau Cap.",
                body)


def a_propos():
    body = f"""
<section class="hero"><div class="wrap narrow center">
  <p class="eyebrow rv">À propos</p>
  <h1 class="rv" style="--d:60ms">Des outils construits <em>d’abord pour nous.</em></h1>
  <p class="lead rv" style="--d:120ms">Un entrepreneur seul. Un marketing toujours repoussé. Des outils pour que ça n’arrive plus.</p>
</div></section>

<section class="alt"><div class="wrap narrow">
  <div class="rv">
    <h2>Dix ans <em>seul aux commandes</em></h2>
    <p class="lead">Cyril Gayet, créateur de Pixapop. Trois entreprises, des réussites, des échecs.</p>
    <p>Le travail était bon. Les clients, contents. Il manquait le reste : se faire connaître, publier, trouver les suivants.</p>
  </div>
  <div class="rv" style="margin-top:36px">
    <h2>La tâche <em>qu’on repousse toujours</em></h2>
    <p>Le métier d’abord, le marketing après. Toujours. Alors nous avons construit l’outil qui le prépare. L’entrepreneur valide.</p>
  </div>
  <div class="rv" style="margin-top:36px">
    <h2>Aujourd’hui, <em>pour vous</em></h2>
    <p>Studio fait le marketing de Pixapop et de Nouveau Cap. Il peut faire le vôtre.</p>
  </div>
</div></section>

<section><div class="wrap">
  <div class="head center rv"><h2>Nos <em>règles</em></h2></div>
  <div class="grid g4">
    <article class="card rv"><div class="ico i2">{icon("clock")}</div><h3>Simple</h3><p>Vous validez. C’est tout.</p></article>
    <article class="card rv" style="--d:70ms"><div class="ico i1">{icon("heart")}</div><h3>Transparent</h3><p>Rien ne part sans votre accord.</p></article>
    <article class="card rv" style="--d:140ms"><div class="ico i3">{icon("shield")}</div><h3>Vos données chez vous</h3><p>En France. Jamais revendues.</p></article>
    <article class="card rv" style="--d:210ms"><div class="ico i4">{icon("target")}</div><h3>Utile</h3><p>Chaque fonction sert à trouver des clients.</p></article>
  </div>
</div></section>
{cta_band("Faisons connaissance.", "Écrivez-nous.")}
"""
    return page("/a-propos/", "À propos · L’histoire de Pixapop",
                "L’histoire de Pixapop : dix ans de vie d’entrepreneur seul, des outils construits d’abord pour notre propre marketing, puis ouverts aux entrepreneurs solo et aux petites entreprises.",
                body)


def contact():
    body = f"""
<section class="hero"><div class="wrap narrow center">
  <p class="eyebrow rv">Contact</p>
  <h1 class="rv" style="--d:60ms">Écrivez-nous, <em>nous vous répondons.</em></h1>
  <p class="lead rv" style="--d:120ms">Une vraie personne vous répond.</p>
</div></section>
<section style="padding-top:0"><div class="wrap">
  <div class="grid g2">
    <article class="card rv"><div class="ico i2">{icon("site")}</div><h3>Un projet de site ou d’application</h3>
      <p>Votre métier, vos clients, votre idée.</p>
      <p class="mail" style="margin-top:16px"><a href="mailto:{PROJECT_EMAIL}?subject=Projet">{PROJECT_EMAIL}</a></p></article>
    <article class="card rv" style="--d:80ms"><div class="ico i3">{icon("mail")}</div><h3>Studio, Pilot, une question</h3>
      <p>Essayer Studio, être prévenu de Pilot, poser une question.</p>
      <p class="mail" style="margin-top:16px"><a href="mailto:{EMAIL}">{EMAIL}</a></p></article>
  </div>
  <p class="note center rv" style="margin-top:24px">Pixapop, nom commercial de {esc(PUB['name'])}, entrepreneur individuel.</p>
</div></section>
"""
    return page("/contact/", "Contact · Pixapop", "Contactez Pixapop : un projet de site ou d’application, une question sur Pixapop Studio ou Pixapop Pilot.", body)


def nouveau_cap():
    p = PRICES
    features = [
        ("Faire <em>le point</em>", ["Votre runway : combien de mois vous pouvez tenir pendant la transition", "Le comparateur de pistes de métier et un plan de départ", "Le score de votre CV et l’essentiel de la VAE, gratuitement"]),
        ("Trouver <em>et financer</em>", ["Des idées de métier proposées par le Copilote à partir de votre parcours", "Projet de transition professionnelle, CPF, démission, immersion : étapes, délais, dossier", "Avec Premium : la présentation écrite de votre projet, rédigée avec l’IA"]),
        ("Avancer <em>chaque semaine</em>", ["Un plan d’action de 90 jours, en étapes concrètes", "Des fiches « Comment faire » avec méthode et scripts", "Des tests de pistes sur le terrain, avec un verdict", "Le feu vert financier et des sessions Focus"]),
        ("Votre CV <em>et LinkedIn</em>", ["Vos corrections prioritaires et l’analyse d’une annonce", "La réécriture par l’IA, sans jamais inventer de chiffre", "Créer son CV : PDF et Word adaptés à chaque annonce", "Votre titre et votre résumé LinkedIn"]),
        ("Le Copilote <em>IA</em>", ["Vos questions à tout moment, par un assistant qui connaît votre parcours (Pilote et Premium)", "Des actions à ajouter à votre plan en un geste", "Avec Premium : un bilan de progression toutes les deux semaines", "Avec Premium : le module VAE complet, diagnostic, dossier et jury"]),
    ]
    feats = "".join(f'<article class="card rv" style="--d:{(k % 3) * 70}ms"><h3>{t}</h3><ul class="checks">{"".join(f"<li>{esc(x)}</li>" for x in items)}</ul></article>' for k, (t, items) in enumerate(features))
    shots = [("home", "Accueil : le mot du Copilote et le bilan"), ("finances", "Finances : votre runway en mois"), ("pistes", "Pistes : comparer les métiers visés"), ("plan", "Plan 90 jours : les étapes de la semaine")]
    gallery = deck(["01_home", "02_financer", "03_idees", "04_finances", "05_pistes", "06_cv", "07_creer"], "Captures d’écran de l’app")
    body = f"""
<section class="hero"><div class="wrap">
  <div class="apphead rv"><img class="appicon" src="/assets/nouveau-cap-icon.png" alt="Icône de Nouveau Cap : une boussole qui pointe vers le nord" width="128" height="128">
    <div><span class="pill"><b>Réalisation</b> Une application conçue, développée et publiée par Pixapop</span><h1 style="margin-top:12px">Nouveau Cap</h1></div></div>
  <p class="lead rv" style="--d:100ms;margin-top:24px">Vous avez plus de 40 ans, une carrière solide, et l’envie de changer de métier. Nouveau Cap vous aide à passer de l’idée au projet, puis du projet au nouveau poste, avec une méthode claire et un Copilote IA qui connaît votre parcours.</p>
  <div class="btns rv" style="--d:150ms;margin-top:24px"><a class="btn primary" href="{APP_SITE}">Le site de Nouveau Cap {ARROW}</a><a class="btn ghost" href="{APP_SITE}#liste">Être prévenu du lancement</a></div>
  <div class="rv" style="--d:200ms;margin-top:36px">{gallery}</div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="head rv"><p class="eyebrow">L’app</p><h2>Tout pour changer de cap, <em>pas à pas.</em></h2></div>
  <div class="grid g3">{feats}</div>
</div></section>

<section><div class="wrap">
  <div class="head rv"><p class="eyebrow">Offres</p><h2>Simple, <em>sans engagement.</em></h2><p class="lead">Résiliable à tout moment dans Google Play.</p></div>
  <div class="grid g4">
    <article class="card plan rv"><h3>Gratuit</h3><p class="price">0 €</p><p>Faire le point par vous-même, sans IA : runway, comparateur de pistes, plan de départ, exemples de ce que fait le Copilote.</p></article>
    <article class="card plan rv" style="--d:70ms"><h3>Pilote</h3><p class="price">{esc(p['pilote'])} <small>/ mois</small></p><p>La méthode guidée pour avancer chaque semaine : plan de 90 jours, fiches, tests de pistes, Mon CV, le Copilote IA (10 messages par jour).</p></article>
    <article class="card plan best rv" style="--d:140ms"><h3>Premium</h3><p class="price">{esc(p['premium'])} <small>/ mois</small></p><p>Le suivi rapproché : bilan toutes les deux semaines, Copilote et fonctions IA sans limite, Créer son CV inclus. {p['trialDays']} jours d’essai gratuit pour un premier abonnement.</p></article>
    <article class="card plan rv" style="--d:210ms"><h3>Créer son CV</h3><p class="price">{esc(p['cvBuilder'])}</p><p>Achat unique, sans abonnement : votre CV rédigé par l’IA à partir de vos réponses, adapté à chaque annonce.</p></article>
  </div>
  <p class="note rv" style="margin-top:16px">Prix toutes taxes comprises. Le prix qui s’applique est celui affiché par Google Play au moment de l’achat.</p>
</div></section>

<section class="alt"><div class="wrap narrow">
  <div class="head rv"><p class="eyebrow">Vos données</p><h2>Votre projet <em>vous appartient.</em></h2></div>
  <p class="lead rv">Votre profil, votre plan et vos CV restent sur votre téléphone. Notre serveur est hébergé à Paris. Rien n’est envoyé à l’IA sans votre accord, pas de publicité, pas de mesure d’audience, et vous pouvez tout effacer depuis l’app.</p>
  <div class="links rv" style="margin-top:22px"><a href="/nouveau-cap/confidentialite/">Politique de confidentialité</a><a href="/nouveau-cap/conditions/">Conditions générales</a><a href="/nouveau-cap/suppression-donnees/">Supprimer vos données</a><a href="/nouveau-cap/mentions-legales/">Mentions légales de l’app</a></div>
  <p class="note rv" style="margin-top:22px">Nouveau Cap est un outil d’aide à la décision et d’organisation. Il ne remplace ni un conseil juridique ou financier, ni un accompagnement professionnel, et ne délivre pas de diplôme.</p>
</div></section>
"""
    ld = {"@context": "https://schema.org", "@type": "MobileApplication", "name": "Nouveau Cap", "operatingSystem": "Android",
          "applicationCategory": "BusinessApplication", "inLanguage": "fr", "url": APP_SITE, "sameAs": [SITE + "/nouveau-cap/"],
          "publisher": {"@type": "Organization", "name": "Pixapop", "url": SITE},
          "offers": [{"@type": "Offer", "name": "Gratuit", "price": "0", "priceCurrency": "EUR"},
                     {"@type": "Offer", "name": "Pilote", "price": p["pilote"].replace(" €", "").replace(",", "."), "priceCurrency": "EUR"},
                     {"@type": "Offer", "name": "Premium", "price": p["premium"].replace(" €", "").replace(",", "."), "priceCurrency": "EUR"}]}
    return page("/nouveau-cap/", "Nouveau Cap · Réussir sa reconversion après 40 ans",
                "Nouveau Cap, l’app de reconversion professionnelle après 40 ans : plan de 90 jours, CV et LinkedIn repensés, Copilote IA. Une application conçue, développée et publiée par Pixapop.",
                body, jsonld=ld)


def legal_page(path, title, description, intro, sections, crumbs, updated=None):
    blocks = "".join(f"<h2>{esc(s['title'])}</h2>" + "".join(f"<p>{esc(l)}</p>" for l in s["lines"]) for s in sections)
    updated = date.fromisoformat(updated or LEGAL["updated"])
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
            "Ce site mesure son audience avec Google Analytics, seulement si vous l’acceptez : rien n’est déposé ni chargé avant votre accord, et vous pouvez changer d’avis à tout moment avec le lien « Cookies » en bas de page. Aucune publicité. Détails dans la page Confidentialité.",
            "L’hébergeur peut conserver temporairement l’adresse IP des visiteurs pour la sécurité du service. Si vous nous écrivez, votre message sert uniquement à vous répondre.",
            "Les données de l’application Nouveau Cap sont décrites dans sa politique de confidentialité."]},
        {"title": "Propriété intellectuelle", "lines": [
            "Les textes, images et logos de ce site appartiennent à Pixapop, sauf mention contraire. Toute reproduction sans autorisation est interdite.",
            "Polices Geist et Instrument Serif, sous licence SIL Open Font License 1.1."]},
    ]
    out.append(legal_page("/mentions-legales/", "Mentions légales", "Mentions légales du site pixapop.fr : éditeur, hébergement, données personnelles.",
                          "", site_notice, '<a href="/">Pixapop</a>', updated="2026-10-07"))
    # Audience measurement of pixapop.fr and its sub-domains (Cyril, 07/10/2026): Google Analytics, with consent only.
    privacy = [
        {"title": "Qui est responsable", "lines": [
            f"Pixapop, nom commercial de {PUB['name']}, entrepreneur individuel. Contact : {EMAIL}.",
            "Cette page concerne la mesure d’audience de pixapop.fr et de ses sous-domaines, dont studio.pixapop.fr."]},
        {"title": "Mesure d’audience avec Google Analytics", "lines": [
            "Avec votre accord seulement, nous utilisons Google Analytics (Google Ireland Limited) pour savoir combien de personnes visitent nos pages, d’où elles viennent (moteur de recherche, réseau social, lien), quelles pages elles lisent, avec quel type d’appareil et depuis quelle ville, à peu près. Le but : améliorer nos pages.",
            "Google Analytics dépose des cookies (_ga et _ga_…) qui contiennent un identifiant tiré au hasard, valables 13 mois au plus. Les signaux Google et toute personnalisation publicitaire sont désactivés : vos visites ne servent à aucune publicité.",
            "Les données de Google Analytics sont conservées 14 mois au plus. Google peut les traiter aux États-Unis : Google LLC adhère au cadre de protection des données UE-États-Unis (Data Privacy Framework)."]},
        {"title": "Votre choix", "lines": [
            "Le bandeau vous propose « Refuser » ou « Accepter », aussi simplement l’un que l’autre. Tant que vous n’avez pas accepté, rien ne vient de Google.",
            "Votre choix est gardé 6 mois dans un petit cookie (pxp_consent), commun à pixapop.fr et à ses sous-domaines. Vous pouvez le changer à tout moment avec le lien « Cookies » en bas de page ; si vous refusez après avoir accepté, les cookies de Google Analytics sont effacés."]},
        {"title": "Hébergement", "lines": [
            "pixapop.fr est hébergé par GitHub Pages (GitHub, Inc.), studio.pixapop.fr par Cloudflare Pages (Cloudflare, Inc.). Ces hébergeurs peuvent conserver temporairement l’adresse IP des visiteurs pour la sécurité du service."]},
        {"title": "Vos droits", "lines": [
            f"Vous pouvez demander l’accès à vos données, leur rectification, leur effacement, ou vous opposer à leur traitement, en écrivant à {EMAIL}. Vous pouvez aussi adresser une réclamation à la CNIL (cnil.fr)."]},
    ]
    out.append(legal_page("/confidentialite/", "Confidentialité", "Confidentialité de pixapop.fr et de ses sous-domaines : mesure d’audience avec Google Analytics, seulement avec votre accord.",
                          "", privacy, '<a href="/">Pixapop</a>', updated="2026-10-07"))
    return out


def not_found():
    body = f"""<section class="hero"><div class="wrap narrow center"><p class="eyebrow">Erreur 404</p><h1>Ce pixel <em>s’est perdu.</em></h1>
<p class="lead">La page demandée n’existe pas ou a changé d’adresse.</p>
<div class="btns"><a class="btn primary" href="/">Revenir à l’accueil {ARROW}</a></div></div></section>"""
    page("/404", "Page introuvable · Pixapop", "Cette page n’existe pas.", body, canonical="/", noindex=True)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    (OUT / "CNAME").write_text("www.pixapop.fr\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    paths = [home(), studio(), pilot(), sur_mesure(), a_propos(), contact(), nouveau_cap(), *legal_pages()]
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
