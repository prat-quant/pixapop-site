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
      <p>Des outils simples et une équipe qui travaille pour vous, pour que les solopreneurs trouvent leurs clients et vendent au juste prix.</p></div>
    <div><b>Solutions</b><a href="/studio/">Pixapop Studio</a><a href="/pilot/">Pixapop Pilot</a><a href="/sur-mesure/">Sites et applications</a><a href="/nouveau-cap/">Nouveau Cap</a></div>
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
    target = OUT / path.strip("/") / "index.html" if path != "/404" else OUT / "404.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    return path


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
    ("Faut-il savoir utiliser l’intelligence artificielle ?", "Non. Elle travaille en coulisses, au meilleur niveau, sans que vous ayez à la maîtriser. Vous parlez de votre entreprise avec vos mots ; vos outils font le reste."),
    ("Est-ce que quelque chose part sans mon accord ?", "Non. Vous décidez et vous validez. Vous pouvez aussi dire ce qui peut partir seul, et changer d’avis à tout moment."),
    ("Combien de temps faut-il pour s’y mettre ?", "Une journée suffit pour prendre en main nos outils. Ensuite, quelques minutes par jour pour décider et valider."),
    ("Combien ça coûte ?", "Les tarifs de Pixapop Studio sont annoncés à l’ouverture de la bêta, le 9 novembre 2026. Notre principe : un investissement modeste, pour un retour qui le dépasse largement."),
    ("Où sont mes données ?", "Hébergées en France, à Paris. Chaque entreprise ne voit que les siennes, et rien n’est revendu."),
]


