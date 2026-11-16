import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

// Guards the shipped character asset. Parses the GLB container directly so the
// check does not depend on three.js or on the build having run.

function parseGlb(buffer) {
  assert.equal(buffer.readUInt32LE(0), 0x46546c67, 'GLB magic');
  let off = 12;
  let json = null;
  while (off < buffer.length) {
    const len = buffer.readUInt32LE(off);
    const type = buffer.readUInt32LE(off + 4);
    const chunk = buffer.subarray(off + 8, off + 8 + len);
    if (type === 0x4e4f534a) json = JSON.parse(chunk.toString('utf8'));
    off += 8 + len;
  }
  return json;
}

const REQUIRED_CLIPS = [
  'idle_observe', 'walk_in_place', 'sleep_enter', 'sleep_loop', 'stretch_exit',
  'cursor_watch', 'pet_react', 'micro_groom', 'micro_ear_tail', 'intro_peek',
];

test('shipped GLB meets the M01 asset budget', async () => {
  const buf = await readFile('assets/pulu-kitten-rigged.glb');
  const glb = parseGlb(buf);
  const acc = glb.accessors;
  let triangles = 0;
  for (const mesh of glb.meshes) {
    for (const prim of mesh.primitives) {
      if (prim.indices !== undefined) triangles += acc[prim.indices].count / 3;
    }
  }
  assert.ok(buf.length <= 12 * 1024 * 1024, `GLB ${buf.length} bytes over 12 MiB`);
  assert.ok(triangles <= 30000, `${triangles} triangles over budget`);
  assert.ok(glb.materials.length <= 4, `${glb.materials.length} materials over budget`);
  assert.equal(glb.images.length, 1, 'expected exactly one embedded atlas');
  for (const mat of glb.materials) {
    assert.ok(mat.alphaMode === undefined, `${mat.name} must stay opaque`);
    assert.notEqual(mat.doubleSided, true, `${mat.name} must stay single sided`);
  }
  const prims = glb.meshes.reduce((n, m) => n + m.primitives.length, 0);
  assert.ok(prims <= 8, `${prims} draw calls over the budget of 8`);
});

test('shipped GLB carries a skin and all ten clips', async () => {
  const glb = parseGlb(await readFile('assets/pulu-kitten-rigged.glb'));
  assert.equal(glb.skins.length, 1, 'expected one skin');
  assert.ok(glb.skins[0].joints.length >= 20);
  const names = glb.animations.map(a => a.name).sort();
  assert.deepEqual(names, [...REQUIRED_CLIPS].sort());
  for (const anim of glb.animations) {
    assert.ok(anim.channels.length > 0, `${anim.name} has no channels`);
  }
  const root = glb.nodes.find(n => n.name === 'PULU_root');
  assert.ok(root && Math.abs(root.scale[0] - 0.19) < 1e-3, 'root must scale the pet to 0.19 m');
});
