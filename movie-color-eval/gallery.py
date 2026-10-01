"""Render data/gallery.png, a grid of every movie's average color, average frame and barcode."""

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ROW_H, SWATCH_W, FRAME_W, BAR_W, TEXT_W = 90, 90, 160, 400, 360


def main():
    movies = json.loads((DATA / "colors.json").read_text())
    W = SWATCH_W + FRAME_W + BAR_W + TEXT_W + 50
    img = Image.new("RGB", (W, ROW_H * len(movies) + 10), (24, 24, 24))
    draw = ImageDraw.Draw(img)
    for i, m in enumerate(movies):
        y = 5 + i * ROW_H
        x = 10
        draw.rectangle([x, y, x + SWATCH_W - 1, y + ROW_H - 11], fill=tuple(m["rgb"]))
        x += SWATCH_W + 10
        d = DATA / "movies" / m["slug"]
        frame = Image.open(d / "frame.png")
        frame.thumbnail((FRAME_W, ROW_H - 10))
        img.paste(frame, (x, y))
        x += FRAME_W + 10
        img.paste(Image.open(d / "barcode.png").resize((BAR_W, ROW_H - 10)), (x, y))
        x += BAR_W + 10
        draw.text((x, y + 20), f"{m['title']} ({m['year']})", fill=(235, 235, 235))
        draw.text((x, y + 40), m["hex"], fill=(160, 160, 160))
    img.save(DATA / "gallery.png")
    print(f"wrote {DATA / 'gallery.png'}")


if __name__ == "__main__":
    main()
