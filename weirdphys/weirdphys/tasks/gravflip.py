"""Gravity flip: shapes float in a closed box, then gravity switches on in some direction.

The demo video shows one arrangement of shapes floating and then collapsing.
The question shows a *new* floating arrangement in the same world and asks which
candidate shows the scene a fixed time after gravity switches on.

Hidden physics per world:
  gravity direction  any direction (often sideways or upward)
  gravity strength   weak to very strong
  elasticity         how bouncy the shapes and walls are
  friction           how grippy surfaces are
Rigid-body dynamics come from pymunk (Chipmunk2D).
"""

from __future__ import annotations

import math

import numpy as np
import pymunk

from ..item import ItemBuild, Option, pick_distractors, pick_keyframes
from ..render import PALETTE, WALL, Canvas, lighten, with_alpha

S = 20.0  # box is S x S meters
FPS = 20
SUBSTEPS = 24  # physics steps per video frame
T_LEVITATE = 0.6
T_DEMO_AFTER = 2.6
T_QUERY = 1.5
OUTLINE = (45, 45, 55)

DIRECTIONS = {
    "down": -90, "up": 90, "left": 180, "right": 0,
    "down-left": -135, "down-right": -45, "up-left": 135, "up-right": 45,
}


def sample_world(rng):
    r = rng.random()
    if r < 0.15:
        name, ang = "down", -90.0
    elif r < 0.75:
        name = str(rng.choice([d for d in DIRECTIONS if d != "down"]))
        ang = float(DIRECTIONS[name])
    else:
        ang = float(rng.uniform(-180, 180))
        name = f"{ang:.0f} deg"
    return {
        "gravity_dir_deg": ang,  # 0 = right, 90 = up, -90 = down
        "gravity_dir_name": name,
        "g": float(np.exp(rng.uniform(np.log(3.0), np.log(60.0)))),
        "elasticity": float(rng.uniform(0.0, 0.85)),
        "friction": float(rng.uniform(0.05, 1.0)),
    }


# --------------------------------------------------------------------------
# shapes


def _shape_spec(rng):
    kind = rng.choice(["box", "box", "circle", "triangle", "pentagon"])
    if kind == "box":
        w, h = float(rng.uniform(0.9, 3.2)), float(rng.uniform(0.9, 2.4))
        verts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
        return {"kind": "box", "verts": verts, "r": math.hypot(w, h) / 2}
    if kind == "circle":
        r = float(rng.uniform(0.5, 1.2))
        return {"kind": "circle", "radius": r, "r": r}
    n = 3 if kind == "triangle" else 5
    r = float(rng.uniform(0.8, 1.5))
    off = float(rng.uniform(0, 2 * math.pi))
    verts = [(r * math.cos(off + 2 * math.pi * i / n), r * math.sin(off + 2 * math.pi * i / n)) for i in range(n)]
    return {"kind": str(kind), "verts": verts, "r": r}


