(function() {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function dkey(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function parse(ds) { var p = ds.split('-').map(Number); return new Date(p[0], p[1] - 1, p[2]); }
  function dayDiff(a, b) { return Math.round((b - a) / 86400000); }

  // ---------------- hero stats ----------------
  var svg = document.getElementById('tlSvg');
  var start = parse(svg.dataset.start), total = parseInt(svg.dataset.days, 10), px = parseInt(svg.dataset.px, 10);
  var now = new Date(), today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  var bands = Array.prototype.slice.call(svg.querySelectorAll('.tl-band'));

  function countUp(el, to, suffix) {
    suffix = suffix || '';
    if (reduce || to <= 0) { el.textContent = to + suffix; return; }
    var t0 = null, dur = 900;
    function step(ts) {
      if (t0 === null) t0 = ts;
      var p = Math.min(1, (ts - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(to * e) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  function heroStats() {
    var offset = dayDiff(start, today);
    var a = document.getElementById('cmdDay'), al = document.getElementById('cmdDayLbl'), as = document.getElementById('cmdDaySub');
    var bar = document.getElementById('cmdBar');
    if (offset < 0) {
      countUp(a, -offset); al.textContent = 'Days to start'; as.textContent = 'Opens ' + start.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      bar.style.width = '0%';
    } else if (offset >= total) {
      a.textContent = total; al.textContent = 'Term complete'; as.textContent = 'All ' + total + ' days'; bar.style.width = '100%';
    } else {
      countUp(a, offset + 1); al.textContent = 'Day of ' + total; as.textContent = (total - offset - 1) + ' days remain';
      setTimeout(function() { bar.style.width = Math.round((offset + 1) / total * 100) + '%'; }, 120);
    }
    // current / next case
    var cur = null, nxt = null;
    bands.forEach(function(b) {
      var s = parse(b.dataset.start), e = parse(b.dataset.end);
      if (today >= s && today <= e) cur = b;
      else if (today < s && !nxt) nxt = b;
    });
    var cb = cur || nxt, cv = document.getElementById('cmdCase'), cl = document.getElementById('cmdCaseLbl'), cs = document.getElementById('cmdCaseSub');
    if (cb) {
      cv.textContent = cb.dataset.code.replace('Case ', '');
      cl.textContent = cur ? 'Current case' : 'Next case';
      cs.textContent = cb.dataset.title;
    } else { cv.textContent = '—'; cl.textContent = 'Case'; cs.textContent = 'No active case'; }
    // essay
    var issue = new Date('2027-02-25T08:30:00'), due = new Date('2027-02-26T08:30:00');
    var ev = document.getElementById('cmdEssay'), el = document.getElementById('cmdEssayLbl'), es = document.getElementById('cmdEssaySub');
    var target = now < issue ? issue : (now < due ? due : null);
    if (target) {
      var days = Math.max(0, Math.ceil((target - now) / 86400000));
      countUp(ev, days); el.textContent = now < issue ? 'Days to essay' : 'Days to return'; es.textContent = now < issue ? 'Distributed 25 Feb' : 'Due 26 Feb';
    } else { ev.textContent = '✓'; el.textContent = 'Essay'; es.textContent = 'Window closed'; }
  }

  // ---------------- timeline ----------------
  var scroller = document.getElementById('tlScroll'), baseW = svg.viewBox.baseVal.width, baseH = svg.viewBox.baseVal.height, zoom = 1;
  function setZoom(z) {
    var center = (scroller.scrollLeft + scroller.clientWidth / 2) / zoom;
    zoom = Math.max(0.55, Math.min(2.6, z));
    svg.setAttribute('width', Math.round(baseW * zoom)); svg.setAttribute('height', Math.round(baseH * zoom));
    scroller.scrollLeft = center * zoom - scroller.clientWidth / 2;
  }
  function placeNeedle() {
    var needle = document.getElementById('tlNeedle'), off = dayDiff(start, today);
    if (off < 0 || off >= total) { needle.setAttribute('display', 'none'); return; }
    needle.removeAttribute('display');
    needle.setAttribute('transform', 'translate(' + (off * px + px / 2) + ' 0)');
  }
  function toToday(smooth) {
    var off = dayDiff(start, today);
    var x = Math.max(0, Math.min(total - 1, off < 0 ? 0 : off)) * px * zoom;
    scroller.scrollTo({ left: x - scroller.clientWidth / 2, behavior: smooth && !reduce ? 'smooth' : 'auto' });
  }
  document.querySelector('.tl-zoom').addEventListener('click', function(e) {
    var b = e.target.closest('[data-tl]'); if (!b) return;
    if (b.dataset.tl === 'in') setZoom(zoom * 1.3);
    else if (b.dataset.tl === 'out') setZoom(zoom / 1.3);
    else toToday(true);
  });
  svg.addEventListener('keydown', function(e) {
    if ((e.key === 'Enter' || e.key === ' ') && e.target.closest('[data-jump-session],[data-jump-date]')) { e.preventDefault(); e.target.closest('[data-jump-session],[data-jump-date]').dispatchEvent(new MouseEvent('click', { bubbles: true })); }
  });
  // mouse drag-to-pan (touch keeps native scrolling)
  (function() {
    var down = false, x0 = 0, s0 = 0, moved = false;
    scroller.addEventListener('pointerdown', function(e) { if (e.pointerType !== 'mouse') return; down = true; moved = false; x0 = e.clientX; s0 = scroller.scrollLeft; });
    window.addEventListener('pointermove', function(e) {
      if (!down) return;
      var dx = e.clientX - x0;
      if (Math.abs(dx) > 4) { moved = true; scroller.classList.add('drag'); }
      scroller.scrollLeft = s0 - dx;
    });
    window.addEventListener('pointerup', function() { down = false; scroller.classList.remove('drag'); });
    scroller.addEventListener('click', function(e) { if (moved) { e.stopPropagation(); e.preventDefault(); moved = false; } }, true);
  })();

  // ---------------- compass spin on scroll ----------------
  var compass = document.querySelector('.cmd-compass'), ticking = false;
  if (compass && !reduce) {
    window.addEventListener('scroll', function() {
      if (ticking) return; ticking = true;
      requestAnimationFrame(function() { compass.style.setProperty('--rot', (window.scrollY * 0.06) + 'deg'); ticking = false; });
    }, { passive: true });
  }

  // ---------------- reveal on scroll ----------------
  function initReveal() {
    var els = document.querySelectorAll('#calAgenda > .session-card, .timeline, .ref-section');
    if (reduce || !('IntersectionObserver' in window)) return;
    document.documentElement.classList.add('js-reveal');
    var io = new IntersectionObserver(function(entries) {
      entries.forEach(function(en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    els.forEach(function(el) { el.classList.add('reveal'); io.observe(el); });
    setTimeout(function() { els.forEach(function(el) { el.classList.add('in'); }); }, 4000);
  }

  heroStats(); placeNeedle(); toToday(false); initReveal();
})();
