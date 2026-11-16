"""Silhouette measurement and IoU check against the approved V05 turnaround.

Usage:
    python3 scripts/character/measure.py render.png --view front
    python3 scripts/character/measure.py --profile          # dump landmark table

Requires Pillow + numpy. The concept image is segmented from its flat background;
guide lines and title text are removed before comparison. IoU is computed after
scaling both silhouettes to the same height and centring them horizontally.
"""

import argparse
import json
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CONCEPT = ROOT / "docs/character/reference/PULU-turnaround-v05.png"
PANELS = {"front": (47, 479), "side": (560, 1011), "back": (1077, 1474)}


def concept_mask(view, path=CONCEPT):
    img = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    x0, x1 = PANELS[view]
    sub = img[:, x0:x1]
    h, w, _ = sub.shape
    bg = np.median(np.concatenate([sub[:, :6], sub[:, -6:]], axis=1), axis=1)
    diff = np.abs(sub - bg[:, None, :]).sum(axis=2) > 26
    diff[:200, :] = False
    diff[diff.sum(axis=1) > 0.8 * w, :] = False
    # flood fill the background so interior light fur is kept
    bgm = np.zeros((h, w), bool)
    dq = deque()
    for y in range(h):
        for x in (0, w - 1):
            if not diff[y, x] and not bgm[y, x]:
                bgm[y, x] = True
                dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not bgm[ny, nx] and not diff[ny, nx]:
                bgm[ny, nx] = True
                dq.append((ny, nx))
    return ~bgm


def render_mask(path):
    img = np.asarray(Image.open(path).convert("RGBA"))
    return img[:, :, 3] > 32


def fit_mask(mask, height=512, width=None):
    """Scale to a common height without changing aspect ratio, then centre."""
    ys, xs = np.where(mask)
    if not len(ys):
        return np.zeros((height, width or height), bool)
    crop = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    scale = height / crop.shape[0]
    new_w = max(1, round(crop.shape[1] * scale))
    im = Image.fromarray((crop * 255).astype(np.uint8)).resize((new_w, height), Image.LANCZOS)
    arr = np.asarray(im) > 127
    if width is None:
        return arr
    canvas = np.zeros((height, width), bool)
    off = max(0, (width - new_w) // 2)
    canvas[:, off:off + min(new_w, width)] = arr[:, :min(new_w, width)]
    return canvas


def iou(a, b):
    inter = (a & b).sum()
    union = (a | b).sum()
    return inter / union if union else 0.0


def profile_table():
    for view in PANELS:
        m = concept_mask(view)
        ys, xs = np.where(m)
        top, bot, left, right = ys.min(), ys.max(), xs.min(), xs.max()
        height = bot - top + 1
        print(f"[{view}] height={height} width={right - left + 1}")
        for i in range(0, 41, 4):
            y = min(top + int(i * height / 40), bot)
            row = np.where(m[y])[0]
            if not len(row):
                continue
            print(f"   z={1 - i / 40:.2f} width={(row.max() - row.min() + 1) / height:.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("render", nargs="?")
    ap.add_argument("--view", default="front", choices=sorted(PANELS))
    ap.add_argument("--against", default="front", choices=sorted(PANELS))
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.profile:
        profile_table()
        return

    if not args.render:
        ap.error("render path required unless --profile")

    rm = render_mask(args.render)
    cm = concept_mask(args.against)
    ys, xs = np.where(rm)
    cs, _ = np.where(cm)
    width = max(round((xs.max() - xs.min() + 1) * 512 / max(1, ys.max() - ys.min() + 1)),
                round((_.max() - _.min() + 1) * 512 / max(1, cs.max() - cs.min() + 1)))
    r = fit_mask(rm, width=width)
    c = fit_mask(cm, width=width)
    score = iou(r, c)
    if args.json:
        print(json.dumps({"render": args.render, "view": args.view,
                          "against": args.against, "iou": round(score, 4)}))
    else:
        print(f"IoU({args.view} render vs {args.against} concept) = {score:.3f}")
    return 0 if score >= 0.90 else 1


if __name__ == "__main__":
    sys.exit(main() or 0)
