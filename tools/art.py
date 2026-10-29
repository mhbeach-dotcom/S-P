"""Stylised map art, per-case hero banners and the term timeline for command.html.

Land is drawn once (in a hidden <defs> SVG) in lon/lat space and re-used by every
hero via <use>, so each banner is just a viewBox plus markers. The coastlines are
hand-simplified: stylised, not survey-accurate.
"""
import datetime, html

K = 0.8  # horizontal squash so mid-latitudes look about right
ASPECT = 0.28  # banner height / width in viewBox units (matches the CSS aspect-ratio)

LAND = {
 'eurasia': [(-5.6,36),(-9,37),(-9.3,39),(-8.8,42),(-9.3,43.2),(-1.8,43.4),(-1.2,46),(-4.5,48.4),(-1.5,48.7),(1.5,50.2),(4,51.5),(7,53.5),(8.5,54),(8.3,57.1),(10.6,57.7),(10.2,54.9),(12,54.2),(14.2,54),(19,54.5),(21,55.5),(21,57),(24,57.3),(24,59.4),(30,60),(22,60.4),(21.3,62),(25,65.2),(21.5,65.5),(17.5,62.5),(16,56),(12.8,55.5),(11,58.5),(5.5,58.8),(5,62),(14,67.5),(20,70),(30,71),(41,67.5),(34,66),(40,64.5),(44,66),(60,69),(70,73),(80,73),(100,77),(113,74),(130,71),(160,70),(180,68),(180,66),(165,60),(156,51),(142,59),(135,54),(140,48),(131,43),(129,41),(127.5,39.5),(129.5,35.5),(126.5,34.5),(126,37),(125,39.5),(121.5,39.2),(122,37),(119,37.5),(121,32),(122,30),(120,26),(117,23.2),(113,22),(110,21),(108,21.5),(106.5,20),(109,15),(109,11.5),(105,8.6),(105,10),(103,10.5),(100.5,13.5),(100,8),(103.5,1.5),(101,3),(98.5,8),(98.5,16),(94.5,16),(94,19),(92,21),(90,22),(87,21.5),(86,20),(82,16.5),(80,15),(80,10),(77.5,8),(76,10.5),(73,17),(72.8,21),(70,21),(68.5,23.5),(66.5,25.4),(61.5,25.2),(57,25.8),(56.5,27),(51,28),(48.5,30),(50,26),(51.5,25),(53,24),(56,26.2),(56.5,24.5),(59.8,22.5),(57.5,19),(52,16),(45,12.8),(43.2,13),(42.7,16),(39,21.5),(35,28),(34.5,29.5),(34.2,31.2),(35,33),(36,35),(36,36.7),(34,36.2),(30,36.3),(27.5,37),(26.3,39),(26.5,40.2),(24,40.9),(23.5,40.3),(24,38),(23,36.5),(21.6,36.8),(21.2,38.3),(20,39.8),(19.5,41.8),(18.5,40.2),(16.5,39),(15.7,38),(15.7,40),(12,41.5),(10.2,43.5),(8.7,44.4),(6.5,43.2),(3.2,43.3),(3,42),(0.8,41),(-0.5,38.5),(-2,36.8)],
 'africa': [(-17,21),(-17,14.7),(-13,9),(-8,4.5),(-4,5),(2,6),(5,4.3),(9.5,4),(9.5,1),(9,-1),(12,-5),(13.5,-12),(12,-17),(14.5,-23),(18,-32),(20,-35),(26,-34),(32.5,-28.5),(35,-24),(35,-20),(40.5,-15),(39.2,-6),(41,-1),(44,3),(51,10.5),(51,12),(43.3,12.5),(39,16),(37.2,21),(34,27),(32.5,30),(30,31.2),(25,31.8),(20,32.2),(15.2,32.3),(11,33),(10.5,36.9),(8,37),(2,36.7),(-2,35.2),(-5.8,35.8),(-9.5,32),(-13,27.5)],
 'namerica': [(-168,66),(-162,70),(-141,69.5),(-128,70),(-115,68),(-95,72),(-90,68),(-94,64),(-94,58.5),(-92,57),(-82,53),(-79,51.5),(-77,56),(-78,62.3),(-72,61.5),(-65,60),(-60,55),(-56,52),(-60,47),(-66,44.5),(-70,43),(-70,41.5),(-74,40.5),(-76,37),(-76,35),(-81,31.5),(-80,25.5),(-82.5,27),(-84,30),(-89,30.2),(-94,29.5),(-97.5,26),(-97.8,22),(-96,19),(-94,18.2),(-91,19),(-90.5,21),(-87,21.5),(-88,18),(-88,15.8),(-83.5,15),(-83.5,11),(-79.5,9.5),(-77.5,8.5),(-80,7.5),(-83,8.2),(-86,11),(-88,13),(-92,14.5),(-96,15.7),(-101,17.5),(-105.5,20),(-105.5,23),(-109,25.5),(-114.7,31.5),(-117,32.5),(-120.5,34.5),(-124.3,40.2),(-124,46),(-124.7,48.4),(-123,49),(-128,51),(-133,55),(-139,59.5),(-147,61),(-152,59),(-157,57),(-162,55.2),(-165,54.5),(-160,58.5),(-162,60),(-165,62),(-161,64)],
 'samerica': [(-77.5,8.5),(-72,12),(-67,10.5),(-62,10.5),(-60,8.5),(-52,5),(-50,0),(-48,-1),(-44,-2.5),(-39,-3.5),(-35,-5.5),(-35,-9),(-39,-14),(-39,-18),(-41,-22),(-45,-23.5),(-48.5,-26),(-49,-29),(-53,-34),(-57,-35),(-57.5,-37.5),(-62,-39),(-65,-41),(-63.5,-43),(-67.5,-46),(-66,-48),(-69,-51),(-68.5,-52.5),(-72,-53.5),(-74.5,-51),(-75.5,-47),(-73.5,-42),(-73.5,-37),(-71.5,-30),(-70.2,-18),(-76,-14),(-81,-6),(-80,-2),(-80.5,0.5),(-78.8,1.8),(-77.5,4)],
 'greenland': [(-73,78),(-60,82),(-30,83.5),(-20,80),(-18,76),(-22,70),(-33,68),(-43,60),(-50,62),(-53,67),(-58,75)],
 'uk': [(-5.7,50),(1.5,51),(1.7,52.8),(0,53.5),(-2,55.8),(-1.8,57.5),(-3.5,58.6),(-5,58.5),(-6,57),(-5.5,55.5),(-3,54.8),(-3,53.3),(-4.7,52.5),(-5.2,51.7),(-3.5,51.3)],
 'ireland': [(-10,51.7),(-6,52),(-6,54.5),(-8,55.3),(-10,54)],
 'iceland': [(-24,65.5),(-18,66.3),(-13.5,65),(-18,63.4),(-22.5,63.8)],
 'honshu': [(130,31.2),(131.5,33.5),(135,34),(140,35),(141,38.5),(142,41.5),(140,41),(139.8,38.5),(137,37),(133,35.5),(130.9,34.3),(129.8,33)],
 'hokkaido': [(140,42),(142,45.5),(145.5,43.3),(143,42)],
 'australia': [(113,-22),(114,-26),(115,-34),(118,-35),(124,-33),(131,-31.5),(135,-34.5),(138,-35.5),(140,-38),(146,-39),(150,-37.5),(153.5,-29),(153,-25),(149,-21),(146,-18.5),(145,-14.8),(142.5,-10.7),(141.5,-13),(140,-17.5),(136.5,-15.5),(135,-12),(131,-12),(129,-15),(126,-14),(122,-17),(119,-20)],
 'borneo': [(109,1.5),(111,2),(115,5),(117.5,7),(119,5),(118,1),(116,-4),(110,-3)],
 'sumatra': [(95,5.5),(98,4),(104,-1),(106,-6),(102,-4),(98,0)],
 'java': [(105.5,-6.5),(114.5,-7.8),(114,-8.7),(106,-7.7)],
 'newguinea': [(131,-1),(141,-2.5),(146,-5),(150,-10.5),(143,-9),(138,-8),(133,-4)],
 'madagascar': [(44,-25),(47,-25),(50,-15.5),(49,-12),(47,-15),(44,-20)],
 'srilanka': [(79.8,6.5),(81.8,7.5),(80.2,9.8)],
 'taiwan': [(120.1,22.5),(121,25.2),(122,25),(121.5,22)],
 'luzon': [(120,18.5),(122.2,18.5),(122,16),(121.7,14),(120.5,14.2),(120,16)],
 'mindanao': [(122,7.5),(124,9.5),(126.5,8),(126,6),(124,6.2)],
 'cuba': [(-85,22),(-80,23),(-74,20),(-78,20)],
 'sicily': [(12.4,37.9),(15.6,38.2),(15.1,36.7),(12.5,37.5)],
 'sardinia': [(8.2,41.1),(9.7,41),(9.5,39.2),(8.5,39)],
 'crete': [(23.5,35.3),(26.3,35.2),(26,35),(23.6,35.1)],
 'nz': [(172.7,-34.5),(178.5,-37.7),(175,-41.5),(173,-40.5)],
}
WATER = {  # lakes / inland seas carved out of the Eurasian polygon
 'black': [(28,41.3),(28.5,43.5),(30.3,45.5),(33.5,46.2),(33,44.8),(36,45.2),(38,47),(41.5,42),(41.5,41.2),(37,41),(32,42),(29,41.2)],
 'caspian': [(47,45),(50,46.5),(53,46.8),(53,41),(53.5,37),(50.5,37),(49,40),(47,43)],
}

