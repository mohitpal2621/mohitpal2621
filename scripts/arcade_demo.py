"""Render the README preview of BUG HUNT (docs/index.html) as a looping, animated SVG, plus its D-pad buttons.

The demo is a real simulation of the game's attract mode (same board size, sprites, font and rules),
recorded once and replayed with SMIL/CSS animation, because a README can't run JavaScript.

    python3 scripts/arcade_demo.py            # writes assets/arcade/*.svg
"""
import math
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "arcade")

W, H, COLS, ROWS, TILE, OX, OY = 160, 108, 15, 8, 10, 5, 12
PX = 4                      # screen pixels per game pixel
PAD = 16                    # bezel around the screen
BOTTOM = 34                 # bezel strip under the screen
START = (1, 3)
DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
SEED, N_BUGS = 706, 5
READY, CLEAR_HOLD = 1.3, 2.6
AI_STEP, BUG_STEP, FLEE, FREEZE = 0.23, 0.6, 0.45, 3.5

CRT = dict(bg="#0b0f14", floor="#262c36", frame="#2d343f", wall="#5b6470", led="#aab4c0", text="#adbac7",
           dim="#636e7b", bright="#f0f6fc", bug="#9ba6b3", frozen="#4f5966")
THEMES = {
    "dark": dict(bezel="#161b22", edge="#30363d", label="#6e7681", cta="#8b949e", led="#3fb950"),
    "light": dict(bezel="#f6f8fa", edge="#d0d7de", label="#6e7781", cta="#57606a", led="#1a7f37"),
}
BTN = {
    "dark": dict(fill="#21262d", edge="#30363d", icon="#c9d1d9"),
    "light": dict(fill="#f6f8fa", edge="#d0d7de", icon="#24292f"),
}
ICONS = {
    "up": '<path d="M17.5 27l6.5-6.5 6.5 6.5" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>',
    "down": '<path d="M17.5 21l6.5 6.5 6.5-6.5" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>',
    "left": '<path d="M27 17.5l-6.5 6.5 6.5 6.5" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>',
    "right": '<path d="M21 17.5l6.5 6.5-6.5 6.5" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>',
    "play": '<path d="M20 17.5v13l10.5-6.5z" fill="{c}"/>',
}

FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"], "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."], "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"], "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"], "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."], "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"], "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"], "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."], "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"], "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."], "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."], "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."], "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."], "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."], "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"], "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."], "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."], "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."], "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."], ":": [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."], "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    ">": [".#...", ".##..", ".###.", ".####", ".###.", ".##..", ".#..."],
}
ROBOT = ["....##....", "....##....", ".########.", ".#..##..#.", ".########.", ".##....##.", "..######..", "#.######.#", "#.######.#", "..##..##.."]
EYELID = ["..........", "..........", "..........", "..##..##..", "..........", "..........", "..........", "..........", "..........", ".........."]
BUG_A = ["..#....#..", "...#..#...", "#..####..#", ".#.####.#.", "..######..", "#.##..##.#", ".###..###.", "..##..##..", ".#.####.#.", "#..####..#"]
BUG_B = ["..#....#..", "...#..#...", "...####...", "##.####.##", "..######..", "..##..##..", "####..####", "..##..##..", "...####...", "##.####.##"]
RACK = [".########.", ".#......#.", ".#.##....#", ".########.", ".#......#.", ".#.##....#", ".########.", ".#......#.", ".#.##....#", ".########."]
LEDS = [(6, 2), (6, 5), (6, 8)]
COFFEE = ["...#.#....", "..#.#.....", "...#.#....", ".#######..", ".########.", ".#######.#", ".########.", ".#######..", "..#####...", ".#######.."]
HEART = [".#.#.", "#####", "#####", ".###.", "..#.."]


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


# ------------------------------------------------------------------ simulation (mirrors the game's demo AI)
def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def flood(walls):
    seen, stack = {START}, [START]
    while stack:
        x, y = stack.pop()
        for dx, dy in DIRS.values():
            n = (x + dx, y + dy)
            if 0 <= n[0] < COLS and 0 <= n[1] < ROWS and n not in walls and n not in seen:
                seen.add(n)
                stack.append(n)
    return seen


