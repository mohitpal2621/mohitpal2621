// PUSH TO PROD: the game engine. Pure and deterministic (fixed 60 Hz steps, no DOM), so the same code
// runs in the browser and in the script that records the README demo.

export const W = 320, H = 176, T = 16, ROWS = 11, FPS = 60;

// ---------------------------------------------------------------- tiles
export const TILE = {
  EMPTY: 0, GROUND: 1, BRICK: 2, QBIT: 3, QCOFFEE: 4, USED: 5, KEY: 6, RACK: 7,
  BIT: 8, PLAT: 9, SPIKE: 10, QDUCK: 11, QMULTI: 12,
};
const SOLID = [false, true, true, true, true, true, true, true, false, false, true, true, true];
const CHAR_TILE = {
  "#": TILE.GROUND, B: TILE.BRICK, "?": TILE.QBIT, P: TILE.QCOFFEE, D: TILE.QDUCK, M: TILE.QMULTI,
  K: TILE.KEY, R: TILE.RACK, o: TILE.BIT, "=": TILE.PLAT, "^": TILE.SPIKE, U: TILE.USED,
};

// ---------------------------------------------------------------- physics tuning (px per frame)
export const PHYS = {
  walk: 1.75, run: 2.4, runCaffeine: 2.7, accWalk: 0.08, accRun: 0.09, accAir: 0.07,
  friction: 0.1, skid: 0.2, gravity: 0.4, gravityHold: 0.2, maxFall: 5,
  jump: 5.2, jumpBoost: 0.45, stompBounce: 3.6, stompBounceHeld: 5.2, coyote: 6, buffer: 6,
};

// ---------------------------------------------------------------- level building
function builder(width) {
  const g = Array.from({ length: ROWS }, () => Array(width).fill("."));
  const set = (x, y, ch) => { if (x >= 0 && x < width && y >= 0 && y < ROWS) g[y][x] = ch; };
  const api = {
    width,
    ground(x0, x1, top = 9) { for (let x = x0; x <= x1; x++) for (let y = top; y < ROWS; y++) set(x, y, "#"); },
    gap(x0, x1) { for (let x = x0; x <= x1; x++) for (let y = 0; y < ROWS; y++) if (g[y][x] === "#") set(x, y, "."); },
    put(x, y, s) { [...s].forEach((ch, i) => set(x + i, y, ch)); },
    col(x, y0, y1, ch) { for (let y = y0; y <= y1; y++) set(x, y, ch); },
    // a staircase of keycaps standing on the ground (row 9); dir +1 climbs to the right
    stairs(x, heights, ch = "K") { heights.forEach((h, i) => { for (let k = 0; k < h; k++) set(x + i, 8 - k, ch); }); },
    coins(x, y, n) { for (let i = 0; i < n; i++) set(x + i, y, "o"); },
    grid: g,
  };
  return api;
}

function makeLevel(def) {
  const b = builder(def.width);
  def.build(b);
  const rows = b.grid.map(r => r.join(""));
  const w = def.width;
  const tiles = new Array(w * ROWS).fill(0);
  const ents = [];
  let start = { x: 2, y: 8 };
  rows.forEach((row, y) => {
    [...row].forEach((ch, x) => {
      if (CHAR_TILE[ch] !== undefined) tiles[y * w + x] = CHAR_TILE[ch];
      else if (ch === "@") start = { x, y };
      else if ("bms".includes(ch)) ents.push({ kind: { b: "bug", m: "moth", s: "spiky" }[ch], tx: x, ty: y });
      else if (ch === "S") ents.push({ kind: "checkpoint", tx: x, ty: y });
      else if (ch === "G") ents.push({ kind: "goal", tx: x, ty: y });
    });
  });
  return {
    id: def.id, name: def.name, stage: def.stage, theme: def.theme, time: def.time, w, rows,
    tiles, start, ents, lifts: def.lifts || [], letters: def.letters || {}, music: def.music,
  };
}