def _pt(lon, lat): return f'{lon * K:.1f} {-lat:.1f}'
def _poly(pts): return 'M' + ' L'.join(_pt(*p) for p in pts) + 'Z'

def defs_svg():
    land = ''.join(_poly(p) for p in LAND.values())
    water = ''.join(_poly(p) for p in WATER.values())
    return (f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
            f'<path id="land" vector-effect="non-scaling-stroke" d="{land}"/><path id="inland" vector-effect="non-scaling-stroke" d="{water}"/>{sky_defs()}</defs></svg>')

# ---- per-case map spec: centre lon/lat, lon span, era label, caption, glyph, markers ----
# marker: (name, lon, lat, side) side 'r' or 'l'
WORLD = (5, 30, 350)
CASES = {
 '0':   dict(view=WORLD, era='Concept & course', glyph='compass', cap='The strategist’s world',
             marks=[('Athens', 23.7, 38, 'r'), ('London', -0.1, 51.5, 'r'), ('Beijing', 116.4, 39.9, 'l')]),
 'I':   dict(view=WORLD, era='Theory', glyph='compass', cap='Where the theorists wrote',
             marks=[('Beijing · Sun Tzu', 116.4, 39.9, 'l'), ('Berlin · Clausewitz', 13.4, 52.5, 'r'), ('Newport · Mahan', -71.3, 41.5, 'r')]),
 'II':  dict(view=(21, 38, 26), era='431–404 BC', glyph='trireme', cap='The Aegean and Sicily',
             marks=[('Athens', 23.7, 38, 'r'), ('Sparta', 22.4, 37.1, 'l'), ('Corinth', 22.9, 37.9, 'l'), ('Syracuse', 15.3, 37.1, 'r'), ('Melos', 24.4, 36.7, 'r')]),
 'III': dict(view=(14, 49, 56), era='1792–1815', glyph='sail', cap='Sea power versus the continent',
             marks=[('London', -0.1, 51.5, 'l'), ('Paris', 2.3, 48.9, 'l'), ('Trafalgar', -6.2, 36.2, 'r'), ('Waterloo', 4.4, 50.7, 'r'), ('Austerlitz', 16.9, 49.1, 'r')]),
 'IV':  dict(view=(14, 49, 56), era='1871–1918', glyph='dread', cap='Imperial Germany and the road to 1914',
             marks=[('London', -0.1, 51.5, 'l'), ('Paris', 2.3, 48.9, 'l'), ('Berlin', 13.4, 52.5, 'r'), ('Vienna', 16.4, 48.2, 'r'), ('Jutland', 6.5, 56.7, 'l'), ('St Petersburg', 30.3, 59.9, 'l')]),
 'V':   dict(view=(16, 48, 62), era='1919–1939', glyph='star', cap='Winning the peace, losing the order',
             marks=[('Versailles', 2.1, 48.8, 'l'), ('Berlin', 13.4, 52.5, 'r'), ('Munich', 11.6, 48.1, 'l'), ('Rome', 12.5, 41.9, 'r'), ('Moscow', 37.6, 55.8, 'l')]),
 'VI':  dict(view=WORLD, era='1939–1945', glyph='plane', cap='A global war',
             marks=[('Berlin', 13.4, 52.5, 'r'), ('Moscow', 37.6, 55.8, 'r'), ('Normandy', -0.5, 49.3, 'l'), ('Pearl Harbor', -157.9, 21.3, 'r'), ('Tokyo', 139.7, 35.7, 'l')]),
 'VII': dict(view=WORLD, era='1945–1953', glyph='missile', cap='A divided world takes shape',
             marks=[('Washington', -77, 38.9, 'r'), ('Berlin', 13.4, 52.5, 'r'), ('Moscow', 37.6, 55.8, 'r'), ('Beijing', 116.4, 39.9, 'l'), ('Seoul', 127, 37.6, 'r')]),
 'VIII': dict(view=WORLD, era='1953–1968', glyph='star', cap='Competition in the Third World',
             marks=[('Havana', -82.4, 23.1, 'r'), ('Cairo', 31.2, 30, 'l'), ('Hanoi', 105.8, 21, 'l'), ('Moscow', 37.6, 55.8, 'r'), ('Washington', -77, 38.9, 'r')]),
 'IX':  dict(view=WORLD, era='1969–1991', glyph='radar', cap='Détente to collapse',
             marks=[('Washington', -77, 38.9, 'r'), ('Warsaw', 21, 52.2, 'l'), ('Moscow', 37.6, 55.8, 'r'), ('Tehran', 51.4, 35.7, 'r'), ('Kabul', 69.2, 34.5, 'r')]),
 'X':   dict(view=(52, 28, 62), era='2001–', glyph='radar', cap='Multi-theater warfare',
             marks=[('Baghdad', 44.4, 33.3, 'l'), ('Kabul', 69.2, 34.5, 'r'), ('Riyadh', 46.7, 24.7, 'l'), ('Damascus', 36.3, 33.5, 'l'), ('Islamabad', 73.1, 33.7, 'r'), ('Cairo', 31.2, 30, 'l')]),
 'XI':  dict(view=(110, 22, 100), era='Today →', glyph='dread', cap='The China challenge',
             marks=[('Beijing', 116.4, 39.9, 'l'), ('Taipei', 121.5, 25, 'r'), ('Tokyo', 139.7, 35.7, 'r'), ('Manila', 121, 14.6, 'r'), ('Guam', 144.8, 13.4, 'r'), ('Singapore', 103.8, 1.3, 'r'), ('New Delhi', 77.2, 28.6, 'r')]),
}

