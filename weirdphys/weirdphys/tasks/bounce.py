"""Bouncing ball: watch a ball bounce around a box, predict the next stretch of its path.

Hidden physics per world:
  gravity      vector (strength from very weak to very strong, sometimes tilted)
  restitution  fraction of speed kept on each bounce (bounciness)
  drag         linear air drag (1/s)
  slip         fraction of along-wall speed kept on each bounce (wall friction)
"""

from __future__ import annotations

import math

import numpy as np

from ..item import ItemBuild, Option, pick_distractors, pick_keyframes
from ..render import WALL, Canvas, lighten, with_alpha

W, H = 20.0, 12.0
R = 0.4
DT = 1 / 2000
FPS = 20
STROBE = 0.1
BALL = (60, 120, 210)
CTX_TRAIL = (150, 150, 160)
PRED = (220, 80, 60)


def sample_world(rng):
    g = float(np.exp(rng.uniform(np.log(1.5), np.log(50.0))))
    tilt = 0.0 if rng.random() < 0.6 else float(rng.choice([-1, 1]) * rng.uniform(15, 60))
    return {
        "g": g,
        "tilt_deg": tilt,
        "restitution": float(rng.uniform(0.25, 0.97)),
        "drag": 0.0 if rng.random() < 0.6 else float(rng.uniform(0.1, 0.6)),
        "slip": float(rng.uniform(0.75, 1.0)),
    }


def gravity_vec(world):
    a = math.radians(world["tilt_deg"])
    return world["g"] * math.sin(a), -world["g"] * math.cos(a)


def simulate(world, state, duration):
    """state = (x, y, vx, vy). Returns array of states sampled every 1/FPS... at DT resolution."""
    gx, gy = gravity_vec(world)
    e, b, slip = world["restitution"], world["drag"], world["slip"]
    x, y, vx, vy = state
    n = int(round(duration / DT))
    out = np.empty((n + 1, 4))
    out[0] = state
    rest_v = 0.15  # below this normal speed, a bounce becomes resting contact
    for i in range(1, n + 1):
        vx += (gx - b * vx) * DT
        vy += (gy - b * vy) * DT
        x += vx * DT
        y += vy * DT
        # walls: (position test, normal axis, sign)
        if x < R and vx < 0:
            x = R
            vx = -e * vx if -vx * e > rest_v else 0.0
            vy *= slip if abs(vx) > 0 else (1 - 2.0 * DT)
        elif x > W - R and vx > 0:
            x = W - R
            vx = -e * vx if vx * e > rest_v else 0.0
            vy *= slip if abs(vx) > 0 else (1 - 2.0 * DT)
        if y < R and vy < 0:
            y = R
            vy = -e * vy if -vy * e > rest_v else 0.0
            vx *= slip if abs(vy) > 0 else (1 - 2.0 * DT)
        elif y > H - R and vy > 0:
            y = H - R
            vy = -e * vy if vy * e > rest_v else 0.0
            vx *= slip if abs(vy) > 0 else (1 - 2.0 * DT)
        out[i] = (x, y, vx, vy)
    return out


def at(traj, t):
    i = min(len(traj) - 1, int(round(t / DT)))
    return traj[i]


def strobe_points(traj, t0=0.0, t1=None):
    t1 = (len(traj) - 1) * DT if t1 is None else t1
    n = int(math.floor((t1 - t0) / STROBE + 1e-9))
    return np.array([at(traj, t0 + i * STROBE)[:2] for i in range(n + 1)])


def rollout_dist(a, b):
    """Mean distance between the two predicted paths, sampled every 0.1 s."""
    return float(np.mean(np.linalg.norm(a["strobe"] - b["strobe"], axis=1)))


def perturbations(world):
    out = []

    def add(label, desc, **changes):
        w = dict(world)
        w.update(changes)
        out.append((label, desc, w))

    add("ordinary_physics", "ordinary Earth physics: 9.8 m/s^2 straight down, restitution 0.8, no drag",
        g=9.81, tilt_deg=0.0, restitution=0.8, drag=0.0, slip=0.95)
    add("gravity_x0.35", "gravity about 1/3 as strong", g=world["g"] * 0.35)
    add("gravity_x2.5", "gravity 2.5x stronger", g=world["g"] * 2.5)
    if world["tilt_deg"]:
        add("gravity_straight_down", "gravity straight down (no tilt)", tilt_deg=0.0)
    add("tilt_plus35", "gravity tilted 35 deg further clockwise", tilt_deg=world["tilt_deg"] + 35)
    add("tilt_minus35", "gravity tilted 35 deg further counter-clockwise", tilt_deg=world["tilt_deg"] - 35)
    if world["restitution"] > 0.55:
        add("less_bouncy", "much less bouncy", restitution=world["restitution"] * 0.4)
    else:
        add("more_bouncy", "much bouncier", restitution=min(0.97, world["restitution"] + 0.45))
    if world["drag"]:
        add("no_drag", "no air drag", drag=0.0)
    else:
        add("heavy_drag", "strong air drag", drag=1.2)
    add("gravity_up", "gravity reversed", tilt_deg=world["tilt_deg"] + 180)
    return out


# --------------------------------------------------------------------------
# drawing

_BG = None


def new_canvas():
    global _BG
    if _BG is None:
        _BG = Canvas(0, 0, W, H, 32)
        _BG.grid(label=True)
        _BG.border(WALL, 4)
    return _BG.clone()