// World 1: LOCALHOST. Teaches run, jump, stomp, blocks and the coffee power-up.
const L1 = {
  id: "1-1", name: "LOCALHOST", stage: 1, theme: "day", time: 160, width: 176, music: "day",
  letters: { 60: "W", 61: "A", 62: "S", 63: "D", 67: "H", 68: "J", 69: "K", 70: "L", 139: "S", 140: "H", 141: "I", 142: "P", 144: "I", 145: "T" },
  build(b) {
    b.ground(0, 37);
    b.put(3, 8, "@");
    b.coins(7, 6, 3);
    b.put(11, 5, "?");
    b.put(16, 8, "b");
    b.put(19, 5, "B?BPB");
    b.put(21, 1, "o");
    b.col(28, 7, 8, "R");
    b.put(32, 8, "b");
    b.put(37, 6, "o"); b.put(38, 5, "oo"); b.put(40, 6, "o");
    b.ground(40, 75);
    b.col(45, 6, 8, "R");
    b.put(45, 5, "o");
    b.put(49, 8, "b"); b.put(51, 8, "b");
    b.put(54, 6, "===="); b.coins(54, 5, 4);
    b.stairs(60, [1, 2, 3, 4]);
    b.gap(64, 66);
    b.ground(67, 108);
    b.stairs(67, [4, 3, 2, 1]);
    b.put(75, 8, "S");
    b.put(80, 5, "BB?BB"); b.coins(80, 2, 5);
    b.put(83, 8, "b"); b.put(81, 4, "b");
    b.col(90, 7, 8, "R"); b.col(96, 6, 8, "R");
    b.put(93, 8, "b");
    b.put(100, 5, "?D?");
    b.coins(109, 5, 3);
    b.gap(109, 111);
    b.ground(112, 175);
    b.put(115, 6, "===="); b.put(120, 3, "===="); b.coins(120, 2, 4);
    b.put(126, 5, "M");
    b.put(129, 8, "b"); b.put(131, 8, "b"); b.put(133, 8, "b");
    b.stairs(139, [1, 2, 3, 4, 5, 6, 6, 6, 6]);
    b.put(150, 8, "G");
  },
};

// World 2: STAGING. Moths, moving lifts and longer running jumps.
const L2 = {
  id: "1-2", name: "STAGING", stage: 2, theme: "dusk", time: 180, width: 196, music: "dusk",
  lifts: [
    { tx: 58, ty: 6, len: 3, range: 4, speed: 0.5 },
    { tx: 122, ty: 7, len: 3, range: 7, speed: 0.6 },
  ],
  letters: { 95: "G", 96: "I", 97: "T", 176: "U", 177: "A", 178: "T" },
  build(b) {
    b.ground(0, 30);
    b.put(3, 8, "@");
    b.put(8, 5, "?B?B?");
    b.put(14, 4, "m");
    b.coins(16, 6, 3);
    b.put(22, 8, "b"); b.put(24, 8, "b");
    b.col(27, 6, 8, "R");
    b.ground(35, 56);
    b.coins(31, 4, 3);
    b.put(38, 5, "BPB");
    b.put(42, 3, "m");
    b.put(45, 8, "b");
    b.put(48, 6, "==="); b.coins(48, 5, 3);
    b.col(53, 5, 8, "R");
    b.ground(70, 100);
    b.put(74, 8, "S");
    b.put(78, 5, "B?B?B"); b.put(80, 1, "o");
    b.put(79, 4, "b");
    b.put(86, 3, "m"); b.put(92, 4, "m");
    b.stairs(95, [1, 2, 3]);
    b.ground(105, 120);
    b.coins(101, 4, 3);
    b.put(108, 5, "?D?");
    b.put(112, 8, "b"); b.put(114, 8, "b"); b.put(116, 8, "b");
    b.ground(135, 195);
    b.coins(125, 4, 4);
    b.put(140, 3, "m");
    b.put(144, 6, "===="); b.put(150, 4, "===="); b.coins(150, 3, 4);
    b.put(147, 8, "b"); b.put(155, 8, "b");
    b.col(159, 6, 8, "R"); b.put(162, 8, "b"); b.col(165, 5, 8, "R");
    b.put(168, 5, "M");
    b.stairs(173, [1, 2, 3, 4, 5, 6, 6, 6]);
    b.put(185, 8, "G");
  },
};

