"""Procedural images as SVG.

Nothing here is a real photograph. Logos, portraits, products, landscapes,
charts, and maps are all drawn from seeds, so the same seed always gives the
same picture. Some images carry text (model numbers, prices, signs) that
appears nowhere else on the page, which makes them useful for multimodal
retrieval tasks.
"""
import math

from .rng import stream, short_hash
from .web import esc

PALETTES = [
    ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
    ["#22223b", "#4a4e69", "#9a8c98", "#c9ada7", "#f2e9e4"],
    ["#003049", "#d62828", "#f77f00", "#fcbf49", "#eae2b7"],
    ["#606c38", "#283618", "#fefae0", "#dda15e", "#bc6c25"],
    ["#0b132b", "#1c2541", "#3a506b", "#5bc0be", "#6fffe9"],
    ["#5f0f40", "#9a031e", "#fb8b24", "#e36414", "#0f4c5c"],
    ["#10002b", "#3c096c", "#7b2cbf", "#c77dff", "#e0aaff"],
    ["#2b2d42", "#8d99ae", "#edf2f4", "#ef233c", "#d90429"],
    ["#1b4332", "#2d6a4f", "#52b788", "#95d5b2", "#d8f3dc"],
    ["#582f0e", "#7f4f24", "#936639", "#a68a64", "#b6ad90"],
]


def palette(seed):
    return stream("palette", seed).choice(PALETTES)


def wrap(w, h, inner, bg=None, title=None):
    t = f"<title>{esc(title)}</title>" if title else ""
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}">{t}{b}{inner}</svg>')