def build_level(rng):
    while True:
        walls = set()
        for _ in range(6):
            ln, hor = (2 if rng.random() < 0.66 else 3), rng.random() < 0.5
            x = 2 + rng.randrange(COLS - 2 - (ln - 1 if hor else 0))
            y = rng.randrange(ROWS - (0 if hor else ln - 1))
            for j in range(ln):
                walls.add((x + j, y) if hor else (x, y + j))
        reach = flood(walls)
        if len(reach) < (COLS * ROWS - len(walls)) * 0.95:
            continue
        spots = sorted(p for p in reach if dist(p, START) >= 4)
        rng.shuffle(spots)
        return walls, sorted(reach), spots[:N_BUGS]


def simulate(seed):
    rng = random.Random(seed)
    walls, reach, spots = build_level(rng)
    free = lambda p: 0 <= p[0] < COLS and 0 <= p[1] < ROWS and p not in walls
    robot = START
    bugs = {i: p for i, p in enumerate(spots)}
    track = {"robot": [], **{i: [] for i in bugs}}
    squashed, events = {}, []
    coffee, coffee_at, coffee_spawn, drink = None, 1.8 + rng.random() * 1.2, None, None
    next_ai, next_bug, t, combo, last_sq, score = AI_STEP, BUG_STEP, 0.0, 0, -9.0, 0
    score_log = [(0.0, 0)]
    while bugs and t < 30:
        pending = [(next_ai, "ai"), (next_bug, "bug")]
        if coffee is None and coffee_spawn is None:
            pending.append((coffee_at, "coffee"))
        t, kind = min(pending)
        if kind == "coffee":
            options = [p for p in reach if p not in bugs.values() and dist(p, robot) >= 3]
            coffee = rng.choice(options)
            coffee_spawn = (t, coffee)
        elif kind == "bug":
            next_bug += BUG_STEP
            order = list(bugs)
            rng.shuffle(order)
            for i in order:
                b = bugs[i]
                taken = set(bugs.values())
                opts = [n for n in ((b[0] + dx, b[1] + dy) for dx, dy in DIRS.values())
                        if free(n) and n != robot and n not in taken]
                if not opts:
                    continue
                pick = None
                if dist(b, robot) <= 3 and rng.random() < FLEE:
                    far = max(dist(n, robot) for n in opts)
                    best = [n for n in opts if dist(n, robot) == far]
                    pick = rng.choice(best)
                elif rng.random() < 0.55:
                    pick = rng.choice(opts)
                if pick:
                    bugs[i] = pick
                    track[i].append((t, pick))
        else:
            next_ai += AI_STEP
            goals = set(bugs.values()) | ({coffee} if coffee else set())
            first, queue, step = {robot: None}, [robot], None
            for cell in queue:
                if cell in goals and first[cell]:
                    step = first[cell]
                    break
                dirs = list(DIRS)
                rng.shuffle(dirs)
                for d in dirs:
                    n = (cell[0] + DIRS[d][0], cell[1] + DIRS[d][1])
                    if free(n) and n not in first:
                        first[n] = first[cell] or d
                        queue.append(n)
            if not step:
                continue
            robot = (robot[0] + DIRS[step][0], robot[1] + DIRS[step][1])
            track["robot"].append((t, robot))
            hit = [i for i, b in bugs.items() if b == robot]
            if hit:
                del bugs[hit[0]]
                combo = combo + 1 if t - last_sq < 1.6 else 0
                last_sq = t
                pts = 10 + 5 * combo
                score += pts
                squashed[hit[0]] = t
                events.append(("squash", t, robot, pts))
                score_log.append((t, score))
            elif coffee and robot == coffee:
                drink, coffee = t, None
                next_bug += FREEZE
                score += 25
                events.append(("coffee", t, robot, 25))
                score_log.append((t, score))
    total = 10 + N_BUGS * 3
    bonus = math.ceil(total - t) * 5
    score_log.append((t, score + bonus))
    return dict(walls=sorted(walls), start_bugs=spots, track=track, squashed=squashed, events=events,
                coffee=coffee_spawn, drink=drink, end=t, bonus=bonus, total=total, score_log=score_log)