// World 3: PRODUCTION. Spikes, spiky bugs and lifts over long drops, then the release.
const L3 = {
  id: "1-3", name: "PRODUCTION", stage: 3, theme: "night", time: 200, width: 204, music: "night",
  lifts: [
    { tx: 36, ty: 7, len: 3, range: 6, speed: 0.55 },
    { tx: 100, ty: 7, len: 3, range: 7, speed: 0.6 },
    { tx: 147, ty: 7, len: 3, range: 8, speed: 0.65 },
  ],
  letters: { 76: "G", 77: "I", 78: "T", 84: "R", 85: "U", 86: "N", 187: "P", 188: "R", 189: "O", 190: "D" },
  build(b) {
    b.ground(0, 34);
    b.put(3, 8, "@");
    b.put(9, 5, "?P?");
    b.put(14, 8, "s");
    b.put(20, 8, "^^"); b.coins(20, 6, 2);
    b.col(25, 6, 8, "R");
    b.put(28, 8, "b"); b.put(30, 8, "b");
    b.coins(40, 4, 5);
    b.ground(48, 80);
    b.put(54, 8, "s");
    b.put(57, 5, "BBMBB");
    b.put(58, 4, "b");
    b.put(64, 8, "^^^"); b.coins(64, 5, 3);
    b.put(70, 3, "m");
    b.put(72, 8, "S");
    b.stairs(76, [1, 2, 3]);
    b.ground(84, 98);
    b.stairs(84, [3, 2, 1]);
    b.put(89, 5, "?D?");
    b.put(92, 8, "s"); b.put(95, 8, "b");
    b.coins(104, 3, 4);
    b.ground(112, 145);
    b.put(115, 8, "^^");
    b.put(124, 8, "b");
    b.put(123, 6, "===="); b.coins(123, 5, 4);
    b.put(128, 3, "m"); b.put(131, 8, "b"); b.put(133, 8, "b");
    b.col(137, 5, 8, "R"); b.put(142, 8, "b");
    b.coins(150, 5, 6);
    b.ground(160, 203);
    b.put(169, 5, "BPB");
    b.put(172, 8, "b"); b.put(175, 8, "s"); b.put(178, 8, "b");
    b.stairs(181, [1, 2, 3, 4, 5, 6, 6, 6, 6, 6]);
    b.put(194, 8, "G");
  },
};

// A short level that shows off everything, used for the title-screen demo and the README recording.
const DEMO = {
  id: "DEMO", name: "LOCALHOST", stage: 1, theme: "day", time: 99, width: 72, music: "day",
  letters: { 54: "S", 55: "H", 56: "I", 57: "P" },
  build(b) {
    b.ground(0, 30);
    b.put(2, 8, "@");
    b.coins(6, 6, 3);
    b.put(10, 5, "?");
    b.put(15, 8, "b");
    b.put(18, 5, "BPB");
    b.col(24, 7, 8, "R");
    b.put(27, 8, "b");
    b.coins(30, 5, 3);
    b.ground(34, 71);
    b.put(36, 6, "===="); b.coins(36, 5, 4);
    b.put(42, 8, "b"); b.put(44, 8, "b");
    b.put(46, 5, "B?B");
    b.stairs(51, [1, 2, 3, 4, 5, 5, 5]);
    b.put(61, 8, "G");
  },
};

export const LEVELS = [L1, L2, L3].map(makeLevel);
export const DEMO_LEVEL = makeLevel(DEMO);

// ---------------------------------------------------------------- state
const clone = o => JSON.parse(JSON.stringify(o));

export function newGame(opts = {}) {
  const s = {
    mode: "title", modeT: 0, frame: 0, score: 0, bits: 0, lives: 3, hi: opts.hi || 0,
    levelIndex: 0, level: null, time: 0, checkpoint: null, demo: !!opts.demo,
    player: null, enemies: [], items: [], lifts: [], particles: [], popups: [], bumps: [],
    cam: 0, combo: 0, prev: 0, events: [], flags: {}, rng: 12345, caffeine: false,
  };
  if (opts.demo) begin(s, false);
  return s;
}

function rand(s) {
  s.rng = (s.rng * 1103515245 + 12345) & 0x7fffffff;
  return s.rng / 0x7fffffff;
}

function emit(s, type, extra) { s.events.push(extra ? Object.assign({ type }, extra) : { type }); }

function setMode(s, mode) { s.mode = mode; s.modeT = 0; }

function startLevel(s, src, fromCheckpoint) {
  const lv = clone(src);
  s.level = lv;
  s.time = lv.time * FPS;
  s.enemies = []; s.items = []; s.particles = []; s.popups = []; s.bumps = [];
  for (const e of lv.ents) {
    if (e.kind === "bug" || e.kind === "spiky" || e.kind === "moth") {
      const m = e.kind === "moth";
      s.enemies.push({
        kind: e.kind, x: e.tx * T + 1, y: e.ty * T + (m ? 3 : 4), w: m ? 12 : 14, h: m ? 9 : 12,
        vx: 0, vy: 0, dir: -1, active: false, alive: true, dead: 0, t: 0, baseY: e.ty * T + 3, flip: false,
      });
    }
  }
  s.lifts = lv.lifts.map(l => ({ x: l.tx * T, y: l.ty * T, x0: l.tx * T, len: l.len, range: l.range * T, speed: l.speed, dir: 1, dx: 0 }));
  const cp = lv.ents.find(e => e.kind === "checkpoint");
  s.goal = lv.ents.find(e => e.kind === "goal");
  s.cp = cp ? { x: cp.tx * T, y: cp.ty * T, on: !!fromCheckpoint } : null;
  const sx = fromCheckpoint && cp ? cp.tx * T + 4 : lv.start.x * T + 3;
  const sy = (fromCheckpoint && cp ? cp.ty : lv.start.y) * T + 2;
  s.player = {
    x: sx, y: sy, w: 10, h: 14, vx: 0, vy: 0, facing: 1, onGround: false, coyote: 0, buffer: 0,
    jumping: false, invuln: 0, duck: 0, dead: false, anim: 0, animT: 0, hidden: false, skid: false, lift: -1,
  };
  s.cam = Math.max(0, Math.min(s.player.x - W * 0.4, lv.w * T - W));
  s.combo = 0;
}

