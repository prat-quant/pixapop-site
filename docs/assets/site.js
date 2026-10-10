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
