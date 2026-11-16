"""Turn an AI-generated strip/grid into PULU sprite frames.

    python3 scripts/art/slice_strip.py raw/strip.png --clip idle_observe \
        --cols 6 --rows 1 --out ../work/sprites/idle_observe

Handles the three things a generated image always needs before it can ship:
  1. key out the flat background (corner-sampled, distance keyed, edge feathered)
  2. despill the fringe left by the key colour
  3. normalise each cell to the 152 px sprite frame with the feet anchored
"""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

FRAME = 152
FILL = 0.92


def key_background(cell, tol=42, feather=2, bg_hex=None):
    """Remove a flat backdrop.

    Sampling the corners fails when the backdrop is close to the subject's own
    colours (beige behind a white-chested cat keys the chest out), so callers can
    force the exact chroma colour they asked the generator for.
    """
    arr = np.asarray(cell.convert("RGB")).astype(np.int16)
    h, w, _ = arr.shape
    pad = max(2, min(h, w) // 20)
    corners = np.concatenate([
        arr[:pad, :pad].reshape(-1, 3), arr[:pad, -pad:].reshape(-1, 3),
        arr[-pad:, :pad].reshape(-1, 3), arr[-pad:, -pad:].reshape(-1, 3),
    ])
    if bg_hex:
        bg = np.array([int(bg_hex[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.int16)
    else:
        bg = np.median(corners, axis=0)
    dist = np.abs(arr - bg).sum(axis=2)
    alpha = np.clip((dist - tol) / max(1.0, tol * 0.6), 0, 1)

    # despill: pull the background hue out of the semi-transparent fringe
    spill = (alpha < 0.98)[..., None]
    arr = np.where(spill, np.clip(arr + (bg - arr) * (1 - alpha)[..., None] * 0.6, 0, 255), arr)

    out = np.dstack([arr, alpha * 255]).astype(np.uint8)
    img = Image.fromarray(out, "RGBA")
    return img.filter(ImageFilter.GaussianBlur(feather * 0.5))


def normalise(frame, size=FRAME, fill=FILL):
    """Scale so the visible pet fills `fill` of the frame, feet on the baseline."""
    bbox = frame.getbbox()
    if not bbox:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pet = frame.crop(bbox)
    scale = (size * fill) / pet.height
    new_w = max(1, round(pet.width * scale))
    new_h = max(1, round(pet.height * scale))
    pet = pet.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - new_w) // 2
    y = size - new_h - round(size * (1 - fill) / 2)
    canvas.paste(pet, (x, y), pet)
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--clip", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=1)
    ap.add_argument("--rows", type=int, default=1)
    ap.add_argument("--tol", type=int, default=42)
    ap.add_argument("--bg", default=None, help="forced chroma colour, e.g. 00FF00")
    ap.add_argument("--size", type=int, default=FRAME)
    ap.add_argument("--fps", type=float, default=8)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--no-key", action="store_true", help="source already has alpha")
    args = ap.parse_args()

    img = Image.open(args.source).convert("RGBA")
    if args.no_key:
        cells = []
        cw, ch = img.width // args.cols, img.height // args.rows
        for r in range(args.rows):
            for c in range(args.cols):
                cells.append(img.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)))
    else:
        cw, ch = img.width // args.cols, img.height // args.rows
        cells = []
        for r in range(args.rows):
            for c in range(args.cols):
                cell = img.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
                cells.append(key_background(cell, tol=args.tol, bg_hex=args.bg))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for i, cell in enumerate(cells):
        normalise(cell, size=args.size).save(out / f"{i:04d}.png")

    meta_path = out / "clip.json"
    meta = {"fps": args.fps, "loop": args.loop, "frames": len(cells)}
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"SLICED {args.clip}: {len(cells)} frames -> {out}")


if __name__ == "__main__":
    main()
