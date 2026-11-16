const allowed = new Set(['idle', 'walk', 'sleep', 'stretch', 'watch', 'pet', 'micro']);
export class Behavior {
  constructor(random = Math.random) { this.random = random; this.state = 'idle'; this.until = 8; this.time = 0; this.paused = false; this.reduced = false; this.lastPet = -Infinity; }
  setPaused(value) { this.paused = !!value; }
  setReduced(value) { this.reduced = !!value; if (value && this.state === 'walk') this.choose('idle', 8); }
  choose(state, duration) { if (!allowed.has(state)) return false; this.state = state; this.until = this.time + duration; return true; }
  pet() { if (this.paused || this.time - this.lastPet < 1.5) return false; this.lastPet = this.time; return this.choose('pet', 1.5); }
  tick(delta) {
    if (this.paused) return this.state;
    this.time += Math.min(Math.max(Number.isFinite(delta) ? delta : 0, 0), 0.1);
    if (this.time >= this.until) {
      if (this.state === 'sleep') this.choose('stretch', 3);
      else if (this.state !== 'idle') this.choose('idle', 8 + this.random() * 8);
      else { const choices = this.reduced ? ['sleep', 'micro', 'watch'] : ['walk', 'sleep', 'watch', 'micro']; const s = choices[Math.min(choices.length - 1, Math.floor(this.random() * choices.length))]; this.choose(s, s === 'sleep' ? 20 : 4); }
    }
    return this.state;
  }
}
export function clampPosition(x, y, area, width, height) {
  return { x: Math.round(Math.min(Math.max(x, area.x), area.x + Math.max(0, area.width - width))), y: Math.round(Math.min(Math.max(y, area.y), area.y + Math.max(0, area.height - height))) };
}