def sample_arrangement(rng):
    """A list of shapes floating near the middle of the box, not touching."""
    n = int(rng.integers(4, 8))
    layout = rng.choice(["cluster", "tower", "row"])
    shapes = []
    if layout == "tower":
        x = float(rng.uniform(7, 13))
        y = float(rng.uniform(3.5, 5.0))
        for _ in range(n):
            sp = _shape_spec(rng)
            y += sp["r"] * (0.75 if sp["kind"] == "box" else 1.0)
            if y + sp["r"] > S - 1.5:
                break
            sp["pos"] = (x + float(rng.uniform(-0.4, 0.4)), y)
            sp["angle"] = 0.0 if sp["kind"] == "box" else float(rng.uniform(0, 2 * math.pi))
            shapes.append(sp)
            y += sp["r"] * (0.75 if sp["kind"] == "box" else 1.0) + 0.12
    elif layout == "row":
        y = float(rng.uniform(6, 14))
        x = float(rng.uniform(2.5, 4.5))
        for _ in range(n):
            sp = _shape_spec(rng)
            x += sp["r"]
            if x + sp["r"] > S - 1.5:
                break
            sp["pos"] = (x, y + float(rng.uniform(-0.6, 0.6)))
            sp["angle"] = float(rng.uniform(0, 2 * math.pi))
            shapes.append(sp)
            x += sp["r"] + 0.15
    else:
        cx, cy = float(rng.uniform(7, 13)), float(rng.uniform(7, 13))
        for _ in range(n):
            sp = _shape_spec(rng)
            for _try in range(200):
                p = (cx + float(rng.normal(0, 2.6)), cy + float(rng.normal(0, 2.6)))
                if not (sp["r"] + 1 < p[0] < S - sp["r"] - 1 and sp["r"] + 1 < p[1] < S - sp["r"] - 1):
                    continue
                if all(math.dist(p, o["pos"]) > sp["r"] + o["r"] + 0.1 for o in shapes):
                    sp["pos"] = p
                    sp["angle"] = float(rng.uniform(0, 2 * math.pi))
                    shapes.append(sp)
                    break
    for i, sp in enumerate(shapes):
        sp["color"] = PALETTE[i % len(PALETTE)]
    return shapes if len(shapes) >= 3 else None


# --------------------------------------------------------------------------
# physics


def simulate(world, shapes, t_before, t_after):
    """Return list of frames; each frame = list of (x, y, angle) per shape, sampled at FPS."""
    space = pymunk.Space()
    space.iterations = 30
    e, f = world["elasticity"], world["friction"]
    wr = 2.0  # thick walls (inner surface stays at 0 and S) so fast shapes cannot tunnel through
    for a, b in [((-wr, -wr), (S + wr, -wr)), ((S + wr, -wr), (S + wr, S + wr)),
                 ((S + wr, S + wr), (-wr, S + wr)), ((-wr, S + wr), (-wr, -wr))]:
        seg = pymunk.Segment(space.static_body, a, b, wr)
        seg.elasticity, seg.friction = e, f
        space.add(seg)
    bodies = []
    for sp in shapes:
        body = pymunk.Body()
        body.position = sp["pos"]
        body.angle = sp["angle"]
        if sp["kind"] == "circle":
            shp = pymunk.Circle(body, sp["radius"])
        else:
            shp = pymunk.Poly(body, sp["verts"], radius=0.02)
        shp.density = 1.0
        shp.elasticity, shp.friction = e, f
        space.add(body, shp)
        bodies.append(body)

    ang = math.radians(world["gravity_dir_deg"])
    gvec = (world["g"] * math.cos(ang), world["g"] * math.sin(ang))
    dt = 1.0 / (FPS * SUBSTEPS)
    frames = []
    n_before = int(round(t_before * FPS))
    n_after = int(round(t_after * FPS))
    for i in range(n_before + n_after + 1):
        frames.append([(b.position.x, b.position.y, b.angle) for b in bodies])
        space.gravity = gvec if i >= n_before else (0.0, 0.0)
        for _ in range(SUBSTEPS):
            space.step(dt)
    return frames


def rollout_dist(a, b):
    pa = np.array([(x, y) for x, y, _ in a["final"]])
    pb = np.array([(x, y) for x, y, _ in b["final"]])
    return float(np.mean(np.linalg.norm(pa - pb, axis=1)))


