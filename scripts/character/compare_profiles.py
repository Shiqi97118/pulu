"""Compare concept vs render silhouette width/depth at matched heights.

    python3 scripts/character/compare_profiles.py docs/character/renders/blockout-front.png

Prints half-width (front/back view) or front/back depth (side view) per z, in
units of the silhouette height, so the numbers can be fed straight back into
scripts/character/build_kitten.py.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import measure  # noqa: E402

STEPS = 19


def extents(mask):
    ys, xs = np.where(mask)
    top, bot = ys.min(), ys.max()
    height = bot - top + 1
    rows = []
    for i in range(STEPS + 1):
        y = min(top + int(i * height / STEPS), bot)
        xs_row = np.where(mask[y])[0]
        if not len(xs_row):
            rows.append((1 - i / STEPS, None, None))
            continue
        rows.append((1 - i / STEPS, xs_row.min(), xs_row.max()))
    cx = (np.median([r[1] for r in rows if r[1] is not None])
          + np.median([r[2] for r in rows if r[2] is not None])) / 2
    return height, cx, rows


def main():
    render = sys.argv[1]
    view = sys.argv[2] if len(sys.argv) > 2 else "front"
    rm = measure.render_mask(render)
    cm = measure.concept_mask(view)
    rh, rcx, rrows = extents(rm)
    ch, ccx, crows = extents(cm)
    print(f"{'z':>5} | {'concept l/r (H)':>22} | {'render l/r (H)':>22} | {'dW':>7}")
    for (z, cl, cr), (_, rl, rr) in zip(crows, rrows):
        if None in (cl, cr, rl, rr):
            continue
        c_l, c_r = (cl - ccx) / ch, (cr - ccx) / ch
        r_l, r_r = (rl - rcx) / rh, (rr - rcx) / rh
        print(f"{z:5.2f} | {c_l:+10.3f} {c_r:+10.3f} | {r_l:+10.3f} {r_r:+10.3f} | "
              f"{(r_r - r_l) - (c_r - c_l):+7.3f}")


if __name__ == "__main__":
    main()