// ---------------------------------------------------------------- tile helpers
export function tileAt(lv, tx, ty) {
  if (ty < 0 || ty >= ROWS) return TILE.EMPTY;
  if (tx < 0 || tx >= lv.w) return TILE.GROUND;
  return lv.tiles[ty * lv.w + tx];
}
const setTile = (lv, tx, ty, v) => { lv.tiles[ty * lv.w + tx] = v; };
const isSolid = (lv, tx, ty) => SOLID[tileAt(lv, tx, ty)];

function moveX(s, e, dx) {
  const lv = s.level;
  e.x += dx;
  const y0 = Math.floor(e.y / T), y1 = Math.floor((e.y + e.h - 0.01) / T);
  if (dx > 0) {
    const tx = Math.floor((e.x + e.w - 0.01) / T);
    for (let ty = y0; ty <= y1; ty++) if (isSolid(lv, tx, ty)) { e.x = tx * T - e.w; return true; }
  } else if (dx < 0) {
    const tx = Math.floor(e.x / T);
    for (let ty = y0; ty <= y1; ty++) if (isSolid(lv, tx, ty)) { e.x = (tx + 1) * T; return true; }
  }
  return false;
}

// returns {floor, ceil:[tx,ty]} after moving vertically
function moveY(s, e, dy, oneWay = true) {
  const lv = s.level, prevBottom = e.y + e.h;
  e.y += dy;
  const x0 = Math.floor(e.x / T), x1 = Math.floor((e.x + e.w - 0.01) / T);
  if (dy > 0) {
    const ty = Math.floor((e.y + e.h - 0.01) / T);
    for (let tx = x0; tx <= x1; tx++) {
      const t = tileAt(lv, tx, ty);
      if (SOLID[t] || (oneWay && t === TILE.PLAT && prevBottom <= ty * T + 0.01)) {
        e.y = ty * T - e.h;
        return { floor: true, tile: t, tx, ty };
      }
    }
  } else if (dy < 0) {
    const ty = Math.floor(e.y / T);
    let hit = null;
    for (let tx = x0; tx <= x1; tx++) if (isSolid(lv, tx, ty)) { hit = hit || []; hit.push(tx); }
    if (hit) {
      e.y = (ty + 1) * T;
      const cx = Math.floor((e.x + e.w / 2) / T);
      return { ceil: [hit.includes(cx) ? cx : hit[0], ty] };
    }
  }
  return {};
}

const overlap = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;

function popup(s, x, y, text) { s.popups.push({ x, y, text, t: 0 }); }

function addScore(s, n, x, y) {
  s.score += n;
  if (x !== undefined) popup(s, x, y, String(n));
}

function addBit(s, x, y) {
  s.bits += 1;
  s.score += 10;
  emit(s, "coin");
  if (s.bits >= 100) { s.bits -= 100; s.lives += 1; emit(s, "oneup"); popup(s, x, y - 8, "1UP"); }
}

function sparkle(s, x, y, n = 6, color = "spark") {
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2 + rand(s) * 0.5, v = 0.8 + rand(s) * 1.2;
    s.particles.push({ kind: color, x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 0.4, t: 0, life: 22 + Math.floor(rand(s) * 10) });
  }
}