def home():
    pains = [
        ("Où vais-je trouver mes prochains clients ?", "La question qui revient chaque mois, et qui empêche de dormir."),
        ("Je publierai demain.", "Les réseaux attendent, et demain devient la semaine prochaine."),
        ("Je baisse un peu mon prix, pour ne pas le perdre.", "On se brade par manque d’assurance, et on travaille trop pour trop peu."),
        ("Il me faudrait huit bras.", "Vendre, produire, relancer, communiquer, gérer : tout repose sur vous, et seulement sur vous."),
        ("L’IA, je n’ai pas le temps de m’y mettre.", "Tout le monde en parle ; vous, vous avez des clients à servir."),
        ("Je ne sais pas ce qui marche.", "On publie un peu, au hasard, sans jamais savoir ce qui ramène vraiment des clients."),
    ]
    pain_html = "".join(f'<article class="card pain rv" style="--d:{(k % 3) * 70}ms"><q>{esc(q)}</q><p>{esc(t)}</p></article>' for k, (q, t) in enumerate(pains))
    sols = [
        ("studio", "i2", "Pixapop Studio", '<span class="tag beta">Bêta le 9 novembre 2026</span>', "Votre stratégie, vos contenus, vos pages, vos e-mails : préparés pour vous, publiés quand vous validez, et améliorés chaque semaine d’après les résultats.", "/studio/", "Découvrir Studio"),
        ("pilot", "i3", "Pixapop Pilot", '<span class="tag soon">Bientôt</span>', "Vos contacts, vos devis, vos rendez-vous et la prospection, au même endroit que votre marketing. En cours de développement.", "/pilot/", "Voir l’aperçu"),
        ("hand", "i1", "Fait pour vous", "", "Vous n’avez pas envie d’y toucher ? Notre équipe prépare tout et le livre dans votre Studio. Vous n’avez plus qu’à valider.", "/contact/", "En parler"),
        ("site", "i4", "Sites et applications", "", "Des sites modernes et des applications pensés pour votre métier, avec tout ce qu’il faut pour vendre, à un tarif accessible.", "/sur-mesure/", "Voir le service"),
    ]
    sol_html = "".join(f'<article class="card lift rv" style="--d:{k * 70}ms"><div class="ico {c}">{icon(i)}</div><h3>{esc(n)}</h3>{t}<p style="margin-top:10px">{esc(d)}</p><a class="more" href="{u}">{esc(l)} {ARROW}</a></article>' for k, (i, c, n, t, d, u, l) in enumerate(sols))
    body = f"""
<section class="hero"><div class="wrap center">
  <p class="eyebrow rv">Pour les solopreneurs</p>
  <h1 class="rv" style="--d:60ms">Vous êtes seul.<br><em>Votre entreprise, non.</em></h1>
  <p class="lead rv" style="--d:120ms">Pixapop vous donne une équipe qui travaille pour vous, jour et nuit, même le week-end : elle fait venir vos prochains clients, fait grandir votre entreprise et vous aide à vendre au juste prix. Vous décidez, vous validez. Elle exécute.</p>
  <div class="btns rv" style="--d:180ms"><a class="btn primary" href="{TRY}">Essayer gratuitement {ARROW}</a><a class="btn ghost" href="/studio/">Voir comment ça marche</a></div>
  <div class="hero-shot rv" style="--d:240ms">
    {shot("8-aujourdhui", "Pixapop Studio, l’écran Aujourd’hui : ce qu’il y a à faire, et le temps que ça prend", True)}
    <span class="float f1" aria-hidden="true"><i style="background:#2BB5A0"></i>Votre article est en ligne</span>
    <span class="float f2" aria-hidden="true"><i style="background:#E0559A"></i>Un nouveau contact est arrivé</span>
    <span class="float f3" aria-hidden="true"><i style="background:#F2A541"></i>Stratégie ajustée d’après vos résultats</span>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="head center rv"><p class="eyebrow">Vous vous reconnaissez ?</p><h2>Seul à tout porter, <em>et à tout décider.</em></h2>
    <p class="lead">Nous sommes solopreneurs, nous aussi. Nous connaissons ces phrases par cœur.</p></div>
  <div class="grid g3 pains">{pain_html}</div>
</div></section>

<section><div class="wrap">
  <div class="head rv"><p class="eyebrow">Ce qui change</p><h2>Les clients vous trouvent. <em>Vous vendez au juste prix.</em></h2>
    <p class="lead">Sans nouveaux clients, tout le reste ne sert à rien. C’est pourquoi tout ce que nous faisons commence par là.</p></div>
  <div class="grid g2">
    <article class="card pillar rv"><div class="num">1</div><h3>Les clients qui vous cherchent vous trouvent</h3>
      <p>Une vraie stratégie d’acquisition, pensée pour qui vous êtes, ce que vous vendez et à qui.</p>
      <ul class="checks"><li>Une stratégie de communication et une direction claire</li><li>Des objectifs, et des chiffres qui disent ce qui marche</li><li>Vos contenus, votre site et vos e-mails, préparés presque tout seuls</li></ul></article>
    <article class="card pillar rv" style="--d:80ms"><div class="num">2</div><h3>Ils deviennent des clients, au bon prix</h3>
      <p>Des offres claires, de nouveaux services à proposer, et un prix appuyé sur les vraies données de votre métier.</p>
      <ul class="checks"><li>Des offres justes, faciles à comprendre</li><li>Un prix que vous pouvez défendre : vous ne vous bradez plus</li><li>Une relation client soignée : des avis, du bouche-à-oreille, des recommandations</li></ul></article>
  </div>
  <div class="card rv" style="margin-top:18px">
    <div class="ico i5">{icon("loop")}</div>
    <h3>Et tout s’améliore, <em>en continu</em></h3>
    <p>Chaque semaine, les résultats reviennent : visites, contacts, demandes. Votre équipe en tire les leçons, crée de nouveaux contenus, ajuste votre site, votre référencement sur Google et votre présence dans les réponses des IA. Vous validez ; elle applique.</p>
    <ol class="loop loop-wrap"><li><b>Mesurer</b><span>les vrais chiffres</span></li><li><b>Comprendre</b><span>ce qui marche, et pourquoi</span></li><li><b>Décider</b><span>vous choisissez</span></li><li><b>Améliorer</b><span>c’est appliqué pour vous</span></li></ol>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="head rv"><p class="eyebrow">Nos solutions</p><h2>Peu d’outils, <em>qui se parlent.</em></h2>
    <p class="lead">Pas un gros logiciel qui fait tout à moitié : quelques outils spécialisés, pris en main en une journée, qui travaillent ensemble. L’intelligence artificielle au meilleur niveau, sans avoir besoin de la maîtriser.</p></div>
  <div class="grid g4">{sol_html}</div>
</div></section>

<section><div class="wrap">
  <div class="head rv"><p class="eyebrow">Une semaine avec Pixapop</p><h2>Vous décidez. <em>Le reste avance sans vous.</em></h2></div>
  <div class="week rv">
    <div><b>Lundi</b><p>Vous validez le plan de la semaine en quelques minutes.</p></div>
    <div><b>Du mardi au vendredi</b><p>Articles, publications et e-mails partent à l’heure prévue, pendant que vous servez vos clients.</p></div>
    <div><b>Le week-end</b><p>Votre équipe continue. Vous, vous profitez des vôtres.</p></div>
    <div><b>Le lundi suivant</b><p>Le bilan chiffré arrive, et la stratégie s’ajuste d’elle-même.</p></div>
  </div>
</div></section>

<section class="alt"><div class="wrap story">
  <blockquote class="rv">« Nous avons créé les outils dont nous avions besoin. Ils peuvent servir à tant d’autres. »</blockquote>
  <div class="rv" style="--d:80ms"><p class="lead">Pixapop est née de dix ans de vie de solopreneur : des réussites, des échecs, et toujours la même tâche repoussée au lendemain, celle qui fait pourtant venir les clients. Nous avons traversé les mêmes difficultés que vous, et voici comment les dépasser.</p>
    <a class="btn ghost" href="/a-propos/">Notre histoire {ARROW}</a></div>
</div></section>

<section><div class="wrap narrow">
  <div class="head center rv"><h2>Vos <em>questions</em></h2></div>
  <div class="faq rv">{faq_block(HOME_FAQ)}</div>
</div></section>
{cta_band("Reprenez votre rôle <em>de chef d’entreprise.</em>", "Votre équipe s’occupe du reste, jour et nuit.")}
"""
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": "Pixapop", "url": SITE, "email": EMAIL,
          "description": "Pixapop aide les solopreneurs à trouver leurs clients et à vendre au juste prix, avec des outils simples qui travaillent pour eux : Pixapop Studio, Pixapop Pilot, sites et applications sur mesure.",
          "logo": SITE + "/favicon.svg", "sameAs": [YOUTUBE], "legalName": f"{PUB['name']}, entrepreneur individuel",
          "address": {"@type": "PostalAddress", "streetAddress": "4775 RD 2085", "postalCode": "06330", "addressLocality": "Roquefort-les-Pins", "addressCountry": "FR"}}
    return page("/", "Pixapop · Une équipe qui travaille pour les solopreneurs",
                "Pixapop aide les solopreneurs à faire venir de nouveaux clients et à vendre au juste prix, avec des outils simples qui travaillent pour eux jour et nuit. Vous décidez, ils exécutent.",
                body, jsonld=ld)


