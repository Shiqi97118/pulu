"""Normalise generated frames and build the atlas + manifest.

    python3 scripts/art/assemble.py --frames ../work/art --out ../work/sprites-ai

Reads scripts/art/clips.json for fps/loop/frame counts, trims each generated PNG
to its alpha bounds, scales it into the 152 px sprite frame with the feet on the
baseline, then writes a summary.json that pack_atlas.py consumes.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from slice_strip import normalise  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default=str(ROOT.parent / "work/art"))
    ap.add_argument("--out", default=str(ROOT.parent / "work/sprites-ai"))
    ap.add_argument("--clips", default=str(ROOT / "scripts/art/clips.json"))
    ap.add_argument("--fallback", default=str(ROOT.parent / "work/sprites"),
                    help="placeholder frames used when a clip is incomplete")
    args = ap.parse_args()

    cfg = json.loads(Path(args.clips).read_text())
    src = Path(args.frames)
    out = Path(args.out)
    fallback = Path(args.fallback)
    summary = {}

    for clip in cfg["clips"]:
        name = clip["name"]
        clip_src = src / name
        frames = sorted(clip_src.glob("*.png")) if clip_src.exists() else []
        expected = len(clip["poses"])
        if len(frames) < expected:
            fb = fallback / name
            fb_frames = sorted(fb.glob("*.png")) if fb.exists() else []
            if fb_frames:
                print(f"FALLBACK {name}: {len(frames)}/{expected} generated, using placeholder")
                dest = out / name
                dest.mkdir(parents=True, exist_ok=True)
                for f in dest.glob("*.png"):
                    f.unlink()
                for i, f in enumerate(fb_frames):
                    Image.open(f).convert("RGBA").save(dest / f"{i:04d}.png")
                summary[name] = {"fps": 6, "loop": True, "frames": len(fb_frames),
                                 "duration": round(len(fb_frames) / 6, 2)}
                continue
            print(f"MISSING {name}: no frames and no fallback")
            continue

        dest = out / name
        dest.mkdir(parents=True, exist_ok=True)
        for f in dest.glob("*.png"):
            f.unlink()
        for i, f in enumerate(frames[:expected]):
            normalise(Image.open(f).convert("RGBA")).save(dest / f"{i:04d}.png")
        summary[name] = {
            "fps": clip["fps"],
            "loop": clip["loop"],
            "frames": expected,
            "duration": round(expected / clip["fps"], 2),
        }
        print(f"ASSEMBLE {name}: {expected} frames @ {clip['fps']}fps")

    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    total = sum(v["frames"] for v in summary.values())
    print(f"ASSEMBLED clips={len(summary)} frames={total}")


if __name__ == "__main__":
    main()
