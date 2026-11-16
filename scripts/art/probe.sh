#!/bin/bash
# Wait for the ChatGPT/Codex turn quota to reset, then try one reference-guided
# key-pose generation. Logs every attempt so the outcome is auditable.
PY=/Users/shiki.liu/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3
cd "$(dirname "$0")/../.." || exit 1
mkdir -p ../work/art
for i in $(seq 1 14); do
  echo "=== attempt $i at $(date +%H:%M:%S) ==="
  $PY scripts/art/gen.py \
    --ref docs/character/reference/PULU-turnaround-v05.png \
    --out ../work/art/keypose-try.png \
    --prompt "Character sheet reference attached. Render ONE sprite image: a photorealistic plush silver-grey tabby kitten sitting upright in a front three-quarter view, facing the viewer, same character as the reference (silver-grey tabby coat, white chest and white paws, big round amber eyes, tiny pink nose, red collar with a red bell, solid dark-grey tail). Full body, centered, soft studio light, plain flat warm-beige background, no text, no cast shadow. Square 1024x1024." 2>&1 | tail -2
  if [ -f ../work/art/keypose-try.png ]; then
    if [ "$(date -r ../work/art/keypose-try.png +%s)" -ge "$(date -v-5M +%s)" ]; then
      echo "FRESH_IMAGE_OK"; exit 0
    fi
  fi
  sleep 180
done
echo "GAVE_UP"
