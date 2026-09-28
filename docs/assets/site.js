// Pixapop micro-interactions: pixels of light, reveal on scroll, light under the pointer, phones that tilt.
// Everything stays readable without it, and motion stops for people who ask for less.
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Reveal on scroll. Blocks stay visible unless the observer reports them below the screen,
  // so a preview, a screenshot or a browser without the observer always shows the whole page.
  var items = [].slice.call(document.querySelectorAll('.rv')).filter(function (el) { return !el.closest('.hero'); });
  var show = function (el) { el.classList.remove('wait'); };
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var el = e.target;
        if (e.isIntersecting) { requestAnimationFrame(function () { show(el); }); io.unobserve(el); }
        else if (!el.hasAttribute('data-seen') && e.boundingClientRect.top > 0) el.classList.add('wait');
        el.setAttribute('data-seen', '');
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
    // Safety nets: a block already on screen is shown on scroll, and nothing stays hidden for long.
    addEventListener('scroll', function () {
      items.forEach(function (el) { if (el.classList.contains('wait') && el.getBoundingClientRect().top < innerHeight) show(el); });
    }, { passive: true });
    setTimeout(function () { items.forEach(show); }, 6000);
  }

  // Light that follows the pointer on glass cards.
  document.querySelectorAll('.glass.lit').forEach(function (el) {
    el.addEventListener('pointermove', function (ev) {
      var r = el.getBoundingClientRect();
      el.style.setProperty('--mx', (ev.clientX - r.left) + 'px');
      el.style.setProperty('--my', (ev.clientY - r.top) + 'px');
    });
  });

  // Phones in the case study lean gently as the page scrolls.
  var tilt = document.querySelector('[data-tilt]');
  if (tilt && !reduce) {
    var onScroll = function () {
      var r = tilt.getBoundingClientRect();
      var p = Math.max(-1, Math.min(1, (r.top + r.height / 2 - innerHeight / 2) / innerHeight));
      tilt.style.transform = 'perspective(1200px) rotateX(' + (p * 6).toFixed(2) + 'deg) translateY(' + (p * 24).toFixed(1) + 'px)';
    };
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // Pixels of light rising in the hero.
  var canvas = document.querySelector('canvas[data-pixels]');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var colors = ['#FF4F8B', '#8B6CFF', '#FF8A3D', '#3EE6C1', '#FFC857', '#FFFFFF'];
  var dots = [], w = 0, h = 0, dpr = Math.min(2, window.devicePixelRatio || 1), mx = 0, my = 0, running = true;
  function size() {
    var r = canvas.getBoundingClientRect();
    w = r.width; h = r.height;
    canvas.width = w * dpr; canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var n = Math.round(Math.min(90, (w * h) / 16000));
    dots = [];
    for (var i = 0; i < n; i++) dots.push(make(true));
  }
  function make(anywhere) {
    return {
      x: Math.random() * w, y: anywhere ? Math.random() * h : h + 10,
      s: 2 + Math.random() * 4, v: 0.12 + Math.random() * 0.35, z: 0.3 + Math.random() * 0.7,
      c: colors[(Math.random() * colors.length) | 0], t: Math.random() * Math.PI * 2
    };
  }
  function frame() {
    if (!running) return;
    ctx.clearRect(0, 0, w, h);
    for (var i = 0; i < dots.length; i++) {
      var d = dots[i];
      d.y -= d.v; d.t += 0.02;
      if (d.y < -10) dots[i] = d = make(false);
      var a = (0.35 + 0.45 * Math.sin(d.t)) * d.z * Math.min(1, d.y / (h * 0.25));
      var x = d.x + mx * 14 * d.z, y = d.y + my * 10 * d.z;
      ctx.globalAlpha = Math.max(0, a);
      ctx.shadowColor = d.c; ctx.shadowBlur = 12 * d.z;
      ctx.fillStyle = d.c;
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(x, y, d.s, d.s, d.s / 3); else ctx.rect(x, y, d.s, d.s);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
    requestAnimationFrame(frame);
  }
  size();
  addEventListener('resize', size);
  addEventListener('pointermove', function (ev) { mx = ev.clientX / innerWidth - 0.5; my = ev.clientY / innerHeight - 0.5; }, { passive: true });
  if (reduce) { running = true; frame(); running = false; return; }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) { var was = running; running = e[0].isIntersecting; if (running && !was) frame(); }).observe(canvas);
  }
  document.addEventListener('visibilitychange', function () { var was = running; running = !document.hidden; if (running && !was) frame(); });
  frame();
})();
