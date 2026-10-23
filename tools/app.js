(function() {
  'use strict';

  var THEME_KEY = 'spTheme', READ_KEY = 'spReadState', SEM_KEY = 'spSeminar';

  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } }
  function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function escapeHtml(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function escapeRegExp(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  function debounce(fn, wait) { var t; return function() { clearTimeout(t); t = setTimeout(fn, wait); }; }

  // ---------------- theme ----------------
  function applyTheme(theme) {
    if (theme === 'dark' || theme === 'light') document.documentElement.setAttribute('data-theme', theme);
    else document.documentElement.removeAttribute('data-theme');
  }
  function toggleTheme() {
    var current = document.documentElement.getAttribute('data-theme');
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    var next = !current ? (prefersDark ? 'light' : 'dark') : (current === 'dark' ? 'light' : 'dark');
    store(THEME_KEY, next);
    applyTheme(next);
  }
  applyTheme(load(THEME_KEY));

  // ---------------- seminar parity ----------------
  function applySeminar(v) {
    document.body.setAttribute('data-sem', v === 'even' || v === 'odd' ? v : 'both');
  }
  (function() {
    var sel = document.getElementById('semPick');
    var saved = load(SEM_KEY) || 'both';
    sel.value = saved;
    applySeminar(saved);
    sel.addEventListener('change', function() {
      store(SEM_KEY, sel.value);
      applySeminar(sel.value);
      refreshTodayAndNextUp();
    });
  })();

  // ---------------- reading checkboxes ----------------
  function loadReadState() { try { return JSON.parse(load(READ_KEY)) || {}; } catch (e) { return {}; } }
  function initReadingCheckboxes() {
    var state = loadReadState();
    document.querySelectorAll('.read-checkbox').forEach(function(cb) {
      var id = cb.dataset.readId, li = cb.closest('li');
      if (state[id]) { cb.checked = true; if (li) li.classList.add('is-read'); }
      cb.addEventListener('change', function() {
        var s = loadReadState();
        if (cb.checked) s[id] = true; else delete s[id];
        store(READ_KEY, JSON.stringify(s));
        if (li) li.classList.toggle('is-read', cb.checked);
      });
    });
  }

  // ---------------- search ----------------
  var searchIndex = [];
  function buildSearchIndex() {
    searchIndex = Array.prototype.map.call(document.querySelectorAll('.session-card'), function(card) {
      return { card: card, code: card.dataset.code, text: card.textContent.toLowerCase() };
    });
  }
  function clearHighlights() {
    document.querySelectorAll('mark.search-hl').forEach(function(mark) {
      var parent = mark.parentNode;
      if (!parent) return;
      while (mark.firstChild) parent.insertBefore(mark.firstChild, mark);
      parent.removeChild(mark);
      parent.normalize();
    });
  }
  function highlightTerms(root, terms) {
    var src = terms.map(escapeRegExp).join('|');
    var testRe = new RegExp(src, 'i'), globalRe = new RegExp(src, 'gi');
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function(node) {
        var p = node.parentNode;
        if (!p || p.nodeName === 'SCRIPT' || p.nodeName === 'STYLE') return NodeFilter.FILTER_REJECT;
        return testRe.test(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    var nodes = [], n;
    while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(function(node) {
      var text = node.nodeValue, frag = document.createDocumentFragment(), last = 0, m;
      globalRe.lastIndex = 0;
      while ((m = globalRe.exec(text))) {
        if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
        var mark = document.createElement('mark');
        mark.className = 'search-hl';
        mark.textContent = m[0];
        frag.appendChild(mark);
        last = globalRe.lastIndex;
      }
      if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
      node.parentNode.replaceChild(frag, node);
    });
  }
  // While searching, hide everything in the calendar except matching case cards
  // and their "Open case" buttons; hide days/months left empty.
  function filterCalendarNoise(terms) {
    document.querySelectorAll('.cal-day-items > *').forEach(function(item) {
      
      item.style.display = terms.length ? 'none' : '';
    });
    var header = null, has = new Map();
    document.querySelectorAll('#calAgenda > *').forEach(function(el) {
      if (el.classList.contains('cal-month-header')) { header = el; has.set(el, false); return; }
      if (!el.classList.contains('cal-day')) return;
      var box = el.querySelector('.cal-day-items');
      var vis = !terms.length || Array.prototype.some.call(box.children, function(c) { return c.style.display !== 'none'; });
      el.style.display = vis ? '' : 'none';
      if (vis && header) has.set(header, true);
    });
    has.forEach(function(v, h) { h.style.display = (!terms.length || v) ? '' : 'none'; });
  }
  function filterSessions() {
    var q = document.getElementById('searchBox').value.trim().toLowerCase();
    var terms = q ? q.split(/\s+/).filter(Boolean) : [];
    var visible = {}, count = 0;
    clearHighlights();
    searchIndex.forEach(function(e) {
      var match = !terms.length || terms.every(function(t) { return e.text.indexOf(t) !== -1; });
      e.card.style.display = match ? '' : 'none';
      if (match) {
        count++; visible[e.code] = true;
        if (terms.length) {
          e.card.open = true;
          e.card.querySelectorAll('.q-collapse').forEach(function(q) { if (terms.some(function(t) { return q.textContent.toLowerCase().indexOf(t) !== -1; })) q.open = true; });
          highlightTerms(e.card, terms);
        }
      }
    });
    document.querySelectorAll('.between-cases').forEach(function(el) { el.style.display = terms.length ? 'none' : ''; });
    filterCalendarNoise(terms);
    document.getElementById('searchClearBtn').style.display = q ? 'flex' : 'none';
    updateNavState();
    document.getElementById('noResults').style.display = (terms.length && !count) ? 'block' : 'none';
    var status = document.getElementById('searchStatus');
    if (terms.length && count) { status.textContent = count + ' of ' + searchIndex.length + ' cases match'; status.style.display = 'block'; }
    else status.style.display = 'none';
  }
  function expandAll() { document.querySelectorAll('.session-card, .q-collapse').forEach(function(c) { c.open = true; }); }
  function collapseAll() { document.querySelectorAll('.session-card, .q-collapse').forEach(function(c) { c.open = false; }); }

  // ---------------- navigation ----------------
  function flash(el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    el.classList.add('flash');
    setTimeout(function() { el.classList.remove('flash'); }, 1600);
  }
  function jumpToSession(code) {
    var card = document.getElementById('card-' + code);
    if (!card) return;
    card.open = true;
    setTimeout(function() { flash(card); }, 30);
  }
  function jumpToDate(date) { var row = document.getElementById('day-' + date); if (row) flash(row); }
  function jumpToRef(id) {
    var el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  var AGENDA_DATES = /*AGENDA_DATES*/[];
  function todayKey(now) { return now.getFullYear() + '-' + pad(now.getMonth() + 1) + '-' + pad(now.getDate()); }
  function jumpToToday() {
    closeDrawer();
    var now = new Date(), today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    if (!AGENDA_DATES.length) return;
    var best = AGENDA_DATES[0], min = Infinity;
    AGENDA_DATES.forEach(function(ds) {
      var p = ds.split('-').map(Number);
      var diff = Math.abs(new Date(p[0], p[1] - 1, p[2]) - today);
      if (diff < min) { min = diff; best = ds; }
    });
    jumpToDate(best);
  }
  function focusSearch() {
    openDrawer();
    var box = document.getElementById('searchBox');
    setTimeout(function() { box.focus(); }, 250);
  }

  // ---------------- comprehensive essay countdown ----------------
  function updateEssayCountdown() {
    var el = document.getElementById('essayCountdown');
    var now = new Date();
    var issue = new Date('2027-02-25T08:30:00'), due = new Date('2027-02-26T08:30:00');
    var target, label;
    if (now < issue) { target = issue; label = 'Distributed in'; }
    else if (now < due) { target = due; label = 'Returned in'; }
    else { el.hidden = true; return; }
    var hrs = Math.floor((target - now) / 3600000);
    el.hidden = false;
    el.innerHTML = '<span class="rc-label">' + label + '</span><span class="rc-time">' + Math.floor(hrs / 24) + 'd ' + (hrs % 24) + 'h</span>';
  }

  // ---------------- today / next hero ----------------
  function formatHHMM(d) { return pad(d.getHours()) + ':' + pad(d.getMinutes()); }
  function formatDateShort(ds) {
    var p = ds.split('-').map(Number), d = new Date(p[0], p[1] - 1, p[2]);
    return d.toLocaleDateString(undefined, { weekday: 'short' }) + ', ' + d.toLocaleDateString(undefined, { month: 'short' }) + ' ' + p[2];
  }
  function isTomorrow(ds, todayStr) {
    var t = todayStr.split('-').map(Number), n = new Date(t[0], t[1] - 1, t[2] + 1);
    return ds === n.getFullYear() + '-' + pad(n.getMonth() + 1) + '-' + pad(n.getDate());
  }
  function hidden(el) { return !!(el.offsetParent === null && getComputedStyle(el).display === 'none'); }
  function parseEvents() {
    var out = [];
    document.querySelectorAll('.cal-item[data-start]').forEach(function(el) {
      if (hidden(el)) return;
      var s = new Date(el.dataset.start), e = new Date(el.dataset.end || el.dataset.start);
      var c = el.dataset.case;
      out.push({ el: el, start: s, end: e, dateStr: el.dataset.start.slice(0, 10), title: el.dataset.title || '',
                 label: c ? (c === '0' ? 'Intro' : 'Case ' + c) : (el.dataset.kind || ''), jump: c || '', date: el.closest('.cal-day').id.replace('day-', '') });
    });
    return out;
  }
  function findTodayAndNext() {
    var now = new Date(), todayStr = todayKey(now), evs = parseEvents(), today = [], next = null;
    evs.forEach(function(ev) {
      if (ev.dateStr < todayStr) return;
      if (ev.dateStr === todayStr) today.push(ev);
      if (!next && (ev.dateStr > todayStr || ev.end >= now)) next = ev;
    });
    return { todayStr: todayStr, today: today, next: next };
  }
  function renderRow(s, now) {
    var cls, state;
    var tail = s.jump ? ' data-jump-session="' + s.jump + '"' : ' data-jump-date="' + s.date + '"';
    if (now < s.start) {
      var diff = s.start - now;
      cls = 'is-upcoming';
      if (diff > 24 * 3600000) state = '<span class="hero-state">' + formatDateShort(s.dateStr) + ' &middot; ' + formatHHMM(s.start) + '</span>';
      else {
        var mins = Math.round(diff / 60000), hh = Math.floor(mins / 60);
        state = '<span class="hero-state hero-countdown">Starts in ' + (hh > 0 ? hh + 'h ' : '') + (mins % 60) + 'm</span>';
      }
    } else if (now <= s.end) {
      cls = 'is-live';
      state = '<span class="hero-state hero-live"><span class="hero-live-dot"></span>In progress</span>';
    } else { cls = 'is-done'; state = '<span class="hero-state">Completed</span>'; }
    return '<button type="button" class="hero-session-row ' + cls + '"' + tail + '><span class="hero-session-code">' + escapeHtml(s.label) +
      '</span><span class="hero-session-title">' + escapeHtml(s.title) + '</span>' + state + '</button>';
  }
  function renderHero() {
    var hero = document.getElementById('heroToday'), data = findTodayAndNext(), now = new Date();
    if (data.today.length) {
      document.getElementById('heroTodayLabel').textContent = 'Today';
      document.getElementById('heroTodaySessions').innerHTML = data.today.map(function(s) { return renderRow(s, now); }).join('');
    } else if (data.next) {
      document.getElementById('heroTodayLabel').textContent = 'Next up';
      document.getElementById('heroTodaySessions').innerHTML = renderRow(data.next, now);
    } else { hero.hidden = true; return; }
    hero.hidden = false;
  }
  function renderNextUpBar() {
    var bar = document.getElementById('nextUpBar'), data = findTodayAndNext(), now = new Date(), target = null;
    for (var i = 0; i < data.today.length; i++) if (now < data.today[i].start) { target = data.today[i]; break; }
    if (!target) target = data.next;
    var btn = document.getElementById('nextUpJumpBtn');
    if (!target) { bar.dataset.hasTarget = 'false'; return; }
    bar.dataset.hasTarget = 'true';
    var lab = target.dateStr === data.todayStr ? 'Today' : isTomorrow(target.dateStr, data.todayStr) ? 'Tomorrow' : formatDateShort(target.dateStr);
    document.getElementById('nextUpText').textContent = 'Next: ' + target.label + ' — ' + lab + ' ' + formatHHMM(target.start);
    btn.removeAttribute('data-jump-session'); btn.removeAttribute('data-jump-date');
    if (target.jump) btn.dataset.jumpSession = target.jump; else btn.dataset.jumpDate = target.date;
  }
  function refreshTodayAndNextUp() { renderHero(); renderNextUpBar(); }
  function initNextUpObserver() {
    var hero = document.getElementById('heroToday'), bar = document.getElementById('nextUpBar');
    if (!('IntersectionObserver' in window)) return;
    new IntersectionObserver(function(entries) {
      bar.classList.toggle('show', !entries[0].isIntersecting && !hero.hidden && bar.dataset.hasTarget !== 'false');
    }, { threshold: 0 }).observe(hero);
  }

  // ---------------- drawer ----------------
  var drawerOpener = null;
  function drawerFocusables() {
    return Array.prototype.filter.call(document.querySelectorAll('.sidebar button, .sidebar input, .sidebar select, .sidebar a[href]'),
      function(el) { return !el.disabled && el.offsetParent !== null; });
  }
  function openDrawer() {
    var sb = document.querySelector('.sidebar');
    if (sb.classList.contains('open')) return;
    drawerOpener = document.activeElement;
    sb.classList.add('open');
    document.getElementById('drawerBackdrop').classList.add('open');
    document.body.style.overflow = 'hidden';
    var f = drawerFocusables()[0];
    if (f && window.innerWidth < 1100) setTimeout(function() { f.focus(); }, 50);
  }
  function closeDrawer() {
    var sb = document.querySelector('.sidebar');
    var wasOpen = sb.classList.contains('open');
    sb.classList.remove('open');
    document.getElementById('drawerBackdrop').classList.remove('open');
    document.body.style.overflow = '';
    if (wasOpen && drawerOpener && drawerOpener.focus && document.contains(drawerOpener)) drawerOpener.focus();
    drawerOpener = null;
  }
  document.addEventListener('keydown', function(e) {
    if (e.key !== 'Tab' || !document.querySelector('.sidebar').classList.contains('open') || window.innerWidth >= 1100) return;
    var f = drawerFocusables();
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });
  (function() { // swipe left to close
    var sb = document.querySelector('.sidebar'), x0 = null, y0 = null;
    sb.addEventListener('touchstart', function(e) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    sb.addEventListener('touchend', function(e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
      x0 = null;
      if (dx < -60 && Math.abs(dx) > Math.abs(dy) * 1.5) closeDrawer();
    }, { passive: true });
  })();

  // ---------------- calendar day state (today / past) ----------------
  function markDays() {
    var t = todayKey(new Date());
    document.querySelectorAll('.cal-day').forEach(function(row) {
      var d = row.id.replace('day-', '');
      row.classList.toggle('is-today', d === t);
      row.classList.toggle('is-past', d < t);
    });
  }

  // ---------------- mobile mini header (current month) ----------------
  function updateMiniHeader() {
    var mh = document.getElementById('miniHeader'), heads = document.querySelectorAll('.cal-month-header'), cur = null;
    for (var i = 0; i < heads.length; i++) {
      if (heads[i].getBoundingClientRect().top <= 60) cur = heads[i]; else break;
    }
    var last = document.querySelector('.cal-agenda').lastElementChild;
    var inCal = cur && last && last.getBoundingClientRect().bottom > 60;
    mh.hidden = !inCal;
    if (inCal) document.getElementById('miniMonth').textContent = cur.textContent;
  }

  // ---------------- bottom-nav state ----------------
  function updateNavState() {
    var q = document.getElementById('searchBox').value.trim();
    document.getElementById('navSearch').classList.toggle('has-badge', !!q);
  }
  function initTodayNav() {
    var row = document.querySelector('.cal-day.is-today'), btn = document.getElementById('navToday');
    if (!row || !('IntersectionObserver' in window)) return;
    new IntersectionObserver(function(en) { btn.classList.toggle('active', en[0].isIntersecting); }, { threshold: 0.3 }).observe(row);
  }

  var ACTIONS = {
    'jump-today': jumpToToday, 'expand-all': expandAll, 'collapse-all': collapseAll,
    'scroll-top': function() { window.scrollTo({ top: 0, behavior: 'smooth' }); },
    'focus-search': focusSearch, 'theme-toggle': toggleTheme, 'open-drawer': openDrawer, 'close-drawer': closeDrawer
  };
  document.addEventListener('click', function(e) {
    var a = e.target.closest('[data-action]');
    if (a && ACTIONS[a.dataset.action]) { ACTIONS[a.dataset.action](); return; }
    var s = e.target.closest('[data-jump-session]');
    if (s) { closeDrawer(); jumpToSession(s.dataset.jumpSession); return; }
    var d = e.target.closest('[data-jump-date]');
    if (d) { closeDrawer(); jumpToDate(d.dataset.jumpDate); return; }
    var r = e.target.closest('[data-jump-ref]');
    if (r) { closeDrawer(); jumpToRef(r.dataset.jumpRef); }
  });
  document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeDrawer(); });

  var box = document.getElementById('searchBox');
  function clearSearchBox() { if (!box.value) return; box.value = ''; filterSessions(); box.focus(); }
  box.addEventListener('input', debounce(filterSessions, 100));
  box.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && this.value) { clearSearchBox(); e.stopPropagation(); }
    else if (e.key === 'Enter') {
      e.preventDefault();
      var m = searchIndex.filter(function(x) { return x.card.style.display !== 'none'; })[0];
      if (m) { closeDrawer(); m.card.open = true; m.card.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    }
  });
  document.getElementById('searchClearBtn').addEventListener('click', clearSearchBox);
  window.addEventListener('scroll', function() {
    document.getElementById('backToTop').classList.toggle('show', window.scrollY > 600);
    if (!miniTick) { miniTick = true; requestAnimationFrame(function() { miniTick = false; updateMiniHeader(); }); }
  });
  var miniTick = false;
  window.addEventListener('resize', debounce(function() { if (window.innerWidth >= 1100) closeDrawer(); }, 200));

  // ---------------- init ----------------
  buildSearchIndex();
  markDays();
  initTodayNav();
  updateMiniHeader();
  document.addEventListener('visibilitychange', function() { if (!document.hidden) { markDays(); refreshTodayAndNextUp(); } });
  initReadingCheckboxes();
  updateEssayCountdown();
  setInterval(updateEssayCountdown, 60000);
  refreshTodayAndNextUp();
  initNextUpObserver();
  setInterval(refreshTodayAndNextUp, 30000);
})();
