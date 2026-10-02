// Records the PUSH TO PROD demo straight from the game engine and writes it as an animated SVG for the README
// (a README can't run JavaScript). Usage: node scripts/arcade_demo.mjs
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { newGame, step, TILE, T, W, H, ROWS, tileAt } from "../docs/game/engine.js";
import { SPRITES, TILES, THEMES, FONT, PAL, HERO_SKINS } from "../docs/game/art.js";
import { DEMO_TAPE } from "../docs/game/demo-tape.js";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const OUT = path.join(ROOT, "art", "arcade", "demo.svg");
const HOLD = 1.8, END = 1.4, PAD = 8;
const th = THEMES.day;

// ---------------------------------------------------------------- record the run
const s = newGame({ demo: true });
while (s.mode !== "play") step(s, 0);
let uid = 0;
const tag = o => (o._id === undefined ? (o._id = ++uid) : o._id);
const frames = [], tileEvents = [], bumpEvents = [];
let prevTiles = s.level.tiles.slice();
function snap() {
  const p = s.player;
  frames.push({
    cam: s.cam, score: s.score, bits: s.bits, mode: s.mode, modeT: s.modeT, frame: s.frame,
    doorT: s.flags.doorT, hidden: p.hidden, timeBonus: Math.ceil(s.time / 60) * 10,
    hero: { x: p.x, y: p.y, anim: p.anim, facing: p.facing, skin: s.caffeine ? "caffeine" : "normal", blink: p.invuln > 0 && Math.floor(s.frame / 3) % 2 === 1 },
    enemies: s.enemies.map(e => ({ id: tag(e), kind: e.kind, x: e.x, y: e.y, dir: e.dir, alive: e.alive, flip: e.flip, dead: e.dead, active: e.active })),
    items: s.items.map(it => ({ id: tag(it), kind: it.kind, x: it.x, y: it.y, t: it.t, rise: it.rise, dir: it.dir })),
    particles: s.particles.map(q => ({ id: tag(q), kind: q.kind, x: q.x, y: q.y })),
    popups: s.popups.map(q => ({ id: tag(q), text: q.text, x: q.x, y: q.y })),
  });
}
snap();
let f = 0;
const tapeLen = DEMO_TAPE.length;
while (!s.demoOver && f < 4000) {
  step(s, f < tapeLen ? DEMO_TAPE[f] : 0);
  f++;
  const tl = s.level.tiles;
  for (let k = 0; k < tl.length; k++) if (tl[k] !== prevTiles[k]) tileEvents.push({ f, tx: k % s.level.w, ty: Math.floor(k / s.level.w), from: prevTiles[k], to: tl[k] });
  prevTiles = tl.slice();
  for (const b of s.bumps) if (b.t === 1) bumpEvents.push({ f, tx: b.tx, ty: b.ty });
  snap();
}
const F = frames.length - 1;
const DUR = HOLD + F / 60 + END;
const kt = fr => ((HOLD + fr / 60) / DUR);
const fmt = v => (Math.round(v * 100) / 100).toString();
const k4 = v => (Math.round(v * 10000) / 10000).toString();
console.log("recorded", F, "frames,", (F / 60).toFixed(1), "s; loop", DUR.toFixed(1), "s; tile events", tileEvents.length);