def perturbations(world):
    out = []

    def add(label, desc, **changes):
        w = dict(world)
        w.update(changes)
        out.append((label, desc, w))

    d = world["gravity_dir_deg"]
    if d != -90:
        add("ordinary_physics", "ordinary physics: gravity straight down at 9.8 m/s^2",
            gravity_dir_deg=-90.0, gravity_dir_name="down", g=9.81, elasticity=0.2, friction=0.6)
    add("dir_opposite", "gravity pointing the opposite way", gravity_dir_deg=d + 180)
    add("dir_rot_cw90", "gravity rotated 90 deg clockwise", gravity_dir_deg=d - 90)
    add("dir_rot_ccw90", "gravity rotated 90 deg counter-clockwise", gravity_dir_deg=d + 90)
    add("dir_rot_cw45", "gravity rotated 45 deg clockwise", gravity_dir_deg=d - 45)
    add("dir_rot_ccw45", "gravity rotated 45 deg counter-clockwise", gravity_dir_deg=d + 45)
    add("gravity_x0.2", "gravity 5x weaker", g=world["g"] * 0.2)
    add("gravity_x4", "gravity 4x stronger", g=world["g"] * 4)
    if world["elasticity"] < 0.6:
        add("super_bouncy", "shapes are super bouncy", elasticity=0.97)
    else:
        add("not_bouncy", "shapes do not bounce at all", elasticity=0.0)
    if world["friction"] > 0.3:
        add("frictionless", "surfaces are frictionless (like ice)", friction=0.0)
    for _, _, w in out:
        w["gravity_dir_deg"] = (w["gravity_dir_deg"] + 180) % 360 - 180
    return out


# --------------------------------------------------------------------------
# drawing

_BG = None


def new_canvas():
    global _BG
    if _BG is None:
        _BG = Canvas(0, 0, S, S, 24)
        _BG.grid(label=True)
        _BG.border(WALL, 5)
    return _BG.clone()


def _world_verts(sp, x, y, a):
    ca, sa = math.cos(a), math.sin(a)
    return [(x + vx * ca - vy * sa, y + vx * sa + vy * ca) for vx, vy in sp["verts"]]


def draw_shapes(c, shapes, state, ghost=False):
    for sp, (x, y, a) in zip(shapes, state):
        if ghost:
            fill, outline, w = None, with_alpha(lighten(sp["color"], 0.2), 150), 1.5
        else:
            fill, outline, w = sp["color"], OUTLINE, 1.8
        if sp["kind"] == "circle":
            c.circle(x, y, sp["radius"], fill=fill, outline=outline, width=w)
            if not ghost:
                r = sp["radius"]
                c.line([(x, y), (x + r * math.cos(a), y + r * math.sin(a))], OUTLINE, 1.8)
        else:
            c.polygon(_world_verts(sp, x, y, a), fill=fill, outline=outline, width=w)


def draw_paths(c, shapes, frames, upto):
    for k, sp in enumerate(shapes):
        pts = [(fr[k][0], fr[k][1]) for fr in frames[: upto + 1]]
        c.line(pts, with_alpha(sp["color"], 170), 1.5)


def scene_frame(shapes, frames, i, n_before, header):
    c = new_canvas()
    draw_shapes(c, shapes, frames[i])
    if i < n_before:
        right = f"gravity OFF   t = {i / FPS:.2f} s"
    else:
        right = f"gravity ON   +{(i - n_before) / FPS:.2f} s"
    c.header(header, right)
    return c.image()


# --------------------------------------------------------------------------
# item


def build(rng):
    for _attempt in range(60):
        world = sample_world(rng)
        demo = sample_arrangement(rng)
        quer = sample_arrangement(rng)
        if demo is None or quer is None:
            continue
        nb = int(round(T_LEVITATE * FPS))
        demo_frames = simulate(world, demo, T_LEVITATE, T_DEMO_AFTER)
        # demo must actually show the collapse
        moved = np.mean([math.dist(demo_frames[0][k][:2], demo_frames[-1][k][:2]) for k in range(len(demo))])
        if moved < 1.5:
            continue

        def rollout(w):
            fr = simulate(w, quer, 0.0, T_QUERY)
            return {"frames": fr, "final": fr[-1]}

        true_opt = Option("true", "the world's real physics", dict(world), rollout=rollout(world))
        pool = [Option(lbl, desc, w, rollout=rollout(w)) for lbl, desc, w in perturbations(world)]
        distractors = pick_distractors(rng, true_opt, pool, rollout_dist, min_dist=1.2, prefer=("ordinary_physics",))
        if distractors is None:
            continue
        return _assemble(world, demo, demo_frames, nb, quer, [true_opt] + distractors)
    raise RuntimeError("could not build a gravflip item")