def offer_designer_mock():
    return """<div class="mock" role="img" aria-label="Aperçu du designer d’offres de Pixapop Studio, en cours de conception">
  <div class="mock-head"><b>Vos offres</b><span class="mock-chip o">Forfait premium</span></div>
  <div class="mock-body">
    <div class="mock-row"><span><b>Séance découverte</b><small>Pour un premier contact, sans engagement</small></span><span class="mock-price">Offre d’appel</span></div>
    <div class="mock-row"><span><b>Accompagnement trois mois</b><small>Votre offre principale, la plus demandée</small></span><span class="mock-price">Offre cœur</span></div>
    <div class="mock-row"><span><b>Suivi à l’année</b><small>Pour vos meilleurs clients</small></span><span class="mock-price">Offre haute</span></div>
    <div><small class="muted">Votre prix, comparé aux vraies données de votre métier</small><div class="mock-bar" style="margin-top:8px"><i style="width:68%"></i></div>
      <div style="display:flex;justify-content:space-between;font-size:12.5px;color:var(--muted);margin-top:6px"><span>Trop bas</span><span>Juste</span><span>Haut de gamme</span></div></div>
  </div>
  <div class="mock-label">Aperçu, en cours de conception</div>
</div>"""


def studio():
    steps = [
        ("1-strategie", "Votre activité en une phrase", "Votre stratégie est prête", "Vous dites ce que vous faites et pour qui. Studio en tire votre stratégie : à qui parler, quoi dire, où, et comment lancer. Plusieurs façons de faire vous sont proposées, chacune expliquée.", "une direction claire, faite pour votre entreprise."),
        (None, "Vos offres et vos prix", "À qui parler, et à quel prix vendre", "Le designer d’offres vous aide à construire des offres justes, pour vos clients en général ou pour un client en particulier, avec un prix appuyé sur les vraies données de votre métier. Il fera partie du forfait premium.", "vous ne vous bradez plus."),
        ("3-mois", "Un mois de contenu en un clic", "Plus jamais la page blanche", "Articles, publications, carrousels, vidéos, e-mails : Studio prépare le mois entier d’après votre stratégie, dans votre ton. Vous gardez ce qui vous va.", "des heures retrouvées chaque semaine."),
        ("4-calendrier", "Vous validez, Studio publie", "Votre présence tourne sans vous", "Chaque contenu a sa date. Un clic pour valider, et il part à l’heure prévue, même quand vous êtes avec vos clients ou en week-end.", "une régularité que vous n’aviez jamais eue."),
        ("5-tunnels", "Pages et tunnels de vente", "Les visiteurs deviennent des contacts", "Une page qui donne envie, un formulaire, une suite d’e-mails écrits pour votre client idéal : vos visiteurs laissent leurs coordonnées, avec leur accord, et reçoivent la suite d’eux-mêmes.", "des prospects qui arrivent pendant que vous travaillez."),
        ("6-audit", "Analytics et audit Google et IA", "Vous voyez ce qui marche", "Studio audite votre site pour Google et pour les IA, relève vos chiffres, et vous dit en clair ce qui vous amène des clients et ce qui vous en fait perdre.", "des décisions prises sur du concret, pas au hasard."),
        ("7-analytics", "La boucle d’amélioration", "Ça s’améliore chaque semaine", "Mesurer, comprendre, décider, tester : Studio vous propose quoi changer d’après vos vrais résultats. Vous acceptez, il applique.", "une acquisition qui progresse sans effort."),
        ("8-aujourdhui", "Chaque matin, l’essentiel", "Vous reprenez votre rôle de chef d’entreprise", "Ce qu’il y a à faire aujourd’hui, et le temps que ça prend. Le plus souvent, quelques minutes suffisent.", "l’esprit libre pour votre vrai métier."),
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
  <h1 class="rv" style="--d:60ms">Votre agence marketing, <em>rien qu’à vous.</em></h1>
  <p class="lead rv" style="--d:120ms">Studio prépare votre marketing de A à Z, le publie quand vous validez, et l’améliore chaque semaine d’après vos résultats. Pour que les clients qui vous cherchent vous trouvent enfin.</p>
  <div class="btns rv" style="--d:180ms"><a class="btn primary" href="{TRY}">Essayer gratuitement {ARROW}</a><a class="btn ghost" href="#visite" data-tour-start>Lancer la visite</a></div>
  <p class="note rv" style="--d:220ms;margin-top:14px">Bêta le lundi 9 novembre 2026.</p>
</div></section>

<section class="alt" id="visite" style="scroll-margin-top:80px"><div class="wrap">
  <div class="head rv"><p class="eyebrow">La visite</p><h2>Huit étapes, <em>et votre marketing tourne.</em></h2><p class="lead">Voici, écran par écran, ce que Studio fait pour vous.</p></div>
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
{cta_band("Essayez Studio, <em>gratuitement.</em>", "Une journée pour le prendre en main, et votre marketing tourne pour vous.", '<a class="btn ghost" href="' + STUDIO_SITE + '">Le site de Pixapop Studio</a>')}
"""
    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Pixapop Studio", "operatingSystem": "Web",
          "applicationCategory": "BusinessApplication", "inLanguage": "fr", "url": STUDIO_SITE,
          "publisher": {"@type": "Organization", "name": "Pixapop", "url": SITE}}
    return page("/studio/", "Pixapop Studio · Votre agence marketing, rien qu’à vous",
                "La visite de Pixapop Studio : votre stratégie, un mois de contenu en un clic, la publication quand vous validez, les pages et tunnels de vente, l’audit Google et IA, et une amélioration chaque semaine.",
                body, jsonld=ld)


def pilot():
    body = f"""
<section class="hero"><div class="wrap center">
  <p class="eyebrow rv">Pixapop Pilot · bientôt</p>
  <h1 class="rv" style="--d:60ms">Le reste de votre entreprise, <em>piloté avec vous.</em></h1>
  <p class="lead rv" style="--d:120ms">Studio fait venir les clients. Pilot vous aidera à les suivre, à leur faire une proposition au bon prix, et à en trouver de nouveaux. Il est en cours de développement : voici ce que nous préparons.</p>
  <div class="btns rv" style="--d:180ms"><a class="btn pilot" href="/contact/">Être prévenu {ARROW}</a><a class="btn ghost" href="/studio/">Découvrir Studio</a></div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="head rv"><p class="eyebrow">En cours de conception</p><h2>Ce que Pilot <em>vous apportera.</em></h2>
    <p class="lead">Rien n’est encore définitif : les écrans ci-dessous sont des maquettes, et ce qui sortira pourra changer.</p></div>
  <div class="grid g2">
    <div class="rv"><h3>Vos contacts et vos clients</h3><p class="muted">Tous vos prospects et clients au même endroit que votre marketing : d’où ils viennent, où ils en sont, ce qu’il faut faire ensuite.</p>
      <div class="mock pilotmock"><div class="mock-head"><b>Vos contacts</b><span class="tag mock">Maquette</span></div><div class="mock-body">
        <div class="mock-row"><span><b>Camille R.</b><small>Venue par votre article sur le blog</small></span><span class="mock-chip b">À rappeler</span></div>
        <div class="mock-row"><span><b>Julien M.</b><small>A demandé votre guide</small></span><span class="mock-chip o">Devis envoyé</span></div>
        <div class="mock-row"><span><b>Sarah L.</b><small>Recommandée par une cliente</small></span><span class="mock-chip g">Cliente</span></div>
      </div><div class="mock-label">Aperçu, en cours de conception</div></div></div>
    <div class="rv" style="--d:80ms"><h3>Vos devis, au juste prix</h3><p class="muted">Une proposition chiffrée tout de suite, appuyée sur vos offres et sur les prix de votre métier, et même préparée à partir de votre rendez-vous.</p>
      <div class="mock pilotmock"><div class="mock-head"><b>Proposition pour Julien M.</b><span class="tag mock">Maquette</span></div><div class="mock-body">
        <div class="mock-row"><span><b>D’après votre rendez-vous de mardi</b><small>Besoins repris, offre proposée, délais</small></span><span class="mock-chip b">Prête à relire</span></div>
        <div><small class="muted">Votre prix, comparé aux prix de votre métier</small><div class="mock-bar" style="margin-top:8px"><i style="width:62%"></i></div></div>
      </div><div class="mock-label">Aperçu, en cours de conception</div></div></div>
  </div>
  <div class="grid g2" style="margin-top:28px">
    <div class="rv"><h3>La prospection, sans y passer vos soirées</h3><p class="muted">Pilot trouvera des contacts qui correspondent à votre client idéal, et leur enverra pour vous des campagnes d’e-mails soignées, dans le respect des règles.</p>
      <div class="mock pilotmock"><div class="mock-head"><b>Campagne de rentrée</b><span class="tag mock">Maquette</span></div><div class="mock-body">
        <div class="mock-row"><span><b>Cible</b><small>Les profils qui ressemblent à vos meilleurs clients</small></span><span class="mock-chip g">Prête</span></div>
        <div class="mock-row"><span><b>Trois e-mails, sur deux semaines</b><small>Écrits dans votre ton, à valider</small></span><span class="mock-chip b">À relire</span></div>
      </div><div class="mock-label">Aperçu, en cours de conception</div></div></div>
    <div class="card rv" style="--d:80ms;align-self:start"><div class="ico i3">{icon("pilot")}</div><h3>Un seul compte, des outils qui se parlent</h3>
      <p>Pilot partagera tout avec Studio : vos offres, votre stratégie, vos contacts. Ce que l’un apprend, l’autre s’en sert. Vous gardez la main, et la vue d’ensemble.</p>
      <ul class="checks"><li>Pris en main en une journée</li><li>Vous décidez, il exécute</li><li>Vos données en France</li></ul></div>
  </div>
</div></section>
{cta_band("Pilot arrive. <em>Soyez prévenu.</em>", "Écrivez-nous : vous saurez dès qu’il sera prêt à être essayé.", '<a class="btn ghost" href="/contact/">Être prévenu</a>')}
"""
    return page("/pilot/", "Pixapop Pilot · Bientôt : contacts, devis et prospection",
                "Pixapop Pilot, en cours de développement : vos contacts et clients, vos devis au juste prix, la prospection par e-mail, au même endroit que votre marketing.",
                body, body_class="pilot-page")


def sur_mesure():
    site_feats = ["Pages de vente", "Tunnels de vente", "Lettres d’information", "Formulaires de contact", "Pages d’inscription", "Prise de rendez-vous", "Référencement Google et IA", "Rapide sur téléphone"]
    feats = "".join(f"<span>{esc(f)}</span>" for f in site_feats)
    body = f"""
<section class="hero"><div class="wrap center">
  <p class="eyebrow rv">Sites et applications sur mesure</p>
  <h1 class="rv" style="--d:60ms">Un site qui vous ressemble, <em>et qui vend.</em></h1>
  <p class="lead rv" style="--d:120ms">Des sites internet modernes et des applications pensés pour votre métier, avec tout ce qu’il faut pour trouver des clients. Une personnalisation poussée très loin, sans coûter des dizaines de milliers d’euros.</p>
  <div class="btns rv" style="--d:180ms"><a class="btn primary" href="/contact/">Parler de votre projet {ARROW}</a><a class="btn ghost" href="#applications">Les applications</a></div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="grid g2" style="align-items:center">
    <div class="rv"><p class="eyebrow">Sites internet</p><h2>Beau, rapide, <em>et pensé pour votre métier.</em></h2>
      <p class="lead">Un artisan, une coach, un thérapeute, une boutique : chaque métier a ses clients et ses façons de choisir. Votre site est construit pour les vôtres, avec les fonctions qui font venir des demandes.</p>
      <div class="features">{feats}</div></div>
    <div class="card rv" style="--d:80ms"><div class="ico i2">{icon("price")}</div><h3>Un tarif accessible</h3>
      <p>Les prix d’un freelance ou d’une petite agence, souvent moins quand vous utilisez aussi nos outils. Pour quelqu’un qui démarre avec un petit budget comme pour une entreprise installée.</p>
      <p class="note" style="margin-top:12px">Sur devis, en attendant nos offres de création de site.</p>
      <a class="more" href="/contact/">Demander un devis {ARROW}</a></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="head rv"><p class="eyebrow">Comment nous travaillons</p><h2>De votre idée <em>à votre premier client.</em></h2></div>
  <ol class="steps">
    <li class="card rv"><h3>Écouter</h3><p>Votre métier, vos clients, ce que le site ou l’application doit changer pour vous.</p></li>
    <li class="card rv" style="--d:70ms"><h3>Dessiner</h3><p>Une première version à regarder sur votre téléphone, pour décider sur du concret.</p></li>
    <li class="card rv" style="--d:140ms"><h3>Construire</h3><p>Les pages, les formulaires, les tunnels, les e-mails, et pour une application la publication sur les stores.</p></li>
    <li class="card rv" style="--d:210ms"><h3>Faire grandir</h3><p>Les résultats mesurés, les améliorations, et Studio pour faire venir les visiteurs.</p></li>
  </ol>
</div></section>

<section class="alt" id="applications" style="scroll-margin-top:80px"><div class="wrap case">
  <div class="rv"><p class="eyebrow">Applications mobiles</p><h2>Nouveau Cap, <em>une application conçue, développée et publiée par Pixapop.</em></h2>
    <p class="lead">Pour les cadres de plus de 40 ans qui changent de métier : un plan de 90 jours, les finances sous contrôle, un CV et un profil LinkedIn repensés, et un Copilote IA qui connaît leur parcours.</p>
    <ul class="checks"><li>Conception : le parcours, les écrans, les textes</li><li>Développement : l’application, le serveur, l’IA, les abonnements</li><li>Publication sur Google Play, avec les pages légales et la fiche du store</li></ul>
    <div class="btns" style="margin-top:24px"><a class="btn ghost" href="/nouveau-cap/">Voir Nouveau Cap {ARROW}</a><a class="btn primary" href="/contact/">Votre application</a></div></div>
  <div class="phones rv" style="--d:100ms" aria-hidden="true">{phone("pistes", "Écran Pistes de Nouveau Cap")}{phone("home", "Écran d’accueil de Nouveau Cap")}{phone("finances", "Écran Finances de Nouveau Cap")}</div>
</div></section>
{cta_band("Votre projet, <em>parlons-en.</em>", "Décrivez-le en quelques lignes : à qui il s’adresse, ce qu’il doit changer. Nous vous répondons personnellement.", '<a class="btn ghost" href="/contact/">Nous écrire</a>')}
"""
    return page("/sur-mesure/", "Sites internet et applications sur mesure · Pixapop",
                "Des sites internet modernes et des applications pensés pour votre métier, avec pages de vente, tunnels, lettres d’information et formulaires, à un tarif accessible. Exemple : Nouveau Cap.",
                body)


def a_propos():
    body = f"""
<section class="hero"><div class="wrap narrow center">
  <p class="eyebrow rv">À propos</p>
  <h1 class="rv" style="--d:60ms">Des outils nés <em>d’un vrai besoin.</em></h1>
  <p class="lead rv" style="--d:120ms">Pixapop n’a pas commencé comme une entreprise de logiciels. Elle a commencé comme une réponse à un problème que vivent presque tous les solopreneurs.</p>
</div></section>

<section class="alt"><div class="wrap narrow">
  <div class="rv">
    <h2>Dix ans <em>seul aux commandes</em></h2>
    <p class="lead">Pixapop a été créée par Cyril Gayet, solopreneur depuis dix ans. Trois entreprises, des réussites et des échecs, et beaucoup d’entrepreneurs accompagnés en chemin, notamment dans la formation.</p>
    <p>Avec le recul, les échecs avaient souvent la même origine. Le métier était là, les clients satisfaits aussi. Ce qui manquait, c’était tout le reste : se faire connaître, tenir une présence régulière, savoir ce qui marche, trouver les clients suivants. Et pour ça, une compétence marketing qui n’était pas le cœur du métier.</p>
  </div>
  <div class="rv" style="margin-top:36px">
    <h2>La tâche <em>qu’on repousse toujours</em></h2>
    <p>Quand on aime son métier, on s’y consacre. Les tâches qui plaisent moins glissent au lendemain, puis à la semaine suivante, puis ne se font pas. Pas de régularité sur les réseaux, des stratégies jamais menées jusqu’au bout. Ce n’est pas un manque de talent ni de sérieux : c’est un manque de bras.</p>
    <p>Les outils existants ne répondaient pas à ce besoin : trop complexes, trop chers, ou faits pour des équipes entières. Alors les premiers outils de Pixapop ont été construits pour un usage personnel : une équipe qui exécute, pendant que l’entrepreneur reprend son vrai rôle, décider et valider.</p>
  </div>
  <div class="rv" style="margin-top:36px">
    <h2>Ce qui servait à un seul <em>peut servir à tous</em></h2>
    <p>Aujourd’hui, l’intelligence artificielle décuple ce qu’un solopreneur peut accomplir. Pixapop la met à votre service, au meilleur niveau, sans que vous ayez à la maîtriser : une stratégie conçue pour vous, des contenus qui partent à l’heure, des résultats mesurés, et une amélioration continue. Le tout pour un investissement modeste, et un retour qui le dépasse largement.</p>
    <p>Nous ne vendons pas des outils. Nous vendons des solutions aux problèmes que nous avons vécus, et que vous vivez peut-être en ce moment.</p>
  </div>
</div></section>

<section><div class="wrap">
  <div class="head center rv"><h2>Ce que nous <em>défendons</em></h2></div>
  <div class="grid g4">
    <article class="card rv"><div class="ico i2">{icon("clock")}</div><h3>La simplicité</h3><p>Des outils pris en main en une journée, et quelques minutes par jour ensuite.</p></article>
    <article class="card rv" style="--d:70ms"><div class="ico i1">{icon("heart")}</div><h3>La transparence</h3><p>Rien ne part sans votre accord, et chaque proposition dit pourquoi.</p></article>
    <article class="card rv" style="--d:140ms"><div class="ico i3">{icon("shield")}</div><h3>Vos données chez vous</h3><p>Hébergées en France, séparées de celles des autres, jamais revendues.</p></article>
    <article class="card rv" style="--d:210ms"><div class="ico i4">{icon("target")}</div><h3>Des résultats</h3><p>Un outil n’a de valeur que s’il vous ramène des clients. C’est notre mesure.</p></article>
  </div>
</div></section>
{cta_band("Faisons connaissance.", "Une question, un projet, ou simplement l’envie d’en savoir plus : écrivez-nous.")}
"""
    return page("/a-propos/", "À propos · L’histoire de Pixapop",
                "L’histoire de Pixapop : dix ans de vie de solopreneur, des outils créés d’abord pour un besoin personnel, puis mis au service de tous les solopreneurs.",
                body)


def contact():
    body = f"""
<section class="hero"><div class="wrap narrow center">
  <p class="eyebrow rv">Contact</p>
  <h1 class="rv" style="--d:60ms">Écrivez-nous, <em>on vous répond.</em></h1>
  <p class="lead rv" style="--d:120ms">Personnellement, et rapidement.</p>
</div></section>
<section style="padding-top:0"><div class="wrap">
  <div class="grid g2">
    <article class="card rv"><div class="ico i2">{icon("site")}</div><h3>Un projet de site ou d’application</h3>
      <p>Dites-nous à qui il s’adresse et ce qu’il doit changer pour vous.</p>
      <p class="mail" style="margin-top:16px"><a href="mailto:{PROJECT_EMAIL}?subject=Projet">{PROJECT_EMAIL}</a></p></article>
    <article class="card rv" style="--d:80ms"><div class="ico i3">{icon("mail")}</div><h3>Studio, Pilot, une question</h3>
      <p>Pour essayer nos outils, être prévenu de Pilot, ou toute autre question.</p>
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
