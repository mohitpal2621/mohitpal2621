#!/usr/bin/env python3
"""BUG HUNT: a tiny turn-based arcade game that lives in a GitHub profile README.

Every move arrives as a GitHub issue titled "arcade|up" (or down, left, right).
The Arcade workflow runs this script, which updates arcade/state.json, redraws the
CRT screen as SVG (dark and light bezel) and points README.md at the new frame.

Usage:
  arcade.py init              start a fresh game
  arcade.py move              apply ISSUE_TITLE / ISSUE_USER from the environment
  arcade.py render            redraw the current state
  arcade.py buttons           draw the D-pad button images
"""
import glob
import json
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARC = os.path.join(ROOT, "arcade")
STATE = os.path.join(ARC, "state.json")
README = os.path.join(ROOT, "README.md")

COLS, ROWS, TILE, PX = 15, 8, 30, 3
START = (1, 3)
DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
ARROW = {"up": "^", "down": "_", "left": "{", "right": "}"}
NL = chr(10)

# ------------------------------------------------------------------ 5x7 pixel font
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    ":": [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "@": [".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "^": [".....", ".....", "..#..", ".###.", "#####", ".....", "....."],
    "_": [".....", ".....", "#####", ".###.", "..#..", ".....", "....."],
    "{": [".....", "...#.", "..##.", ".###.", "..##.", "...#.", "....."],
    "}": [".....", ".#...", ".##..", ".###.", ".##..", ".#...", "....."],
}

# ------------------------------------------------------------------ 10x10 sprites
ROBOT = ["....##....", "....##....", ".########.", ".#..##..#.", ".########.",
         ".##....##.", "..######..", "#.######.#", "#.######.#", "..##..##.."]
EYELID = ["..........", "..........", "..........", "..##..##..", "..........",
          "..........", "..........", "..........", "..........", ".........."]
BUG_A = ["..#....#..", "...#..#...", "#..####..#", ".#.####.#.", "..######..",
         "#.##..##.#", ".###..###.", "..##..##..", ".#.####.#.", "#..####..#"]
BUG_B = ["..#....#..", "...#..#...", "...####...", "##.####.##", "..######..",
         "..##..##..", "####..####", "..##..##..", "...####...", "##.####.##"]
RACK = [".########.", ".#......#.", ".#.##....#", ".########.", ".#......#.",
        ".#.##....#", ".########.", ".#......#.", ".#.##....#", ".########."]
LEDS = [(6, 2), (6, 5), (6, 8)]


def runs_path(rows):
    parts = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            if row[x] == "#":
                start = x
                while x < len(row) and row[x] == "#":
                    x += 1
                parts.append(f"M{start} {y}h{x - start}v1h-{x - start}z")
            else:
                x += 1
    return "".join(parts)


def glyph_defs(chars):
    out = []
    for ch in sorted(set(chars)):
        if ch == " " or ch not in FONT:
            continue
        out.append(f'<path id="f{ord(ch)}" d="{runs_path(FONT[ch])}"/>')
    return "".join(out)


class Text:
    def __init__(self):
        self.used = set()

    def __call__(self, s, x, y, scale=2, cls="t", anchor="start"):
        s = s.upper()
        self.used.update(s)
        width = len(s) * 6 - 1
        if anchor == "middle":
            x -= width * scale / 2
        elif anchor == "end":
            x -= width * scale
        uses = "".join(f'<use href="#f{ord(c)}" x="{i * 6}"/>' for i, c in enumerate(s) if c != " " and c in FONT)
        return f'<g class="{cls}" transform="translate({x:g} {y:g}) scale({scale})">{uses}</g>'


# ------------------------------------------------------------------ game logic
def free_cells(walls):
    return [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in walls]


def reachable(start, walls):
    seen, stack = {start}, [start]
    while stack:
        x, y = stack.pop()
        for dx, dy in DIRS.values():
            n = (x + dx, y + dy)
            if 0 <= n[0] < COLS and 0 <= n[1] < ROWS and n not in walls and n not in seen:
                seen.add(n)
                stack.append(n)
    return seen


def new_level(state):
    level = state["level"]
    rng = random.Random(f"{state['seed']}-{level}")
    for _ in range(200):
        walls = set()
        for _ in range(min(5 + level, 12)):
            length = rng.choice([2, 2, 3])
            horizontal = rng.random() < 0.5
            x = rng.randrange(2, COLS - (length if horizontal else 1))
            y = rng.randrange(0, ROWS - (1 if horizontal else length))
            for i in range(length):
                walls.add((x + i, y) if horizontal else (x, y + i))
        walls.discard(START)
        reach = reachable(START, walls)
        if len(reach) < len(free_cells(walls)) * 0.95:
            continue
        spots = [c for c in reach if abs(c[0] - START[0]) + abs(c[1] - START[1]) >= 4]
        rng.shuffle(spots)
        state["walls"] = sorted([list(w) for w in walls])
        state["bugs"] = sorted([list(c) for c in spots[:min(3 + level, 9)]])
        state["player"] = list(START)
        return
    raise RuntimeError("could not build a level")


def fresh_state():
    state = {"version": 1, "seed": random.randrange(1 << 30), "level": 1, "moves": 0, "squashed": 0,
             "scores": {}, "last": None}
    new_level(state)
    return state


def wander(state, rng):
    walls = {tuple(w) for w in state["walls"]}
    bugs = [tuple(b) for b in state["bugs"]]
    player = tuple(state["player"])
    order = list(range(len(bugs)))
    rng.shuffle(order)
    for i in order:
        if rng.random() > 0.55:
            continue
        x, y = bugs[i]
        options = []
        for dx, dy in DIRS.values():
            n = (x + dx, y + dy)
            if 0 <= n[0] < COLS and 0 <= n[1] < ROWS and n not in walls and n != player and n not in bugs:
                options.append(n)
        if options:
            bugs[i] = rng.choice(options)
    state["bugs"] = sorted([list(b) for b in bugs])


def apply_move(state, user, direction):
    dx, dy = DIRS[direction]
    px, py = state["player"]
    nx, ny = px + dx, py + dy
    walls = {tuple(w) for w in state["walls"]}
    bugs = {tuple(b) for b in state["bugs"]}
    scores = state["scores"]
    scores[user] = scores.get(user, 0) + 1
    gained, event, at = 1, "move", [nx, ny]
    if not (0 <= nx < COLS and 0 <= ny < ROWS) or (nx, ny) in walls:
        event, at = "bonk", [px, py]
    else:
        state["player"] = [nx, ny]
        if (nx, ny) in bugs:
            bugs.discard((nx, ny))
            state["bugs"] = sorted([list(b) for b in bugs])
            state["squashed"] += 1
            scores[user] += 10
            gained += 10
            event = "squash"
    state["moves"] += 1
    if not state["bugs"]:
        scores[user] += 50
        gained += 50
        state["level"] += 1
        new_level(state)
        event = "clear"
    elif event != "squash":
        wander(state, random.Random(f"{state['seed']}-{state['moves']}"))
    state["last"] = {"user": user, "dir": direction, "event": event, "at": at, "gained": gained}
    return event, gained


# ------------------------------------------------------------------ rendering
THEMES = {
    "dark": dict(bezel="#161b22", edge="#30363d", label="#6e7681", led="#3fb950"),
    "light": dict(bezel="#eaeef2", edge="#d0d7de", label="#6e7781", led="#1a7f37"),
}
CRT = dict(bg="#0b0f14", floor="#262c36", wall="#5b6470", led="#9aa4b1", dim="#5b6470",
           text="#adbac7", bright="#f0f6fc", bug="#9ba6b3")


def render(state, mode):
    th = THEMES[mode]
    T = Text()
    W, H = 760, 380
    ox, oy = 32, 62
    parts = []

    # floor dots and play-area frame
    dots = "".join(f"M{ox + x * TILE + 14} {oy + y * TILE + 14}h2v2h-2z" for x in range(COLS) for y in range(ROWS))
    parts.append(f'<path d="{dots}" fill="{CRT["floor"]}"/>')
    parts.append(f'<rect x="{ox - 6}" y="{oy - 6}" width="{COLS * TILE + 12}" height="{ROWS * TILE + 12}" '
                 f'fill="none" stroke="{CRT["floor"]}" stroke-width="2" stroke-dasharray="2 4"/>')

    # racks with blinking LEDs
    for i, (x, y) in enumerate(state["walls"]):
        tx, ty = ox + x * TILE, oy + y * TILE
        parts.append(f'<use href="#rack" transform="translate({tx} {ty}) scale({PX})"/>')
        for j, (lx, ly) in enumerate(LEDS):
            dur = 0.9 + ((i * 7 + j * 3) % 9) * 0.23
            delay = -((i * 5 + j * 11) % 13) * 0.17
            parts.append(f'<rect class="led" x="{tx + lx * PX}" y="{ty + ly * PX}" width="{PX}" height="{PX}" '
                         f'style="animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s"/>')

    # bugs
    for i, (x, y) in enumerate(state["bugs"]):
        delay = -(i * 0.17) % 0.5
        parts.append(
            f'<g transform="translate({ox + x * TILE} {oy + y * TILE}) scale({PX})" fill="{CRT["bug"]}">'
            f'<use class="fa" href="#bugA" style="animation-delay:{delay:.2f}s"/>'
            f'<use class="fb" href="#bugB" style="animation-delay:{delay:.2f}s"/></g>'
        )

    # player robot
    px, py = state["player"]
    parts.append(
        f'<g transform="translate({ox + px * TILE} {oy + py * TILE})"><g class="bob">'
        f'<g transform="scale({PX})" fill="{CRT["bright"]}"><use href="#robot"/>'
        f'<path class="eye" d="{runs_path(EYELID)}"/></g></g></g>'
    )

    # last-move effects
    last = state.get("last")
    if last and last["event"] in ("squash", "bonk"):
        ax, ay = last["at"]
        label = f"+{last['gained']}" if last["event"] == "squash" else "BONK!"
        cx, cy = ox + ax * TILE + 15, oy + ay * TILE - 4
        ly = cy - 14 if ay > 0 else oy + TILE + 6
        parts.append(f'<g class="pop">{T(label, cx, ly, 2, "hi", "middle")}</g>')
        if last["event"] == "squash":
            burst = []
            for k, (bx, by) in enumerate([(-9, -9), (9, -9), (-12, 0), (12, 0), (-9, 9), (9, 9)]):
                burst.append(f'<rect x="{cx + bx - 1.5}" y="{cy + 19 + by - 1.5}" width="3" height="3"/>')
            parts.append(f'<g class="burst" fill="{CRT["bright"]}">{"".join(burst)}</g>')
    if last and last["event"] == "clear":
        level_txt = f"LEVEL {state['level']:02d}"
        mx = ox + COLS * TILE / 2
        box = (f'<rect x="{mx - 170}" y="{oy + 78}" width="340" height="96" fill="{CRT["bg"]}" fill-opacity=".94" '
               f'stroke="{CRT["text"]}" stroke-width="2"/>'
               f'<rect x="{mx - 164}" y="{oy + 84}" width="328" height="84" fill="none" stroke="{CRT["dim"]}" stroke-width="1"/>')
        parts.append(f'<g class="splash">{box}{T(level_txt, mx, oy + 98, 4, "hi", "middle")}'
                     f'{T("CLEARED BY @" + last["user"][:14], mx, oy + 144, 2, "t", "middle")}</g>')

    # HUD
    hud = [T("BUG HUNT", ox - 2, 24, 3, "hi")]
    rx = 498
    hud.append(T(f"LVL {state['level']:02d}", rx, 30, 2, "t"))
    hud.append(T(f"BUGS {len(state['bugs']):02d}", 726, 30, 2, "t", "end"))
    hud.append(T("HI-SCORES", rx, oy, 2, "hi"))
    hud.append(f'<rect x="{rx}" y="{oy + 22}" width="228" height="2" fill="{CRT["floor"]}"/>')
    top = sorted(state["scores"].items(), key=lambda kv: (-kv[1], kv[0].lower()))[:5]
    for i in range(5):
        y = oy + 34 + i * 22
        if i < len(top):
            name, pts = top[i]
            name = name.upper()
            name = name if len(name) <= 12 else name[:11] + "."
            hud.append(T(f"{i + 1} {name}", rx, y, 2, "t"))
            hud.append(T(str(min(pts, 9999)), 726, y, 2, "t", "end"))
        else:
            hud.append(T(f"{i + 1} ----------", rx, y, 2, "d"))
    hud.append(T("SQUASHED", rx, oy + 156, 2, "d"))
    hud.append(T(str(state["squashed"]), 726, oy + 156, 2, "t", "end"))
    hud.append(T("PLAYERS", rx, oy + 178, 2, "d"))
    hud.append(T(str(len(state["scores"])), 726, oy + 178, 2, "t", "end"))
    hud.append(T("LAST MOVE", rx, oy + 204, 2, "d"))
    if last:
        who = "@" + last["user"].upper()
        who = who if len(who) <= 16 else who[:15] + "."
        hud.append(T(f"{who} {ARROW[last['dir']]}", rx, oy + 226, 2, "t"))
    else:
        hud.append(T("PLAYER 1 READY?", rx, oy + 226, 2, "t"))
    hud.append(f'<g class="press">{T("PRESS ^ _ { } BELOW TO PLAY", ox + COLS * TILE / 2, oy + ROWS * TILE + 18, 2, "hi", "middle")}</g>')

    body = "".join(parts) + "".join(hud)
    css = NL.join([
        f".t{{fill:{CRT['text']}}}.hi{{fill:{CRT['bright']}}}.d{{fill:{CRT['dim']}}}.led{{fill:{CRT['led']}}}",
        ".fa{animation:fa .6s steps(1,end) infinite}.fb{opacity:0;animation:fb .6s steps(1,end) infinite}",
        "@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}",
        ".bob{animation:bob 1.2s steps(1,end) infinite}@keyframes bob{0%{transform:translateY(0)}50%{transform:translateY(-3px)}}",
        ".eye{opacity:0;animation:eye 3.8s steps(1,end) infinite}@keyframes eye{0%{opacity:0}90%{opacity:1}95%{opacity:0}}",
        ".led{animation:led 1.4s steps(1,end) infinite}@keyframes led{0%{opacity:1}50%{opacity:.15}}",
        ".press{animation:press 1.2s steps(1,end) infinite}@keyframes press{0%{opacity:1}60%{opacity:0}}",
        ".pop{animation:pop 2.4s ease-out .3s both}@keyframes pop{0%{opacity:0;transform:translateY(8px)}12%{opacity:1}70%{opacity:1}100%{opacity:0;transform:translateY(-14px)}}",
        ".burst{animation:burst .9s ease-out .3s both}@keyframes burst{0%{opacity:1}100%{opacity:0}}",
        ".splash{animation:splash 3.2s steps(1,end) .2s both}@keyframes splash{0%,12%,24%,36%{opacity:1}6%,18%,30%{opacity:0}75%{opacity:1}100%{opacity:0}}",
        ".crt{animation:flick 8s infinite}@keyframes flick{0%,41%,44%,100%{opacity:1}42%{opacity:.88}}",
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}",
    ])
    defs = (
        glyph_defs(T.used)
        + f'<path id="robot" d="{runs_path(ROBOT)}"/>'
        + f'<path id="bugA" d="{runs_path(BUG_A)}"/><path id="bugB" d="{runs_path(BUG_B)}"/>'
        + f'<path id="rack" fill="{CRT["wall"]}" d="{runs_path(RACK)}"/>'
        + '<pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" fill-opacity=".35"/></pattern>'
        + f'<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>'
        + '<linearGradient id="glare" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".07"/><stop offset=".35" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        + '<filter id="glow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        + f'<clipPath id="screen"><rect x="14" y="14" width="{W - 28}" height="{H - 28}" rx="12"/></clipPath>'
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">BUG HUNT, a playable arcade game</title>
  <desc id="d">Level {state['level']}, {len(state['bugs'])} bugs left, {state['squashed']} squashed by {len(state['scores'])} players.</desc>
  <style>{css}</style>
  <defs>{defs}</defs>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="{th['bezel']}" stroke="{th['edge']}"/>
  <circle cx="{W - 26}" cy="{H - 7.5}" r="2.5" fill="{th['led']}"/>
  <g clip-path="url(#screen)">
    <rect x="14" y="14" width="{W - 28}" height="{H - 28}" fill="{CRT['bg']}"/>
    <g class="crt" filter="url(#glow)">{body}</g>
    <rect x="14" y="14" width="{W - 28}" height="{H - 28}" fill="url(#scan)"/>
    <rect x="14" y="14" width="{W - 28}" height="{H - 28}" fill="url(#vig)"/>
    <rect x="14" y="14" width="{W - 28}" height="{H - 28}" fill="url(#glare)"/>
  </g>
  <rect x="14.5" y="14.5" width="{W - 29}" height="{H - 29}" rx="12" fill="none" stroke="#000" stroke-opacity=".6"/>
</svg>
"""


# ------------------------------------------------------------------ D-pad buttons
BTN = {
    "dark": dict(fill="#21262d", edge="#30363d", icon="#c9d1d9"),
    "light": dict(fill="#f6f8fa", edge="#d0d7de", icon="#24292f"),
}
ICONS = {
    "up": "M17.5 27l6.5-6.5 6.5 6.5",
    "down": "M17.5 21l6.5 6.5 6.5-6.5",
    "left": "M27 17.5l-6.5 6.5 6.5 6.5",
    "right": "M21 17.5l6.5 6.5-6.5 6.5",
    "refresh": "M31.2 21.5a7.8 7.8 0 1 0 .6 4.6M31.6 15.8v5.9h-5.9",
}


def buttons(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for mode, c in BTN.items():
        for name, d in ICONS.items():
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">'
                   f'<rect x="4.5" y="4.5" width="39" height="39" rx="8" fill="{c["fill"]}" stroke="{c["edge"]}"/>'
                   f'<path d="{d}" fill="none" stroke="{c["icon"]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
            with open(os.path.join(out_dir, f"{name}-{mode}.svg"), "w", encoding="utf-8") as fh:
                fh.write(svg + NL)
    with open(os.path.join(out_dir, "blank.svg"), "w", encoding="utf-8") as fh:
        fh.write('<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"/>' + NL)


# ------------------------------------------------------------------ files
def load():
    with open(STATE, encoding="utf-8") as fh:
        return json.load(fh)


def save(state):
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=1, sort_keys=True)
        fh.write(NL)


def write_screens(state):
    for old in glob.glob(os.path.join(ARC, "screen-*.svg")):
        os.remove(old)
    stamp = f"{state['moves']:06d}"
    for mode in THEMES:
        with open(os.path.join(ARC, f"screen-{stamp}-{mode}.svg"), "w", encoding="utf-8") as fh:
            fh.write(render(state, mode))
    if os.path.exists(README):
        with open(README, encoding="utf-8") as fh:
            text = fh.read()
        text, n = re.subn(r"arcade/screen-\d{6}-(dark|light)\.svg", lambda m: f"arcade/screen-{stamp}-{m.group(1)}.svg", text)
        if n:
            with open(README, "w", encoding="utf-8") as fh:
                fh.write(text)


def comment(state, user, direction, event, gained):
    lines = {
        "move": f"@{user} moved **{direction}**. The bugs scuttled around. **+{gained}**",
        "bonk": f"@{user} bonked into a server rack going **{direction}**. Still earns **+{gained}** for trying.",
        "squash": f"@{user} moved **{direction}** and squashed a bug! **+{gained}**",
        "clear": f"@{user} squashed the last bug and cleared the level! **+{gained}** (level bonus included). Level {state['level']} is up.",
    }
    board = f"Level {state['level']} · {len(state['bugs'])} bugs left · you have {state['scores'][user]} points."
    return (f"🕹️ {lines[event]}{NL}{NL}{board}{NL}{NL}"
            f"The screen on https://github.com/mohitpal2621 refreshes in a few seconds. Thanks for playing!")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"
    if cmd == "init":
        state = fresh_state()
        save(state)
        write_screens(state)
        buttons(os.path.join(ARC, "buttons"))
    elif cmd == "render":
        write_screens(load())
    elif cmd == "buttons":
        buttons(os.path.join(ARC, "buttons"))
    elif cmd == "move":
        title = os.environ.get("ISSUE_TITLE", "").strip().lower()
        user = os.environ.get("ISSUE_USER", "").strip()
        m = re.fullmatch(r"arcade\|(up|down|left|right)", title)
        if not m or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", user):
            print("🕹️ That move isn't one I know. Use the arrow buttons on https://github.com/mohitpal2621 to play.")
            sys.exit(3)
        state = load()
        event, gained = apply_move(state, user, m.group(1))
        save(state)
        write_screens(state)
        print(comment(state, user, m.group(1), event, gained))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