// ---------------------------------------------------------------- svg helpers
function runs(rows, ch) {
  const out = [];
  rows.forEach((r, y) => {
    let x = 0;
    while (x < r.length) {
      if (r[x] === ch) { const s0 = x; while (x < r.length && r[x] === ch) x++; out.push(`M${s0} ${y}h${x - s0}v1h-${x - s0}z`); }
      else x++;
    }
  });
  return out.join("");
}
function sprite(rows, key) {
  return Object.entries(key).map(([ch, col]) => { const d = runs(rows, ch); return d && col ? `<path fill="${col}" d="${d}"/>` : ""; }).join("");
}
const flipX = (w = 16) => ` transform="translate(${w} 0) scale(-1 1)"`;
const flipY = (h = 16) => ` transform="translate(0 ${h}) scale(1 -1)"`;
// a linear track with redundant samples dropped (keeps the file small)
function track(samples, tol = 0.2) {
  // samples: [{t (0..1), v: [..numbers]}]
  const keep = [samples[0]];
  let a = 0;
  for (let b = 2; b < samples.length; b++) {
    const A = samples[a], B = samples[b];
    let ok = true;
    for (let m = a + 1; m < b && ok; m++) {
      const M = samples[m], u = (M.t - A.t) / ((B.t - A.t) || 1);
      for (let d = 0; d < M.v.length; d++) if (Math.abs(A.v[d] + (B.v[d] - A.v[d]) * u - M.v[d]) > tol) { ok = false; break; }
    }
    if (!ok) { keep.push(samples[b - 1]); a = b - 1; }
  }
  keep.push(samples[samples.length - 1]);
  return keep;
}
function moveAnim(samples) {
  const k = track(samples);
  return `<animateTransform attributeName="transform" type="translate" values="${k.map(x => x.v.map(fmt).join(" ")).join(";")}" keyTimes="${k.map(x => k4(x.t)).join(";")}" dur="${fmt(DUR)}s" repeatCount="indefinite"/>`;
}
// discrete on/off visibility from a per-frame boolean series
function showAnim(on) {
  const vals = [], times = [];
  const at0 = on[0] ? 1 : 0;
  vals.push(at0); times.push(0);
  let cur = at0;
  for (let fr = 1; fr <= F; fr++) {
    const v = on[fr] ? 1 : 0;
    if (v !== cur) { vals.push(v); times.push(kt(fr)); cur = v; }
  }
  if (vals.length === 1) return { initial: at0, anim: "" };
  return { initial: at0, anim: `<animate attributeName="opacity" calcMode="discrete" values="${vals.join(";")}" keyTimes="${times.map(k4).join(";")}" dur="${fmt(DUR)}s" repeatCount="indefinite"/>` };
}
function series(fn) {
  const out = [];
  out.push({ t: 0, v: fn(frames[0]) });
  for (let fr = 0; fr <= F; fr++) out.push({ t: kt(fr), v: fn(frames[fr]) });
  out.push({ t: 1, v: fn(frames[F]) });
  return out;
}

// font
const glyphIds = new Set();
function text(str, x, y, fill, scale = 1, align = "left") {
  str = String(str);
  const wpx = (str.length * 6 - 1) * scale;
  if (align === "center") x = Math.round(x - wpx / 2); else if (align === "right") x -= wpx;
  const uses = [...str].map((c, i) => { if (c === " " || !FONT[c]) return ""; glyphIds.add(c); return `<use href="#f${c.charCodeAt(0)}" x="${i * 6}"/>`; }).join("");
  return `<g fill="${fill}" transform="translate(${x} ${y})${scale !== 1 ? ` scale(${scale})` : ""}">${uses}</g>`;
}
function shadowText(str, x, y, fill, scale = 1, align = "left") {
  return text(str, x + scale, y + scale, "#1b1325", scale, align) + text(str, x, y, fill, scale, align);
}

// ---------------------------------------------------------------- defs: sprites, tiles
const defs = [];
const heroUsed = new Set(frames.map(fr => `${fr.hero.anim}-${fr.hero.facing < 0 ? "L" : "R"}-${fr.hero.skin}`));
for (const key of heroUsed) {
  const [anim, dir, skin] = key.split("-");
  const k = Object.assign({}, SPRITES.hero.key, HERO_SKINS[skin]);
  defs.push(`<g id="h${anim}${dir}${skin[0]}"${dir === "L" ? flipX() : ""}>${sprite(SPRITES.hero.frames[+anim], k)}</g>`);
}
defs.push(`<g id="bugA">${sprite(SPRITES.bug.frames[0], SPRITES.bug.key)}</g><g id="bugB">${sprite(SPRITES.bug.frames[1], SPRITES.bug.key)}</g><g id="bugS">${sprite(SPRITES.bug.frames[2], SPRITES.bug.key)}</g>`);
SPRITES.bit.frames.forEach((fr, i) => defs.push(`<g id="bit${i}">${sprite(fr, SPRITES.bit.key)}</g>`));
SPRITES.coffee.frames.forEach((fr, i) => defs.push(`<g id="cof${i}">${sprite(fr, SPRITES.coffee.key)}</g>`));
defs.push(`<g id="heart">${sprite(SPRITES.heart.frames[0], SPRITES.heart.key)}</g><g id="minibit">${sprite(SPRITES.minibit.frames[0], SPRITES.minibit.key)}</g>`);
for (const name of ["groundTop", "ground", "brick", "used", "key", "rack", "platform"]) defs.push(`<g id="t_${name}">${sprite(TILES[name], th.tile)}</g>`);
defs.push(`<g id="t_rack2">${sprite(TILES.rack, Object.assign({}, th.tile, { g: th.tile.v, v: th.tile.g, r: PAL.yellow }))}</g>`);
[th.tile.y, PAL.lemon, PAL.orange].forEach((y, i) => defs.push(`<g id="t_block${i}">${sprite(TILES.block, Object.assign({}, th.tile, { y }))}</g>`));