GLYPH = {
 'compass': '<path d="M32 4 38 26 60 32 38 38 32 60 26 38 4 32 26 26Z"/><circle cx="32" cy="32" r="4" class="hole"/>',
 'star': '<path d="M32 5 39 24 59 25 43 38 49 58 32 46 15 58 21 38 5 25 25 24Z"/>',
 'trireme': '<path d="M6 40Q32 54 58 40L52 46Q32 56 12 46Z"/><path d="M14 38 50 38 46 34 18 34Z"/><path d="M30 12 30 33 46 33Q46 20 30 12Z"/><path d="M12 48 6 58M22 51 18 60M32 52 32 61M42 51 46 60M52 48 58 58" class="stroke"/>',
 'sail': '<path d="M8 44Q32 58 56 44L52 50Q32 58 12 50Z"/><path d="M31 6 31 44" class="stroke"/><path d="M29 8Q14 20 14 36L29 36Z"/><path d="M33 8Q50 20 50 36L33 36Z"/><path d="M13 40 51 40" class="stroke"/>',
 'dread': '<path d="M4 42 60 42 54 52 12 52Z"/><rect x="14" y="34" width="10" height="8"/><rect x="40" y="34" width="10" height="8"/><rect x="26" y="26" width="12" height="16"/><path d="M30 26 30 14M34 26 34 18" class="stroke"/><path d="M22 36 8 30M42 36 56 30" class="stroke"/>',
 'plane': '<path d="M32 4 36 22 60 36 60 42 36 36 36 50 44 56 44 60 32 57 20 60 20 56 28 50 28 36 4 42 4 36 28 22Z"/>',
 'missile': '<path d="M32 3Q42 14 42 34L42 46 22 46 22 34Q22 14 32 3Z"/><path d="M22 36 12 52 22 48ZM42 36 52 52 42 48Z"/><path d="M28 48 32 62 36 48Z" class="flame"/><circle cx="32" cy="26" r="4" class="hole"/>',
 'radar': '<circle cx="32" cy="32" r="26" class="ring"/><circle cx="32" cy="32" r="17" class="ring"/><circle cx="32" cy="32" r="8" class="ring"/><path d="M32 32 54 14" class="stroke sweep"/><circle cx="46" cy="22" r="3"/>',
}

