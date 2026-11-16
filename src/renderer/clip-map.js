// Maps a behavior state to the atlas clip that renders it.
//
// This is the only place that names a clip for a state. tests/sprite-assets.test.js
// checks two things against it, because both used to drift silently:
//   - every key is a state Behavior.choose() accepts;
//   - every value exists in assets/sprites/manifest.json.
// The renderer entry used to carry this object inline, so a rename in the atlas
// could leave a state pointing at a clip that no longer existed.
export const clipFor = {
  idle: 'idle_observe',
  walk: 'walk_in_place',
  sleep: 'sleep_loop',
  stretch: 'stretch_exit',
  watch: 'cursor_watch',
  pet: 'pet_react',
  micro: 'micro_ear_tail',
};

// Clip played when a state has no mapping or the mapped clip is missing.
export const FALLBACK_CLIP = 'idle_observe';