// ---------------------------------------------------------------- background (same recipe as the game)
function seeded(seed) { let v = seed; return () => (v = (v * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff; }
function disc(cx, cy, r) {
  let d = "";
  for (let dy = -r; dy <= r; dy++) { const half = Math.round(Math.sqrt(r * r - dy * dy)); d += `M${cx - half} ${cy + dy}h${half * 2 + 1}v1h-${half * 2 + 1}z`; }
  return d;
}
function sky() {
  const band = H / th.sky.length;
  let out = th.sky.map((c, i) => `<rect y="${Math.round(i * band)}" width="${W}" height="${Math.ceil(band) + 1}" fill="${c}"/>`).join("");
  for (let i = 1; i < th.sky.length; i++) {
    const y0 = Math.round(i * band);
    out += `<rect y="${y0}" width="${W}" height="2" fill="url(#dith${i})"/>`;
    defs.push(`<pattern id="dith${i}" width="2" height="2" patternUnits="userSpaceOnUse"><rect width="1" height="1" fill="${th.sky[i - 1]}"/><rect x="1" y="1" width="1" height="1" fill="${th.sky[i - 1]}"/></pattern>`);
  }
  return out;
}
function cloudsLayer() {
  const r = seeded(7);
  let shade = "", body = "", bar = "";
  for (let i = 0; i < 6; i++) {
    const cx = 40 + i * 104 + Math.floor(r() * 30), cy = 18 + Math.floor(r() * 30), sz = 8 + Math.floor(r() * 5);
    const parts = [[0, 0, sz], [sz, 2, sz - 2], [-sz, 3, sz - 3], [sz * 2 - 3, 5, sz - 4]];
    parts.forEach(([dx, dy, rr]) => (shade += disc(cx + dx, cy + dy + 1, rr)));
    parts.forEach(([dx, dy, rr]) => (body += disc(cx + dx, cy + dy, rr)));
    bar += `M${cx - sz - 2} ${cy + 4}h${sz * 3 + 4}v4h-${sz * 3 + 4}z`;
  }
  return `<path fill="${th.cloudSh}" d="${shade}"/><path fill="${th.cloud}" d="${body}${bar}"/>`;
}
function hillsLayer() {
  let edge = "", body = "", dots = "";
  [[60, 40], [190, 26], [300, 46], [430, 30]].forEach(([cx, rr]) => {
    edge += disc(cx, 60, rr + 1); body += disc(cx, 60, rr);
    for (let k = 0; k < 4; k++) dots += `M${cx - 6 + k * 4} ${60 - rr + 6 + (k % 2) * 3}h2v2h-2z`;
  });
  return `<path fill="#008751" d="${edge}"/><path fill="${th.far}" d="${body}"/><path fill="#a8e7c8" d="${dots}"/>`;
}
function bushesLayer() {
  let sh = "", body = "";
  [[30, 1], [150, 2], [260, 0], [330, 1]].forEach(([cx, n]) => { for (let i = 0; i <= n; i++) { sh += disc(cx + i * 12, 22, 9); body += disc(cx + i * 12, 23, 8); } });
  return `<path fill="${th.nearSh}" d="${sh}"/><path fill="${th.near}" d="${body}"/>`;
}
function parallax(id, content, width, k, y, copies) {
  defs.push(`<g id="${id}">${content}</g>`);
  const uses = Array.from({ length: copies }, (_, i) => `<use href="#${id}" x="${i * width}" y="${y}"/>`).join("");
  return `<g>${moveAnim(series(fr => [-fr.cam * k, 0]))}${uses}</g>`;
}

// ---------------------------------------------------------------- world
const lv = s.level, lv0 = newGame({ demo: true }).level;
const world = [];
const isDyn = new Set(tileEvents.map(e => e.tx + "," + e.ty));
const bumpsAt = {};
for (const b of bumpEvents) (bumpsAt[b.tx + "," + b.ty] = bumpsAt[b.tx + "," + b.ty] || []).push(b.f);
const SHIMMER = `dur="0.5s" repeatCount="indefinite"`;
function blockShimmer(x, y) {
  return [0, 1, 2].map(i => `<use href="#t_block${i}" x="${x}" y="${y}" opacity="${i === 0 ? 1 : 0}"><animate attributeName="opacity" calcMode="discrete" values="${[0, 1, 2].map(j => (j === i ? 1 : 0)).join(";")}" keyTimes="0;.3333;.6667" ${SHIMMER}/></use>`).join("");
}
function tileUse(t, tx, ty) {
  const x = tx * T, y = ty * T;
  switch (t) {
    case TILE.GROUND: return `<use href="#t_${tileAt(lv0, tx, ty - 1) === TILE.GROUND ? "ground" : "groundTop"}" x="${x}" y="${y}"/>`;
    case TILE.BRICK: return `<use href="#t_brick" x="${x}" y="${y}"/>`;
    case TILE.QBIT: case TILE.QCOFFEE: case TILE.QDUCK: case TILE.QMULTI: return blockShimmer(x, y);
    case TILE.USED: return `<use href="#t_used" x="${x}" y="${y}"/>`;
    case TILE.KEY: {
      const top = tileAt(lv0, tx, ty - 1) !== TILE.KEY && lv0.letters[tx];
      return `<use href="#t_key" x="${x}" y="${y}"/>` + (top ? text(lv0.letters[tx], x + 6, y + 3, "#1b1325") : "");
    }
    case TILE.RACK: return `<use href="#t_rack" x="${x}" y="${y}"/><use href="#t_rack2" x="${x}" y="${y}" opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1" keyTimes="0;.5" dur="1s" begin="-${(tx % 2) * 0.5}s" repeatCount="indefinite"/></use>`;
    case TILE.PLAT: return `<use href="#t_platform" x="${x}" y="${y}"/>`;
    default: return "";
  }
}
// static tiles
for (let ty = 0; ty < ROWS; ty++) {
  for (let tx = 0; tx < lv0.w; tx++) {
    const t = lv0.tiles[ty * lv0.w + tx];
    if (!t || t === TILE.BIT || isDyn.has(tx + "," + ty)) continue;
    world.push(tileUse(t, tx, ty));
  }
}
// pits fade to dark
for (let tx = 0; tx < lv0.w; tx++) {
  if (lv0.tiles[9 * lv0.w + tx] || lv0.tiles[10 * lv0.w + tx]) continue;
  world.push(`<rect x="${tx * T}" y="150" width="16" height="${H - 150}" fill="#1d2b53"/><rect x="${tx * T}" y="138" width="16" height="12" fill="url(#pitd)"/>`);
}
defs.push(`<pattern id="pitd" width="4" height="2" patternUnits="userSpaceOnUse"><rect width="1" height="1" fill="#1d2b53"/><rect x="2" y="1" width="1" height="1" fill="#1d2b53"/></pattern>`);
// tiles that change during the run: blocks that get used, bits that get collected, bricks that break
const perFrameTile = (tx, ty) => frames.map((_, fr) => {
  let t = lv0.tiles[ty * lv0.w + tx];
  for (const e of tileEvents) if (e.tx === tx && e.ty === ty && e.f <= fr) t = e.to;
  return t;
});
const coinTiles = [];
for (let ty = 0; ty < ROWS; ty++) for (let tx = 0; tx < lv0.w; tx++) if (lv0.tiles[ty * lv0.w + tx] === TILE.BIT) coinTiles.push([tx, ty]);
for (const [tx, ty] of coinTiles) {
  const seq = perFrameTile(tx, ty), vis = showAnim(seq.map(t => t === TILE.BIT));
  const order = [0, 1, 2, 3, 2, 1], period = 42 / 60;
  const spin = [0, 1, 2, 3].map(i => {
    const on = order.map(o => (o === i ? 1 : 0));
    return `<use href="#bit${i}" x="${tx * T}" y="${ty * T}" opacity="${on[0]}"><animate attributeName="opacity" calcMode="discrete" values="${on.join(";")}" keyTimes="${order.map((_, j) => k4(j / 6)).join(";")}" dur="${fmt(period)}s" begin="-${fmt(((tx * 7) % 42) / 60)}s" repeatCount="indefinite"/></use>`;
  }).join("");
  world.push(`<g opacity="${vis.initial}">${vis.anim}${spin}</g>`);
}
for (const key of isDyn) {
  const [tx, ty] = key.split(",").map(Number);
  const seq = perFrameTile(tx, ty);
  if (lv0.tiles[ty * lv0.w + tx] === TILE.BIT) continue;
  const kinds = [...new Set(seq)];
  const bumps = bumpsAt[key] || [];
  let bump = "";
  if (bumps.length) {
    const samples = series(fr => {
      let off = 0;
      for (const b0 of bumps) { const dt = fr.frame - frames[0].frame - b0; if (dt >= 0 && dt < 10) off = dt < 5 ? -dt : -(10 - dt); }
      return [0, off];
    });
    bump = moveAnim(samples);
  }
  const layers = kinds.filter(t => t).map(t => {
    const vis = showAnim(seq.map(v => v === t));
    return `<g opacity="${vis.initial}">${vis.anim}${tileUse(t, tx, ty)}</g>`;
  }).join("");
  world.push(`<g>${bump}${layers}</g>`);
}

// the server at the goal
const goal = lv0.ents.find(e => e.kind === "goal");
{
  const x = goal.tx * T, top = 32, bottom = 144;
  const doneOn = frames.map(fr => fr.mode === "goal" && fr.hidden);
  const openOn = frames.map(fr => fr.mode === "goal");
  const done = showAnim(doneOn), open = showAnim(openOn), shut = showAnim(openOn.map(v => !v)), idleOn = showAnim(doneOn.map(v => !v));
  let units = "";
  for (let i = 0; i < 4; i++) {
    const uy = top + 16 + i * 16;
    units += `<rect x="${x + 6}" y="${uy}" width="36" height="11" fill="#141220"/>`;
    for (let k = 0; k < 4; k++) {
      const col = [PAL.green, PAL.yellow, PAL.blue, PAL.red][k], per = (12 + k * 5) * 2 / 60;
      units += `<rect x="${x + 9 + k * 5}" y="${uy + 4}" width="3" height="3" fill="${col}"><animate attributeName="fill" calcMode="discrete" values="${col};#2a2730" keyTimes="0;.5" dur="${fmt(per)}s" begin="-${fmt(((i + k) % 2) * per / 2)}s" repeatCount="indefinite"/></rect>`;
    }
    units += `<rect x="${x + 31}" y="${uy + 3}" width="8" height="1" fill="#5f574f"/><rect x="${x + 31}" y="${uy + 6}" width="8" height="1" fill="#5f574f"/>`;
  }
  world.push(`<g><rect x="${x + 23}" y="${top - 14}" width="2" height="14" fill="#1b1325"/>
    <g opacity="${idleOn.initial}">${idleOn.anim}<rect x="${x + 21}" y="${top - 18}" width="6" height="5" fill="${PAL.red}"><animate attributeName="fill" calcMode="discrete" values="${PAL.red};${PAL.crimson}" keyTimes="0;.5" dur=".67s" repeatCount="indefinite"/></rect></g>
    <g opacity="${done.initial}">${done.anim}<rect x="${x + 17}" y="${top - 22}" width="14" height="13" fill="${PAL.green}" fill-opacity=".25"/><rect x="${x + 21}" y="${top - 18}" width="6" height="5" fill="${PAL.green}"/></g>
    <rect x="${x}" y="${top}" width="48" height="${bottom - top}" fill="#1b1325"/><rect x="${x + 2}" y="${top + 2}" width="44" height="${bottom - top - 2}" fill="#5f574f"/>
    <rect x="${x + 4}" y="${top + 4}" width="40" height="${bottom - top - 4}" fill="#3a3640"/>${units}
    <rect x="${x + 3}" y="${top + 4}" width="42" height="9" fill="#1b1325"/>
    <g opacity="${idleOn.initial}">${idleOn.anim}${text("SERVER", x + 24, top + 5, PAL.yellow, 1, "center")}</g>
    <g opacity="${done.initial}">${done.anim}${text("SERVER", x + 24, top + 5, PAL.green, 1, "center")}</g>
    <rect x="${x + 13}" y="${bottom - 26}" width="22" height="26" fill="#1b1325"/>
    <g opacity="${shut.initial}">${shut.anim}<rect x="${x + 15}" y="${bottom - 24}" width="18" height="24" fill="#83769c"/><rect x="${x + 29}" y="${bottom - 13}" width="2" height="2" fill="${PAL.yellow}"/></g>
    <g opacity="${open.initial}">${open.anim}<rect x="${x + 15}" y="${bottom - 24}" width="18" height="24" fill="#0c1022"/></g></g>`);
}

// items (the coffee and bits that pop out of blocks)
const itemIds = [...new Set(frames.flatMap(fr => fr.items.map(i => i.id)))];
const rising = [], items = [];
for (const id of itemIds) {
  const at = frames.map(fr => fr.items.find(i => i.id === id));
  const first = at.find(Boolean), vis = showAnim(at.map(Boolean));
  const pos = series(fr => { const it = fr.items.find(i => i.id === id) || first; return [it.x, it.y]; });
  let body;
  if (first.kind === "pop") body = [0, 1, 2, 3].map(i => `<use href="#bit${i}" opacity="${i ? 0 : 1}"><animate attributeName="opacity" calcMode="discrete" values="${[0, 1, 2, 3].map(j => (j === i ? 1 : 0)).join(";")}" keyTimes="0;.25;.5;.75" dur=".13s" repeatCount="indefinite"/></use>`).join("");
  else body = `<use href="#cof0"/><use href="#cof1" opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1" keyTimes="0;.5" dur=".4s" repeatCount="indefinite"/></use>`;
  const g = `<g opacity="${vis.initial}">${vis.anim}<g>${moveAnim(pos)}${body}</g></g>`;
  (first.rise > 0 ? rising : items).push(g);
}

// enemies
const enemyIds = [...new Set(frames.flatMap(fr => fr.enemies.map(e => e.id)))];
const enemies = [];
for (const id of enemyIds) {
  const at = frames.map(fr => fr.enemies.find(e => e.id === id));
  const first = at.find(Boolean);
  if (first.kind !== "bug") continue;
  const pos = series(fr => { const e = fr.enemies.find(q => q.id === id) || first; return [e.x - 1, e.y - 4]; });
  const st = at.map((e, fr) => {
    if (!e) return "none";
    if (!e.alive) return e.flip ? "flip" : (e.dead < 30 ? "squash" : "none");
    const walk = Math.floor(frames[fr].frame / 8) % 2 ? "A" : "B";
    return walk + (e.dir > 0 ? "R" : "L");
  });
  const variants = {
    AL: '<use href="#bugA"/>', BL: '<use href="#bugB"/>',
    AR: `<use href="#bugA"${flipX()}/>`, BR: `<use href="#bugB"${flipX()}/>`,
    squash: '<use href="#bugS"/>', flip: `<use href="#bugA"${flipY()}/>`,
  };
  const body = Object.entries(variants).filter(([k]) => st.includes(k)).map(([k, u]) => {
    const vis = showAnim(st.map(v => v === k));
    return `<g opacity="${vis.initial}">${vis.anim}${u}</g>`;
  }).join("");
  enemies.push(`<g>${moveAnim(pos)}${body}</g>`);
}

// the hero
const heroPos = series(fr => [fr.hero.x - 3, fr.hero.y - 2]);
const heroKeys = frames.map(fr => (fr.hidden || fr.hero.blink ? "none" : `h${fr.hero.anim}${fr.hero.facing < 0 ? "L" : "R"}${fr.hero.skin[0]}`));
const heroBody = [...new Set(heroKeys)].filter(k => k !== "none").map(k => {
  const vis = showAnim(heroKeys.map(v => v === k));
  return `<g opacity="${vis.initial}">${vis.anim}<use href="#${k}"/></g>`;
}).join("");
const hero = `<g>${moveAnim(heroPos)}${heroBody}</g>`;

// particles and score popups
const fx = [];
const partIds = [...new Set(frames.flatMap(fr => fr.particles.map(q => q.id)))];
for (const id of partIds) {
  const at = frames.map(fr => fr.particles.find(q => q.id === id));
  const first = at.find(Boolean);
  const vis = showAnim(at.map(Boolean));
  const pos = series(fr => { const q = fr.particles.find(x => x.id === id) || first; return [Math.round(q.x), Math.round(q.y)]; });
  const col = first.kind === "dust" ? PAL.white : first.kind === "brick" ? th.tile.b : PAL.yellow;
  const size = first.kind === "brick" ? 4 : 2;
  fx.push(`<g opacity="${vis.initial}">${vis.anim}<g>${moveAnim(pos)}<rect width="${size}" height="${size}" fill="${col}"/></g></g>`);
}
const popIds = [...new Set(frames.flatMap(fr => fr.popups.map(q => q.id)))];
for (const id of popIds) {
  const at = frames.map(fr => fr.popups.find(q => q.id === id));
  const first = at.find(Boolean);
  const vis = showAnim(at.map(Boolean));
  const pos = series(fr => { const q = fr.popups.find(x => x.id === id) || first; return [Math.round(q.x + 8), Math.round(q.y)]; });
  fx.push(`<g opacity="${vis.initial}">${vis.anim}<g>${moveAnim(pos)}${shadowText(first.text, 0, 0, PAL.white, 1, "center")}</g></g>`);
}

// ---------------------------------------------------------------- HUD and overlays
function valueWindows(get, render) {
  const vals = frames.map(get);
  const uniq = [...new Set(vals)];
  return uniq.map(v => { const vis = showAnim(vals.map(x => x === v)); return `<g opacity="${vis.initial}">${vis.anim}${render(v)}</g>`; }).join("");
}
const pad6 = n => String(n).padStart(6, "0");
const hud = [
  shadowText("SCORE", 6, 4, PAL.white),
  valueWindows(fr => fr.score, v => shadowText(pad6(v), 42, 4, PAL.white)),
  `<use href="#minibit" x="92" y="4"/>`,
  shadowText("x", 101, 4, PAL.white),
  valueWindows(fr => fr.bits, v => shadowText(String(v).padStart(2, "0"), 107, 4, PAL.white)),
  shadowText("1-1", 128, 4, PAL.yellow), shadowText("LOCALHOST", 152, 4, PAL.white),
  `<use href="#heart" x="294" y="4"/>`, shadowText("3", 303, 4, PAL.white),
].join("");
const doorFrame = frames.findIndex(fr => fr.hidden);
const bannerOn = frames.map((fr, i) => doorFrame >= 0 && i >= doorFrame + 30);
const bannerVis = showAnim(bannerOn);
const bonus = frames[doorFrame >= 0 ? doorFrame : F].timeBonus;
const banner = `<g opacity="${bannerVis.initial}">${bannerVis.anim}<rect x="40" y="70" width="${W - 80}" height="42" fill="#0c1022" fill-opacity=".88"/><rect x="40" y="70" width="${W - 80}" height="2" fill="#1b1325"/><rect x="40" y="110" width="${W - 80}" height="2" fill="#1b1325"/>
  ${shadowText("CODE PUSHED!", W / 2, 80, PAL.yellow, 1, "center")}${shadowText("TIME BONUS " + bonus, W / 2, 92, PAL.white, 1, "center")}</g>`;
function logoText(str, cx, y, scale, colors, outline) {
  const wpx = (str.length * 6 - 1) * scale, x0 = Math.round(cx - wpx / 2);
  let out = "";
  for (const [dx, dy] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, -1], [-1, 1], [1, 1], [0, 2], [1, 2], [-1, 2], [0, 3], [1, 3], [-1, 3]]) out += text(str, x0 + dx, y + dy, outline, scale);
  [...str].forEach((c, i) => {
    const rows = FONT[c];
    if (!rows) return;
    rows.forEach((r, ry) => {
      const col = colors[Math.min(colors.length - 1, Math.floor(ry / 7 * colors.length))];
      const d = runs([r], "#").replace(/M(\d+) 0/g, (m, x) => `M${x0 + (i * 6 + Number(x)) * scale} ${y + ry * scale}`).replace(/h(\d+)v1h-(\d+)z/g, (m, a) => `h${a * scale}v${scale}h-${a * scale}z`);
      out += `<path fill="${col}" d="${d}"/>`;
    });
  });
  return out;
}
const hk = HOLD / DUR;
const title = `<g opacity="1"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;${k4(hk * 0.85)};${k4(hk)};1" dur="${fmt(DUR)}s" repeatCount="indefinite"/>
  <rect x="28" y="22" width="264" height="86" fill="#0c1022" fill-opacity=".62"/><rect x="28" y="22" width="264" height="2" fill="#1b1325"/><rect x="28" y="106" width="264" height="2" fill="#1b1325"/>
  ${logoText("PUSH TO PROD", W / 2, 32, 3, [PAL.yellow, PAL.yellow, PAL.orange, PAL.tangerine], "#1b1325")}
  ${shadowText("A TINY CODING PLATFORMER", W / 2, 62, PAL.blue, 1, "center")}
  <g>${shadowText("PRESS START", W / 2, 84, PAL.yellow, 1, "center")}<animate attributeName="opacity" calcMode="discrete" values="1;0" keyTimes="0;.5" dur="1s" repeatCount="indefinite"/></g></g>`;
