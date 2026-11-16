/**
 * Sprite player for the PULU 2D character (ADR-001).
 *
 * Draws a clip from an atlas manifest onto a 2D canvas. Deliberately small and
 * dependency free: the desktop shell only needs "play clip X", "pause", and an
 * alpha hit test.
 *
 * Manifest shape (see docs/character/SPRITE_SPEC.md):
 * {
 *   frameSize: {w, h},
 *   anchor: {x, y},                       // feet centre, in frame pixels
 *   clips: [{
 *     name, loop, fps,
 *     sheet: 'pulu-atlas-idle.webp',
 *     frames: [{x, y, w, h}]
 *   }]
 * }
 */

export class SpritePlayer {
  constructor(canvas, {onReady, onTick, base = 'sprites/'} = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.ctx.imageSmoothingEnabled = true;
    this.manifest = null;
    this.sheets = new Map();
    this.onReady = onReady;
    this.onTick = onTick;
    this.base = base;
    this.current = null;
    this.frame = 0;
    this.elapsed = 0;
    this.paused = false;
    this.reduced = false;
    this.raf = null;
    this.last = 0;
    this.alphaCache = new Map();
  }

  async load(source) {
    // a manifest object is passed in by the bundle: file:// fetch is blocked by
    // CSP/CORS, images are not, so only the sheets are fetched at runtime
    this.manifest = typeof source === 'string' ? await (await fetch(source)).json() : source;
    this.canvas.width = this.manifest.frameSize.w;
    this.canvas.height = this.manifest.frameSize.h;
    this.onReady?.();
    return this.manifest;
  }

  async _sheet(clip) {
    if (this.sheets.has(clip.sheet)) return this.sheets.get(clip.sheet);
    const image = new Image();
    image.src = new URL(this.base + clip.sheet, location.href).href;
    await image.decode();
    this.sheets.set(clip.sheet, image);
    return image;
  }

  async play(name, {immediate = false} = {}) {
    const clip = this.manifest?.clips.find(c => c.name === name);
    // A missing clip used to return false in silence: the previous clip kept
    // playing and nothing anywhere said why. Surface it instead.
    if (!clip) {
      console.warn(`sprite clip not found in manifest: ${name}`);
      return false;
    }
    if (this.current?.name === name && !immediate) return true;
    await this._sheet(clip);
    this.current = clip;
    this.frame = 0;
    this.elapsed = 0;
    this.draw();
    this._start();
    return true;
  }

  _fps() {
    if (!this.current) return 12;
    return this.reduced ? Math.min(4, this.current.fps) : this.current.fps;
  }

  _start() {
    if (this.raf !== null) return;
    this.last = performance.now();
    const tick = now => {
      const dt = Math.min((now - this.last) / 1000, 0.1);
      this.last = now;
      this.onTick?.(dt);
      if (!this.paused && this.current) this._advance(dt);
      this.draw();
      this.raf = requestAnimationFrame(tick);
    };
    this.raf = requestAnimationFrame(tick);
  }

  _advance(dt) {
    const clip = this.current;
    const step = 1 / this._fps();
    this.elapsed += dt;
    while (this.elapsed >= step) {
      this.elapsed -= step;
      this.frame += 1;
      if (this.frame >= clip.frames.length) {
        if (clip.loop === false) {
          this.frame = clip.frames.length - 1;
          this.paused = true;
          return;
        }
        this.frame = 0;
      }
    }
  }

  draw() {
    if (!this.current) return;
    const {ctx, canvas} = this;
    const rect = this.current.frames[this.frame];
    const sheet = this.sheets.get(this.current.sheet);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!sheet) return;
    ctx.drawImage(sheet, rect.x, rect.y, rect.w, rect.h, 0, 0, canvas.width, canvas.height);
  }

  setPaused(paused) {
    this.paused = paused;
  }

  setReduced(reduced) {
    this.reduced = reduced;
  }

  async stop() {
    if (this.raf !== null) cancelAnimationFrame(this.raf);
    this.raf = null;
    this.current = null;
    this.draw();
  }

  /**
   * Alpha hit test for the current frame. Built once per frame into an offscreen
   * canvas; a 152 px sprite is cheap to sample per pointer move.
   */
  async hit(x, y) {
    if (!this.current) return false;
    const key = `${this.current.name}:${this.frame}`;
    let mask = this.alphaCache.get(key);
    if (!mask) {
      const rect = this.current.frames[this.frame];
      const sheet = this.sheets.get(this.current.sheet);
      if (!sheet) return false;
      const off = new OffscreenCanvas(rect.w, rect.h);
      const octx = off.getContext('2d');
      octx.drawImage(sheet, rect.x, rect.y, rect.w, rect.h, 0, 0, rect.w, rect.h);
      mask = octx.getImageData(0, 0, rect.w, rect.h).data;
      this.alphaCache.set(key, mask);
      if (this.alphaCache.size > 40) {
        const oldest = this.alphaCache.keys().next().value;
        this.alphaCache.delete(oldest);
      }
    }
    const sx = Math.floor((x / this.canvas.clientWidth) * this.canvas.width);
    const sy = Math.floor((y / this.canvas.clientHeight) * this.canvas.height);
    if (sx < 0 || sy < 0 || sx >= this.canvas.width || sy >= this.canvas.height) return false;
    return mask[(sy * this.canvas.width + sx) * 4 + 3] > 24;
  }
}
