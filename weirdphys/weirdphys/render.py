"""Small 2D renderer on top of Pillow.

Everything is drawn in world units (meters, y up) and converted to pixels by a
Canvas. Drawing happens at SS x resolution and is downsampled at the end, which
gives cheap anti-aliasing.
"""

from __future__ import annotations

import io
import math
import os
import shutil
import subprocess
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

SS = 2  # supersampling factor

BG = (247, 245, 240)
GRID_MINOR = (230, 227, 220)
GRID_MAJOR = (210, 206, 197)
AXIS_TEXT = (140, 136, 128)
INK = (40, 40, 46)
GROUND = (120, 104, 84)
GROUND_FILL = (196, 182, 160)
WALL = (90, 90, 100)

PALETTE = [
    (230, 85, 70),
    (60, 130, 220),
    (245, 175, 40),
    (80, 175, 100),
    (160, 95, 200),
    (240, 125, 175),
    (40, 175, 190),
    (150, 110, 70),
    (120, 120, 130),
]

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]
_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


@lru_cache(maxsize=None)
def font(size: int, bold: bool = False):
    for path in _BOLD_CANDIDATES if bold else _FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


class Canvas:
    """A world-coordinate drawing surface."""

    def __init__(self, x0, y0, x1, y1, px_per_m, margin=(36, 30, 14, 26)):
        # margin = (left, top, right, bottom) in output pixels
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.s = px_per_m
        self.ml, self.mt, self.mr, self.mb = margin
        self.w = int(round((x1 - x0) * px_per_m)) + self.ml + self.mr
        self.h = int(round((y1 - y0) * px_per_m)) + self.mt + self.mb
        self.img = Image.new("RGB", (self.w * SS, self.h * SS), BG)
        self.d = ImageDraw.Draw(self.img, "RGBA")

    def clone(self) -> "Canvas":
        """Cheap copy (used to reuse a pre-drawn static background)."""
        c = Canvas.__new__(Canvas)
        c.__dict__.update(self.__dict__)
        c.img = self.img.copy()
        c.d = ImageDraw.Draw(c.img, "RGBA")
        return c

    # coordinate transforms -------------------------------------------------
    def px(self, x, y):
        return (
            (self.ml + (x - self.x0) * self.s) * SS,
            (self.mt + (self.y1 - y) * self.s) * SS,
        )

    def L(self, length_m):
        return length_m * self.s * SS

    # primitives -------------------------------------------------------------
    def line(self, pts, color=INK, width=2.0):
        if len(pts) < 2:
            return
        self.d.line([self.px(*p) for p in pts], fill=color, width=max(1, int(width * SS)), joint="curve")

    def circle(self, x, y, r_m=None, r_px=None, fill=INK, outline=None, width=1.5):
        cx, cy = self.px(x, y)
        r = self.L(r_m) if r_m is not None else r_px * SS
        self.d.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=fill,
            outline=outline,
            width=max(1, int(width * SS)) if outline else 0,
        )

    def polygon(self, pts, fill=None, outline=INK, width=1.5):
        self.d.polygon([self.px(*p) for p in pts], fill=fill, outline=outline, width=max(1, int(width * SS)))

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1.5):
        a = self.px(x0, y1)
        b = self.px(x1, y0)
        self.d.rectangle([a, b], fill=fill, outline=outline, width=max(1, int(width * SS)) if outline else 0)

    def cross(self, x, y, size_px=7, color=INK, width=2.5):
        cx, cy = self.px(x, y)
        s = size_px * SS
        w = max(1, int(width * SS))
        self.d.line([(cx - s, cy - s), (cx + s, cy + s)], fill=color, width=w)
        self.d.line([(cx - s, cy + s), (cx + s, cy - s)], fill=color, width=w)

    def arrow(self, a, b, color=INK, width=2.0, head_px=9):
        self.line([a, b], color=color, width=width)
        ax, ay = self.px(*a)
        bx, by = self.px(*b)
        ang = math.atan2(by - ay, bx - ax)
        h = head_px * SS
        p1 = (bx - h * math.cos(ang - 0.45), by - h * math.sin(ang - 0.45))
        p2 = (bx - h * math.cos(ang + 0.45), by - h * math.sin(ang + 0.45))
        self.d.polygon([(bx, by), p1, p2], fill=color)

    def text_px(self, x_px, y_px, s, size=13, color=INK, bold=False, anchor="la", bg=None):
        f = font(size * SS, bold)
        pos = (x_px * SS, y_px * SS)
        if bg is not None:
            box = self.d.textbbox(pos, s, font=f, anchor=anchor)
            pad = 3 * SS
            self.d.rounded_rectangle([box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad], radius=4 * SS, fill=bg)
        self.d.text(pos, s, font=f, fill=color, anchor=anchor)

    def text(self, x, y, s, size=12, color=INK, bold=False, anchor="mm", bg=None):
        px, py = self.px(x, y)
        self.text_px(px / SS, py / SS, s, size=size, color=color, bold=bold, anchor=anchor, bg=bg)

    # scenery ----------------------------------------------------------------
    def grid(self, minor=1.0, major=5.0, label=True):
        def frange(a, b, step):
            v = math.ceil(a / step) * step
            while v <= b + 1e-9:
                yield v
                v += step

        for x in frange(self.x0, self.x1, minor):
            major_line = abs(x / major - round(x / major)) < 1e-6
            self.line([(x, self.y0), (x, self.y1)], GRID_MAJOR if major_line else GRID_MINOR, 1.0)
        for y in frange(self.y0, self.y1, minor):
            major_line = abs(y / major - round(y / major)) < 1e-6
            self.line([(self.x0, y), (self.x1, y)], GRID_MAJOR if major_line else GRID_MINOR, 1.0)
        if label:
            for x in frange(self.x0, self.x1, major):
                px, py = self.px(x, self.y0)
                self.text_px(px / SS, py / SS + 6, f"{x:g}", size=10, color=AXIS_TEXT, anchor="mt")
            for y in frange(self.y0, self.y1, major):
                px, py = self.px(self.x0, y)
                self.text_px(px / SS - 6, py / SS, f"{y:g}", size=10, color=AXIS_TEXT, anchor="rm")
            self.text_px(self.w - self.mr, self.h - 4, "meters (grid = 1 m)", size=9, color=AXIS_TEXT, anchor="rd")

    def border(self, color=WALL, width=3.0):
        self.rect(self.x0, self.y0, self.x1, self.y1, outline=color, width=width)

    def header(self, left: str, right: str = "", color=INK):
        self.text_px(self.ml, 8, left, size=13, bold=True, color=color)
        if right:
            self.text_px(self.w - self.mr, 8, right, size=13, color=color, anchor="ra")

    def image(self) -> Image.Image:
        return self.img.resize((self.w, self.h), Image.LANCZOS)