def draw_path(c, traj, t0, t1, color, alpha=255, dots=True):
    i0, i1 = int(round(t0 / DT)), int(round(t1 / DT))
    seg = traj[i0 : i1 + 1]
    if len(seg) > 1:
        step = max(1, len(seg) // 400)
        pts = [tuple(p) for p in seg[::step, :2]] + [tuple(seg[-1, :2])]
        c.line(pts, with_alpha(color, alpha * 0.5), 1.5)
    if dots:
        for p in strobe_points(traj, t0, t1):
            c.circle(p[0], p[1], r_px=2.6, fill=with_alpha(color, alpha))


def ctx_frame(traj, t, header):
    c = new_canvas()
    draw_path(c, traj, 0, t, CTX_TRAIL)
    p = at(traj, t)
    c.circle(p[0], p[1], R, fill=BALL)
    c.header(header, f"t = {t:.2f} s")
    return c.image()


# --------------------------------------------------------------------------
# item


def build(rng):
    for _attempt in range(80):
        world = sample_world(rng)
        x0 = float(rng.uniform(2, W - 2))
        y0 = float(rng.uniform(6, H - 1.5))
        sp = float(rng.uniform(2, 10))
        # start moving sideways or downward (never up), so the opening motion is easy to read
        ang = float(rng.uniform(math.radians(190), math.radians(350)))
        state0 = (x0, y0, sp * math.cos(ang), sp * math.sin(ang))
        t_ctx = float(round(rng.uniform(2.5, 4.0), 1))
        t_pred = 3.0
        ctx = simulate(world, state0, t_ctx)
        # the context must show some motion and at least one bounce, so there is something to learn from
        path_len = float(np.sum(np.linalg.norm(np.diff(ctx[::40, :2], axis=0), axis=1)))
        if path_len < 4:
            continue
        sv = ctx[:, 2:]
        flips = np.sum(np.sign(sv[1:]) * np.sign(sv[:-1]) < 0)
        if flips < 1:
            continue
        s1 = tuple(ctx[-1])

        def rollout(w):
            fut = simulate(w, s1, t_pred)
            return {"traj": fut, "strobe": strobe_points(fut)}

        true_opt = Option("true", "the world's real physics", dict(world), rollout=rollout(world))
        # the true future must move, otherwise every option looks alike
        if float(np.linalg.norm(true_opt.rollout["strobe"][-1] - np.array(s1[:2]))) < 0.8:
            continue
        pool = [Option(lbl, desc, w, rollout=rollout(w)) for lbl, desc, w in perturbations(world)]
        distractors = pick_distractors(rng, true_opt, pool, rollout_dist, min_dist=1.0, prefer=("ordinary_physics",))
        if distractors is None:
            continue
        return _assemble(world, state0, ctx, t_ctx, t_pred, [true_opt] + distractors)
    raise RuntimeError("could not build a bounce item")


def _assemble(world, state0, ctx, t_ctx, t_pred, options):
    n = int(round(t_ctx * FPS))
    video_t = [min(i / FPS, t_ctx) for i in range(n + 1)]
    frames = [(ctx_frame(ctx, t, "Watch the ball"), t) for t in video_t]
    video = [f for f, _ in frames]
    keyframes = [(f, f"t = {t:.2f} s") for f, t in pick_keyframes(frames, 8)]

    c = new_canvas()
    draw_path(c, ctx, 0, t_ctx, BALL)
    p = ctx[-1]
    c.circle(p[0], p[1], R, fill=BALL)
    c.header("Path so far (dots every 0.1 s)", f"0 to {t_ctx:.1f} s")
    summary = c.image()

    c = new_canvas()
    draw_path(c, ctx, 0, t_ctx, CTX_TRAIL, alpha=200)
    c.circle(p[0], p[1], R, fill=BALL)
    c.header("Where will the ball be?", f"now: t = {t_ctx:.1f} s")
    query = c.image()

    for o in options:
        fut = o.rollout["traj"]
        c = new_canvas()
        c.circle(p[0], p[1], R, fill=with_alpha(lighten(BALL, 0.5), 255))
        draw_path(c, fut, 0, t_pred, PRED)
        q = fut[-1]
        c.circle(q[0], q[1], R, fill=BALL)
        c.header(f"Candidate: next {t_pred:.1f} s (red dots every 0.1 s)", f"t = {t_ctx:.1f} to {t_ctx + t_pred:.1f} s")
        o.image = c.image()
        o.frames = []
        m = int(round(t_pred * FPS))
        for i in range(m + 1):
            t = i / FPS
            c = new_canvas()
            draw_path(c, fut, 0, t, PRED)
            q = at(fut, t)
            c.circle(q[0], q[1], R, fill=BALL)
            c.header("Candidate outcome", f"t = {t_ctx + t:.2f} s")
            o.frames.append(c.image())
        o.params = {k: round(v, 3) for k, v in o.params.items()}

    setup = {
        "start_state": [round(v, 3) for v in state0],
        "t_context": t_ctx,
        "t_predict": t_pred,
        "state_at_cut": [round(float(v), 3) for v in ctx[-1]],
        "true_end": [round(float(v), 3) for v in options[0].rollout["traj"][-1, :2]],
    }
    prompt = {
        "intro": (
            "This is a 2D simulated world whose physics may be different from Earth's. Gravity can be any strength "
            "and may not point straight down, the ball's bounciness and air drag are unknown, and the walls of the box "
            f"are solid. Grid squares are 1 m. You are shown a video of a ball moving for {t_ctx:.1f} s."
        ),
        "question": (
            f"Each candidate image shows a possible path for the next {t_pred:.1f} s (red dots every 0.1 s, the solid "
            "blue ball is where it ends up). Which candidate is what will actually happen in this world?"
        ),
    }
    world_out = {k: round(v, 3) for k, v in world.items()}
    return ItemBuild("bounce", world_out, setup, video, keyframes, summary, query, options, prompt, FPS)