// ---------------------------------------------------------------- blocks
function hitBlock(s, tx, ty) {
  const lv = s.level, t = tileAt(lv, tx, ty), p = s.player;
  const bump = () => {
    s.bumps.push({ tx, ty, t: 0 });
    // knock out anything standing on the block
    for (const e of s.enemies) {
      if (!e.alive || e.kind === "moth") continue;
      if (Math.abs(e.y + e.h - ty * T) < 3 && e.x + e.w > tx * T - 2 && e.x < tx * T + T + 2) knockOut(s, e, 100);
    }
    for (const it of s.items) if (Math.abs(it.y + 16 - ty * T) < 3 && Math.abs(it.x - tx * T) < 12) { it.vy = -3; it.dir = -(it.dir || 1); }
    // a bit sitting on top of the block gets knocked into your pocket
    if (tileAt(lv, tx, ty - 1) === TILE.BIT) {
      setTile(lv, tx, ty - 1, TILE.EMPTY);
      s.items.push({ kind: "pop", x: tx * T, y: (ty - 1) * T - 8, vx: 0, vy: -4.2, t: 0 });
      addBit(s, tx * T, ty * T - T);
    }
  };
  if (t === TILE.BRICK) {
    if (s.caffeine) {
      setTile(lv, tx, ty, TILE.EMPTY);
      for (let i = 0; i < 4; i++) {
        s.particles.push({ kind: "brick", x: tx * T + 4 + (i % 2) * 8, y: ty * T + 4 + (i >> 1) * 8, vx: (i % 2 ? 1 : -1) * (1 + (i >> 1) * 0.4), vy: -4 + (i >> 1) * 1.5, t: 0, life: 60 });
      }
      addScore(s, 50);
      emit(s, "break");
      bump();
    } else { bump(); emit(s, "bump"); }
  } else if (t === TILE.QBIT || t === TILE.QMULTI) {
    if (t === TILE.QMULTI) {
      lv.multi = lv.multi || {};
      const k = tx + "," + ty;
      lv.multi[k] = (lv.multi[k] || 0) + 1;
      if (lv.multi[k] >= 6) setTile(lv, tx, ty, TILE.USED);
    } else setTile(lv, tx, ty, TILE.USED);
    s.items.push({ kind: "pop", x: tx * T, y: ty * T - 14, vx: 0, vy: -4.2, t: 0 });
    addBit(s, tx * T, ty * T);
    bump();
  } else if (t === TILE.QCOFFEE || t === TILE.QDUCK) {
    setTile(lv, tx, ty, TILE.USED);
    s.items.push({ kind: t === TILE.QDUCK ? "duck" : "coffee", x: tx * T, y: ty * T, vx: 0, vy: 0, t: 0, rise: 16, dir: 1 });
    emit(s, "sprout");
    bump();
  } else {
    emit(s, "thud");
  }
}

function knockOut(s, e, pts) {
  if (!e.alive) return;
  e.alive = false; e.flip = true; e.vy = -3.5; e.vx = e.x < s.player.x ? -1 : 1; e.dead = 0;
  addScore(s, pts, e.x, e.y);
  emit(s, "kick");
}

// ---------------------------------------------------------------- player
function hurt(s) {
  const p = s.player;
  if (p.invuln > 0 || p.duck > 0 || p.dead) return;
  if (s.caffeine) {
    s.caffeine = false; p.invuln = 120; emit(s, "shrink");
  } else die(s);
}

function die(s) {
  const p = s.player;
  if (p.dead) return;
  p.dead = true; p.vx = 0; p.vy = -5.5; p.duck = 0;
  s.caffeine = false;
  setMode(s, "dying");
  emit(s, "die");
}