const fade = `<rect width="${W}" height="${H}" fill="#000"><animate attributeName="opacity" values="1;0;0;1" keyTimes="0;${k4(0.25 / DUR)};${k4(1 - 0.3 / DUR)};1" dur="${fmt(DUR)}s" repeatCount="indefinite"/></rect>`;

// ---------------------------------------------------------------- assemble
const camMove = moveAnim(series(fr => [-fr.cam, 0]));
const screen = [
  `<g>${sky()}</g>`,
  parallax("clouds", cloudsLayer(), 640, 0.2, 8, 2),
  parallax("hills", hillsLayer(), 512, 0.45, 84, 3),
  parallax("bushes", bushesLayer(), 384, 0.75, 122, 4),
  `<g>${camMove}${rising.join("")}${world.join("")}${items.join("")}${enemies.join("")}${hero}${fx.join("")}</g>`,
  hud, banner, title, fade,
].join("");
const glyphs = [...glyphIds].map(c => `<path id="f${c.charCodeAt(0)}" d="${runs(FONT[c], "#")}"/>`).join("");
const OW = W + PAD * 2, OH = H + PAD * 2;
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${OW * 2}" height="${OH * 2}" viewBox="0 0 ${OW} ${OH}" role="img" aria-labelledby="t d">
<title id="t">PUSH TO PROD gameplay demo</title>
<desc id="d">A recorded run of PUSH TO PROD, a tiny retro platformer: the developer hero grabs coffee from a code block, stomps bugs, collects bits, climbs the SHIP staircase and pushes the code into the server.</desc>
<defs>${glyphs}${defs.join("")}<clipPath id="scr"><rect width="${W}" height="${H}"/></clipPath></defs>
<g shape-rendering="crispEdges"><rect width="${OW}" height="${OH}" fill="#000"/><rect x="2" y="2" width="${OW - 4}" height="${OH - 4}" fill="#1d2b53"/><rect x="${PAD - 2}" y="${PAD - 2}" width="${W + 4}" height="${H + 4}" fill="#000"/>
<g transform="translate(${PAD} ${PAD})" clip-path="url(#scr)">${screen}</g></g>
</svg>
`;
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, svg);
console.log("wrote", OUT, (svg.length / 1024).toFixed(1), "KB");
