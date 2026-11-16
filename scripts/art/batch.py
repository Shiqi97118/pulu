"""Generate every sprite frame for the clip set, resumably.

    python3 scripts/art/batch.py --clips scripts/art/clips.json --only walk_in_place
    python3 scripts/art/batch.py --limit 30        # keep a batch bounded

Per clip: frame 0 is generated from the clip's anchor reference (the approved
idle frame, or a dedicated pose anchor), then frames 1..n-1 are generated from
frame 0 so the model only has to change one thing at a time. Existing frames are
skipped, so the job can be interrupted and resumed.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "scripts/art/gen.py"
ART = ROOT.parent / "work/art"


def run_gen(prompt, ref, out, retries=2):
    for attempt in range(retries + 1):
        proc = subprocess.run(
            [sys.executable, str(GEN), "--prompt", prompt, "--out", str(out),
             "--ref", str(ref)],
            capture_output=True, text=True, stdin=subprocess.DEVNULL,
        )
        try:
            result = json.loads(proc.stdout.strip().splitlines()[-1])
        except (json.JSONDecodeError, IndexError):
            result = {"ok": False, "reason": proc.stdout[-300:] + proc.stderr[-300:]}
        if result.get("ok") and Path(out).exists():
            return True, result
        time.sleep(4)
    return False, result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", default=str(ROOT / "scripts/art/clips.json"))
    ap.add_argument("--only", default=None, help="comma separated clip names")
    ap.add_argument("--limit", type=int, default=0, help="stop after N new frames")
    ap.add_argument("--out", default=str(ART))
    args = ap.parse_args()

    cfg = json.loads(Path(args.clips).read_text())
    identity = cfg["identity"]
    out_root = Path(args.out)
    only = set(args.only.split(",")) if args.only else None

    made = 0
    for clip in cfg["clips"]:
        name = clip["name"]
        if only and name not in only:
            continue
        clip_dir = out_root / name
        clip_dir.mkdir(parents=True, exist_ok=True)
        anchor = out_root / clip["anchor_ref"]
        if not anchor.exists():
            print(f"SKIP {name}: anchor {anchor} missing", flush=True)
            continue
        for i, pose in enumerate(clip["poses"]):
            target = clip_dir / f"{i:03d}.png"
            if target.exists():
                continue
            if args.limit and made >= args.limit:
                print(f"STOP at limit ({made} new frames)", flush=True)
                return
            # frame 0 establishes the pose; later frames refine from it
            ref = anchor if i == 0 else clip_dir / "000.png"
            if not Path(ref).exists():
                ref = anchor
            lead = clip.get("anchor_pose", "") if i == 0 else ""
            prompt = (
                f"{identity}\n\nThis kitten is {lead or pose}. "
                + (f"Relative to the attached image, change only this: {pose}. "
                   "Keep the character, fur pattern, colours, collar, tail, camera angle, "
                   "scale and position identical." if i > 0 else
                   "Full body, centred, feet near the bottom edge.")
            )
            ok, result = run_gen(prompt, ref, target)
            made += 1
            print(f"{'OK ' if ok else 'FAIL'} {name} frame {i:03d} {'' if ok else result}", flush=True)
    print(f"BATCH_DONE new_frames={made}", flush=True)


if __name__ == "__main__":
    main()