function updatePlayer(s, inp, pressed) {
  const p = s.player, lv = s.level;
  const dir = (inp & 2 ? 1 : 0) - (inp & 1 ? 1 : 0);
  const running = !!(inp & 8);
  const max = running ? (s.caffeine ? PHYS.runCaffeine : PHYS.run) : PHYS.walk;
  p.skid = false;
  if (dir !== 0) {
    if (p.onGround && p.vx * dir < -0.3) { p.vx += dir * PHYS.skid; p.skid = true; }
    else {
      const nv = p.vx + dir * (p.onGround ? (running ? PHYS.accRun : PHYS.accWalk) : PHYS.accAir);
      if (Math.abs(nv) <= max) p.vx = nv;
      else if (Math.abs(p.vx) <= max) p.vx = Math.sign(nv) * max;
      else p.vx = Math.sign(p.vx) * Math.max(max, Math.abs(p.vx) - 0.05);
    }
    if (p.onGround || Math.abs(p.vx) < 0.2) p.facing = dir;
  } else if (p.onGround) {
    p.vx -= Math.sign(p.vx) * Math.min(Math.abs(p.vx), PHYS.friction);
  }
  // jumping: coyote time + input buffering, higher when running, variable height while held
  p.coyote = p.onGround ? PHYS.coyote : Math.max(0, p.coyote - 1);
  p.buffer = pressed & 4 ? PHYS.buffer : Math.max(0, p.buffer - 1);
  if (p.buffer > 0 && p.coyote > 0) {
    p.vy = -(PHYS.jump + PHYS.jumpBoost * Math.min(1, Math.abs(p.vx) / PHYS.run));
    p.jumping = true; p.coyote = 0; p.buffer = 0; p.onGround = false; p.lift = -1;
    emit(s, "jump");
  }
  const holding = !!(inp & 4);
  p.hold = holding;
  const g = p.vy < 0 && holding && p.jumping ? PHYS.gravityHold : PHYS.gravity;
  p.vy = Math.min(p.vy + g, PHYS.maxFall);
  if (p.vy >= 0) p.jumping = false;

  // ride a lift
  if (p.lift >= 0 && s.lifts[p.lift]) moveX(s, p, s.lifts[p.lift].dx);
  moveX(s, p, p.vx) && (p.vx = 0);
  if (p.x < s.cam) { p.x = s.cam; if (p.vx < 0) p.vx = 0; }
  const prevBottom = p.y + p.h;
  const r = moveY(s, p, p.vy);
  p.onGround = false; p.lift = -1;
  if (r.floor) {
    p.vy = 0; p.onGround = true; s.combo = 0;
    if (r.tile === TILE.SPIKE) hurt(s);
  }
  if (r.ceil) { p.vy = Math.max(p.vy, 0.5); hitBlock(s, r.ceil[0], r.ceil[1]); }
  // lifts are one-way platforms
  if (!p.onGround && p.vy >= 0) {
    s.lifts.forEach((l, i) => {
      const top = l.y;
      if (prevBottom <= top + 0.5 && p.y + p.h >= top && p.x + p.w > l.x + 1 && p.x < l.x + l.len * T - 1) {
        p.y = top - p.h; p.vy = 0; p.onGround = true; p.lift = i; s.combo = 0;
      }
    });
  }
  // side-touching spikes also hurts
  const cx = Math.floor((p.x + p.w / 2) / T), by = Math.floor((p.y + p.h + 1) / T);
  if (tileAt(lv, cx, by) === TILE.SPIKE && p.onGround) hurt(s);
  // collect bits (tiles)
  for (let ty = Math.floor(p.y / T); ty <= Math.floor((p.y + p.h - 1) / T); ty++) {
    for (let tx = Math.floor(p.x / T); tx <= Math.floor((p.x + p.w - 1) / T); tx++) {
      if (tileAt(lv, tx, ty) === TILE.BIT) {
        setTile(lv, tx, ty, TILE.EMPTY);
        addBit(s, tx * T, ty * T);
        sparkle(s, tx * T + 8, ty * T + 8, 5);
      }
    }
  }
  // animation
  if (!p.onGround) p.anim = 4;
  else if (Math.abs(p.vx) < 0.1) { p.anim = 0; p.animT = 0; }
  else {
    p.animT += Math.abs(p.vx) * 0.12 + 0.05;
    p.anim = 1 + (Math.floor(p.animT) % 3);
  }
  if (p.invuln > 0) p.invuln--;
  if (p.duck > 0) { p.duck--; if (p.duck === 0) emit(s, "duck-end"); }
  if (p.y > H + 24) die(s);
}

// ---------------------------------------------------------------- enemies, items, lifts
function updateEnemies(s) {
  const p = s.player, lv = s.level;
  for (const e of s.enemies) {
    if (!e.alive) {
      if (e.flip) { e.vy += 0.3; e.x += e.vx; e.y += e.vy; }
      e.dead++;
      continue;
    }
    if (!e.active) {
      if (e.x < s.cam + W + 24) e.active = true;
      else continue;
    }
    e.t++;
    if (e.kind === "moth") {
      e.x += e.dir * 0.55;
      e.y = e.baseY + Math.sin(e.t * 0.06) * 14;
      const tx = Math.floor((e.x + (e.dir > 0 ? e.w : 0)) / T);
      if (isSolid(lv, tx, Math.floor((e.y + e.h / 2) / T))) e.dir *= -1;
      if (Math.abs(e.x - (e.home ?? (e.home = e.x))) > 5 * T) e.dir = e.x > e.home ? -1 : 1;
    } else {
      e.vx = e.dir * (e.kind === "spiky" ? 0.4 : 0.45);
      e.vy = Math.min(e.vy + PHYS.gravity, PHYS.maxFall);
      if (moveX(s, e, e.vx)) e.dir *= -1;
      const r = moveY(s, e, e.vy);
      if (r.floor) e.vy = 0;
      for (const o of s.enemies) {
        if (o !== e && o.alive && o.active && o.kind !== "moth" && overlap(e, o)) {
          e.dir = e.x < o.x ? -1 : 1; o.dir = -e.dir;
        }
      }
      if (e.y > H + 32) { e.alive = false; e.dead = 999; }
    }
    if (e.x + e.w < s.cam - 64) { e.alive = false; e.dead = 999; }
    // player interaction
    if (p.dead || !overlap(p, e)) continue;
    if (p.duck > 0) { knockOut(s, e, 200); continue; }
    const fromAbove = p.vy > 0 && p.y + p.h - p.vy <= e.y + 6;
    if (fromAbove && e.kind !== "spiky") {
      e.alive = false; e.flip = e.kind === "moth"; e.dead = 0;
      if (e.flip) { e.vy = 0; e.vx = 0; }
      s.combo += 1;
      const pts = Math.min(100 * Math.pow(2, s.combo - 1), 1600);
      addScore(s, pts, e.x, e.y);
      p.vy = -(p.hold ? PHYS.stompBounceHeld : PHYS.stompBounce);
      p.jumping = p.hold;
      emit(s, "stomp", { combo: s.combo });
      sparkle(s, e.x + e.w / 2, e.y + e.h, 4, "dust");
    } else hurt(s);
  }
  s.enemies = s.enemies.filter(e => e.alive || e.dead < 120);
}

