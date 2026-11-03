"""Slingshot: watch demo launches, predict where a new launch lands.

Hidden physics per world:
  gravity  vector (strength and a possible tilt away from straight down)
  wind     constant sideways acceleration
  drag     linear air drag coefficient (1/s)
  k        launcher strength: launch speed = k * pull distance
"""

from __future__ import annotations

import math

import numpy as np

from ..item import ItemBuild, Option, pick_distractors, pick_keyframes
from ..render import GROUND, GROUND_FILL, INK, Canvas, lighten, with_alpha

W, H = 36.0, 18.0
R_BALL = 0.35
DT = 1 / 1000
FPS = 20
STROBE = 0.1  # seconds between trail dots
PILLAR_W = 0.5
FORK = 0.9  # fork height above the pillar top
BALL = (205, 60, 50)
TRAIL = (205, 60, 50)
DEMO_COLORS = [(60, 120, 210), (40, 160, 110), (170, 90, 200)]


# --------------------------------------------------------------------------
# physics


def sample_world(rng):
    g = float(np.exp(rng.uniform(np.log(2.5), np.log(40.0))))
    tilt = 0.0 if rng.random() < 0.5 else float(rng.choice([-1, 1]) * rng.uniform(8, 30))
    wind = 0.0 if rng.random() < 0.5 else float(rng.choice([-1, 1]) * rng.uniform(0.1, 0.35) * g)
    drag = 0.0 if rng.random() < 0.5 else float(rng.uniform(0.1, 0.5))
    # Pick k so a 1 m pull at 45 deg would fly ~14-26 m in vacuum.
    k = float(math.sqrt(rng.uniform(12, 22) * g))
    return {"g": g, "tilt_deg": tilt, "wind": wind, "drag": drag, "k": k}


def gravity_vec(world):
    a = math.radians(world["tilt_deg"])
    return world["g"] * math.sin(a), -world["g"] * math.cos(a)


def launch_point(shot):
    return shot["x"], shot["h"] + FORK


def simulate(world, shot, tmax=12.0):
    """Return dict with positions sampled every DT, landing info and in-bounds flag."""
    gx, gy = gravity_vec(world)
    gx += world["wind"]
    b = world["drag"]
    th = math.radians(shot["angle"])
    v = world["k"] * shot["pull"]
    x, y = launch_point(shot)
    vx, vy = v * math.cos(th), v * math.sin(th)
    xs, ys = [x], [y]
    t = 0.0
    landed = False
    while t < tmax:
        vx += (gx - b * vx) * DT
        vy += (gy - b * vy) * DT
        x += vx * DT
        y += vy * DT
        t += DT
        if y <= R_BALL and vy < 0:
            y = R_BALL
            xs.append(x)
            ys.append(y)
            landed = True
            break
        xs.append(x)
        ys.append(y)
        if x < -2 or x > W + 2 or y > H + 4:
            break
    xs, ys = np.array(xs), np.array(ys)
    in_bounds = bool(landed and xs.min() > R_BALL and xs.max() < W - R_BALL and ys.max() < H - R_BALL)
    i_apex = int(np.argmax(ys))
    return {
        "x": xs,
        "y": ys,
        "T": len(xs) * DT,
        "landed": landed,
        "in_bounds": in_bounds,
        "landing": (float(xs[-1]), float(ys[-1])),
        "apex": (float(xs[i_apex]), float(ys[i_apex])),
    }


def at_time(sim, t):
    i = min(len(sim["x"]) - 1, int(round(t / DT)))
    return float(sim["x"][i]), float(sim["y"][i])


def rollout_dist(a, b):
    la, lb = np.array(a["landing"]), np.array(b["landing"])
    pa, pb = np.array(a["apex"]), np.array(b["apex"])
    return float(max(np.linalg.norm(la - lb), np.linalg.norm(pa - pb)))


def sample_shot(rng, world, avoid=()):
    for _ in range(400):
        shot = {
            "x": float(rng.uniform(2, 20)),
            "h": float(rng.choice([0.0, rng.uniform(1, 6)])),
            "angle": float(rng.uniform(20, 75)),
            "pull": float(round(rng.uniform(0.5, 1.4), 2)),
        }
        shot["angle"] = float(round(shot["angle"]))
        if any(abs(shot["angle"] - a["angle"]) < 8 and abs(shot["pull"] - a["pull"]) < 0.15 for a in avoid):
            continue
        if any(abs(shot["x"] - a["x"]) < 5 for a in avoid):
            continue
        sim = simulate(world, shot)
        if not sim["in_bounds"] or sim["T"] < 0.7:
            continue
        if abs(sim["landing"][0] - shot["x"]) < 4:
            continue
        return shot, sim
    return None, None


