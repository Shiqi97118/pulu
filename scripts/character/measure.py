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


def _morph(m, k, op):
    """Square binary dilation/erosion without wrap-around."""
    pad = np.pad(m, k, mode="constant", constant_values=(op == "erode"))
    h, w = m.shape
    out = np.ones_like(m) if op == "erode" else np.zeros_like(m)
    for dy in range(2 * k + 1):
        for dx in range(2 * k + 1):
            window = pad[dy:dy + h, dx:dx + w]
            out = out & window if op == "erode" else out | window
    return out


def _largest_component(m):
    h, w = m.shape
    seen = np.zeros_like(m)
    best, best_n = np.zeros_like(m), 0
    ys_all, xs_all = np.where(m)
    for y0, x0 in zip(ys_all, xs_all):
        if seen[y0, x0]:
            continue
        stack = [(y0, x0)]
        seen[y0, x0] = True
        pts = []
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if len(pts) > best_n:
            best_n = len(pts)
            best = np.zeros_like(m)
            for py, px in pts:
                best[py, px] = True
    return best


def _grow_background(sub, tol=6):
    """Region-grow from the panel border, comparing each pixel to its parent.

    The backdrop is a smooth gradient, so neighbour differences stay tiny while
    the fur edge jumps. This is robust to vignetting, unlike a global model.
    """
    h, w, _ = sub.shape
    bg = np.zeros((h, w), bool)
    stack = []
    for x in range(w):
        for y in (0, h - 1):
            if not bg[y, x]:
                bg[y, x] = True
                stack.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not bg[y, x]:
                bg[y, x] = True
                stack.append((y, x))
    while stack:
        y, x = stack.pop()
        cur = sub[y, x]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not bg[ny, nx]:
                if np.abs(sub[ny, nx] - cur).sum() < tol:
                    bg[ny, nx] = True
                    stack.append((ny, nx))
    return bg


def concept_mask(view, path=CONCEPT):
    img = np.asarray(Image.open(path).convert("RGB")).astype(np.float64)
    x0, x1 = PANELS[view]
    sub = img[:, x0:x1]
    bg = _grow_background(sub, tol=6)
    m = ~bg
    m[:205, :] = False                    # title row
    # the ground guide line sits in the background; region growing leaves it
    m = _morph(_morph(m, 1, "dilate"), 1, "erode")
    # vertical erosion removes the 1-2px horizontal guide lines, keeps the cat
    m[1:] &= m[:-1].copy()
    m = _largest_component(m)
    h, w = m.shape
    holes = ~m
    seen = np.zeros_like(holes)
    stack = [(y, x) for y in range(h) for x in (0, w - 1) if holes[y, x]]
    stack += [(y, x) for x in range(w) for y in (0, h - 1) if holes[y, x]]
    for y, x in stack:
        seen[y, x] = True
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and holes[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                stack.append((ny, nx))
    return m | (~seen & holes)


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
