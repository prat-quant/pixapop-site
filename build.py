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


def phone(src, alt):
    return f'<div class="phone"><img src="/assets/app/{src}.jpg" alt="{esc(alt)}" width="390" height="844" loading="lazy" decoding="async"></div>'


def faq_block(items):
    return "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in items)


def cta_band(title_html, lead, second=None):
    second = second or ('<a class="btn ghost" href="/contact/">Nous écrire</a>')
    return f"""<section><div class="wrap"><div class="cta-band rv">
  <h2>{title_html}</h2><p class="lead">{esc(lead)}</p>
  <div class="btns" style="justify-content:center"><a class="btn primary" href="{TRY}">Essayer gratuitement {ARROW}</a>{second}</div>
</div></div></section>"""


HOME_FAQ = [
    ("Faut-il savoir utiliser l’intelligence artificielle ?", "Non. Vous parlez de votre activité avec vos mots, Studio prépare le reste. Votre seul geste : relire et valider."),
    ("Est-ce que quelque chose part sans mon accord ?", "Non. Chaque post, article ou e-mail attend votre validation. Si vous le souhaitez, vous pouvez laisser un type de contenu partir seul, et revenir en arrière quand vous voulez."),
    ("Combien de temps faut-il y passer ?", "Le temps de relire et de valider. Studio prépare la semaine ou le mois d’avance ; vous validez quand vous voulez, en une fois ou au fil des jours."),
    ("ChatGPT ne fait-il pas déjà la même chose ?", "ChatGPT écrit ce que vous lui demandez, une fois. Studio garde votre stratégie, votre ton et vos résultats, prépare le mois entier, publie à l’heure prévue et mesure ce qui marche. Vous pouvez aussi relier votre propre IA à Studio."),
    ("Mes textes vont-ils ressembler à ceux de tout le monde ?", "Studio écrit d’après la fiche de votre entreprise : votre métier, vos clients, vos mots, et ce que vous ne voulez jamais lire. Ce qui ne vous ressemble pas, vous le corrigez avant de valider, et Studio s’en souvient pour la suite."),
    ("Combien ça coûte ?", "Les tarifs de Pixapop Studio seront annoncés à l’ouverture de la bêta, le lundi 9 novembre 2026."),
    ("Où sont mes données ?", "Hébergées en France, à Paris. Chaque entreprise ne voit que les siennes, et rien n’est revendu."),
]