def perturbations(world):
    """Alternative physics used for the wrong options."""
    out = []

    def add(label, desc, **changes):
        w = dict(world)
        w.update(changes)
        out.append((label, desc, w))

    if world["tilt_deg"] or world["wind"] or world["drag"]:
        add("ordinary_physics", "ordinary physics: straight-down gravity, no wind, no drag (same strength + launcher)",
            tilt_deg=0.0, wind=0.0, drag=0.0)
    if abs(world["g"] - 9.81) / 9.81 > 0.35:
        add("earth_gravity", "Earth gravity (9.8 m/s^2), everything else the same", g=9.81)
    add("gravity_x0.5", "gravity half as strong", g=world["g"] * 0.5)
    add("gravity_x2", "gravity twice as strong", g=world["g"] * 2)
    add("launcher_x0.75", "launcher 25% weaker", k=world["k"] * 0.75)
    add("launcher_x1.3", "launcher 30% stronger", k=world["k"] * 1.3)
    add("tilt_plus20", "gravity tilted 20 deg further clockwise", tilt_deg=world["tilt_deg"] + 20)
    add("tilt_minus20", "gravity tilted 20 deg further counter-clockwise", tilt_deg=world["tilt_deg"] - 20)
    if world["wind"]:
        add("wind_flipped", "wind blowing the other way", wind=-world["wind"])
        add("no_wind", "no wind", wind=0.0)
    else:
        add("wind_right", "wind pushing right", wind=0.25 * world["g"])
        add("wind_left", "wind pushing left", wind=-0.25 * world["g"])
    if world["drag"]:
        add("no_drag", "no air drag", drag=0.0)
    else:
        add("heavy_drag", "strong air drag", drag=0.45)
    return out


# --------------------------------------------------------------------------
# drawing


_BG = None


def new_canvas():
    global _BG
    if _BG is None:
        _BG = Canvas(0, -1.0, W, H, 18)
        _BG.grid(label=True)
        _BG.rect(0, -1.0, W, 0, fill=GROUND_FILL)
        _BG.line([(0, 0), (W, 0)], GROUND, 3)
    return _BG.clone()


def draw_slingshot(c, shot, pulled: bool, color=INK, alpha=255, label=True, label_color=INK, tag=""):
    x, h = shot["x"], shot["h"]
    col = with_alpha(color, alpha)
    if h > 0:
        c.rect(x - PILLAR_W / 2, 0, x + PILLAR_W / 2, h, fill=with_alpha(lighten(GROUND, 0.25), alpha))
    fx, fy = launch_point(shot)
    # Y-shaped fork
    c.line([(x, h), (x, h + 0.45)], col, 4)
    lp, rp = (x - 0.4, fy + 0.1), (x + 0.4, fy + 0.1)
    c.line([(x, h + 0.45), lp], col, 4)
    c.line([(x, h + 0.45), rp], col, 4)
    th = math.radians(shot["angle"])
    if pulled:
        bx, by = fx - shot["pull"] * math.cos(th), fy - shot["pull"] * math.sin(th)
        band = with_alpha((120, 70, 40), alpha)
        c.line([lp, (bx, by)], band, 2.5)
        c.line([rp, (bx, by)], band, 2.5)
        c.circle(bx, by, R_BALL, fill=with_alpha(BALL, alpha))
        # aim arrow (direction only, fixed length)
        c.arrow((fx, fy), (fx + 2.2 * math.cos(th), fy + 2.2 * math.sin(th)), with_alpha((90, 90, 90), alpha), 1.5)
    else:
        c.line([lp, rp], with_alpha((120, 70, 40), alpha), 2)
    if label:
        c.text(x, h + FORK + 1.6, f"{tag}pull {shot['pull']:.2f} m @ {shot['angle']:.0f}°",
               size=11, color=with_alpha(label_color, alpha), bg=(255, 255, 255, int(0.85 * alpha)))