# --------------------------------------------------------------------------
# output helpers


def save_png(img: Image.Image, path: str):
    # The scenes are flat colors plus anti-aliased edges, so a 256-color palette is visually lossless
    # and about 3x smaller than RGB.
    img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(path, optimize=True)


def save_gif(frames: list[Image.Image], path: str, fps: int = 20, hold_last: float = 1.2, scale: float = 1.0,
             frame_step: int = 1):
    """Save an animated GIF with a shared palette (keeps files small)."""
    if not frames:
        return
    if frame_step > 1:
        frames = frames[::frame_step] + ([frames[-1]] if (len(frames) - 1) % frame_step else [])
        fps = max(1, round(fps / frame_step))
    if scale != 1.0:
        size = (round(frames[0].width * scale), round(frames[0].height * scale))
        frames = [f.resize(size, Image.LANCZOS) for f in frames]
    # Build one adaptive palette from a sample of frames so colors are stable.
    sample = frames[:: max(1, len(frames) // 6)][:6]
    strip = Image.new("RGB", (frames[0].width, frames[0].height * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * frames[0].height))
    pal = strip.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    dur = int(round(1000 / fps))
    durations = [dur] * len(q)
    durations[-1] = int(hold_last * 1000)
    q[0].save(path, save_all=True, append_images=q[1:], duration=durations, loop=0, optimize=True, disposal=1)


def save_mp4(frames: list[Image.Image], path: str, fps: int = 20) -> bool:
    """Encode an H.264 mp4 with ffmpeg if it is installed. Returns success."""
    if not frames or shutil.which("ffmpeg") is None:
        return False
    w, h = frames[0].size
    w2, h2 = w - (w % 2), h - (h % 2)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w2}x{h2}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", "-preset", "veryfast", "-movflags", "+faststart",
        path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    buf = io.BytesIO()
    for f in frames:
        f = f.crop((0, 0, w2, h2)) if (w2, h2) != (w, h) else f
        buf.write(f.tobytes())
    proc.communicate(buf.getvalue())
    return proc.returncode == 0


def lighten(c, amt=0.6):
    return tuple(int(v + (255 - v) * amt) for v in c[:3])


def with_alpha(c, a):
    return (c[0], c[1], c[2], int(a))
