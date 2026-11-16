import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile, stat} from 'node:fs/promises';
import {clipFor, FALLBACK_CLIP} from '../src/renderer/clip-map.js';
import {Behavior} from '../src/core/behavior.js';

// Guards the shipped 2D asset (ADR-001): the atlas must contain exactly the
// clips the renderer can play, no more and no less.
//
// scripts/art/clips.json defines fourteen poses as the design set, but the
// behavior state machine only drives seven states. Shipping the other seven
// would be dead weight in the bundle and would make the manifest claim actions
// nobody can trigger, so the atlas carries only what clip-map.js maps.
// Generate the rest when those states are actually wired up.

const SHIPPED = [...new Set([...Object.values(clipFor), FALLBACK_CLIP])].sort();

test('the atlas ships exactly the clips the renderer can play', async () => {
  const manifest = JSON.parse(await readFile('assets/sprites/manifest.json', 'utf8'));
  const names = manifest.clips.map(c => c.name).sort();
  assert.deepEqual(names, SHIPPED, 'manifest must match clip-map.js: no missing clip, no dead weight');
  assert.equal(manifest.frameSize.w, 152);
  assert.ok(manifest.anchor.y > 0.9, 'anchor should sit near the feet');
  for (const clip of manifest.clips) {
    assert.ok(clip.frames.length >= 2, `${clip.name} needs at least two frames`);
    assert.ok(clip.fps > 0 && clip.fps <= 24, `${clip.name} fps out of range`);
    for (const f of clip.frames) {
      assert.ok(f.w > 0 && f.h > 0, `${clip.name} has an empty frame rect`);
    }
  }
});

test('sprite atlas stays inside the size budget', async () => {
  const manifest = JSON.parse(await readFile('assets/sprites/manifest.json', 'utf8'));
  let total = 0;
  for (const clip of manifest.clips) {
    const info = await stat(`assets/sprites/${clip.sheet}`);
    assert.ok(info.size > 0, `${clip.sheet} is empty`);
    total += info.size;
  }
  assert.ok(total <= 6 * 1024 * 1024, `sprite atlas ${(total / 1024 / 1024).toFixed(2)} MiB over 6 MiB`);
});

// The renderer used to carry its state-to-clip object inline, so renaming a
// clip in the atlas could leave a state pointing at a name that no longer
// existed, and SpritePlayer.play() then returned false in silence. Manifest
// coverage is pinned by the test above; this one pins the other half: every
// state clip-map.js names must be a state the machine actually accepts.

test('every mapped state is one Behavior accepts', () => {
  const behavior = new Behavior(() => 0);
  for (const state of Object.keys(clipFor)) {
    assert.equal(behavior.choose(state, 1000), true, `Behavior.choose rejects state "${state}"`);
  }
});

test('the behavior machine never enters a state that has no clip', () => {
  const picks = [0.05, 0.3, 0.55, 0.8, 0.95];
  let n = 0;
  const behavior = new Behavior(() => picks[n++ % picks.length]);
  const seen = new Set();
  for (let i = 0; i < 4000; i++) seen.add(behavior.tick(0.1));
  behavior.time += 10;
  behavior.lastPet = -Infinity;
  assert.equal(behavior.pet(), true, 'pet() should be accepted after the cooldown');
  seen.add(behavior.state);

  for (const state of seen) {
    assert.ok(clipFor[state], `Behavior entered "${state}" but no clip is mapped`);
  }
  assert.ok(seen.size >= 6, `expected the machine to explore states, saw: ${[...seen].join(', ')}`);
});