# ------------------------------------------------------------------ svg helpers
class Svg:
    def __init__(self, loop):
        self.T = loop
        self.used = set()

    def k(self, t):
        return f"{max(0.0, min(1.0, t / self.T)):.4f}"

    def text(self, s, x, y, cls, scale=1, anchor="start"):
        s = s.upper()
        self.used.update(s)
        width = len(s) * 6 - 1
        if anchor == "middle":
            x -= width * scale / 2
        elif anchor == "end":
            x -= width * scale
        uses = "".join(f'<use href="#f{ord(c)}" x="{i * 6}"/>' for i, c in enumerate(s) if c in FONT)
        sc = f" scale({scale})" if scale != 1 else ""
        return f'<g class="{cls}" transform="translate({x:g} {y:g}){sc}">{uses}</g>'

    def window(self, a, b, inner, extra=""):
        """Show `inner` only between a and b seconds of every loop."""
        if a <= 0 and b >= self.T:
            return f"<g{extra}>{inner}</g>"
        if a <= 0:
            vals, kts = "1;0", f"0;{self.k(b)}"
        elif b >= self.T:
            vals, kts = "0;1", f"0;{self.k(a)}"
        else:
            vals, kts = "0;1;0", f"0;{self.k(a)};{self.k(b)}"
        return (f'<g opacity="{vals[0]}"{extra}><animate attributeName="opacity" values="{vals}" keyTimes="{kts}" '
                f'calcMode="discrete" dur="{self.T:g}s" repeatCount="indefinite"/>{inner}</g>')

    def path_anim(self, start, moves, tween, offset):
        """Translate keyframes for an entity that hops between tiles."""
        pos = lambda p: f"{OX + p[0] * TILE} {OY + p[1] * TILE}"
        vals, kts, cur, last_t = [pos(start)], ["0"], start, 0.0
        for t, p in moves:
            a = max(offset + t, last_t)
            b = min(a + tween, self.T)
            vals += [pos(cur), pos(p)]
            kts += [self.k(a), self.k(b)]
            cur, last_t = p, b
        vals.append(pos(cur))
        kts.append("1")
        return (f'<animateTransform attributeName="transform" type="translate" values="{";".join(vals)}" '
                f'keyTimes="{";".join(kts)}" dur="{self.T:g}s" repeatCount="indefinite"/>')


def panel(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{CRT["bg"]}" fill-opacity=".94"/>'
            f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" fill="none" stroke="{CRT["text"]}"/>'
            f'<rect x="{x + 2.5}" y="{y + 2.5}" width="{w - 5}" height="{h - 5}" fill="none" stroke="{CRT["floor"]}"/>')


