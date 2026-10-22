#!/usr/bin/env python3
"""Build index.html (single self-contained file) from data/*.json.

Usage:  python3 tools/build.py
"""
import json, hashlib, html, re, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / 'data'
T = ROOT / 'tools'
cases_raw = json.load(open(D / 'cases_raw.json', encoding='utf-8'))
sched = json.load(open(D / 'schedule.json', encoding='utf-8'))
themes = json.load(open(D / 'themes.json', encoding='utf-8'))
meta = json.load(open(D / 'meta.json', encoding='utf-8'))

esc = lambda s: html.escape(s, quote=True)
SHORT = sched['short']
LECT = sched['lectures']
DAYS = sched['days']
ORDER = ['0', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']

def d2(s): return datetime.date.fromisoformat(s)
def fmt(s, wd=False):
    d = d2(s)
    return (d.strftime('%a ') if wd else '') + d.strftime('%b ') + str(d.day)
def rng(a, b):
    if a == b: return fmt(a)
    da, db = d2(a), d2(b)
    if da.month == db.month: return da.strftime('%b ') + f'{da.day}–{db.day}'
    return fmt(a) + ' – ' + fmt(b)
def code(c): return 'Intro' if c == '0' else 'Case ' + c

# ---- per-case dates derived from calendar ----
case_days = {c: [] for c in ORDER}
sem_days = {c: [] for c in ORDER}
for d, items in DAYS.items():
    seen = set()
    for it in items:
        c = it.get('case')
        if not c: continue
        if c not in seen: case_days[c].append(d); seen.add(c)
        if it['k'] == 'sem' and d not in sem_days[c]: sem_days[c].append(d)
first_day = {c: case_days[c][0] for c in ORDER}

SVG = {
 'target': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="0.6" fill="currentColor"/>',
 'eye': '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
 'book': '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/>',
 'q': '<circle cx="12" cy="12" r="9"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 2.5-3 4.5"/><circle cx="12" cy="17.5" r="0.6" fill="currentColor"/>',
 'mic': '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v4"/>',
 'cal': '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
}
def sub(title, icon, body, cls=''):
    return (f'<div class="subsection {cls}"><h4><span class="sec-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{SVG[icon]}</svg></span>{title}</h4>{body}</div>')

def rid(*a): return hashlib.sha1('|'.join(a).encode()).hexdigest()[:8]

def dlist(ds):
    # ['2026-11-13','2026-11-16'] -> 'Nov 13, 16'; months repeat only when they change
    out, last = [], None
    for d in ds:
        dt = d2(d)
        out.append((dt.strftime('%b ') if dt.month != last else '') + str(dt.day))
        last = dt.month
    return ', '.join(out)

def case_card(c):
    m = meta['cases'][c]
    cdays = case_days[c]
    lec_dates = sorted({l['date'] for l in LECT[c] if l['date']})
    metaline = 'Lecture' + ('s ' if len(lec_dates) != 1 else ' ') + dlist(lec_dates)
    if any(not l['date'] for l in LECT[c]): metaline += ' + asynch'
    if sem_days[c]: metaline += ' &middot; Seminars ' + dlist(sem_days[c])
    if c == '0':
        body = ''
        body += sub('Course Introduction', 'eye', ''.join(f'<p>{esc(p)}</p>' for p in meta['intro_paras']))
        body += sub('Lecture', 'mic', lec_list(c))
        body += sub('Seminars', 'cal', sem_list(c))
        body += sub('Learning outcomes', 'target', learning_html(), 'span-all')
    else:
        data = cases_raw[c]
        gen = data['general']
        head = ''.join(f'<p>{esc(p)}</p>' for p in gen[:2])
        rest = ''.join(f'<p>{esc(p)}</p>' for p in gen[2:])
        if rest:
            head += f'<details class="more"><summary>Read the full case overview ({len(gen) - 2} more paragraphs)</summary>{rest}</details>'
        body = f'<div class="card-block-label">{esc(m["full"])}</div>'
        body += sub('Overview', 'eye', head)
        body += sub('Lectures', 'mic', lec_list(c)) 
        qs = ''.join(f'<li>{esc(q)}</li>' for q in data['questions'])
        body += sub(f'Essay &amp; Discussion Questions ({len(data["questions"])})', 'q', f'<ul class="plain-list q-list">{qs}</ul>', 'span-all')
        rds = ''
        for i, r in enumerate(data['readings']):
            link = meta.get('links', {}).get(f'{c}.{i+1}')
            cite = esc(r['cite'])
            if link: cite = f'<a href="{esc(link)}" target="_blank" rel="noopener">{cite}</a>'
            src = f'<span class="cite-src">{esc(r["src"])}</span>' if r['src'] else ''
            note = f'<span class="cite-note">{esc(r["note"])}</span>' if r['note'] else ''
            rds += (f'<li class="cite cite-req"><label class="read-toggle"><input type="checkbox" class="read-checkbox" '
                    f'data-read-id="{rid(c, str(i), r["cite"])}" aria-label="Mark as read"></label>'
                    f'<span class="cite-text"><span class="plain">{i+1}. {cite}</span>{src}{note}</span></li>')
        body += sub(f'Required Reading ({len(data["readings"])})', 'book', f'<ul class="cite-list">{rds}</ul>', 'span-all')
        body += sub('Seminars', 'cal', sem_list(c))
    title = m['short_title']
    return (f'<details class="session-card cal-session-card" id="card-{c}" data-code="{c}">'
            f'<summary><span class="code">{code(c)}</span><span class="title-wrap"><span class="title">{esc(title)}</span>'
            f'<span class="card-meta-line">{metaline}</span></span>'
            f'<span class="badges"><span class="badge badge-type">{"Lecture" if c == "0" else "Case study"}</span></span></summary>'
            f'<div class="card-body">{body}</div></details>')

def lec_list(c):
    out = ''
    for l in LECT[c]:
        when = fmt(l['date'], True) if l['date'] else 'Asynch'
        jump = f' data-jump-date="{l["date"]}"' if l['date'] else ''
        out += (f'<li><span class="lec-when">{when}</span> <button type="button" class="lec-jump"{jump}>{esc(l["title"])}</button> '
                f'<span class="lec-who">&mdash; {esc(l["presenter"])}</span></li>')
    return f'<ul class="lec-list">{out}</ul>'

def sem_list(c):
    parts = []
    for d in sem_days[c]:
        its = [i for i in DAYS[d] if i['k'] == 'sem' and i['case'] == c]
        for i in its:
            parts.append(f'<li><span class="lec-when">{fmt(d, True)}</span> <button type="button" class="lec-jump" data-jump-date="{d}">'
                         f'{i["par"]} seminars{" (" + i["label"] + ")" if i.get("label") else ""}</button> '
                         f'<span class="lec-who">&mdash; {i["time"]}</span></li>')
    return f'<ul class="lec-list">{"".join(parts)}</ul>'

def learning_html():
    return meta['learning_html']

# ---- calendar ----
def hhmm(s): return s[:2] + ':' + s[2:]
def iso_t(d, t): return f'{d}T{t[:2]}:{t[2:4]}:00'
def item_html(d, it, lec_iter):
    k = it['k']
    if k == 'lec':
        c = it['case']
        l = next(lec_iter[(c, d)])
        t0, t1 = it['time'].split('-')
        ttl = l['title']
        tag = 'Intro lecture' if it.get('intro') else 'Lecture'
        return (f'<button type="button" class="cal-item cal-item-lecture" data-jump-session="{c}" data-start="{iso_t(d, t0)}" '
                f'data-end="{iso_t(d, t1)}" data-case="{c}" data-title="{esc(ttl)}" data-kind="{tag}">'
                f'<span class="cal-item-time">{it["time"]}</span><span class="cal-item-main"><span class="cal-tag">{tag}</span> '
                f'{esc(ttl)} <span class="cal-item-format">&mdash; {esc(l["presenter"])} &middot; {it["room"]}</span></span></button>')
    if k == 'sem':
        c = it['case']
        t0, t1 = it['time'].split('-')
        lab = f'{it["par"]} Seminars' + (f' ({it["label"]})' if it.get('label') else '') + f' &mdash; {esc(SHORT[c])}'
        ttl = f'{it["par"]} Seminars — {SHORT[c]}'
        return (f'<button type="button" class="cal-item cal-item-seminar sem-{it["par"].lower()}" data-jump-session="{c}" '
                f'data-start="{iso_t(d, t0)}" data-end="{iso_t(d, t1)}" data-case="{c}" data-title="{esc(ttl)}" data-kind="Seminar">'
                f'<span class="cal-item-time">{it["time"]}</span><span class="cal-item-main"><span class="cal-tag">Seminar</span> {lab}</span></button>')
    if k == 'holiday': return f'<div class="cal-item cal-item-holiday"><span class="cal-item-main">{esc(it["text"])}</span></div>'
    if k == 'pmw': return '<div class="cal-item cal-item-pmw"><span class="cal-item-main"><span class="cal-tag">Other course</span> Perspectives on Modern Warfare Course</span></div>'
    if k == 'elective': return f'<div class="cal-item cal-item-elective"><span class="cal-item-main"><span class="cal-tag">Electives</span> Electives/LDPA Day {it["n"]}</span></div>'
    if k == 'reflect': return '<div class="cal-item cal-item-reflect"><span class="cal-item-main"><span class="cal-tag" style="background:#7a8aa8">Study</span> Student Reflection / Preparation Day</span></div>'
    if k == 'note': return f'<div class="cal-item cal-item-note"><span class="cal-tag">Note</span><span class="cal-item-main">{esc(it["text"])}</span></div>'
    if k == 'event':
        t0, t1 = it['time'].split('-')
        return (f'<div class="cal-item cal-item-event" data-start="{iso_t(d, t0)}" data-end="{iso_t(d, t1)}" data-title="{esc(it["text"])}" data-kind="Event">'
                f'<span class="cal-item-time">{it["time"]}</span><span class="cal-item-main"><span class="cal-tag">Event</span> {esc(it["text"])}</span></div>')
    if k == 'deadline':
        return (f'<div class="cal-item cal-item-deadline" data-start="{it["due"]}" data-end="{it["due"]}" data-title="{esc(it["text"])}" data-kind="Deadline">'
                f'<span class="cal-item-time">{it["time"]}</span><span class="cal-item-main"><span class="cal-tag">Deadline</span> {esc(it["text"])}</span></div>')
    raise ValueError(k)

def make_iters():
    its = {}
    for c, ls in LECT.items():
        by = {}
        for l in ls:
            if l['date']: by.setdefault(l['date'], []).append(l)
        for d, arr in by.items(): its[(c, d)] = iter(arr)
    return its

def calendar_html():
    lec_iter = make_iters()
    out = []
    month = None
    # case banners span the run of days from a case's first to last dated item
    last_day = {c: case_days[c][-1] for c in ORDER}
    open_case = None
    between = False
    for d, items in DAYS.items():
        dt = d2(d)
        if (dt.year, dt.month) != month:
            month = (dt.year, dt.month)
            out.append(f'<h3 class="cal-month-header" id="month-{dt:%Y-%m}">{dt:%B %Y}</h3>')
        cs = [c for c in ORDER if any(i.get('case') == c for i in items)]
        if open_case and d > last_day[open_case]: open_case = None
        for c in cs:
            if first_day[c] == d:
                out.append(case_card(c)); open_case = c; between = False
        if not open_case and not between:
            out.append('<div class="between-cases">Between cases</div>'); between = True
        parts = [item_html(d, it, lec_iter) for it in items]
        out.append(f'<div class="cal-day" id="day-{d}"><div class="cal-day-date"><span class="cal-dow">{dt:%A}</span>'
                   f'<span class="cal-dnum">{dt:%b} {dt.day}</span></div><div class="cal-day-items">{"".join(parts)}</div></div>')
    return '<div class="cal-agenda" id="calAgenda">' + ''.join(out) + '</div>'

def case_index_html():
    rows = ''
    for c in ORDER:
        cd = case_days[c]
        rows += (f'<li><button type="button" data-jump-session="{c}"><span class="ci-num">{"Intro" if c == "0" else c}</span>'
                 f'<span>{esc(SHORT[c])}</span><span class="ci-dates">{rng(cd[0], cd[-1])}</span></button></li>')
    return f'<ul class="case-index">{rows}</ul>'

def fix_title(t):
    for a, b in ((' For ', ' for '), (' The ', ' the '), (' Of ', ' of ')): t = t.replace(a, b)
    return t

def reference_html():
    out = '<section class="ref-section" id="reference"><h2>Course Reference</h2>'
    out += f'<details class="ref-panel"><summary>Learning outcomes</summary><div class="ref-body">{meta["learning_html"]}</div></details>'
    out += f'<details class="ref-panel"><summary>Grading &amp; essays</summary><div class="ref-body">{meta["grading_html"]}</div></details>'
    th = ''
    for t in themes:
        th += (f'<details class="ref-panel"><summary>{t["n"]}. {esc(fix_title(t["title"]))}</summary><div class="ref-body">'
               + ''.join(f'<p>{esc(p)}</p>' for p in t['paras']) + '</div></details>')
    out += f'<details class="ref-panel" open><summary>The 11 course themes (guiding questions)</summary><div class="ref-body">{th}</div></details>'
    out += f'<details class="ref-panel"><summary>Source files (Google Drive)</summary><div class="ref-body ref-links">{meta["links_html"]}</div></details>'
    return out + '</section>'

AGENDA = list(DAYS.keys())
css = (T / 'jmo_base.css').read_text(encoding='utf-8') + (T / 'extra.css').read_text(encoding='utf-8')
js = (T / 'app.js').read_text(encoding='utf-8').replace('/*AGENDA_DATES*/[]', json.dumps(AGENDA))
shell = (T / 'shell.html').read_text(encoding='utf-8')
page = (shell.replace('{{CSS}}', css).replace('{{JS}}', js).replace('{{CASE_INDEX}}', case_index_html())
        .replace('{{CALENDAR}}', calendar_html()).replace('{{REFERENCE}}', reference_html())
        .replace('{{TOTAL_CASES}}', str(len(ORDER))))
(ROOT / 'index.html').write_text(page, encoding='utf-8')
print('wrote index.html', len(page) // 1024, 'KB')