def home():
    pains = [
        ("On est invisibles.", "Studio écrit vos posts et les articles de votre blog, et vérifie votre fiche Google en huit points. Votre entreprise se montre chaque semaine, là où vos clients cherchent."),
        ("Je gère TOUT par moi-même.", "Studio prépare le mois entier en un clic, d’après votre stratégie. Votre part : relire et valider."),
        ("Suis-je trop cher ?", "Dans votre stratégie, Studio donne son avis sur vos prix, comparés à votre marché. Pilot, à venir, préparera vos devis à partir de votre grille."),
        ("c’est pas le travail bien fait qui gagne, mais le devis le moins cher.", "Vos contenus montrent ce que vous faites mieux : vos réalisations, vos avis, votre méthode. Vos clients ont d’autres raisons de vous choisir que le prix."),
        ("Du trafic, mais aucune conversion.", "Studio crée vos pages et vos tunnels de vente : une page claire, un formulaire, une suite d’e-mails. Le visiteur laisse ses coordonnées et reçoit la suite."),
        ("J’ai l’impression que je ne vais pas y arriver", "Chaque semaine, Studio vous montre vos vrais chiffres et propose quoi changer. Vous voyez ce qui avance, et ce qui reste à faire."),
    ]
    pain_html = "".join(f'<article class="card pain rv" style="--d:{(k % 3) * 70}ms"><q>{esc(q)}</q><p><b>Ce que Pixapop change :</b> {esc(t)}</p></article>' for k, (q, t) in enumerate(pains))
    sols = [
        ("studio", "i2", "Pixapop Studio", '<span class="tag beta">Bêta le 9 novembre 2026</span>', "Votre stratégie, vos posts, vos articles, vos pages et vos e-mails, préparés chaque semaine d’après votre métier. Vous validez, Studio publie.", "/studio/", "Voir Studio écran par écran"),
        ("pilot", "i3", "Pixapop Pilot", '<span class="tag soon">Bientôt</span>', "Vos contacts, vos devis au bon prix et la prospection, reliés à votre marketing. En cours de développement.", "/pilot/", "Voir les maquettes"),
        ("hand", "i1", "Fait pour vous", "", "Pas envie d’y toucher du tout ? Notre équipe prépare votre marketing dans votre Studio. Vous n’avez plus qu’à valider.", "/contact/", "En parler"),
        ("site", "i4", "Sites et applications", "", "Un site ou une application pour votre métier, avec pages de vente, formulaires et e-mails, au prix d’un freelance.", "/sur-mesure/", "Voir les sites"),
    ]
    sol_html = "".join(f'<article class="card lift rv" style="--d:{k * 70}ms"><div class="ico {c}">{icon(i)}</div><h3>{esc(n)}</h3>{t}<p style="margin-top:10px">{esc(d)}</p><a class="more" href="{u}">{esc(l)} {ARROW}</a></article>' for k, (i, c, n, t, d, u, l) in enumerate(sols))
    body = f"""
<section class="hero"><div class="wrap center">
  <p class="eyebrow rv">Pour les solopreneurs</p>
  <h1 class="rv" style="--d:60ms">Maintenant, vous savez <em>comment trouver vos clients.</em></h1>
  <p class="lead rv" style="--d:120ms">Votre marketing est toujours à jour : vos posts, vos articles, vos pages, vos e-mails, vos réseaux. Le système tourne pour vous. Vous relisez, vous corrigez et vous validez. Rien de plus à faire.</p>
  <div class="btns rv" style="--d:180ms"><a class="btn primary" href="{TRY}">Essayer gratuitement {ARROW}</a><a class="btn ghost" href="/studio/">Voir Studio écran par écran</a></div>
  <p class="note rv" style="--d:210ms;margin-top:14px">Rien n’est publié sans votre accord. Bêta ouverte le lundi 9 novembre 2026.</p>
  <div class="hero-shot rv" style="--d:240ms">
    {shot("8-aujourdhui", "Pixapop Studio, l’écran Aujourd’hui : les actions du jour et le temps que prend chacune", True)}
    <span class="float f1" aria-hidden="true"><i style="background:#2BB5A0"></i>Votre article est en ligne</span>
    <span class="float f2" aria-hidden="true"><i style="background:#E0559A"></i>Un nouveau contact est arrivé</span>
    <span class="float f3" aria-hidden="true"><i style="background:#F2A541"></i>Stratégie ajustée d’après vos résultats</span>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="head center rv"><p class="eyebrow">Ce qu’écrivent les entrepreneurs seuls</p><h2>« On est invisibles. »</h2>
    <p class="lead">C’est la phrase qui revient le plus quand ils parlent de leurs clients. Voici les autres, et ce que Pixapop y change.</p></div>
  <div class="grid g3 pains">{pain_html}</div>
  <p class="note center rv" style="margin-top:18px">Phrases relevées telles quelles sur des forums d’entrepreneurs, en octobre 2026. Leurs auteurs ne sont pas des clients de Pixapop.</p>
</div></section>

<section><div class="wrap">
  <div class="head rv"><p class="eyebrow">Ce que fait Pixapop</p><h2>Être trouvé, <em>puis vendre au bon prix.</em></h2>
    <p class="lead">Tout ce que nous construisons sert à deux choses : que les clients qui vous cherchent vous trouvent, et qu’ils achètent au prix juste.</p></div>
  <div class="grid g2">
    <article class="card pillar rv"><div class="num">1</div><h3>Les clients qui vous cherchent vous trouvent</h3>
      <p>Studio part de votre activité, de vos clients et de ce qu’ils tapent sur Google. Il en tire votre stratégie : à qui parler, quoi dire, sur quels réseaux.</p>
      <ul class="checks"><li>Une stratégie écrite pour votre entreprise, dès la première session</li><li>Vos posts, articles, pages et e-mails, préparés d’après elle</li><li>Votre site vérifié pour Google et pour les réponses des IA comme ChatGPT</li></ul></article>
    <article class="card pillar rv" style="--d:80ms"><div class="num">2</div><h3>Ils achètent, au bon prix</h3>
      <p>Une page claire pour chaque offre, des e-mails qui répondent aux questions avant l’achat, et un avis franc sur vos prix.</p>
      <ul class="checks"><li>L’avis de Studio sur vos prix, comparés à votre marché</li><li>Des pages de vente et des tunnels prêts à l’emploi</li><li>Bientôt avec Pilot : vos contacts et vos devis au même endroit</li></ul></article>
  </div>
  <div class="card rv" style="margin-top:18px">
    <div class="ico i5">{icon("loop")}</div>
    <h3>Chaque semaine, <em>un peu mieux</em></h3>
    <p>Studio relève vos chiffres (visites, contacts, demandes), explique ce qui marche et ce qui ne marche pas, puis propose quoi changer : un sujet à creuser, une page à refaire, un test à lancer. Vous acceptez, il applique.</p>
    <ol class="loop loop-wrap"><li><b>Mesurer</b><span>vos vrais chiffres</span></li><li><b>Comprendre</b><span>ce qui marche, et pourquoi</span></li><li><b>Décider</b><span>vous choisissez</span></li><li><b>Tester</b><span>Studio applique et mesure</span></li></ol>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="head rv"><p class="eyebrow">Nos outils</p><h2>Peu d’outils, <em>qui partagent ce qu’ils savent.</em></h2>
    <p class="lead">Studio pour votre marketing, Pilot (à venir) pour vos clients et vos devis, et nos sites sur mesure. Ils partagent la même fiche de votre entreprise : vous n’expliquez votre activité qu’une fois.</p></div>
  <div class="grid g4">{sol_html}</div>
</div></section>

<section><div class="wrap">
  <div class="grid g2" style="align-items:center">
    <div class="rv"><p class="eyebrow">Petites entreprises</p><h2>Seul au marketing <em>dans une équipe de quinze ?</em></h2>
      <p class="lead">Vous gérez la communication d’une entreprise de 5, 15 ou 40 personnes, souvent en plus d’un autre poste. Studio prépare le plan du mois, les contenus et le bilan chiffré ; vous relisez et vous validez, au lieu de tout écrire.</p>
      <div class="btns" style="margin-top:20px"><a class="btn ghost" href="/contact/">Nous présenter votre entreprise {ARROW}</a></div></div>
    <div class="card rv" style="--d:80ms"><div class="ico i3">{icon("target")}</div><h3>Ce que vous gagnez</h3>
      <ul class="checks"><li>Un plan écrit, que vous pouvez montrer à votre direction</li><li>Des contenus réguliers, sans recruter</li><li>Des chiffres chaque semaine, et ce qu’il faut changer</li></ul></div>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="head rv"><p class="eyebrow">Comment ça tourne</p><h2>Vous validez, <em>Studio publie.</em></h2></div>
  <div class="week rv">
    <div><b>Une fois</b><p>Studio a préparé la semaine ou le mois. Vous relisez, vous corrigez, vous validez.</p></div>
    <div><b>Ensuite</b><p>Vos posts, articles et e-mails partent à l’heure prévue, pendant que vous êtes avec vos clients.</p></div>
    <div><b>Le week-end</b><p>Ce qui est prévu le samedi part le samedi. Vous, vous êtes en week-end.</p></div>
    <div><b>Chaque semaine</b><p>Le bilan arrive : vos chiffres, et ce que Studio propose de changer.</p></div>
  </div>
</div></section>

<section><div class="wrap story">
  <h2 class="rv">Construit d’abord <em>pour nous.</em></h2>
  <div class="rv" style="--d:80ms"><p class="lead">Pixapop est née de dix ans de vie d’entrepreneur seul : trois entreprises, et toujours la même tâche repoussée au lendemain, celle qui fait venir les clients. Studio a d’abord servi à notre propre marketing, avant d’être ouvert aux autres.</p>
    <a class="btn ghost" href="/a-propos/">Notre histoire {ARROW}</a></div>
</div></section>

<section class="alt"><div class="wrap narrow">
  <div class="head center rv"><h2>Vos <em>questions</em></h2></div>
  <div class="faq rv">{faq_block(HOME_FAQ)}</div>
</div></section>
{cta_band("Votre marketing du mois, <em>prêt d’avance.</em>", "Dites à Studio ce que vous faites : il prépare votre stratégie et votre premier mois de contenus. Rien ne part sans votre accord.")}
"""
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": "Pixapop", "url": SITE, "email": EMAIL,
          "description": "Pixapop aide les entrepreneurs solo et les petites entreprises à trouver des clients et à vendre au bon prix : Pixapop Studio (marketing préparé, validé par vous), Pixapop Pilot (CRM et devis, à venir), sites et applications sur mesure.",
          "logo": SITE + "/favicon.svg", "sameAs": [YOUTUBE], "legalName": f"{PUB['name']}, entrepreneur individuel",
          "address": {"@type": "PostalAddress", "streetAddress": "4775 RD 2085", "postalCode": "06330", "addressLocality": "Roquefort-les-Pins", "addressCountry": "FR"}}
    return page("/", "Pixapop · Trouver des clients quand on travaille seul",
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
        ("1-strategie", "Votre activité, avec vos mots", "Votre stratégie, écrite pour vous", "Vous dites ce que vous faites, pour qui, et ce que vous vendez. Studio en tire votre cible, ce qu’il faut lui dire, sur quels réseaux, et deux ou trois façons de lancer, chacune expliquée.", "vous savez enfin quoi publier, et pourquoi."),
        (None, "Vos offres et vos prix", "Le designer d’offres", "Il vous aidera à construire une offre d’appel, une offre principale et une offre haute, avec un prix comparé aux vraies données de votre métier. Il fera partie du forfait premium.", "un prix que vous pouvez défendre."),
        ("3-mois", "Un mois en un clic", "Le mois entier, prêt d’un coup", "Articles, posts, carrousels, vidéos courtes, e-mails : Studio prépare les quatre semaines d’après votre stratégie et dans votre ton. Vous gardez, vous corrigez, ou vous demandez une autre version.", "plus de page blanche le dimanche soir."),
        ("4-calendrier", "Le calendrier éditorial", "Vous validez, Studio publie", "Chaque contenu a sa date et son réseau. Un clic sur Valider, et il part à l’heure prévue, même le samedi.", "une présence régulière, sans y penser."),
        ("5-tunnels", "Pages et tunnels de vente", "Les visiteurs laissent leurs coordonnées", "Studio crée la page, le formulaire et la suite d’e-mails. Le visiteur s’inscrit (avec son accord), reçoit vos e-mails aux bonnes dates et arrive dans vos contacts.", "des contacts qui s’ajoutent pendant que vous travaillez."),
        ("6-audit", "Audit Google et IA", "Votre site, vu par Google et par ChatGPT", "Collez l’adresse de votre site : Studio relève ce qui gêne Google, teste si les IA vous citent, et vous dit quoi corriger en premier.", "vous savez quoi corriger, et dans quel ordre."),
        ("7-analytics", "Analytics", "Chaque semaine, quoi changer", "Studio relève vos chiffres, explique ce qui marche et propose des changements : un sujet à creuser, une page à refaire, un test à lancer. Vous acceptez, il applique.", "des décisions prises sur des chiffres."),
        ("8-aujourdhui", "Ce qui attend votre accord", "Tout au même endroit", "L’écran Aujourd’hui montre ce qui attend votre validation et le temps que prend chaque action. Vous validez quand vous voulez, la semaine ou le mois d’un coup.", "votre temps pour vos clients."),
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
  <h1 class="rv" style="--d:60ms">Un mois de marketing préparé <em>d’après votre métier.</em></h1>
  <p class="lead rv" style="--d:120ms">Studio écrit votre stratégie, vos posts, vos articles, vos pages et vos e-mails, les publie quand vous validez, et vous dit chaque semaine ce qui a marché.</p>
  <div class="btns rv" style="--d:180ms"><a class="btn primary" href="{TRY}">Essayer gratuitement {ARROW}</a><a class="btn ghost" href="#visite" data-tour-start>Lancer la visite</a></div>
  <p class="note rv" style="--d:220ms;margin-top:14px">Rien n’est publié sans votre accord. Bêta le lundi 9 novembre 2026.</p>
</div></section>

<section class="alt" id="visite" style="scroll-margin-top:80px"><div class="wrap">
  <div class="head rv"><p class="eyebrow">La visite</p><h2>Huit écrans, <em>de la stratégie au bilan.</em></h2><p class="lead">Les vrais écrans de Studio, dans l’ordre où vous les utiliserez.</p></div>
  <div class="tour" data-tour tabindex="-1">
    <div class="tour-top"><div class="tour-progress" aria-hidden="true"><i></i></div><span class="tour-count" aria-live="polite"></span></div>
    {html_steps}
    <div class="tour-nav"><button class="btn ghost" type="button" data-prev>Étape précédente</button><div class="tour-dots" aria-label="Choisir une étape"></div><button class="btn primary" type="button" data-next>Étape suivante</button></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="head rv"><p class="eyebrow">En vidéo</p><h2>Studio <em>en une minute.</em></h2></div>
  <div class="vids rv">{vid("16x9", 1280, 720, "Présentation de Pixapop Studio, format horizontal", "v169")}{vid("9x16", 720, 1280, "Présentation de Pixapop Studio, format vertical", "v916")}</div>
</div></section>
{cta_band("Essayez Studio <em>sur votre propre activité.</em>", "Dites ce que vous faites : Studio prépare votre stratégie et vos premiers contenus. Rien ne part sans votre accord.", '<a class="btn ghost" href="' + STUDIO_SITE + '">Le site de Pixapop Studio</a>')}
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
  <h1 class="rv" style="--d:60ms">Vos contacts et vos devis, <em>au même endroit que votre marketing.</em></h1>
  <p class="lead rv" style="--d:120ms">Pilot sera le CRM de Pixapop, pour les entrepreneurs solo et les petites entreprises. Il suivra chaque contact, préparera vos devis au bon prix et prospectera pour vous. Voici les maquettes.</p>
  <div class="btns rv" style="--d:180ms"><a class="btn pilot" href="/contact/">Être prévenu {ARROW}</a><a class="btn ghost" href="/studio/">Découvrir Studio</a></div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="head rv"><p class="eyebrow">En cours de conception</p><h2>Ce que Pilot <em>fera pour vous.</em></h2>
    <p class="lead">Ces écrans sont des maquettes : ce qui sortira pourra changer.</p></div>
  <div class="grid g2">
    <div class="rv"><h3>Chaque contact, et où il en est</h3><p class="muted">D’où vient chaque prospect (votre article, votre guide, une recommandation), où il en est, et ce qu’il faut faire ensuite.</p>
      <div class="mock pilotmock"><div class="mock-head"><b>Vos contacts</b><span class="tag mock">Maquette</span></div><div class="mock-body">
        <div class="mock-row"><span><b>Camille R.</b><small>Venue par votre article sur le blog</small></span><span class="mock-chip b">À rappeler</span></div>
        <div class="mock-row"><span><b>Julien M.</b><small>A demandé votre guide</small></span><span class="mock-chip o">Devis envoyé</span></div>
        <div class="mock-row"><span><b>Sarah L.</b><small>Recommandée par une cliente</small></span><span class="mock-chip g">Cliente</span></div>
      </div><div class="mock-label">Aperçu, en cours de conception</div></div></div>
    <div class="rv" style="--d:80ms"><h3>Vos devis, au prix juste</h3><p class="muted">Une proposition préparée à partir de votre rendez-vous, avec vos offres et votre grille de prix. Pilot ne fixe jamais un prix seul : il part de vos tarifs, et vous montre où vous vous situez dans votre métier.</p>
      <div class="mock pilotmock"><div class="mock-head"><b>Proposition pour Julien M.</b><span class="tag mock">Maquette</span></div><div class="mock-body">
        <div class="mock-row"><span><b>D’après votre rendez-vous de mardi</b><small>Besoins repris, offre proposée, délais</small></span><span class="mock-chip b">Prête à relire</span></div>
        <div><small class="muted">Votre prix, comparé aux prix de votre métier</small><div class="mock-bar" style="margin-top:8px"><i style="width:62%"></i></div></div>
      </div><div class="mock-label">Aperçu, en cours de conception</div></div></div>
  </div>
  <div class="grid g2" style="margin-top:28px">
    <div class="rv"><h3>La prospection, sans y passer vos soirées</h3><p class="muted">Pilot trouvera des contacts qui ressemblent à vos meilleurs clients et leur écrira dans votre ton, dans le respect du RGPD. Chaque e-mail attendra votre validation.</p>
      <div class="mock pilotmock"><div class="mock-head"><b>Campagne de rentrée</b><span class="tag mock">Maquette</span></div><div class="mock-body">
        <div class="mock-row"><span><b>Cible</b><small>Les profils qui ressemblent à vos meilleurs clients</small></span><span class="mock-chip g">Prête</span></div>
        <div class="mock-row"><span><b>Trois e-mails, sur deux semaines</b><small>Écrits dans votre ton, à valider</small></span><span class="mock-chip b">À relire</span></div>
      </div><div class="mock-label">Aperçu, en cours de conception</div></div></div>
    <div class="card rv" style="--d:80ms;align-self:start"><div class="ico i3">{icon("pilot")}</div><h3>Relié à Studio</h3>
      <p>Pilot partagera la fiche de votre entreprise avec Studio : vos offres, votre stratégie, vos contacts. Un contact venu d’un article de Studio arrivera dans Pilot avec son historique.</p>
      <ul class="checks"><li>Chaque envoi validé par vous</li><li>Vos devis partent de vos tarifs</li><li>Vos données hébergées en France</li></ul></div>
  </div>
</div></section>
{cta_band("Soyez prévenu <em>dès que Pilot est prêt.</em>", "Écrivez-nous : nous vous prévenons dès que Pilot peut être essayé.", '<a class="btn ghost" href="/contact/">Être prévenu</a>')}
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
  <h1 class="rv" style="--d:60ms">Un site pour votre métier, <em>qui fait venir des demandes.</em></h1>
  <p class="lead rv" style="--d:120ms">Sites vitrines, pages de vente, tunnels et applications mobiles, construits pour vos clients à vous. Au prix d’un freelance ou d’une petite agence, et souvent moins si vous utilisez aussi Studio.</p>
  <div class="btns rv" style="--d:180ms"><a class="btn primary" href="/contact/">Demander un devis {ARROW}</a><a class="btn ghost" href="#applications">Voir une application</a></div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="grid g2" style="align-items:center">
    <div class="rv"><p class="eyebrow">Sites internet</p><h2>Pensé pour la façon <em>dont vos clients choisissent.</em></h2>
      <p class="lead">Un plombier est choisi pour sa réactivité et sa zone, une coach pour la confiance qu’elle inspire, une boutique pour ses produits. Votre site met en avant ce qui décide vos clients, avec les fonctions qui transforment une visite en demande.</p>
      <div class="features">{feats}</div></div>
    <div class="card rv" style="--d:80ms"><div class="ico i2">{icon("price")}</div><h3>Combien coûte un site internet ?</h3>
      <p>Le prix dépend du nombre de pages et des fonctions (formulaire, tunnel, prise de rendez-vous). Nous le fixons dans un devis, avant de commencer. Il reste dans les prix d’un freelance ou d’une petite agence, souvent en dessous si vous utilisez aussi nos outils.</p>
      <p class="note" style="margin-top:12px">Sur devis, en attendant nos offres de création de site.</p>
      <a class="more" href="/contact/">Demander un devis {ARROW}</a></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="head rv"><p class="eyebrow">Comment ça se passe</p><h2>De votre idée <em>à votre site en ligne.</em></h2></div>
  <ol class="steps">
    <li class="card rv"><h3>Écouter</h3><p>Un premier échange sur votre métier, vos clients et ce que le site doit vous apporter.</p></li>
    <li class="card rv" style="--d:70ms"><h3>Dessiner</h3><p>Une première version à regarder sur votre téléphone, pour décider sur du concret.</p></li>
    <li class="card rv" style="--d:140ms"><h3>Construire</h3><p>Les pages, les formulaires, les tunnels, les e-mails ; pour une application, la publication sur les stores.</p></li>
    <li class="card rv" style="--d:210ms"><h3>Faire grandir</h3><p>Les visites et les demandes mesurées, et Studio pour faire venir du monde.</p></li>
  </ol>
</div></section>

<section class="alt" id="applications" style="scroll-margin-top:80px"><div class="wrap case">
  <div class="rv"><p class="eyebrow">Applications mobiles</p><h2>Nouveau Cap, <em>une application conçue, développée et publiée par Pixapop.</em></h2>
    <p class="lead">Pour les cadres de plus de 40 ans qui changent de métier : un plan de 90 jours, les finances sous contrôle, un CV et un profil LinkedIn retravaillés, et un Copilote IA qui connaît leur parcours.</p>
    <ul class="checks"><li>Conception : le parcours, les écrans, les textes</li><li>Développement : l’application, le serveur, l’IA, les abonnements</li><li>Publication sur Google Play, avec les pages légales et la fiche du store</li></ul>
    <div class="btns" style="margin-top:24px"><a class="btn ghost" href="/nouveau-cap/">Voir Nouveau Cap {ARROW}</a><a class="btn primary" href="/contact/">Parler de votre application</a></div></div>
  <div class="phones rv" style="--d:100ms" aria-hidden="true">{phone("pistes", "Écran Pistes de Nouveau Cap")}{phone("home", "Écran d’accueil de Nouveau Cap")}{phone("finances", "Écran Finances de Nouveau Cap")}</div>
</div></section>
{cta_band("Parlons de <em>votre site.</em>", "Dites-nous en quelques lignes votre métier, vos clients et ce que le site doit changer. Nous vous répondons personnellement.", '<a class="btn ghost" href="/contact/">Nous écrire</a>')}
"""
    return page("/sur-mesure/", "Création de site internet pour artisans et indépendants · Pixapop",
                "Création de site internet et d’applications pour votre métier : site vitrine, pages de vente, tunnels, formulaires. Prix fixé dans un devis, au tarif d’un freelance. Exemple : Nouveau Cap.",
                body)


def a_propos():
    body = f"""
<section class="hero"><div class="wrap narrow center">
  <p class="eyebrow rv">À propos</p>
  <h1 class="rv" style="--d:60ms">Des outils construits <em>d’abord pour nous.</em></h1>
  <p class="lead rv" style="--d:120ms">Pixapop a été créée par un entrepreneur seul, pour régler un problème qu’il vivait : faire son métier et, en même temps, trouver les clients suivants.</p>
</div></section>

<section class="alt"><div class="wrap narrow">
  <div class="rv">
    <h2>Dix ans <em>seul aux commandes</em></h2>
    <p class="lead">Le créateur de Pixapop, Cyril Gayet, travaille seul depuis dix ans : trois entreprises, des réussites, des échecs, et de nombreux entrepreneurs formés et conseillés en chemin.</p>
    <p>Avec le recul, les échecs avaient souvent la même cause. Le travail était bien fait et les clients contents. Ce qui manquait : se faire connaître, publier régulièrement, savoir ce qui marche, trouver les clients suivants.</p>
  </div>
  <div class="rv" style="margin-top:36px">
    <h2>La tâche <em>qu’on repousse toujours</em></h2>
    <p>Quand on aime son métier, on s’y consacre. Le marketing glisse au lendemain, puis à la semaine suivante. Les outils existants demandaient du temps, de l’argent ou une équipe entière.</p>
    <p>Les premiers outils de Pixapop ont donc été construits pour un usage personnel : un outil qui prépare le travail, et un entrepreneur qui décide et valide.</p>
  </div>
  <div class="rv" style="margin-top:36px">
    <h2>Puis ouverts <em>aux autres entrepreneurs</em></h2>
    <p>Studio prépare aujourd’hui le marketing de Pixapop et celui de Nouveau Cap, notre application de reconversion. Nous l’ouvrons aux entrepreneurs solo et aux petites entreprises, avec une règle : chaque fonction doit vous aider à trouver des clients ou à vendre au bon prix. Sinon, nous ne la construisons pas.</p>
  </div>
</div></section>

<section><div class="wrap">
  <div class="head center rv"><h2>Nos <em>règles</em></h2></div>
  <div class="grid g4">
    <article class="card rv"><div class="ico i2">{icon("clock")}</div><h3>Simple</h3><p>Votre marketing préparé d’avance ; vous relisez et vous validez, sans jargon ni formation à suivre.</p></article>
    <article class="card rv" style="--d:70ms"><div class="ico i1">{icon("heart")}</div><h3>Transparent</h3><p>Rien ne part sans votre accord, et chaque proposition dit pourquoi.</p></article>
    <article class="card rv" style="--d:140ms"><div class="ico i3">{icon("shield")}</div><h3>Vos données chez vous</h3><p>Hébergées en France, séparées de celles des autres, jamais revendues.</p></article>
    <article class="card rv" style="--d:210ms"><div class="ico i4">{icon("target")}</div><h3>Utile</h3><p>Chaque fonction doit vous aider à trouver des clients ou à vendre au bon prix.</p></article>
  </div>
</div></section>
{cta_band("Faisons connaissance.", "Une question, un projet ? Écrivez-nous, nous vous répondons personnellement.")}
"""
    return page("/a-propos/", "À propos · L’histoire de Pixapop",
                "L’histoire de Pixapop : dix ans de vie d’entrepreneur seul, des outils construits d’abord pour notre propre marketing, puis ouverts aux entrepreneurs solo et aux petites entreprises.",
                body)


def contact():
    body = f"""
<section class="hero"><div class="wrap narrow center">
  <p class="eyebrow rv">Contact</p>
  <h1 class="rv" style="--d:60ms">Écrivez-nous, <em>nous vous répondons.</em></h1>
  <p class="lead rv" style="--d:120ms">Une personne lit chaque message et vous répond.</p>
</div></section>
<section style="padding-top:0"><div class="wrap">
  <div class="grid g2">
    <article class="card rv"><div class="ico i2">{icon("site")}</div><h3>Un projet de site ou d’application</h3>
      <p>Dites-nous votre métier, vos clients, et ce que le site ou l’application doit changer pour vous.</p>
      <p class="mail" style="margin-top:16px"><a href="mailto:{PROJECT_EMAIL}?subject=Projet">{PROJECT_EMAIL}</a></p></article>
    <article class="card rv" style="--d:80ms"><div class="ico i3">{icon("mail")}</div><h3>Studio, Pilot, une question</h3>
      <p>Pour essayer Studio, être prévenu de la sortie de Pilot, présenter votre entreprise ou poser une question.</p>
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
    gallery = "".join(phone(f, alt) for f, alt in shots)
    body = f"""
<section class="hero"><div class="wrap">
  <div class="apphead rv"><img class="appicon" src="/assets/nouveau-cap-icon.png" alt="Icône de Nouveau Cap : une boussole qui pointe vers le nord" width="128" height="128">
    <div><span class="pill"><b>Réalisation</b> Une application conçue, développée et publiée par Pixapop</span><h1 style="margin-top:12px">Nouveau Cap</h1></div></div>
  <p class="lead rv" style="--d:100ms;margin-top:24px">Vous avez plus de 40 ans, une carrière solide, et l’envie de changer de métier. Nouveau Cap vous aide à passer de l’idée au projet, puis du projet au nouveau poste, avec une méthode claire et un Copilote IA qui connaît votre parcours.</p>
  <div class="btns rv" style="--d:150ms;margin-top:24px"><a class="btn primary" href="{APP_SITE}">Le site de Nouveau Cap {ARROW}</a><a class="btn ghost" href="{APP_SITE}#liste">Être prévenu du lancement</a></div>
  <div class="gallery rv" style="--d:200ms;margin-top:36px" aria-label="Captures d’écran de l’app">{gallery}</div>
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