def glyph_svg(name):
    return (f'<svg viewBox="0 0 64 64" class="glyph" aria-hidden="true" focusable="false">{GLYPH[name]}</svg>')

def hero_html(c, code_label):
    s = CASES[c]
    clon, clat, span = s['view']
    xs = [m[1] * K for m in s['marks']]
    ys = [-m[2] for m in s['marks']]
    # fit the viewBox around the markers (labels need room), never tighter than 80% of the nominal span
    w = max((max(xs) - min(xs)) / 0.62, (max(ys) - min(ys)) / (ASPECT * 0.8), span * K * 0.8)
    w = min(w, 360 * K)
    cx = (max(xs) + min(xs)) / 2 if span < 300 else clon * K
    cy = (max(ys) + min(ys)) / 2 if span < 300 else -clat
    h = w * ASPECT
    x0, y0 = cx - w / 2, cy - h / 2
    clon, clat = cx / K, -cy
    span = w / K
    fs = w * 0.017
    # graticule every 10 degrees (5 when zoomed in)
    step = 5 if span <= 70 else 10
    lines = []
    lo = int((clon - span / 2) // step) * step
    for lon in range(lo, int(clon + span / 2) + step, step):
        lines.append(f'M{lon * K:.1f} {y0:.1f}V{y0 + h:.1f}')
    la = int((clat - h / 2) // step) * step
    for lat in range(la, int(clat + h / 2) + step, step):
        lines.append(f'M{x0:.1f} {-lat:.1f}H{x0 + w:.1f}')
    marks = ''
    for name, lon, lat, side in s['marks']:
        x, y = lon * K, -lat
        r = fs * 0.34
        tx = x + (r * 2.2 if side == 'r' else -r * 2.2)
        anchor = 'start' if side == 'r' else 'end'
        marks += (f'<g class="mk"><circle class="mk-ring" cx="{x:.1f}" cy="{y:.1f}" r="{r * 2:.1f}"/>'
                  f'<circle class="mk-dot" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>'
                  f'<text x="{tx:.1f}" y="{y + fs * 0.34:.1f}" text-anchor="{anchor}" font-size="{fs:.2f}">{html.escape(name)}</text></g>')
    vb = f'{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}'
    return (f'<div class="case-hero"><svg class="case-map" viewBox="{vb}" preserveAspectRatio="xMidYMid slice" role="img" '
            f'aria-label="Stylised map: {html.escape(s["cap"])}"><rect class="sea" x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}"/>'
            f'<path class="grat" d="{"".join(lines)}"/><use href="#land" class="land"/><use href="#inland" class="inland"/>{marks}</svg>'
            f'<div class="case-hero-plaque"><span class="plq-code">{html.escape(code_label)}</span><span class="plq-era">{html.escape(s["era"])}</span></div>'
            f'<div class="case-hero-cap">{html.escape(s["cap"])}</div>'
            f'<div class="case-hero-glyph">{glyph_svg(s["glyph"])}</div>'
            f'<div class="case-hero-note">Stylised map</div></div>')

# ---- term timeline ----
PAL = ['#6b7a90', '#1f4e79', '#2a6f97', '#2f8f9d', '#3a9a7a', '#5f9e4a', '#a98a2e', '#c27a2a', '#b85a3a', '#a03f55', '#7b4b94', '#4a5fa8']

def timeline_html(days, order, case_days, short, code, fmt):
    d2 = datetime.date.fromisoformat
    keys = list(days.keys())
    start, end = d2(keys[0]), d2(keys[-1])
    n = (end - start).days + 1
    PX = 14
    W = n * PX
    TOP, BAND_Y, BAND_H, MK_Y, H = 30, 34, 56, 104, 138
    idx = lambda d: (d2(d) - start).days
    g = []
    # weekend shading + week ticks
    for i in range(n):
        dt = start + datetime.timedelta(days=i)
        if dt.weekday() >= 5:
            g.append(f'<rect class="tl-wkend" x="{i * PX}" y="{TOP}" width="{PX}" height="{H - TOP}"/>')
        if dt.weekday() == 0:
            g.append(f'<path class="tl-week" d="M{i * PX} {TOP}V{H}"/>')
    # month labels
    last_m = None
    for i in range(n):
        dt = start + datetime.timedelta(days=i)
        if (dt.year, dt.month) != last_m:
            last_m = (dt.year, dt.month)
            g.append(f'<path class="tl-month-tick" d="M{i * PX} 6V{H}"/><text class="tl-month" x="{i * PX + 6}" y="20">{dt:%B %Y}</text>')
    # case bands
    for k, c in enumerate(order):
        cd = case_days[c]
        x0, x1 = idx(cd[0]) * PX, (idx(cd[-1]) + 1) * PX
        wd = x1 - x0
        label = ('Intro' if c == '0' else c)
        full = f'{code(c)}: {short[c]} · {fmt(cd[0])}–{fmt(cd[-1])}'
        txt = ''
        if wd >= 150: txt = f'{label} · {short[c]}'
        elif wd >= 40: txt = label
        g.append(f'<g class="tl-band" data-jump-session="{c}" data-start="{cd[0]}" data-end="{cd[-1]}" data-code="{html.escape(code(c))}" '
                 f'data-title="{html.escape(short[c])}" tabindex="0" role="button" aria-label="{html.escape(full)}">'
                 f'<title>{html.escape(full)}</title><rect x="{x0 + 1}" y="{BAND_Y}" width="{wd - 2}" height="{BAND_H}" rx="6" fill="{PAL[k % len(PAL)]}"/>'
                 f'<text x="{x0 + 8}" y="{BAND_Y + 33}">{html.escape(txt)}</text></g>')
    # markers
    kinds = {'holiday': ('Holiday', 'mk-hol'), 'elective': ('Electives', 'mk-el'), 'pmw': ('Other course', 'mk-pmw'),
             'reflect': ('Reflection day', 'mk-ref'), 'deadline': ('Essay', 'mk-dl'), 'event': ('Event', 'mk-ev')}
    for d, items in days.items():
        seen = set()
        for it in items:
            kk = it['k']
            if kk not in kinds or kk in seen: continue
            seen.add(kk)
            lab, cls = kinds[kk]
            t = it.get('text') or lab
            cx = idx(d) * PX + PX / 2
            g.append(f'<circle class="tl-mk {cls}" cx="{cx}" cy="{MK_Y + 14}" r="5" data-jump-date="{d}" tabindex="0" role="button" '
                     f'aria-label="{html.escape(lab)} {fmt(d)}"><title>{html.escape(lab)} · {fmt(d)}'
                     f'{" · " + html.escape(t) if kk in ("deadline", "event", "holiday") else ""}</title></circle>')
    needle = f'<g id="tlNeedle" display="none"><path d="M0 {TOP - 4}V{H}"/><text y="{TOP - 8}">Today</text></g>'
    legend = ('<div class="tl-legend"><span class="mk-hol">Holiday</span><span class="mk-el">Electives</span><span class="mk-pmw">Other course</span>'
              '<span class="mk-ref">Reflection</span><span class="mk-dl">Essay</span><span class="mk-ev">Event</span></div>')
    svg = (f'<svg id="tlSvg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" data-start="{start.isoformat()}" data-days="{n}" data-px="{PX}" '
           f'role="group" aria-label="Term timeline">{"".join(g)}{needle}</svg>')
    return ('<section class="timeline" id="timeline"><div class="tl-head"><h2>Term at a glance</h2>'
            '<div class="tl-zoom"><button type="button" data-tl="out" aria-label="Zoom out">−</button>'
            '<button type="button" data-tl="in" aria-label="Zoom in">+</button>'
            '<button type="button" data-tl="now">Today</button></div></div>'
            f'<div class="tl-scroll" id="tlScroll" tabindex="0" aria-label="Scrollable term timeline">{svg}</div>{legend}'
            '<p class="tl-hint">Tap a band to open that case; tap a dot to jump to the day. Drag or scroll sideways to move along the term.</p></section>')


# ---- illustrated scenes (original SVG artwork; no external images) ----
SKIES = {
 'dawn':  ('#1b3a63', '#e8a05a'), 'dusk': ('#2a2f5a', '#e0764a'), 'night': ('#050d1c', '#1d4274'),
 'day':   ('#4f86bd', '#d8e6f1'), 'storm': ('#222a36', '#8b97a6'), 'fire': ('#26090c', '#cf6a2a'),
}

def sky_defs():
    g = ''.join(f'<linearGradient id="sky-{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
                for k, (a, b) in SKIES.items())
    g += '<linearGradient id="sea-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#17375f"/><stop offset="1" stop-color="#071a33"/></linearGradient>'
    return g

def _waves(y, n=21, amp=4):
    return f'<path class="sc-wave" d="M-10 {y}' + f' q10 -{amp} 20 0 t20 0' * n + '"/>'
def _sea(y=88): return f'<rect x="0" y="{y}" width="400" height="{120 - y}" fill="url(#sea-g)"/>' + _waves(y + 4) + _waves(y + 12, amp=3)
def _sun(x, y, r=16): return f'<circle cx="{x}" cy="{y}" r="{r * 2.2}" class="sc-glow"/><circle cx="{x}" cy="{y}" r="{r}" class="sc-sun"/>'
def _stars(pts): return ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" class="sc-star"/>' for x, y, r in pts)
def _g(x, y, s, inner, rot=0): return f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">{inner}</g>'

SAIL = ('<path d="M-42 0H42L33 10H-35Z"/><path d="M-20 0V-40M0 0V-48M22 0V-38" class="sc-line"/>'
        + ''.join(f'<path d="M{m-14} {-h*.92}H{m+14}L{m+11} {-h*.48}H{m-11}Z"/><path d="M{m-16} {-h*.42}H{m+16}L{m+14} -5H{m-14}Z"/>' for m, h in ((-20, 40), (0, 48), (22, 38)))
        + '<path d="M42 0 54 -6" class="sc-line"/>')
TRIREME = ('<path d="M-38 2Q0 14 38 2L46 -4 40 -2 36 -6H-34L-40 -2Z"/><path d="M-6 -6V-36" class="sc-line"/><path d="M-26 -34H14L12 -12H-24Z" class="sc-sail"/>'
           '<path d="M-30 2 -36 12M-18 5-22 14M-6 6-8 15M6 6 8 15M18 5 22 14M30 2 36 12" class="sc-line"/><path d="M38 2 52 8" class="sc-line"/>')
DREAD = ('<path d="M-60 0H60L52 9H-52Z"/><rect x="-30" y="-8" width="60" height="8"/><rect x="-14" y="-20" width="12" height="12"/><rect x="6" y="-16" width="9" height="8"/>'
         '<rect x="-22" y="-30" width="5" height="22"/><rect x="-6" y="-34" width="5" height="26"/><path d="M-4 -34V-52M20 -16V-40" class="sc-line"/>'
         '<path d="M-52 -5 -66 -9M48 -5 62 -9M-40 -5-52 -2" class="sc-line"/><rect x="-46" y="-8" width="10" height="8"/><rect x="34" y="-8" width="10" height="8"/>')
CARRIER = '<path d="M-70 0H72L64 9H-60Z"/><rect x="-66" y="-5" width="136" height="5"/><rect x="20" y="-18" width="12" height="13"/><path d="M26 -18V-26" class="sc-line"/>'
CONTAINER = ('<path d="M-70 0H70L62 10H-60Z"/><rect x="-62" y="-12" width="124" height="12" class="sc-mid"/>'
             + ''.join(f'<rect x="{-60 + i * 10}" y="{-22 + (i % 3) * -0}" width="9" height="{10}" class="sc-box{i % 3}"/>' for i in range(0, 12))
             + '<rect x="-62" y="-22" width="124" height="0"/><rect x="46" y="-28" width="12" height="28"/>')
PLANE = GLYPH['plane']
MISSILE = GLYPH['missile']

def _plane(x, y, s, rot=0): return _g(x, y, s, PLANE.replace('class="hole"', ''), rot)

SCENES = {}
SCENES['0'] = ('dawn', _sun(300, 80, 15) + _sea(88)
    + ''.join(f'<path d="M300 80 L{300 + 160 * __import__("math").cos(a)} {80 - 160 * __import__("math").sin(a)}" class="sc-ray"/>' for a in (0.25, 0.5, 0.75, 1.0, 1.3, 1.6, 1.9, 2.3, 2.7))
    + _g(300, 38, 0.9, GLYPH['compass'], 0).replace('<g ', '<g class="sc-gold" '))
SCENES['I'] = ('dusk', _sun(90, 70, 14)
    + '<path d="M0 88 0 66 40 76 90 60 150 78 210 62 270 80 330 66 400 74V120H0Z" class="sc-far"/><path d="M0 100 70 84 140 96 230 82 320 96 400 86V120H0Z" class="sc-near"/>'
    + ''.join(f'<path d="M{x} 96V{y}" class="sc-line"/><path d="M{x} {y}h14l-4 4 4 4h-14" class="sc-gold"/>' for x, y in ((250, 64), (290, 70), (330, 66)))
    + '<path d="M180 94 196 86 204 88 222 80" class="sc-line"/><circle cx="204" cy="87" r="3.4"/>')
SCENES['II'] = ('dusk', _sun(310, 74, 18) + '<path d="M0 90 60 78 130 70 200 74 270 66 400 92V120H0Z" class="sc-far"/>'
    + '<path d="M40 90 70 62H200L230 90Z" class="sc-near"/><path d="M62 62H208L135 44Z" class="sc-temple"/><rect x="66" y="60" width="136" height="4" class="sc-temple"/>'
    + ''.join(f'<rect x="{74 + i * 17}" y="64" width="7" height="24" class="sc-temple"/>' for i in range(8))
    + _sea(96) + _g(330, 104, 0.9, TRIREME))
SCENES['III'] = ('storm', _sun(70, 48, 10) + _sea(86) + _g(230, 92, 1.25, SAIL) + _g(110, 90, 0.7, SAIL)
    + '<path d="M240 50q14-10 30-6t26-8" class="sc-smoke"/><circle cx="298" cy="36" r="4" class="sc-fire"/><circle cx="312" cy="30" r="2" class="sc-fire"/>')
SCENES['IV'] = ('storm', '<path d="M0 86H400" class="sc-line"/>' + _sea(86) + _g(240, 92, 1.1, DREAD) + _g(80, 94, 0.55, DREAD)
    + '<path d="M40 30 10 86M60 30 120 86" class="sc-beam"/><circle cx="330" cy="82" r="4"/><path d="M330 82V70h8" class="sc-line"/>'
    + '<path d="M200 36q10 -8 20 0t20 -2" class="sc-smoke"/>')
SCENES['V'] = ('dusk', _sun(60, 84, 16) + '<path d="M0 92 40 84 90 90 150 80 200 90 260 82 330 92 400 84V120H0Z" class="sc-far"/>'
    + '<path d="M0 104 80 96 170 106 270 96 400 106V120H0Z" class="sc-near"/>'
    + _g(240, 40, 1.1, '<path d="M-24 8Q-8 -10 14 -8Q4 0 -4 4L8 14Q-8 16 -24 8Z" class="sc-gold"/><path d="M14 -8 22 -12" class="sc-line"/>')
    + _plane(330, 30, 0.35, -20) + _plane(360, 46, 0.3, -20) + _plane(300, 56, 0.28, -20))
SCENES['VI'] = ('night', _stars([(30, 14, 1), (90, 26, .8), (170, 12, 1), (330, 20, 1.1), (380, 40, .8)]) + '<path d="M60 90 90 20M110 90 80 20M300 90 330 18" class="sc-beam"/>'
    + _sea(90) + _g(250, 94, 1.2, CARRIER) + _plane(130, 44, 0.5, 70) + _plane(180, 30, 0.42, 70) + _plane(100, 62, 0.4, 70) + _plane(350, 50, 0.36, 70))
SCENES['VII'] = ('dawn', _sun(330, 72, 12) + '<path d="M0 90H400V120H0Z" class="sc-near"/><path d="M0 92H400" class="sc-line"/>'
    + ''.join(f'<path d="M{x} 92V76" class="sc-line"/>' for x in range(10, 400, 24)) + '<path d="M0 78H400M0 84H400" class="sc-wire"/>'
    + _plane(130, 44, 0.8, 90)
    + '<circle cx="300" cy="62" r="10" class="sc-fire"/><circle cx="288" cy="68" r="8" class="sc-fire"/><circle cx="312" cy="68" r="8" class="sc-fire"/><path d="M296 90 300 70 304 90Z" class="sc-fire"/>')
SCENES['VIII'] = ('night', _stars([(20, 16, 1), (80, 40, 1), (150, 12, .8), (250, 24, 1), (370, 18, 1.2), (40, 70, .8)])
    + '<ellipse cx="200" cy="52" rx="170" ry="26" class="sc-orbit"/><circle cx="148" cy="30" r="7" class="sc-gold"/><path d="M148 30 130 20M148 30 166 20M148 30 130 40M148 30 166 40" class="sc-line"/>'
    + '<path d="M0 100 100 92 220 102 330 90 400 98V120H0Z" class="sc-near"/>'
    + ''.join(f'<path d="M{x} 100V{y}" class="sc-line"/><path d="M{x} {y} q-14 -2 -18 8M{x} {y} q14 -2 18 8M{x} {y} q0 -10 0 -12" class="sc-line"/>' for x, y in ((40, 72), (360, 68)))
    + _g(300, 52, 0.7, MISSILE, 35).replace('<g ', '<g class="sc-gold" '))
SCENES['IX'] = ('fire', _sun(330, 78, 14)
    + ''.join(f'<rect x="{x}" y="{y}" width="24" height="9" class="sc-brick"/>' for y in range(40, 112, 9) for x in range(-12 + (12 if (y // 9) % 2 else 0), 400, 24) if not (150 < x < 230 and y < 100))
    + '<path d="M150 112 160 70 180 82 200 54 220 78 240 112Z" class="sc-gap"/><path d="M190 108 196 80 206 90 212 70 218 108Z" class="sc-gold"/>'
    + '<path d="M300 12 340 90M340 12 300 90" class="sc-beam"/>')
SCENES['X'] = ('dusk', _sun(60, 80, 14) + '<path d="M0 100H400V120H0Z" class="sc-near"/>'
    + ''.join(f'<rect x="{x}" y="{100 - h}" width="{w}" height="{h}" class="sc-near"/>' for x, h, w in ((120, 36, 14), (136, 56, 12), (150, 30, 16), (168, 70, 10), (180, 44, 14), (196, 28, 18), (216, 62, 12), (230, 38, 14)))
    + '<path d="M300 100V76M280 76q20 -20 40 0Z" class="sc-near"/><path d="M300 76 320 60" class="sc-line"/><circle cx="322" cy="58" r="3" class="sc-gold"/>'
    + _plane(290, 34, 0.32, 80) + _plane(340, 24, 0.26, 80) + '<path d="M80 40h40M100 40v8M92 48h16" class="sc-line"/>')
SCENES['XI'] = ('day', _sun(340, 30, 10) + _sea(86) + _g(180, 94, 1.1, CONTAINER)
    + '<path d="M60 20 340 20" class="sc-wire"/>' + ''.join(f'<circle cx="{x}" cy="{y}" r="2.6" class="sc-gold"/>' for x, y in ((90, 18), (150, 26), (230, 14), (300, 24)))
    + '<path d="M90 18 150 26 230 14 300 24" class="sc-wire"/><path d="M30 86V58M24 58h12l-6-10Z" class="sc-line"/>')

def scene_html(c):
    sky, inner = SCENES[c]
    return (f'<svg class="card-art" viewBox="0 0 400 120" preserveAspectRatio="xMaxYMid slice" aria-hidden="true" focusable="false">'
            f'<rect width="400" height="120" fill="url(#sky-{sky})"/>{inner}</svg>')

def frontispiece_html():
    return ('<div class="cmd-sea" aria-hidden="true"><svg viewBox="0 0 800 70" preserveAspectRatio="none">'
            '<g class="cmd-sea-a">' + _waves(40, n=41, amp=5).replace('class="sc-wave"', 'class="sc-wave2"') + '</g>'
            '<g class="cmd-sea-b">' + _waves(52, n=41, amp=4).replace('class="sc-wave"', 'class="sc-wave3"') + '</g></svg>'
            '<div class="cmd-ship"><svg viewBox="-70 -60 140 70">' + f'<g class="sc-silhouette">{SAIL}</g></svg></div></div>')
