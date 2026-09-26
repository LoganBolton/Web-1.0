"""Drawing the chart of Averra."""
from ..world.geo import CITIES, CITY, NATIONS
from .svg import wrap, text

LAND = {
    "SLT": [(140, 190), (180, 120), (250, 100), (330, 120), (400, 95), (470, 90), (540, 85),
            (620, 110), (700, 130), (720, 190), (650, 200), (560, 170), (460, 180), (360, 190),
            (260, 190), (180, 210)],
    "VEY": [(180, 210), (260, 190), (360, 190), (460, 180), (560, 170), (590, 230), (560, 300),
            (560, 400), (540, 470), (520, 500), (420, 520), (330, 515), (260, 510), (200, 480),
            (150, 430), (130, 350), (140, 260)],
    "KHR": [(560, 170), (650, 200), (720, 190), (780, 170), (790, 250), (770, 330), (740, 400),
            (680, 420), (600, 420), (560, 400), (560, 300), (590, 230)],
    "ODD": [(720, 190), (700, 130), (760, 60), (850, 40), (960, 50), (990, 120), (960, 220),
            (900, 300), (820, 320), (770, 330), (790, 250), (780, 170)],
}
ISLANDS = {
    "SLT": [(380, 60, 34, 16)],
    "PEL": [(565, 612, 80, 30), (440, 622, 34, 16), (682, 640, 30, 14), (762, 600, 26, 13),
            (382, 660, 22, 11)],
}
FILL = {"VEY": "#e9d5e4", "SLT": "#d6e4f0", "KHR": "#e7ddd5", "PEL": "#d5efe9", "ODD": "#eceff3"}
SALLOW = [(575, 260), (520, 300), (470, 330), (400, 345), (330, 360), (300, 420), (280, 490)]
CANAL = [(430, 420), (470, 450), (500, 470), (520, 500)]


def _poly(pts):
    return " ".join(f"{x},{y}" for x, y in pts)


def world_map(w=1000, h=700, highlight=None, routes=(), show_labels=True, only=None,
              label_landmarks=False, scale=True):
    p = [f'<rect width="{w}" height="{h}" fill="#a8d5e2"/>']
    for code, pts in LAND.items():
        op = "1" if not only or code == only else ".45"
        p.append(f'<polygon points="{_poly(pts)}" fill="{FILL[code]}" stroke="#7a8a99" '
                 f'stroke-width="1.5" opacity="{op}"/>')
    for code, isl in ISLANDS.items():
        op = "1" if not only or code == only else ".45"
        for x, y, rx, ry in isl:
            p.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{FILL[code]}" '
                     f'stroke="#7a8a99" stroke-width="1.5" opacity="{op}"/>')
    # the Kethren Spine
    for i, (x, y) in enumerate([(600, 190), (630, 240), (660, 210), (690, 280), (660, 330),
                                (710, 340), (620, 350), (740, 260), (700, 200)]):
        p.append(f'<polygon points="{x - 12},{y + 10} {x},{y - 12} {x + 12},{y + 10}" '
                 f'fill="#a1887f" stroke="#6d4c41"/>')
    p.append(f'<polyline points="{_poly(SALLOW)}" fill="none" stroke="#5dade2" stroke-width="3"/>')
    p.append(f'<polyline points="{_poly(CANAL)}" fill="none" stroke="#2e86c1" stroke-width="2" '
             f'stroke-dasharray="5 3"/>')
    for x1, y1, x2, y2, col in routes:
        p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="2.5" '
                 f'stroke-dasharray="7 4"/>')
    p.append(text(470, 40, "THE GREY REACH", 16, "#4a6c80", "middle", "bold", "Georgia, serif",
                  'letter-spacing="4"'))
    p.append(text(520, 560, "THE GLASS SEA", 16, "#4a6c80", "middle", "bold", "Georgia, serif",
                  'letter-spacing="4"'))
    p.append(text(700, 412, "Kethren Spine", 11, "#6d4c41", "middle", "normal", "Georgia, serif",
                  'font-style="italic"'))
    p.append(text(385, 338, "R. Sallow", 10, "#2e86c1", "middle", "normal", "Georgia, serif",
                  'font-style="italic"'))
    for c in CITIES:
        if only and c.nation != only:
            continue
        hi = highlight and c.name in highlight
        if c.kind == "capital":
            p.append(f'<rect x="{c.x - 5}" y="{c.y - 5}" width="10" height="10" fill="#b91c1c" '
                     f'stroke="#fff" transform="rotate(45 {c.x} {c.y})"/>')
        else:
            p.append(f'<circle cx="{c.x}" cy="{c.y}" r="{6 if hi else 4}" '
                     f'fill="{"#dc2626" if hi else "#1f2937"}" stroke="#fff"/>')
        if show_labels:
            p.append(text(c.x + 8, c.y + 4, c.name, 12 if hi else 11, "#111",
                          weight="bold" if (hi or c.kind == "capital") else "normal"))
    for code, n in NATIONS.items():
        if code == "PEL":
            x, y = 560, 690
        else:
            xs = [pt[0] for pt in LAND[code]]
            ys = [pt[1] for pt in LAND[code]]
            x, y = sum(xs) / len(xs), sum(ys) / len(ys) + (30 if code == "VEY" else 0)
            if code == "SLT":
                y = 160
        p.append(text(x, y, n.short.upper(), 14, "#555", "middle", "bold", "Georgia, serif",
                      'opacity=".55" letter-spacing="6"'))
    if scale:
        p.append(f'<line x1="40" y1="{h - 30}" x2="140" y2="{h - 30}" stroke="#111" stroke-width="3"/>')
        p.append(text(40, h - 38, "50 leagues", 11, "#111"))
    return wrap(w, h, "".join(p), title="Chart of Averra")


def city_route_line(a, b, color="#b45309"):
    ca, cb = CITY[a], CITY[b]
    return (ca.x, ca.y, cb.x, cb.y, color)