function updateItems(s) {
  const p = s.player;
  for (const it of s.items) {
    it.t++;
    if (it.kind === "pop") {
      it.vy += 0.3; it.y += it.vy;
      if (it.t > 26) { it.done = true; sparkle(s, it.x + 8, it.y + 8, 5); popup(s, it.x, it.y, "10"); }
      continue;
    }
    if (it.rise > 0) { it.y -= 1; it.rise--; continue; }
    const box = { x: it.x + 2, y: it.y + 2, w: 12, h: 14 };
    if (it.kind === "coffee") {
      it.vx = it.dir * 0.9;
    } else if (it.kind === "duck") {
      it.vx = it.dir * 1.0;
    }
    it.vy = Math.min((it.vy || 0) + 0.3, PHYS.maxFall);
    if (moveX(s, box, it.vx)) it.dir *= -1;
    const r = moveY(s, box, it.vy);
    if (r.floor) it.vy = it.kind === "duck" ? -3.6 : 0;
    it.x = box.x - 2; it.y = box.y - 2;
    if (it.y > H + 32) it.done = true;
    if (!p.dead && overlap(p, box)) {
      it.done = true;
      if (it.kind === "coffee") { s.caffeine = true; emit(s, "powerup"); }
      else { p.duck = 600; emit(s, "duck"); }
      addScore(s, 1000, it.x, it.y);
    }
  }
  s.items = s.items.filter(i => !i.done);
}

function updateLifts(s) {
  for (const l of s.lifts) {
    const nx = l.x + l.dir * l.speed;
    l.dx = nx - l.x;
    l.x = nx;
    if (l.x > l.x0 + l.range) { l.x = l.x0 + l.range; l.dir = -1; }
    if (l.x < l.x0) { l.x = l.x0; l.dir = 1; }
  }
}

function updateFx(s) {
  for (const q of s.particles) {
    q.t++; q.x += q.vx; q.y += q.vy;
    q.vy += q.kind === "brick" ? 0.3 : q.kind === "firework" ? 0.04 : 0.05;
  }
  s.particles = s.particles.filter(q => q.t < q.life);
  for (const q of s.popups) { q.t++; q.y -= 0.6; }
  s.popups = s.popups.filter(q => q.t < 40);
  for (const b of s.bumps) b.t++;
  s.bumps = s.bumps.filter(b => b.t < 10);
}

function camera(s) {
  const p = s.player, lv = s.level;
  const target = Math.max(0, Math.min(p.x + p.w / 2 - W * 0.42, lv.w * T - W));
  // only scroll forward, like the classics; never backward past the player
  if (target > s.cam) s.cam += Math.min(target - s.cam, 4);
}