def text(x, y, s, size=14, fill="#000", anchor="start", weight="normal", family="sans-serif",
         extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="{family}" {extra}>{esc(s)}</text>')


# ---------------------------------------------------------------------------
# Logos
# ---------------------------------------------------------------------------
def logo(name, seed=None, w=240, h=64, colors=None, style=None, family="Georgia, serif"):
    rng = stream("logo", seed or name)
    pal = colors or palette(seed or name)
    style = style if style is not None else rng.randrange(5)
    mark_c, text_c = pal[0], pal[1] if len(pal) > 1 else "#222"
    mark = ""
    cx, cy, r = 32, h / 2, h / 2 - 8
    if style == 0:
        mark = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{mark_c}"/>' + \
               text(cx, cy + 7, name[0], 22, "#fff", "middle", "bold", family)
    elif style == 1:
        pts = " ".join(f"{cx + r * math.cos(a * math.pi / 3):.1f},{cy + r * math.sin(a * math.pi / 3):.1f}"
                       for a in range(6))
        mark = f'<polygon points="{pts}" fill="{mark_c}"/>' + \
               text(cx, cy + 7, name[0], 20, "#fff", "middle", "bold", family)
    elif style == 2:
        mark = (f'<rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" rx="6" '
                f'fill="{mark_c}"/><path d="M{cx - r + 6},{cy + 4} L{cx},{cy - r + 8} '
                f'L{cx + r - 6},{cy + 4}" stroke="#fff" stroke-width="4" fill="none"/>')
    elif style == 3:
        mark = "".join(f'<circle cx="{cx - 10 + i * 10}" cy="{cy}" r="{9 - i}" fill="{c}"/>'
                       for i, c in enumerate(pal[:3]))
    else:
        mark = (f'<path d="M{cx},{cy - r} Q{cx + r},{cy} {cx},{cy + r} Q{cx - r},{cy} {cx},{cy - r}" '
                f'fill="{mark_c}"/>')
    label = text(64, cy + 8, name, 22, text_c, weight="bold", family=family)
    return wrap(w, h, mark + label, title=name)


def flag(nation):
    """Flags of the five nations."""
    w, h = 90, 60
    if nation == "VEY":
        inner = ('<rect width="90" height="60" fill="#6b2d5c"/>'
                 + "".join(f'<path d="M{8 + i * 9},46 q4,-8 8,0" stroke="#e8c547" stroke-width="2.5" '
                           f'fill="none"/>' for i in range(9))
                 + '<circle cx="45" cy="22" r="9" fill="#e8c547"/>')
    elif nation == "SLT":
        inner = ('<rect width="90" height="60" fill="#1f4e79"/>'
                 '<rect y="24" width="90" height="12" fill="#f2f2f2"/>'
                 '<path d="M10,50 L20,40 L30,50 L40,40 L50,50 L60,40 L70,50 L80,40" '
                 'stroke="#f2f2f2" stroke-width="2" fill="none"/>')
    elif nation == "KHR":
        inner = ('<rect width="90" height="60" fill="#3d3d3d"/>'
                 '<polygon points="0,60 30,18 45,34 60,12 90,60" fill="#d4652f"/>'
                 '<rect x="42" y="40" width="6" height="20" fill="#3d3d3d"/>')
    elif nation == "PEL":
        inner = ('<rect width="90" height="60" fill="#0f766e"/>'
                 '<circle cx="45" cy="30" r="14" fill="#fde68a"/>'
                 '<circle cx="45" cy="30" r="20" fill="none" stroke="#fde68a" stroke-width="2" '
                 'stroke-dasharray="3 4"/>')
    else:
        inner = ('<rect width="90" height="60" fill="#e5e7eb"/>'
                 '<path d="M45,10 C55,25 52,38 45,50 C38,38 35,25 45,10 Z" fill="#1e3a8a"/>')
    return wrap(w, h, inner, title=f"Flag of {nation}")


# ---------------------------------------------------------------------------
# Portraits
# ---------------------------------------------------------------------------
SKIN = ["#f1c7a5", "#e0ac69", "#c68642", "#8d5524", "#ffdbac", "#d7a17a", "#a26d4f"]
HAIR = ["#2c1b10", "#5a3825", "#b55239", "#e6c07b", "#8f8f8f", "#1b1b1b", "#d9d9d9", "#704214"]


def portrait(seed, w=160, h=160, bg=None, label=None):
    rng = stream("face", seed)
    skin, hair = rng.choice(SKIN), rng.choice(HAIR)
    bg = bg or rng.choice(["#dbeafe", "#fee2e2", "#dcfce7", "#fef9c3", "#ede9fe", "#e0f2fe",
                           "#fae8ff", "#f5f5f4"])
    cx = w / 2
    face_w = w * rng.uniform(0.26, 0.32)
    face_h = h * rng.uniform(0.32, 0.38)
    fy = h * 0.46
    shirt = rng.choice(["#1f2937", "#7c2d12", "#1e3a8a", "#065f46", "#6b21a8", "#9f1239",
                        "#374151", "#b45309"])
    parts = [f'<rect width="{w}" height="{h}" fill="{bg}"/>',
             f'<ellipse cx="{cx}" cy="{h * 1.02}" rx="{w * 0.42}" ry="{h * 0.3}" fill="{shirt}"/>',
             f'<rect x="{cx - w * 0.07}" y="{fy + face_h * 0.7}" width="{w * 0.14}" height="{h * 0.14}" '
             f'fill="{skin}"/>']
    hs = rng.randrange(4)
    if hs == 0:  # long
        parts.append(f'<ellipse cx="{cx}" cy="{fy + 10}" rx="{face_w * 1.25}" ry="{face_h * 1.25}" '
                     f'fill="{hair}"/>')
    elif hs == 1:  # bun
        parts.append(f'<circle cx="{cx}" cy="{fy - face_h * 1.05}" r="{face_w * 0.45}" fill="{hair}"/>')
    parts.append(f'<ellipse cx="{cx}" cy="{fy}" rx="{face_w}" ry="{face_h}" fill="{skin}"/>')
    if hs != 3:
        top = fy - face_h * 1.12
        parts.append(f'<path d="M{cx - face_w * 1.05},{fy - face_h * 0.2} Q{cx - face_w * 1.1},{top} '
                     f'{cx},{top} Q{cx + face_w * 1.1},{top} {cx + face_w * 1.05},{fy - face_h * 0.2} '
                     f'Q{cx + face_w * 0.7},{fy - face_h * 0.75} {cx},{fy - face_h * 0.62} '
                     f'Q{cx - face_w * 0.7},{fy - face_h * 0.75} {cx - face_w * 1.05},{fy - face_h * 0.2}Z" '
                     f'fill="{hair}"/>')
    if rng.random() < 0.25:  # beard
        parts.append(f'<path d="M{cx - face_w * 0.95},{fy + face_h * 0.1} Q{cx - face_w * 0.8},{fy + face_h * 1.25} '
                     f'{cx},{fy + face_h * 1.2} Q{cx + face_w * 0.8},{fy + face_h * 1.25} {cx + face_w * 0.95},{fy + face_h * 0.1} '
                     f'Q{cx},{fy + face_h * 0.55} {cx - face_w * 0.95},{fy + face_h * 0.1}Z" fill="{hair}"/>')
    ey = fy - face_h * 0.1
    for dx in (-1, 1):
        parts.append(f'<ellipse cx="{cx + dx * face_w * 0.4}" cy="{ey}" rx="{w * 0.022}" '
                     f'ry="{w * 0.027}" fill="#222"/>')
        parts.append(f'<path d="M{cx + dx * face_w * 0.4 - w * 0.04},{ey - w * 0.05} q{w * 0.04},{-w * 0.02} {w * 0.08},0" '
                     f'stroke="{hair}" stroke-width="2.5" fill="none"/>')
    if rng.random() < 0.3:  # spectacles
        for dx in (-1, 1):
            parts.append(f'<circle cx="{cx + dx * face_w * 0.4}" cy="{ey}" r="{w * 0.06}" fill="none" '
                         f'stroke="#333" stroke-width="2"/>')
        parts.append(f'<line x1="{cx - face_w * 0.4 + w * 0.06}" y1="{ey}" x2="{cx + face_w * 0.4 - w * 0.06}" y2="{ey}" '
                     f'stroke="#333" stroke-width="2"/>')
    parts.append(f'<path d="M{cx},{ey + 4} l-{w * 0.02},{face_h * 0.3} h{w * 0.03}" stroke="#00000033" '
                 f'stroke-width="2" fill="none"/>')
    my = fy + face_h * 0.5
    curve = rng.uniform(1, 8)
    parts.append(f'<path d="M{cx - face_w * 0.3},{my} Q{cx},{my + curve} {cx + face_w * 0.3},{my}" '
                 f'stroke="#7a3b2e" stroke-width="2.5" fill="none" stroke-linecap="round"/>')
    if label:
        parts.append(f'<rect x="0" y="{h - 22}" width="{w}" height="22" fill="rgba(0,0,0,.55)"/>')
        parts.append(text(cx, h - 7, label, 11, "#fff", "middle"))
    return wrap(w, h, "".join(parts))


# ---------------------------------------------------------------------------
# Landscapes
# ---------------------------------------------------------------------------
def landscape(seed, kind="hills", w=640, h=360, caption=None, sign=None):
    """Kinds: hills, sea, mountains, moor, city, marsh, night."""
    rng = stream("land", seed)
    night = kind == "night" or rng.random() < 0.12
    if night:
        sky = ("#0b1026", "#28305a")
    else:
        sky = rng.choice([("#9ecfff", "#e8f4ff"), ("#f7b267", "#fde2c0"), ("#a0c4ff", "#fdfcdc"),
                          ("#cfd8dc", "#eceff1"), ("#ffcad4", "#f3e8ff")])
    gid = f"g{short_hash(seed)}"
    parts = [f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{sky[0]}"/><stop offset="1" stop-color="{sky[1]}"/>'
             f'</linearGradient></defs>', f'<rect width="{w}" height="{h}" fill="url(#{gid})"/>']
    # two moons: Ossa (large) and Pith (small)
    ox, oy = rng.uniform(0.15, 0.85) * w, rng.uniform(0.1, 0.3) * h
    parts.append(f'<circle cx="{ox:.0f}" cy="{oy:.0f}" r="{h * 0.07:.0f}" fill="#f5f1e0" '
                 f'opacity="{0.95 if night else 0.55}"/>')
    parts.append(f'<circle cx="{ox + rng.uniform(-160, 160):.0f}" cy="{oy + rng.uniform(-10, 40):.0f}" '
                 f'r="{h * 0.022:.0f}" fill="#e7d7c1" opacity="{0.95 if night else 0.5}"/>')
    if night:
        for _ in range(40):
            parts.append(f'<circle cx="{rng.uniform(0, w):.0f}" cy="{rng.uniform(0, h * 0.5):.0f}" '
                         f'r="{rng.uniform(0.5, 1.5):.1f}" fill="#fff"/>')
    layers = 3
    base_cols = {
        "hills": ["#6a994e", "#386641", "#a7c957"], "mountains": ["#6c757d", "#495057", "#adb5bd"],
        "moor": ["#8a7f5a", "#6b5e3c", "#b7a86b"], "sea": ["#2a6f97", "#014f86", "#61a5c2"],
        "city": ["#6d6875", "#4a4e69", "#9a8c98"], "marsh": ["#7a8b5a", "#5c6b40", "#9aad6f"],
        "night": ["#1b263b", "#0d1b2a", "#415a77"],
    }.get(kind, ["#6a994e", "#386641", "#a7c957"])
    for i in range(layers):
        col = base_cols[(i + 2) % 3] if not night else ["#1b263b", "#0d1b2a", "#415a77"][i]
        y0 = h * (0.45 + i * 0.15)
        amp = h * (0.18 if kind == "mountains" and i == 0 else 0.06)
        pts = [f"0,{h}"]
        steps = 12
        for s in range(steps + 1):
            x = s * w / steps
            y = y0 - amp * (rng.random() if kind == "mountains" else math.sin(s * 0.9 + rng.random()))
            pts.append(f"{x:.0f},{y:.0f}")
        pts.append(f"{w},{h}")
        parts.append(f'<polygon points="{" ".join(pts)}" fill="{col}"/>')
        if kind == "sea" and i == 0:
            for _ in range(12):
                x, y = rng.uniform(0, w), rng.uniform(h * 0.5, h)
                parts.append(f'<path d="M{x:.0f},{y:.0f} q8,-5 16,0" stroke="#cde" fill="none"/>')
    if kind == "city":
        x = 0
        while x < w:
            bw, bh = rng.uniform(20, 60), rng.uniform(40, 180)
            parts.append(f'<rect x="{x:.0f}" y="{h - bh:.0f}" width="{bw:.0f}" height="{bh:.0f}" '
                         f'fill="{rng.choice(["#3d405b", "#4a4e69", "#22223b"])}"/>')
            for wy in range(int(h - bh + 8), h - 8, 14):
                for wx in range(int(x + 5), int(x + bw - 6), 10):
                    if rng.random() < 0.4:
                        parts.append(f'<rect x="{wx}" y="{wy}" width="4" height="6" fill="#ffd166"/>')
            x += bw + rng.uniform(0, 6)
    if kind == "sea" and rng.random() < 0.7:
        # a lighthouse
        lx = rng.uniform(0.1, 0.8) * w
        parts.append(f'<polygon points="{lx},{h * 0.62} {lx + 14},{h * 0.62} {lx + 10},{h * 0.3} '
                     f'{lx + 4},{h * 0.3}" fill="#f8f9fa" stroke="#c00" stroke-width="3" '
                     f'stroke-dasharray="10 10"/>')
        parts.append(f'<circle cx="{lx + 7}" cy="{h * 0.28}" r="5" fill="#ffd166"/>')
    if sign:
        sx, sy = w * 0.62, h * 0.66
        parts.append(f'<rect x="{sx - 4}" y="{sy + 20}" width="6" height="{h * 0.3}" fill="#5c4033"/>')
        parts.append(f'<rect x="{sx - 90}" y="{sy - 20}" width="180" height="44" fill="#fdf6e3" '
                     f'stroke="#5c4033" stroke-width="3"/>')
        lines = sign.split("\n")
        for i, ln in enumerate(lines[:2]):
            parts.append(text(sx, sy - 2 + i * 17, ln, 14, "#3b2f2f", "middle", "bold", "Georgia, serif"))
    if caption:
        parts.append(f'<rect x="0" y="{h - 26}" width="{w}" height="26" fill="rgba(0,0,0,.45)"/>')
        parts.append(text(10, h - 9, caption, 13, "#fff"))
    return wrap(w, h, "".join(parts))


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
def product(kind, seed, label=None, w=300, h=300):
    rng = stream("prod", seed)
    pal = palette(seed)
    main, accent = rng.choice(pal[:3]), rng.choice(pal[2:])
    bg = "#f7f7f5"
    p = [f'<rect width="{w}" height="{h}" fill="{bg}"/>',
         f'<ellipse cx="150" cy="262" rx="95" ry="12" fill="#e2e2dd"/>']
    k = kind
    if k in ("kettle", "teapot"):
        p += [f'<ellipse cx="150" cy="180" rx="80" ry="72" fill="{main}"/>',
              f'<path d="M225,170 q45,-10 50,-60" stroke="{main}" stroke-width="14" fill="none"/>',
              f'<path d="M100,120 q50,-70 100,0" stroke="{accent}" stroke-width="10" fill="none"/>',
              f'<rect x="130" y="100" width="40" height="14" rx="6" fill="{accent}"/>']
    elif k in ("lamp",):
        p += [f'<polygon points="95,90 205,90 180,40 120,40" fill="{accent}"/>',
              f'<rect x="143" y="90" width="14" height="130" fill="{main}"/>',
              f'<ellipse cx="150" cy="235" rx="60" ry="18" fill="{main}"/>',
              '<circle cx="150" cy="100" r="16" fill="#fff5b8"/>']
    elif k in ("slate", "loom"):
        p += [f'<rect x="95" y="40" width="110" height="210" rx="16" fill="#1f2937"/>',
              f'<rect x="103" y="54" width="94" height="170" rx="6" fill="{main}"/>',
              '<circle cx="150" cy="236" r="6" fill="#6b7280"/>']
    elif k in ("book",):
        p += [f'<rect x="85" y="50" width="130" height="190" fill="{main}"/>',
              f'<rect x="85" y="50" width="14" height="190" fill="{accent}"/>',
              f'<rect x="110" y="90" width="90" height="4" fill="#fff"/>',
              f'<rect x="110" y="102" width="70" height="4" fill="#fff"/>']
    elif k in ("boots", "shoes"):
        p += [f'<path d="M70,90 h60 v110 h90 q20,0 20,30 v10 h-170 z" fill="{main}"/>',
              f'<rect x="70" y="225" width="170" height="16" fill="{accent}"/>']
    elif k in ("coat", "shirt", "scarf"):
        p += [f'<path d="M100,50 l50,20 l50,-20 l45,40 l-25,30 l-15,-12 v140 h-110 v-140 l-15,12 '
              f'l-25,-30 z" fill="{main}"/>',
              f'<line x1="150" y1="70" x2="150" y2="248" stroke="{accent}" stroke-width="4"/>']
    elif k in ("jar", "preserve", "spice", "tea"):
        p += [f'<rect x="100" y="90" width="100" height="150" rx="14" fill="{main}" opacity=".85"/>',
              f'<rect x="95" y="70" width="110" height="26" rx="4" fill="{accent}"/>',
              '<rect x="112" y="140" width="76" height="50" fill="#fffdf5"/>']
    elif k in ("telescope",):
        p += [f'<rect x="60" y="100" width="190" height="34" rx="6" fill="{main}" '
              f'transform="rotate(-20 150 117)"/>',
              f'<line x1="150" y1="130" x2="110" y2="250" stroke="{accent}" stroke-width="6"/>',
              f'<line x1="150" y1="130" x2="190" y2="250" stroke="{accent}" stroke-width="6"/>',
              f'<line x1="150" y1="130" x2="150" y2="255" stroke="{accent}" stroke-width="6"/>']
    elif k in ("clock", "watch"):
        p += [f'<circle cx="150" cy="150" r="95" fill="{main}"/>',
              '<circle cx="150" cy="150" r="80" fill="#fffdf5"/>',
              f'<line x1="150" y1="150" x2="150" y2="90" stroke="#222" stroke-width="5"/>',
              f'<line x1="150" y1="150" x2="195" y2="165" stroke="{accent}" stroke-width="4"/>']
    elif k in ("record",):
        p += ['<circle cx="150" cy="150" r="100" fill="#111"/>',
              f'<circle cx="150" cy="150" r="36" fill="{main}"/>',
              '<circle cx="150" cy="150" r="4" fill="#f7f7f5"/>']
    elif k in ("chair",):
        p += [f'<rect x="100" y="40" width="100" height="110" fill="{main}"/>',
              f'<rect x="90" y="150" width="120" height="20" fill="{accent}"/>',
              f'<rect x="95" y="170" width="10" height="80" fill="{main}"/>',
              f'<rect x="195" y="170" width="10" height="80" fill="{main}"/>']
    elif k in ("bag", "backpack"):
        p += [f'<rect x="85" y="90" width="130" height="150" rx="20" fill="{main}"/>',
              f'<path d="M115,90 q35,-60 70,0" stroke="{accent}" stroke-width="10" fill="none"/>',
              f'<rect x="110" y="150" width="80" height="50" rx="8" fill="{accent}"/>']
    elif k in ("plant",):
        p += [f'<polygon points="110,170 190,170 178,250 122,250" fill="{accent}"/>',
              *[f'<ellipse cx="{150 + dx}" cy="{120 + dy}" rx="18" ry="40" fill="#3a7d44" '
                f'transform="rotate({dx} {150 + dx} {120 + dy})"/>'
                for dx, dy in ((-30, 10), (0, -10), (30, 10), (-15, 20), (15, 20))]]
    elif k in ("candle", "soap"):
        p += [f'<rect x="115" y="110" width="70" height="130" fill="{main}"/>',
              '<path d="M150,70 q12,20 0,36 q-12,-16 0,-36" fill="#ffb703"/>']
    elif k in ("game", "toy"):
        p += [f'<rect x="70" y="80" width="160" height="130" fill="{main}"/>',
              f'<rect x="70" y="80" width="160" height="30" fill="{accent}"/>',
              '<circle cx="150" cy="165" r="28" fill="#fff" opacity=".8"/>']
    else:
        p += [f'<rect x="90" y="80" width="120" height="160" rx="10" fill="{main}"/>',
              f'<rect x="90" y="80" width="120" height="30" rx="10" fill="{accent}"/>']
    if label:
        p.append(f'<rect x="8" y="8" width="{min(284, 12 + len(label) * 8)}" height="24" rx="4" '
                 f'fill="#fff" stroke="#ccc"/>')
        p.append(text(14, 25, label, 13, "#333", family="monospace"))
    return wrap(w, h, "".join(p))


def house(seed, w=480, h=320, sign=None):
    rng = stream("house", seed)
    wall = rng.choice(["#e9d8a6", "#f4f1de", "#d6ccc2", "#b5838d", "#a3b18a", "#cdb4db"])
    roof = rng.choice(["#6b4226", "#3d405b", "#7f5539", "#343a40", "#9b2226"])
    p = [f'<rect width="{w}" height="{h}" fill="#bde0fe"/>',
         f'<rect y="{h * 0.72}" width="{w}" height="{h * 0.28}" fill="#90be6d"/>']
    floors = rng.randint(1, 3)
    bw = rng.uniform(200, 320)
    bx = (w - bw) / 2
    fh = 62
    top = h * 0.75 - floors * fh
    p.append(f'<rect x="{bx:.0f}" y="{top:.0f}" width="{bw:.0f}" height="{floors * fh}" fill="{wall}" '
             f'stroke="#555"/>')
    p.append(f'<polygon points="{bx - 15:.0f},{top:.0f} {bx + bw / 2:.0f},{top - rng.uniform(40, 90):.0f} '
             f'{bx + bw + 15:.0f},{top:.0f}" fill="{roof}"/>')
    for f in range(floors):
        n = int(bw // 60)
        for i in range(n):
            wx = bx + 20 + i * (bw - 40) / max(1, n - 1) - 12 if n > 1 else bx + bw / 2 - 12
            wy = top + f * fh + 16
            p.append(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="24" height="28" fill="#e0fbfc" '
                     f'stroke="#555"/>')
    p.append(f'<rect x="{bx + bw / 2 - 14:.0f}" y="{h * 0.75 - 44:.0f}" width="28" height="44" '
             f'fill="{roof}"/>')
    if rng.random() < 0.5:
        p.append(f'<rect x="{bx + bw * 0.75:.0f}" y="{top - 60:.0f}" width="16" height="40" fill="#6c584c"/>')
    if sign:
        p.append(f'<rect x="{w - 150}" y="{h - 70}" width="130" height="36" fill="#fff" stroke="#c1121f" '
                 f'stroke-width="3"/>')
        p.append(text(w - 85, h - 47, sign, 13, "#c1121f", "middle", "bold"))
    return wrap(w, h, "".join(p))


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
def line_chart(values, w=640, h=260, color="#1d4ed8", labels=None, title=None, y_fmt="{:.2f}",
               fill=True):
    pad_l, pad_r, pad_t, pad_b = 56, 16, 28 if title else 12, 28
    lo, hi = min(values), max(values)
    if hi == lo:
        hi = lo + 1
    span = hi - lo
    lo -= span * 0.08
    hi += span * 0.08
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b

    def X(i):
        return pad_l + iw * i / max(1, len(values) - 1)

    def Y(v):
        return pad_t + ih * (1 - (v - lo) / (hi - lo))

    p = [f'<rect width="{w}" height="{h}" fill="#fff"/>']
    if title:
        p.append(text(pad_l, 18, title, 13, "#111", weight="bold"))
    for i in range(5):
        v = lo + (hi - lo) * i / 4
        y = Y(v)
        p.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w - pad_r}" y2="{y:.1f}" stroke="#eee"/>')
        p.append(text(pad_l - 6, y + 4, y_fmt.format(v), 10, "#666", "end"))
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(values))
    if fill:
        p.append(f'<polygon points="{pad_l},{pad_t + ih} {pts} {X(len(values) - 1):.1f},{pad_t + ih}" '
                 f'fill="{color}" opacity=".12"/>')
    p.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"/>')
    if labels:
        step = max(1, len(labels) // 6)
        for i in range(0, len(labels), step):
            p.append(text(X(i), h - 8, labels[i], 10, "#666", "middle"))
    return wrap(w, h, "".join(p))


def bar_chart(pairs, w=640, h=260, color="#0f766e", title=None, y_fmt="{:.0f}", color2=None,
              pairs2=None):
    pad_l, pad_r, pad_t, pad_b = 48, 12, 28 if title else 12, 30
    vals = [v for _, v in pairs] + ([v for _, v in pairs2] if pairs2 else [])
    hi = max(vals + [1]) * 1.1
    lo = min(0, min(vals))
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
    n = len(pairs)
    bw = iw / n * (0.4 if pairs2 else 0.7)
    p = [f'<rect width="{w}" height="{h}" fill="#fff"/>']
    if title:
        p.append(text(pad_l, 18, title, 13, "#111", weight="bold"))

    def Y(v):
        return pad_t + ih * (1 - (v - lo) / (hi - lo))

    for i in range(5):
        v = lo + (hi - lo) * i / 4
        p.append(f'<line x1="{pad_l}" y1="{Y(v):.1f}" x2="{w - pad_r}" y2="{Y(v):.1f}" stroke="#eee"/>')
        p.append(text(pad_l - 6, Y(v) + 4, y_fmt.format(v), 10, "#666", "end"))
    for i, (lab, v) in enumerate(pairs):
        x = pad_l + iw * (i + 0.5) / n - (bw if pairs2 else bw / 2)
        p.append(f'<rect x="{x:.1f}" y="{min(Y(v), Y(0)):.1f}" width="{bw:.1f}" '
                 f'height="{abs(Y(0) - Y(v)):.1f}" fill="{color}"><title>{esc(lab)}: {esc(y_fmt.format(v))}</title></rect>')
        if pairs2:
            v2 = pairs2[i][1]
            p.append(f'<rect x="{x + bw:.1f}" y="{min(Y(v2), Y(0)):.1f}" width="{bw:.1f}" '
                     f'height="{abs(Y(0) - Y(v2)):.1f}" fill="{color2 or "#f59e0b"}"/>')
        p.append(text(pad_l + iw * (i + 0.5) / n, h - 10, lab, 10, "#444", "middle"))
    return wrap(w, h, "".join(p))


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
def moons(ossa_phase, pith_phase, w=320, h=160, label=None):
    """Phases in [0,1): 0 new, 0.5 full."""
    def disc(cx, cy, r, phase, col):
        lit = 1 - abs(phase - 0.5) * 2  # 0 new .. 1 full
        # draw dark disc, then lit ellipse part
        rx = abs(1 - 2 * lit) * r
        side = 1 if phase < 0.5 else -1
        return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#2d3142"/>'
                f'<path d="M{cx},{cy - r} A{r},{r} 0 0 {1 if side > 0 else 0} {cx},{cy + r} '
                f'A{rx:.1f},{r} 0 0 {1 if (lit < 0.5) == (side > 0) else 0} {cx},{cy - r}Z" fill="{col}"/>')
    p = [f'<rect width="{w}" height="{h}" fill="#0b1026"/>',
         disc(w * 0.32, h * 0.5, h * 0.33, ossa_phase, "#f5f1e0"),
         disc(w * 0.75, h * 0.5, h * 0.14, pith_phase, "#e7d7c1"),
         text(w * 0.32, h - 8, "Ossa", 11, "#ccc", "middle"),
         text(w * 0.75, h - 8, "Pith", 11, "#ccc", "middle")]
    if label:
        p.append(text(8, 16, label, 12, "#fff"))
    return wrap(w, h, "".join(p))


