"""Paint the PULU coat atlas from the approved V05 markings.

    python3 scripts/character/paint_coat.py --out assets/coat-atlas.png

The atlas layout is shared with build_kitten.py through atlas_layout.json.
Angle convention: u = 0.5 is the FRONT of the animal, u = 0/1 is the BACK seam,
so the back stripes have to stay continuous across the wrap.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
LAYOUT = ROOT / "scripts/character/atlas_layout.json"


def tri(x):
    return 2.0 * np.abs(x - np.floor(x + 0.5))


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def mix(c1, c2, t):
    t = t[..., None]
    return c1 * (1 - t) + c2 * t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "assets/coat-atlas.png"))
    ap.add_argument("--size", type=int)
    args = ap.parse_args()

    cfg = json.loads(LAYOUT.read_text())
    size = args.size or cfg["size"]
    pal = {k: np.array(v, float) for k, v in cfg["palette"].items()}

    u = (np.arange(size) + 0.5) / size
    v = (np.arange(size) + 0.5) / size
    U, V = np.meshgrid(u, v)          # V increases upward (flip at save time)

    img = np.zeros((size, size, 3), float)
    img[:] = pal["silver"]

    # ---------------------------------------------------------------- body
    x0, y0, x1, y1 = cfg["regions"]["body"]
    m = (U >= x0) & (U < x1) & (V >= y0) & (V < y1)
    a = (U - 0.5) * 2 * np.pi          # 0 = front, +-pi = back
    h = (V - y0) / (y1 - y0)           # 0 = ground, 1 = shoulder

    front = np.cos(a)                  # 1 front, -1 back
    body = np.zeros_like(img)
    # white chest/belly wrapping round the front third, fading in above the paws
    chest = smoothstep(0.42, 0.70, front) * smoothstep(0.08, 0.26, h) * (1 - smoothstep(0.88, 1.0, h))
    body[:] = pal["silver"]
    body = mix(body, pal["white"], chest)

    # back: three longitudinal stripes, slightly irregular, fading at the flanks
    backness = smoothstep(-0.10, -0.62, front)
    wave = tri(a * (9.0 / (2 * np.pi)) + 0.07 * np.sin(9 * a))
    stripe = smoothstep(0.52, 0.80, wave) * backness * smoothstep(0.18, 0.40, h) * (1 - smoothstep(0.92, 1.0, h))
    body = mix(body, pal["stripe"], stripe)

    # side bullseye: an off-centre blot plus an open ring on each flank
    for side in (-1, 1):
        ca = side * np.pi * 0.62       # flank angle
        d = np.hypot((a - ca) * 0.95, (h - 0.52) * 2.6)
        blot = 1 - smoothstep(0.13, 0.22, d)
        ring = smoothstep(0.33, 0.37, d) * (1 - smoothstep(0.43, 0.47, d))
        ring = ring * (0.45 + 0.55 * np.sin(a * 3.0 + 1.1))   # broken, irregular arc
        body = mix(body, pal["stripe"], 0.9 * blot + 0.60 * np.clip(ring, 0, 1))
    img[m] = body[m]

    # ---------------------------------------------------------------- head
    x0, y0, x1, y1 = cfg["regions"]["head"]
    m = (U >= x0) & (U < x1) & (V >= y0) & (V < y1)
    hr = (U - x0) / (x1 - x0)
    hv = (V - y0) / (y1 - y0)          # 0 = chin, 1 = crown
    ha = (hr - 0.5) * 2 * np.pi

    head = np.zeros_like(img)
    head[:] = pal["silver"]
    # white muzzle, chin and cheek field
    muzzle = smoothstep(0.30, 0.72, np.cos(ha)) * (1 - smoothstep(0.50, 0.66, hv))
    head = mix(head, pal["white"], muzzle)
    # cheek ruffs: white bleeding up the sides of the lower head
    cheek = smoothstep(0.45, 0.85, np.abs(np.cos(ha))) * (1 - smoothstep(0.30, 0.52, hv)) \
        * smoothstep(0.05, 0.30, hv) * 0.55
    head = mix(head, pal["white"], cheek)
    # forehead: fine irregular arcs running down into the neck
    ftone = smoothstep(0.55, 0.78, hv) * smoothstep(-0.55, 0.15, np.cos(ha))
    arcs = smoothstep(0.50, 0.78, tri(ha * (10.0 / (2 * np.pi)) + 0.08 * np.sin(10 * ha)))
    head = mix(head, pal["stripe"], 0.75 * arcs * ftone)
    # central "M" mark above the eyes
    central = (1 - smoothstep(0.12, 0.26, np.abs(ha))) * smoothstep(0.62, 0.74, hv) \
        * (1 - smoothstep(0.90, 0.98, hv))
    head = mix(head, pal["stripe"], 0.55 * central)
    img[m] = head[m]

    # ---------------------------------------------------------------- legs
    x0, y0, x1, y1 = cfg["regions"]["legs"]
    m = (U >= x0) & (U < x1) & (V >= y0) & (V < y1)
    lv = (V - y0) / (y1 - y0)
    leg = mix(pal["white"], pal["silver"], smoothstep(0.55, 0.95, lv))
    img[m] = leg[m]

    # ---------------------------------------------------------------- tail (solid dark)
    x0, y0, x1, y1 = cfg["regions"]["tail"]
    m = (U >= x0) & (U < x1) & (V >= y0) & (V < y1)
    img[m] = pal["tail"]

    # ---------------------------------------------------------------- ears
    x0, y0, x1, y1 = cfg["regions"]["ears"]
    m = (U >= x0) & (U < x1) & (V >= y0) & (V < y1)
    ev = (V - y0) / (y1 - y0)
    ear = mix(pal["silver"], pal["silver_dark"], smoothstep(0.35, 1.0, ev) * 0.35)
    img[m] = ear[m]

    # ---------------------------------------------------------------- white parts
    x0, y0, x1, y1 = cfg["regions"]["white"]
    m = (U >= x0) & (U < x1) & (V >= y0) & (V < y1)
    img[m] = pal["white"]

    # ---------------------------------------------------------------- nose
    x0, y0, x1, y1 = cfg["regions"]["nose"]
    m = (U >= x0) & (U < x1) & (V >= y0) & (V < y1)
    img[m] = pal["nose_pink"]

    # ---------------------------------------------------------------- eyes
    x0, y0, x1, y1 = cfg["regions"]["eye"]
    m = (U >= x0) & (U < x1) & (V >= y0) & (V < y1)
    ecx, ecy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2 * 0.96, (y1 - y0) / 2 * 0.96
    du = (U - ecx) / rx
    dv = (V - ecy) / ry
    dist = np.hypot(du, dv)
    eye = np.zeros_like(img)
    eye[:] = pal["eye_dark"]
    iris = (dist > 0.56) & (dist < 0.88)
    eye[iris] = pal["iris"]
    rim = (dist >= 0.88) & (dist <= 1.0)
    eye[rim] = pal["eye_dark"]
    hl = np.hypot(du + 0.30, dv - 0.34)
    eye[hl < 0.22] = pal["highlight"]
    hl2 = np.hypot(du - 0.26, dv + 0.30)
    eye[hl2 < 0.10] = pal["highlight"] * 0.72
    img[m] = eye[m]

    out = np.clip(img, 0, 255).astype(np.uint8)
    Image.fromarray(out[::-1]).save(args.out)   # flip: atlas v grows up
    print(f"wrote {args.out} ({size}x{size})")


if __name__ == "__main__":
    main()
