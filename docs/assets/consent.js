// Pixapop: Google Analytics only with the visitor's consent (Cyril, 07/10/2026). Shared by pixapop.fr and studio.pixapop.fr
// (same file in both repositories, keep them identical). One purpose only, audience measurement, no advertising.
// Nothing from Google is loaded before « Accepter »; « Refuser » is as easy; the choice is kept 6 months in a first-party
// cookie on .pixapop.fr (so one choice covers the site and its sub-domains) and can be changed at any time with any element
// carrying data-consent-open (the « Cookies » link). Refusing after accepting removes Google Analytics cookies.
(function () {
  var ID = 'G-2SN8Q7DH7M', KEY = 'pxp_consent', SIX_MONTHS = 183 * 24 * 3600;
  var host = location.hostname, root = /(^|\.)pixapop\.fr$/.test(host) ? '; domain=.pixapop.fr' : '';
  if (!/(^|\.)pixapop\.fr$/.test(host)) return;   // never on another address (a preview, a reseller's Studio)
  function read() { var m = document.cookie.match(new RegExp('(?:^|; )' + KEY + '=([01])')); return m ? m[1] : null; }
  function write(v) { document.cookie = KEY + '=' + v + '; max-age=' + SIX_MONTHS + '; path=/' + root + '; SameSite=Lax' + (location.protocol === 'https:' ? '; Secure' : ''); }
  function clearGa() {
    document.cookie.split('; ').forEach(function (c) {
      var n = c.split('=')[0];
      if (/^_ga(_|$)/.test(n)) ['', '; domain=.pixapop.fr', '; domain=' + host].forEach(function (d) { document.cookie = n + '=; max-age=0; path=/' + d; });
    });
  }
  var loaded = false;
  function load() {
    if (loaded) return; loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
    window.gtag('js', new Date());
    window.gtag('config', ID, { allow_google_signals: false, allow_ad_personalization_signals: false, cookie_expires: 390 * 24 * 3600 });   // 13 months at most (CNIL)
    var s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + ID;
    document.head.appendChild(s);
  }
  function close() { var b = document.getElementById('px-consent'); if (b) b.remove(); }
  function choose(v) {
    write(v); close();
    if (v === '1') load();
    else { if (loaded) window['ga-disable-' + ID] = true; clearGa(); }
  }
  function show() {
    close();
    var b = document.createElement('div');
    b.id = 'px-consent'; b.className = 'px-consent'; b.setAttribute('role', 'region'); b.setAttribute('aria-label', 'Cookies');
    b.innerHTML = '<div class="px-consent-in"><p><b>Vos cookies, votre choix</b><span>Nous mesurons l’audience du site avec Google Analytics, sans aucune publicité. ' +
      'Rien n’est déposé sans votre accord. <a href="https://www.pixapop.fr/confidentialite/">Confidentialité</a></span></p>' +
      '<div class="px-consent-b"><button type="button" data-consent="0">Refuser</button><button type="button" data-consent="1">Accepter</button></div></div>';
    document.body.appendChild(b);
    b.addEventListener('click', function (e) { var t = e.target.closest('[data-consent]'); if (t) choose(t.getAttribute('data-consent')); });
  }
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-consent-open]');
    if (t) { e.preventDefault(); show(); }
  });
  window.pixapopConsent = { open: show, state: read };
  var start = function () { var v = read(); if (v === '1') load(); else if (v == null) show(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
