"""Pack sprite frames into per-clip WebP strips plus a manifest.

    python3 scripts/art/pack_atlas.py --frames ../work/sprites --out assets/sprites

One horizontal strip per clip keeps slicing trivial and lets the runtime lazy-load
only the clip it needs. See docs/character/SPRITE_SPEC.md.
"""

import argparse
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--quality", type=int, default=82)
    ap.add_argument("--lossless", action="store_true")
    args = ap.parse_args()

    frames_dir = Path(args.frames)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = json.loads((frames_dir / "summary.json").read_text())
    clips = []
    total = 0

    for name, meta in summary.items():
        clip_dir = frames_dir / name
        files = sorted(clip_dir.glob("*.png"))
        if not files:
            print("SKIP_EMPTY", name)
            continue
        first = Image.open(files[0]).convert("RGBA")
        w, h = first.size
        strip = Image.new("RGBA", (w * len(files), h), (0, 0, 0, 0))
        frames = []
        for i, f in enumerate(files):
            strip.paste(Image.open(f).convert("RGBA"), (i * w, 0))
            frames.append({"x": i * w, "y": 0, "w": w, "h": h})
        sheet = f"{name}.webp"
        strip.save(out_dir / sheet, "WEBP", quality=args.quality,
                   method=6, lossless=args.lossless)
        size = (out_dir / sheet).stat().st_size
        total += size
        clips.append({
            "name": name,
            "fps": meta["fps"],
            "loop": meta["loop"],
            "duration": meta["duration"],
            "sheet": sheet,
            "frames": frames,
        })
        print(f"PACK {name:14s} frames={len(frames):3d} {size/1024:6.1f} KiB")

    manifest = {
        "frameSize": {"w": w, "h": h},
        "anchor": {"x": 0.5, "y": 0.985},
        "generatedFrom": "placeholder 3D render (visual parity with the GLB)",
        "clips": clips,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"TOTAL {total/1024:.1f} KiB across {len(clips)} clips")


if __name__ == "__main__":
    main()
