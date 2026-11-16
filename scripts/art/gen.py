#!/usr/bin/env python3
"""Drive the Codex CLI's image generation to produce PULU sprite frames.

The CLI exposes a server-side `image_gen` tool. We run it head-less with
`codex exec --json`, collect each `image_generation_call` event's saved path and
copy the PNG into the workspace.

    python3 scripts/art/gen.py --prompt "..." --out work/art/idle-01.png
    python3 scripts/art/gen.py --prompt "..." --ref docs/character/reference/PULU-turnaround-v05.png

Requires the ChatGPT/Codex account to have turn quota; image generation itself is
not separately metered, but the agent turn is.
"""

import argparse
import json
import os
import shutil
import subprocess
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Keep the isolated Codex home OUTSIDE the repository. It receives a copy of
# auth.json below, and an earlier layout put it at <repo>/.codexhome, where a
# `git add -A` committed the Codex login token to a public branch.
CODEX_HOME = Path(os.environ.get("PULU_CODEX_HOME") or (ROOT.parent / ".codexhome"))


def find_codex():
    """Locate the Codex CLI: explicit override, PATH, then known installs."""
    override = os.environ.get("PULU_CODEX_BIN")
    if override:
        return Path(override)
    found = shutil.which("codex")
    if found:
        return Path(found)
    if sys.platform == "darwin":
        candidates = [Path.home() / ".codex/plugins/.plugin-appserver/codex-cli/CodexCLI.app/Contents/MacOS/codex"]
    elif sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData/Local")) / "OpenAI/Codex/bin"
        candidates = sorted(base.glob("*/codex.exe"))
    else:
        candidates = []
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


INSTRUCTION = (
    "Use the image generation tool to produce exactly one PNG image. "
    "Do not write code, do not run shell commands, do not create other files. "
    "When it is done, reply with the image path only."
)


def run(prompt, ref=None, timeout=600):
    codex_bin = find_codex()
    if codex_bin is None:
        sys.exit("codex CLI not found; set PULU_CODEX_BIN to its path")
    home = CODEX_HOME.resolve()
    if home == ROOT.resolve() or ROOT.resolve() in home.parents:
        sys.exit(f"refusing to keep a Codex home inside the repository: {home}")
    home.mkdir(parents=True, exist_ok=True)
    auth = home / "auth.json"
    if not auth.exists():
        shutil.copy(Path.home() / ".codex/auth.json", auth)
        auth.chmod(0o600)

    cmd = [
        str(codex_bin), "exec", "--json",
        "--ignore-user-config", "--skip-git-repo-check",
        "-C", str(ROOT),
    ]
    # --image is a multi-value option and would swallow the positional prompt,
    # so use the = form and keep the prompt as the last argument
    if ref:
        cmd += [f"--image={ref}"]
    cmd += [f"{prompt}\n\n{INSTRUCTION}"]

    env = dict(os.environ, CODEX_HOME=str(home))
    started = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env,
                         stdin=subprocess.DEVNULL)
    # only images written by THIS run count; stale files from earlier sessions
    # would otherwise be reported as success

    images, errors = [], []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = json.dumps(event)
        if event.get("type") == "error" or "'error'" in text:
            msg = event.get("message") or event.get("error", {}).get("message")
            if msg:
                errors.append(msg)
        for key in ("savedPath", "saved_path"):
            if key in text:
                images.append(event)
        if event.get("type") == "item.completed" and "image_gen" in text:
            images.append(event)
    return proc, images, errors, started


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", default=None)
    args = ap.parse_args()

    proc, images, errors, started = run(args.prompt, args.ref)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # the tool usually writes into ~/.codex/generated_images/exec-*.png
    def fresh(paths):
        return sorted((p for p in paths if p.stat().st_mtime >= started - 1),
                      key=lambda p: p.stat().st_mtime, reverse=True)

    candidates = fresh((home / "generated_images").glob("**/*.png"))
    if not candidates:
        candidates = fresh((Path.home() / ".codex/generated_images").glob("**/*.png"))

    if not candidates:
        print(json.dumps({"ok": False, "errors": errors, "stdout": proc.stdout[-600:],
                      "stderr": proc.stderr[-600:], "code": proc.returncode}, ensure_ascii=False))
        sys.exit(1)

    shutil.copy(candidates[0], out)
    print(json.dumps({"ok": True, "out": str(out), "source": str(candidates[0]),
                      "errors": errors}, ensure_ascii=False))


if __name__ == "__main__":
    main()