// ---------------------------------------------------------------- the main step
export function step(s, inp = 0) {
  s.events = [];
  const pressed = inp & ~s.prev;
  s.prev = inp;
  s.frame++;
  s.modeT++;
  switch (s.mode) {
    case "title":
      if (pressed & 16) { s.score = 0; s.bits = 0; s.lives = 3; s.levelIndex = 0; s.caffeine = false; begin(s, false); emit(s, "start"); }
      break;
    case "intro":
      if (s.modeT >= (s.demo ? 2 : 150)) { setMode(s, "play"); emit(s, "music"); }
      break;
    case "play":
      if (pressed & 16 && !s.demo) { setMode(s, "pause"); emit(s, "pause"); break; }
      updateLifts(s);
      updatePlayer(s, inp, pressed);
      if (s.mode !== "play") break;
      updateEnemies(s);
      updateItems(s);
      camera(s);
      // checkpoint and goal
      if (s.cp && !s.cp.on && s.player.x > s.cp.x) {
        s.cp.on = true; s.checkpoint = s.levelIndex; emit(s, "save"); popup(s, s.cp.x, s.cp.y - 10, "SAVED");
      }
      if (s.goal && s.player.x + s.player.w >= s.goal.tx * T + 2 && !s.player.dead) {
        setMode(s, "goal"); s.player.vx = 0; s.player.duck = 0; emit(s, "goal");
      }
      if (s.mode === "play" && !s.demo) {
        s.time--;
        if (s.time === 100 * FPS) emit(s, "hurry");
        if (s.time <= 0) { s.time = 0; die(s); }
      }
      break;
    case "pause":
      if (pressed & 16) { setMode(s, "play"); emit(s, "resume"); }
      return s.events;
    case "dying": {
      const p = s.player;
      if (s.modeT > 30) { p.vy = Math.min(p.vy + 0.25, 6); p.y += p.vy; }
      if (s.modeT === 150) {
        s.lives -= 1;
        if (s.demo) { s.demoOver = true; }
        else if (s.lives <= 0) { setMode(s, "gameover"); emit(s, "gameover"); if (s.score > s.hi) s.hi = s.score; }
        else begin(s, s.checkpoint === s.levelIndex);
      }
      break;
    }
    case "goal": goalStep(s); break;
    case "gameover":
      if (s.modeT > 90 && pressed & 16) { setMode(s, "title"); }
      break;
    case "win":
      winStep(s);
      if (s.modeT > 240 && pressed & 16) { setMode(s, "title"); }
      break;
  }
  updateFx(s);
  return s.events;
}

// jump straight to a level (used by tests and the level-select shortcut)
export function gotoLevel(s, i) {
  s.levelIndex = Math.max(0, Math.min(LEVELS.length - 1, i));
  s.checkpoint = null;
  begin(s, false);
}

function begin(s, fromCheckpoint) {
  if (!fromCheckpoint) s.checkpoint = null;
  startLevel(s, s.demo ? DEMO_LEVEL : LEVELS[s.levelIndex], fromCheckpoint);
  setMode(s, "intro");
}

// walk into the server, count the time bonus, then move on
function goalStep(s) {
  const p = s.player, g = s.goal, door = g.tx * T + 14;
  if (!p.hidden) {
    p.vy = Math.min(p.vy + PHYS.gravity, PHYS.maxFall);
    const r = moveY(s, p, p.vy);
    p.onGround = !!r.floor;
    if (r.floor) p.vy = 0;
    if (p.onGround) {
      if (p.x < door) { p.x = Math.min(door, p.x + 1.1); p.facing = 1; p.animT += 0.2; p.anim = 1 + (Math.floor(p.animT) % 3); }
      else { p.hidden = true; s.flags.doorT = s.modeT; emit(s, "door"); }
    } else p.anim = 4;
    camera(s);
    return;
  }
  const since = s.modeT - s.flags.doorT;
  if (since === 40) emit(s, "clear");
  if (since > 90 && s.time > 0) {
    const n = Math.min(s.time, FPS);
    s.time -= n; s.score += Math.ceil(n / FPS) * 10;
    if (s.frame % 3 === 0) emit(s, "tick");
    s.flags.tallyEnd = s.modeT;
  }
  if (since > 90 && s.time <= 0 && s.modeT - (s.flags.tallyEnd || 0) > 80) {
    if (s.demo) { s.demoOver = true; return; }
    if (s.score > s.hi) s.hi = s.score;
    s.flags = {};
    if (s.levelIndex < LEVELS.length - 1) { s.levelIndex++; s.checkpoint = null; begin(s, false); }
    else { setMode(s, "win"); emit(s, "win"); }
  }
}

function winStep(s) {
  if (s.modeT % 24 === 1) {
    const x = 40 + rand(s) * (W - 80), y = 30 + rand(s) * 60;
    const colors = ["red", "yellow", "green", "blue", "pink", "orange"];
    const c = colors[Math.floor(rand(s) * colors.length)];
    for (let i = 0; i < 18; i++) {
      const a = (i / 18) * Math.PI * 2, v = 1.2 + rand(s) * 0.6;
      s.particles.push({ kind: "firework", color: c, x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, t: 0, life: 50 });
    }
    emit(s, "firework");
  }
}

// ---------------------------------------------------------------- inputs
export const KEY = { LEFT: 1, RIGHT: 2, JUMP: 4, RUN: 8, START: 16 };

// run-length encoded input tapes: [[frames, mask], ...]
export function tape(runs) {
  const out = [];
  for (const [n, m] of runs) for (let i = 0; i < n; i++) out.push(m);
  return out;
}
