// pixapop.fr (refonte du 10/10/2026) : light or dark theme (light by default, the choice is remembered), the mobile menu, blocks
// that appear gently when they come into view, and the guided tour of Studio. Everything stays readable without this script.
(function () {
  'use strict';
  var root = document.documentElement;

  // Theme : always light unless the visitor chose dark on this site.
  var btn = document.querySelector('[data-theme-toggle]');
  if (btn) btn.addEventListener('click', function () {
    var dark = root.getAttribute('data-theme') !== 'dark';
    if (dark) root.setAttribute('data-theme', 'dark'); else root.removeAttribute('data-theme');
    btn.setAttribute('aria-pressed', String(dark));
    try { localStorage.setItem('pxp_theme', dark ? 'dark' : 'light'); } catch (e) {}
  });

  // Mobile menu.
  var menu = document.querySelector('[data-menu]'), nav = document.querySelector('.nav');
  if (menu && nav) menu.addEventListener('click', function () {
    var open = !nav.classList.contains('open');
    nav.classList.toggle('open', open); menu.setAttribute('aria-expanded', String(open));
  });

  // Reveal : a block starts hidden only if the browser confirms it is below the screen ; it appears when it comes into view.
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!still && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.remove('pre'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    Array.prototype.forEach.call(document.querySelectorAll('.rv'), function (el) {
      if (el.getBoundingClientRect().top > window.innerHeight) { el.classList.add('pre'); io.observe(el); }
    });
  }

  // Guided tour of Studio : one step at a time, with a progress bar, dots, previous / next and the arrow keys.
  var tour = document.querySelector('[data-tour]');
  if (tour) {
    var steps = tour.querySelectorAll('.step'), dots = tour.querySelector('.tour-dots'), bar = tour.querySelector('.tour-progress i'),
      count = tour.querySelector('.tour-count'), prev = tour.querySelector('[data-prev]'), next = tour.querySelector('[data-next]'), cur = 0;
    tour.classList.add('on');
    Array.prototype.forEach.call(steps, function (s, i) {
      var d = document.createElement('button'); d.type = 'button'; d.setAttribute('aria-label', 'Étape ' + (i + 1));
      d.addEventListener('click', function () { show(i); }); dots.appendChild(d);
    });
    function show(i) {
      cur = Math.max(0, Math.min(steps.length - 1, i));
      Array.prototype.forEach.call(steps, function (s, k) { s.classList.toggle('cur', k === cur); });
      Array.prototype.forEach.call(dots.children, function (d, k) { d.setAttribute('aria-current', String(k === cur)); });
      bar.style.width = ((cur + 1) / steps.length * 100) + '%';
      count.textContent = 'Étape ' + (cur + 1) + ' sur ' + steps.length;
      prev.disabled = cur === 0;
      next.textContent = cur === steps.length - 1 ? 'Revoir depuis le début' : 'Étape suivante';
    }
    prev.addEventListener('click', function () { show(cur - 1); });
    next.addEventListener('click', function () { show(cur === steps.length - 1 ? 0 : cur + 1); });
    tour.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { show(cur + 1); } else if (e.key === 'ArrowLeft') { show(cur - 1); }
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-tour-start]'), function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault(); show(0);
        tour.scrollIntoView({ behavior: still ? 'auto' : 'smooth', block: 'start' });
        setTimeout(function () { next.focus({ preventScroll: true }); }, still ? 0 : 500);
      });
    });
    show(0);
  }
})();
// Pixapop motion (Cyril, 10/10/2026 : « des petites animations sympas, comme un site web moderne », the same on every site we
// make) : pixels of light rising slowly in the hero with a soft glow behind, a light that follows the pointer on the cards, and
// the title that rises gently when the page opens. Everything stays readable without it, and stops for people who ask for less.
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var root = document.documentElement;
  document.addEventListener('pointermove', function (ev) {
    var el = ev.target.closest && ev.target.closest('[data-lit]');
    if (!el) return;
    var r = el.getBoundingClientRect();
    el.style.setProperty('--mx', (ev.clientX - r.left) + 'px'); el.style.setProperty('--my', (ev.clientY - r.top) + 'px');
  }, { passive: true });
  Array.prototype.forEach.call(document.querySelectorAll('.card, .st-feat, .st-steps li, .st-card a, .st-plan, .loop li, .mock'), function (el) { el.setAttribute('data-lit', ''); });

  var hero = document.querySelector('.hero, .st-hero');
  if (!hero) return;
  hero.classList.add('px-hero');
  var canvas = document.createElement('canvas');
  canvas.className = 'px-field'; canvas.setAttribute('aria-hidden', 'true');
  hero.insertBefore(canvas, hero.firstChild);
  var ctx = canvas.getContext('2d');
  var dark = function () { return root.getAttribute('data-theme') === 'dark'; };
  var colors = ['#FF4F8B', '#8B6CFF', '#F2A541', '#2BB5A0', '#5B8DEF', '#E0559A', '#FFC857'];
  var dots = [], w = 0, h = 0, dpr = Math.min(2, window.devicePixelRatio || 1), mx = 0, my = 0, running = true;
  function make(anywhere) {
    return { x: Math.random() * w, y: anywhere ? Math.random() * h : h + 10, s: 3 + Math.random() * 5, v: 0.12 + Math.random() * 0.32,
      z: 0.35 + Math.random() * 0.65, c: colors[(Math.random() * colors.length) | 0], t: Math.random() * Math.PI * 2 };
  }
  function size() {
    var r = canvas.getBoundingClientRect(); w = r.width; h = r.height;
    canvas.width = w * dpr; canvas.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var n = Math.round(Math.min(80, (w * h) / 15000)); dots = [];
    for (var i = 0; i < n; i++) dots.push(make(true));
  }
  function frame() {
    if (!running) return;
    ctx.clearRect(0, 0, w, h);
    var k = dark() ? 1 : 0.85;
    for (var i = 0; i < dots.length; i++) {
      var d = dots[i];
      if (!reduce) { d.y -= d.v; d.t += 0.02; }
      if (d.y < -10) dots[i] = d = make(false);
      var a = (0.35 + 0.45 * Math.sin(d.t)) * d.z * Math.min(1, d.y / (h * 0.25)) * k;
      var x = d.x + mx * 14 * d.z, y = d.y + my * 10 * d.z;
      ctx.globalAlpha = Math.max(0, a); ctx.shadowColor = d.c; ctx.shadowBlur = (dark() ? 14 : 10) * d.z; ctx.fillStyle = d.c;
      ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y, d.s, d.s, d.s / 3); else ctx.rect(x, y, d.s, d.s); ctx.fill();
    }
    ctx.globalAlpha = 1;
    if (!reduce) requestAnimationFrame(frame);
  }
  size(); addEventListener('resize', size);
  addEventListener('pointermove', function (ev) { mx = ev.clientX / innerWidth - 0.5; my = ev.clientY / innerHeight - 0.5; }, { passive: true });
  if (reduce) { frame(); return; }
  if ('IntersectionObserver' in window) new IntersectionObserver(function (e) { var was = running; running = e[0].isIntersecting; if (running && !was) frame(); }).observe(canvas);
  document.addEventListener('visibilitychange', function () { var was = running; running = !document.hidden; if (running && !was) frame(); });
  frame();
})();
// Light theme (Cyril, 10/10/2026 : the mosaic, « moins de carrés, laisse de l'espace ») : a few pastel squares on a grid, mostly
// towards the edges, nothing behind the title, lighting up slowly in a wave like the Pixapop logo. The dark theme keeps the pixels.
(function () {
  'use strict';
  var root = document.documentElement, hero = document.querySelector('.px-hero');
  if (!hero) return;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var c = document.createElement('canvas'); c.className = 'px-mosaic'; c.setAttribute('aria-hidden', 'true');
  hero.insertBefore(c, hero.firstChild);
  var x = c.getContext('2d'), dpr = Math.min(2, window.devicePixelRatio || 1), w = 0, h = 0, cells = [], running = true;
  var cols = ['#FF4F8B', '#8B6CFF', '#F2A541', '#2BB5A0', '#5B8DEF', '#FFC43A'], S = 18, G = 14;
  function size() {
    var r = c.getBoundingClientRect(); w = r.width; h = r.height; c.width = w * dpr; c.height = h * dpr; x.setTransform(dpr, 0, 0, dpr, 0, 0); cells = [];
    var cx = w / 2, cy = Math.min(h, 640) * 0.42;
    for (var yy = 10; yy < Math.min(h, 760); yy += S + G) for (var xx = 10; xx < w; xx += S + G) {
      var d = Math.hypot((xx - cx) / (w * 0.5), (yy - cy) / 380);
      if (d < 0.62 || Math.random() > 0.16 * Math.min(1, (d - 0.55) * 2.2)) continue;
      cells.push({ x: xx, y: yy, c: cols[(Math.random() * cols.length) | 0], p: Math.random() * 6.28, d: d });
    }
  }
  function frame(t) {
    if (!running) return;
    x.clearRect(0, 0, w, h);
    if (root.getAttribute('data-theme') !== 'dark') cells.forEach(function (k) {
      var wave = Math.max(0, Math.sin((t || 0) / 1300 - k.d * 4 + k.p * 0.3)), a = 0.10 + 0.32 * Math.pow(wave, 3);
      x.globalAlpha = a; x.fillStyle = k.c; x.beginPath(); if (x.roundRect) x.roundRect(k.x, k.y, S, S, 5); else x.rect(k.x, k.y, S, S); x.fill();
    });
    x.globalAlpha = 1;
    if (!reduce) requestAnimationFrame(frame);
  }
  size(); addEventListener('resize', size);
  if ('IntersectionObserver' in window) new IntersectionObserver(function (e) { var was = running; running = e[0].isIntersecting; if (running && !was) requestAnimationFrame(frame); }).observe(c);
  requestAnimationFrame(frame);
})();