def _assemble(world, demo, demo_frames, nb, quer, options):
    frames = [(scene_frame(demo, demo_frames, i, nb, "Demo"), i) for i in range(len(demo_frames))]
    video = [f for f, _ in frames]

    def cap(i):
        return f"t = {i / FPS:.2f} s, gravity off" if i < nb else f"gravity on for {(i - nb) / FPS:.2f} s"

    keyframes = [(frames[0][0], cap(0))]
    after = frames[nb + 3 :]  # skip the first instants after the switch (they look identical to frame 0)
    keyframes += [(f, cap(i)) for f, i in pick_keyframes(after, 7)]

    c = new_canvas()
    draw_shapes(c, demo, demo_frames[0], ghost=True)
    draw_paths(c, demo, demo_frames, len(demo_frames) - 1)
    draw_shapes(c, demo, demo_frames[-1])
    c.header("Demo: start (outlines) and end", f"gravity on for {T_DEMO_AFTER:.1f} s")
    summary = c.image()

    q0 = [(sp["pos"][0], sp["pos"][1], sp["angle"]) for sp in quer]
    c = new_canvas()
    draw_shapes(c, quer, q0)
    c.header("New scene (floating)", "gravity OFF")
    query = c.image()

    for o in options:
        fr = o.rollout["frames"]
        c = new_canvas()
        draw_shapes(c, quer, fr[0], ghost=True)
        draw_paths(c, quer, fr, len(fr) - 1)
        draw_shapes(c, quer, fr[-1])
        c.header("Candidate", f"gravity on for {T_QUERY:.1f} s")
        o.image = c.image()
        o.frames = []
        for i in range(len(fr)):
            c = new_canvas()
            draw_shapes(c, quer, fr[0], ghost=True)
            draw_shapes(c, quer, fr[i])
            c.header("Candidate outcome", f"gravity ON   +{i / FPS:.2f} s")
            o.frames.append(c.image())
        o.params = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in o.params.items()}

    def shape_out(sp):
        d = {"kind": sp["kind"], "pos": [round(v, 3) for v in sp["pos"]], "angle": round(sp["angle"], 3),
             "color": sp["color"]}
        if sp["kind"] == "circle":
            d["radius"] = round(sp["radius"], 3)
        else:
            d["verts"] = [[round(a, 3), round(b, 3)] for a, b in sp["verts"]]
        return d

    setup = {
        "demo_shapes": [shape_out(s) for s in demo],
        "query_shapes": [shape_out(s) for s in quer],
        "t_levitate": T_LEVITATE,
        "t_demo_after": T_DEMO_AFTER,
        "t_query": T_QUERY,
    }
    prompt = {
        "intro": (
            "This is a 2D simulated world inside a closed box with solid walls. Its physics may be very different "
            "from Earth's. Gravity starts switched off so the shapes float, then it switches on, but it can point in "
            "any direction (sideways, up, diagonal) and can be weak or strong. How bouncy and how slippery things are "
            "is also unknown. Grid squares are 1 m. You are shown a demo video of some shapes floating and then "
            "gravity switching on."
        ),
        "question": (
            "The query image shows a new set of floating shapes in the same world. Gravity will switch on exactly as "
            f"it did in the demo. Which candidate shows the scene {T_QUERY:.1f} s after gravity switches on? In the "
            "candidates, faint outlines mark where each shape started and thin lines trace the path of each shape's center."
        ),
    }
    world_out = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in world.items()}
    return ItemBuild("gravflip", world_out, setup, video, keyframes, summary, query, options, prompt, FPS)