def comic_panel(seed, lines, w=300, h=260, chars=2):
    """A single comic panel with a squid, a person, and speech balloons."""
    rng = stream("panel", seed)
    bg = rng.choice(["#fff7e6", "#eef6ff", "#f3f0ff", "#effaf0"])
    p = [f'<rect width="{w}" height="{h}" fill="{bg}" stroke="#111" stroke-width="3"/>']
    # bookshelves
    for i in range(3):
        y = 150 + i * 30
        p.append(f'<rect x="10" y="{y}" width="{w - 20}" height="4" fill="#8d6e63"/>')
        x = 14
        while x < w - 24:
            bw = rng.randint(6, 12)
            p.append(f'<rect x="{x}" y="{y - rng.randint(16, 24)}" width="{bw}" height="24" '
                     f'fill="{rng.choice(["#c0392b", "#2980b9", "#27ae60", "#8e44ad", "#d35400"])}"/>')
            x += bw + 2
    # squid (Inkling)
    sx = 80
    p.append(f'<ellipse cx="{sx}" cy="120" rx="30" ry="40" fill="#b388eb"/>')
    for i in range(5):
        p.append(f'<path d="M{sx - 22 + i * 11},150 q{rng.randint(-8, 8)},20 {rng.randint(-6, 6)},34" '
                 f'stroke="#b388eb" stroke-width="7" fill="none" stroke-linecap="round"/>')
    p.append(f'<circle cx="{sx - 10}" cy="115" r="6" fill="#fff"/><circle cx="{sx - 10}" cy="115" r="3"/>')
    p.append(f'<circle cx="{sx + 10}" cy="115" r="6" fill="#fff"/><circle cx="{sx + 10}" cy="115" r="3"/>')
    if chars > 1:
        px = 220
        p.append(f'<circle cx="{px}" cy="100" r="22" fill="{rng.choice(SKIN)}"/>')
        p.append(f'<rect x="{px - 22}" y="122" width="44" height="70" rx="10" fill="#34495e"/>')
    y = 24
    for i, ln in enumerate(lines[:2]):
        bx = 10 if i == 0 else w / 2 - 10
        bw = w / 2 + 0
        p.append(f'<rect x="{bx}" y="{y - 16}" width="{bw}" height="{28 + 14 * (len(ln) // 26)}" rx="10" '
                 f'fill="#fff" stroke="#111"/>')
        words = ln.split()
        row, rows = "", []
        for wd in words:
            if len(row) + len(wd) > 24:
                rows.append(row)
                row = wd
            else:
                row = (row + " " + wd).strip()
        rows.append(row)
        for j, r in enumerate(rows):
            p.append(text(bx + 8, y + j * 14, r, 11, "#111", family="Comic Sans MS, cursive"))
        y += 22 + 14 * len(rows)
    return wrap(w, h, "".join(p))


def banner(seed, headline, sub="", w=728, h=90):
    """An advertisement banner."""
    rng = stream("ad", seed)
    pal = palette(seed)
    p = [f'<rect width="{w}" height="{h}" fill="{pal[0]}"/>',
         f'<circle cx="{w - 60}" cy="{h / 2}" r="{h}" fill="{pal[2]}" opacity=".5"/>',
         text(20, h / 2 + 2, headline, 26 if len(headline) < 30 else 20, "#fff", weight="bold"),
         text(20, h / 2 + 26, sub, 13, pal[4] if len(pal) > 4 else "#fff")]
    if rng.random() < 0.5:
        p.append(f'<rect x="{w - 150}" y="{h / 2 - 18}" width="120" height="36" rx="18" fill="{pal[3]}"/>')
        p.append(text(w - 90, h / 2 + 5, "Click now", 14, "#111", "middle", "bold"))
    return wrap(w, h, "".join(p))