def draw_trail(c, sim, t_end=None, color=TRAIL, alpha=255, dots=True, line=True, cross=True):
    T = sim["T"] if t_end is None else min(t_end, sim["T"])
    n = max(1, int(round(T / DT)))
    xs, ys = sim["x"][: n + 1], sim["y"][: n + 1]
    if line and len(xs) > 1:
        step = max(1, len(xs) // 300)
        pts = list(zip(xs[::step], ys[::step])) + [(xs[-1], ys[-1])]
        c.line(pts, with_alpha(color, alpha * 0.55), 1.5)
    if dots:
        t = 0.0
        while t <= T + 1e-9:
            px, py = at_time(sim, t)
            c.circle(px, py, r_px=2.4, fill=with_alpha(color, alpha))
            t += STROBE
    if cross and t_end is None:
        c.cross(*sim["landing"], color=with_alpha(color, alpha))


def shot_frames(world, shot, sim, header, under=None, aim_s=0.5, hold_s=0.4):
    """Animate one launch. `under(c)` draws persistent background content."""
    frames = []
    for i in range(int(aim_s * FPS)):
        c = new_canvas()
        if under:
            under(c)
        draw_slingshot(c, shot, pulled=True)
        c.header(header, "aiming...")
        frames.append((c.image(), None))
    n = int(math.ceil(sim["T"] * FPS))
    for i in range(n + 1):
        t = min(i / FPS, sim["T"])
        c = new_canvas()
        if under:
            under(c)
        draw_slingshot(c, shot, pulled=False)
        draw_trail(c, sim, t_end=t, cross=False)
        c.circle(*at_time(sim, t), R_BALL, fill=BALL)
        c.header(header, f"t = {t:.2f} s after release")
        frames.append((c.image(), t))
    for i in range(int(hold_s * FPS)):
        c = new_canvas()
        if under:
            under(c)
        draw_slingshot(c, shot, pulled=False)
        draw_trail(c, sim)
        c.circle(*sim["landing"], R_BALL, fill=BALL)
        c.header(header, f"landed at t = {sim['T']:.2f} s")
        frames.append((c.image(), sim["T"]))
    return frames


# --------------------------------------------------------------------------
# item


def build(rng, n_demos=2):
    for _attempt in range(50):
        world = sample_world(rng)
        demos = []
        for _ in range(n_demos):
            shot, sim = sample_shot(rng, world, avoid=[d[0] for d in demos])
            if shot is None:
                break
            demos.append((shot, sim))
        if len(demos) < n_demos:
            continue
        qshot, qsim = sample_shot(rng, world, avoid=[d[0] for d in demos])
        if qshot is None:
            continue
        true_opt = Option("true", "the world's real physics", dict(world), rollout=qsim)
        pool = []
        for label, desc, w in perturbations(world):
            s = simulate(w, qshot)
            if s["in_bounds"]:
                pool.append(Option(label, desc, w, rollout=s))
        distractors = pick_distractors(rng, true_opt, pool, rollout_dist, min_dist=2.5,
                                       prefer=("ordinary_physics", "earth_gravity"))
        if distractors is None:
            continue
        return _assemble(world, demos, qshot, [true_opt] + distractors)
    raise RuntimeError("could not build a slingshot item")


def _assemble(world, demos, qshot, options):
    # Context video: the demo shots one after another, earlier shots left faintly in view.
    video, keyframes = [], []
    for i, (shot, sim) in enumerate(demos):
        prev = demos[:i]

        def under(c, prev=prev):
            for j, (s, m) in enumerate(prev):
                draw_slingshot(c, s, pulled=False, alpha=90, label=False)
                draw_trail(c, m, color=DEMO_COLORS[j], alpha=90)

        fr = shot_frames(world, shot, sim, f"Demo shot {i + 1} of {len(demos)}", under=under)
        video += [f for f, _ in fr]
        flight = [(f, t) for f, t in fr if t is not None]
        for f, t in pick_keyframes(flight, 4):
            keyframes.append((f, f"demo shot {i + 1}, t = {t:.2f} s after release"))

    # Summary: all demo shots with timing dots.
    c = new_canvas()
    for j, (s, m) in enumerate(demos):
        draw_slingshot(c, s, pulled=True, label_color=DEMO_COLORS[j], tag=f"shot {j + 1}: ")
        draw_trail(c, m, color=DEMO_COLORS[j])
        lx, ly = m["landing"]
        c.text(lx, ly + 0.9, f"{m['T']:.2f} s", size=11, color=DEMO_COLORS[j], bg=(255, 255, 255, 200))
    c.header("Demo shots (dots every 0.1 s)")
    summary = c.image()

    c = new_canvas()
    draw_slingshot(c, qshot, pulled=True)
    c.header("New shot: where will it land?")
    query = c.image()

    for o in options:
        sim = o.rollout
        c = new_canvas()
        draw_slingshot(c, qshot, pulled=False)
        draw_trail(c, sim)
        c.circle(*sim["landing"], R_BALL, fill=BALL)
        c.header("Candidate outcome (dots every 0.1 s)")
        o.image = c.image()
        o.frames = [f for f, _ in shot_frames(o.params, qshot, sim, "Candidate outcome")]
        o.params = {k: round(v, 3) for k, v in o.params.items()}

    setup = {
        "demos": [{**s, "landing": m["landing"], "flight_time": round(m["T"], 3)} for s, m in demos],
        "query_shot": qshot,
        "true_landing": options[0].rollout["landing"],
    }
    prompt = {
        "intro": (
            "This is a 2D simulated world whose physics may be different from Earth's. Gravity can be stronger, "
            "weaker or tilted, there can be wind and air drag, and the slingshot's strength is unknown. "
            "Launch speed is proportional to how far the ball is pulled back. Grid squares are 1 m. "
            f"You are shown {len(demos)} demo launches from slingshots placed at different spots. The pull "
            "distance and launch angle are written above each slingshot, and the grey arrow shows the launch direction."
        ),
        "question": (
            "A new slingshot in the same world is pulled back as shown in the query image. Which candidate image "
            "shows what will actually happen (the full flight path and where the ball lands)? Trail dots are "
            "0.1 s apart in every image."
        ),
    }
    world_out = {k: round(v, 3) for k, v in world.items()}
    return ItemBuild("slingshot", world_out, setup, video, keyframes, summary, query, options, prompt, FPS)