def render(sim, mode):
    th = THEMES[mode]
    loop = READY + sim["end"] + CLEAR_HOLD
    S = Svg(loop)
    play = lambda t: READY + t
    end = play(sim["end"])
    out = []

    # board: floor dots, dotted frame, racks with blinking LEDs
    walls = set(map(tuple, sim["walls"]))
    dots = "".join(f"M{OX + x * TILE + 4} {OY + y * TILE + 4}h1v1h-1z" for x in range(COLS) for y in range(ROWS) if (x, y) not in walls)
    out.append(f'<path d="{dots}" fill="{CRT["floor"]}"/>')
    frame = []
    for x in range(OX - 2, OX + COLS * TILE + 2, 3):
        frame += [f"M{x} {OY - 2}h1v1h-1z", f"M{x} {OY + ROWS * TILE + 1}h1v1h-1z"]
    for y in range(OY - 2, OY + ROWS * TILE + 2, 3):
        frame += [f"M{OX - 2} {y}h1v1h-1z", f"M{OX + COLS * TILE + 1} {y}h1v1h-1z"]
    out.append(f'<path d="{"".join(frame)}" fill="{CRT["frame"]}"/>')
    for i, (x, y) in enumerate(sim["walls"]):
        tx, ty = OX + x * TILE, OY + y * TILE
        out.append(f'<use href="#rack" x="{tx}" y="{ty}"/>')
        for j, (lx, ly) in enumerate(LEDS):
            dur = 0.84 + ((i * 7 + j * 5) % 11) * 0.14
            delay = -((i * 5 + j * 11) % 13) * 0.13
            out.append(f'<rect class="led" x="{tx + lx}" y="{ty + ly}" width="1" height="1" '
                       f'style="animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s"/>')

    # coffee
    if sim["coffee"]:
        t0, (cx, cy) = sim["coffee"]
        t1 = play(sim["drink"]) + 0.04 if sim["drink"] is not None else loop
        out.append(S.window(play(t0), t1, f'<g class="bob"><use href="#coffee" x="{OX + cx * TILE}" y="{OY + cy * TILE}" class="hi"/></g>'))

    # bugs: two-frame walk, dimmed and still while frozen, gone once squashed
    frz = (play(sim["drink"]), play(sim["drink"]) + FREEZE) if sim["drink"] is not None else None
    for i, start in enumerate(sim["start_bugs"]):
        moves = sim["track"][i]
        delay = -((i * 0.13) % 0.34)
        body = (f'<g class="bug"><use class="fa" href="#bugA" style="animation-delay:{delay:.2f}s"/>'
                f'<use class="fb" href="#bugB" style="animation-delay:{delay:.2f}s"/></g>')
        if frz:
            vals, kts = "1;0;1", f"0;{S.k(frz[0])};{S.k(frz[1])}"
            body = (f'<g>{body}<animate attributeName="opacity" values="{vals}" keyTimes="{kts}" calcMode="discrete" '
                    f'dur="{loop:g}s" repeatCount="indefinite"/></g>'
                    f'<g opacity="0"><use href="#bugA" class="fz"/><animate attributeName="opacity" values="0;1;0" '
                    f'keyTimes="{kts}" calcMode="discrete" dur="{loop:g}s" repeatCount="indefinite"/></g>')
        gone = play(sim["squashed"][i]) + 0.05 if i in sim["squashed"] else loop
        anim = S.path_anim(start, moves, 0.15, READY)
        mover = f'<g transform="translate({OX + start[0] * TILE} {OY + start[1] * TILE})">{anim}{body}</g>'
        out.append(S.window(0, gone, mover))

    # robot
    anim = S.path_anim(START, sim["track"]["robot"], 0.08, READY)
    out.append(f'<g transform="translate({OX + START[0] * TILE} {OY + START[1] * TILE})">{anim}'
               f'<g class="bob"><use href="#robot" class="hi"/><path class="eye hi" d="{runs_path(EYELID)}"/></g></g>')

    # squash bursts and score popups
    for kind, t, (x, y), pts in sim["events"]:
        a = play(t)
        cx, cy = OX + x * TILE + 5, OY + y * TILE + 5
        if kind == "squash":
            dots = "".join(f'<rect x="{math.cos(n / 10 * math.tau + .3) * 11 - .5:.2f}" y="{math.sin(n / 10 * math.tau + .3) * 11 - .5:.2f}" width="1" height="1"/>'
                           for n in range(10))
            grow = (f'<g><animateTransform attributeName="transform" type="scale" values=".12;.12;1;1" '
                    f'keyTimes="0;{S.k(a + .04)};{S.k(a + .5)};1" dur="{loop:g}s" repeatCount="indefinite"/>{dots}</g>')
            out.append(S.window(a + .04, a + .5, grow, f' class="hi" transform="translate({cx} {cy})"'))
        py = OY + TILE + 3 if y == 0 else OY + y * TILE - 8
        label = S.text(f"+{pts}", 0, 0, "hi", 1, "middle")
        rise = (f'<g><animateTransform attributeName="transform" type="translate" values="{cx} {py};{cx} {py};{cx} {py - 5};{cx} {py - 5}" '
                f'keyTimes="0;{S.k(a)};{S.k(a + .8)};1" dur="{loop:g}s" repeatCount="indefinite"/>{label}</g>')
        out.append(S.window(a, a + .8, rise))

    # HUD: score, level, lives
    hud = []
    log = sim["score_log"]
    for n, (t, sc) in enumerate(log):
        t_next = play(log[n + 1][0]) if n + 1 < len(log) else loop
        if n + 1 < len(log) and log[n + 1][0] == t:
            continue
        hud.append(S.window(0 if n == 0 else play(t), t_next, S.text(f"SCORE {sc:05d}", 5, 2, "t")))
    hud.append(S.text("LEVEL 01", 132, 2, "t", 1, "end"))
    hud.append("".join(f'<use href="#heart" x="{139 + i * 6}" y="3" class="hi"/>' for i in range(3)))

    # timer bar and countdown
    frac_end = (sim["total"] - sim["end"]) / sim["total"]
    hud.append(f'<rect x="{OX}" y="95" width="{COLS * TILE}" height="2" fill="{CRT["floor"]}"/>')
    hud.append(f'<rect x="{OX}" y="95" width="{COLS * TILE}" height="2" fill="{CRT["text"]}">'
               f'<animate attributeName="width" values="{COLS * TILE};{COLS * TILE};{COLS * TILE * frac_end:.2f};{COLS * TILE * frac_end:.2f}" '
               f'keyTimes="0;{S.k(READY)};{S.k(end)};1" dur="{loop:g}s" repeatCount="indefinite"/></rect>')
    secs = list(range(0, int(math.floor(sim["end"])) + 1))
    for n in secs:
        a = 0 if n == 0 else play(n)
        b = play(n + 1) if n + 1 <= sim["end"] else loop
        hud.append(S.window(a, b, S.text(f"DEPLOY IN {sim['total'] - n}S", 5, 100, "d")))

    # right status: bugs left, or the freeze countdown
    marks = [(0.0, f"BUGS {N_BUGS:02d}")]
    left = N_BUGS
    for kind, t, _, _ in sim["events"]:
        if kind == "squash":
            left -= 1
            marks.append((t, f"BUGS {left:02d}"))
    if sim["drink"] is not None:
        d = sim["drink"]
        frozen_marks = [(d + FREEZE - s, f"FROZEN {s}S") for s in range(math.ceil(FREEZE), 0, -1)]
        frozen_marks[0] = (d, frozen_marks[0][1])
        marks = [m for m in marks if not (d <= m[0] < d + FREEZE)]
        marks += frozen_marks
        after = N_BUGS - sum(1 for k, t, _, _ in sim["events"] if k == "squash" and t < d + FREEZE)
        marks.append((d + FREEZE, f"BUGS {after:02d}"))
    marks = sorted(m for m in marks if m[0] < sim["end"]) + [(sim["end"], "BUGS 00")]
    for n, (t, label) in enumerate(marks):
        a = 0 if n == 0 else play(t)
        b = play(marks[n + 1][0]) if n + 1 < len(marks) else loop
        cls = "hi" if label.startswith("FROZEN") else "d"
        hud.append(S.window(a, b, S.text(label, 155, 100, cls, 1, "end")))

    # overlays: level intro, level clear, flash
    ready = panel(28, 29, 104, 42) + S.text("LEVEL 01", 80, 34, "hi", 2, "middle") + S.text(f"SQUASH {N_BUGS} BUGS", 80, 56, "t", 1, "middle")
    clear = (panel(24, 26, 112, 50) + S.text("CLEAR!", 80, 32, "hi", 2, "middle")
             + S.text(f"TIME BONUS +{sim['bonus']}", 80, 52, "t", 1, "middle") + S.text("NEXT: LEVEL 02", 80, 62, "d", 1, "middle"))
    over = [S.window(0, READY, ready), S.window(end + .3, loop, clear)]
    over.append(f'<rect width="{W}" height="{H}" fill="{CRT["bright"]}" opacity="0"><animate attributeName="opacity" '
                f'values="0;0;.16;0;0" keyTimes="0;{S.k(end)};{S.k(end + .01)};{S.k(end + .2)};1" dur="{loop:g}s" repeatCount="indefinite"/></rect>')

    screen = "".join(out) + "".join(hud) + "".join(over)

    # bezel strip under the screen
    sw, sh = W * PX, H * PX
    total_w, total_h = sw + 2 * PAD, sh + PAD + BOTTOM
    k = 1.5
    ly = PAD + sh + (BOTTOM - PAD / 2 - 7 * k) / 2 + 2
    plate = S.text("PIXEL MATRIX - MONO SOUND", PAD + 4, ly, "lb", k)
    words = "PRESS ANY BUTTON TO PLAY"
    right = sw + PAD - 18
    left = right - (len(words) * 6 - 1) * k
    cta = f'<g class="press">{S.text(">", left - 10 * k, ly, "ct", k)}</g>' + S.text(words, right, ly, "ct", k, "end")

    css = "".join([
        f".t{{fill:{CRT['text']}}}.hi{{fill:{CRT['bright']}}}.d{{fill:{CRT['dim']}}}.led{{fill:{CRT['led']}}}",
        f".bug{{fill:{CRT['bug']}}}.fz{{fill:{CRT['frozen']}}}.lb{{fill:{th['label']}}}.ct{{fill:{th['cta']}}}",
        ".fa{animation:fa .34s steps(1,end) infinite}.fb{opacity:0;animation:fb .34s steps(1,end) infinite}",
        "@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}",
        ".bob{animation:bob 1.04s steps(1,end) infinite}@keyframes bob{0%{transform:translateY(0)}50%{transform:translateY(-1px)}}",
        ".eye{opacity:0;animation:eye 3.8s steps(1,end) infinite}@keyframes eye{0%{opacity:0}95%{opacity:1}}",
        ".led{animation:led 1.4s steps(1,end) infinite}@keyframes led{0%{opacity:1}50%{opacity:.12}}",
        ".press{animation:press 1.1s steps(1,end) infinite}@keyframes press{0%{opacity:1}55%{opacity:0}}",
        ".crt{animation:flick 9s infinite}@keyframes flick{0%,61%,64%,100%{opacity:1}62%{opacity:.9}}",
        "@media (prefers-reduced-motion:reduce){.fa,.fb,.bob,.eye,.led,.press,.crt{animation:none}}",
    ])
    glyphs = "".join(f'<path id="f{ord(c)}" d="{runs_path(FONT[c])}"/>' for c in sorted(S.used) if c in FONT)
    defs = (glyphs
            + f'<path id="robot" d="{runs_path(ROBOT)}"/><path id="bugA" d="{runs_path(BUG_A)}"/><path id="bugB" d="{runs_path(BUG_B)}"/>'
            + f'<path id="rack" fill="{CRT["wall"]}" d="{runs_path(RACK)}"/><path id="coffee" d="{runs_path(COFFEE)}"/>'
            + f'<path id="heart" d="{runs_path(HEART)}"/>'
            + '<pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" fill-opacity=".28"/></pattern>'
            + '<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".58" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>'
            + '<linearGradient id="glare" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".05"/><stop offset=".38" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            + '<filter id="glow" x="-3%" y="-3%" width="106%" height="106%"><feGaussianBlur stdDeviation=".42" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            + f'<clipPath id="clip"><rect x="{PAD}" y="{PAD}" width="{sw}" height="{sh}" rx="8"/></clipPath>')
    squashes = sum(1 for e in sim["events"] if e[0] == "squash")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}" role="img" aria-labelledby="t d">
  <title id="t">BUG HUNT demo</title>
  <desc id="d">A looping demo of BUG HUNT, a retro browser game: the robot grabs a coffee to freeze the bugs and squashes all {squashes} of them before the deploy timer runs out.</desc>
  <style>{css}</style>
  <defs>{defs}</defs>
  <rect x=".5" y=".5" width="{total_w - 1}" height="{total_h - 1}" rx="18" fill="{th['bezel']}" stroke="{th['edge']}"/>
  {plate}{cta}
  <circle cx="{sw + PAD - 5}" cy="{ly + 3.5 * k}" r="2.5" fill="{th['led']}" fill-opacity=".85"/>
  <g clip-path="url(#clip)">
    <rect x="{PAD}" y="{PAD}" width="{sw}" height="{sh}" fill="{CRT['bg']}"/>
    <g class="crt" transform="translate({PAD} {PAD}) scale({PX})" filter="url(#glow)">{screen}</g>
    <rect x="{PAD}" y="{PAD}" width="{sw}" height="{sh}" fill="url(#scan)"/>
    <rect x="{PAD}" y="{PAD}" width="{sw}" height="{sh}" fill="url(#vig)"/>
    <rect x="{PAD}" y="{PAD}" width="{sw}" height="{sh}" fill="url(#glare)"/>
  </g>
  <rect x="{PAD + .5}" y="{PAD + .5}" width="{sw - 1}" height="{sh - 1}" rx="8" fill="none" stroke="#000" stroke-opacity=".6"/>
</svg>
"""


def buttons():
    for mode, c in BTN.items():
        for name, icon in ICONS.items():
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">'
                   f'<rect x="4.5" y="4.5" width="39" height="39" rx="8" fill="{c["fill"]}" stroke="{c["edge"]}"/>'
                   f'{icon.format(c=c["icon"])}</svg>\n')
            with open(os.path.join(OUT, f"{name}-{mode}.svg"), "w", encoding="utf-8") as fh:
                fh.write(svg)


def main():
    os.makedirs(OUT, exist_ok=True)
    sim = simulate(SEED)
    for mode in THEMES:
        with open(os.path.join(OUT, f"demo-{mode}.svg"), "w", encoding="utf-8") as fh:
            fh.write(render(sim, mode))
    buttons()
    print(f"demo: {len(sim['events'])} events, play {sim['end']:.2f}s, loop {READY + sim['end'] + CLEAR_HOLD:.2f}s")


if __name__ == "__main__":
    main()
