"""The retro profile art: a pixel-art dev room, pixel section icons, a waving avatar, pixel buttons,
a typing intro line and the tech-stack panel. Everything is plain SVG with SMIL animation.

Usage: python3 scripts/retro_art.py   (writes art/retro/*.svg)
"""
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retro_kit import P, Text, FONT, frame, runs_path, sprite_paths  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "art", "retro")
INK = "#1b1325"


def anim_discrete(values, dur, begin=0, attr="opacity"):
    n = len(values)
    times = ";".join(f"{i / n:.4f}" for i in range(n))
    b = f' begin="{-begin:g}s"' if begin else ""
    return (f'<animate attributeName="{attr}" calcMode="discrete" values="{";".join(map(str, values))}" '
            f'keyTimes="{times}" dur="{dur:g}s"{b} repeatCount="indefinite"/>')


class Canvas:
    """A tiny pixel buffer that turns into one merged <path> per colour."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[None] * w for _ in range(h)]

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                self.px[yy][xx] = c

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def sprite(self, x, y, rows, key):
        for ry, row in enumerate(rows):
            for rx, ch in enumerate(row):
                c = key.get(ch)
                if c:
                    self.dot(x + rx, y + ry, c)

    def svg(self):
        by = {}
        for y, row in enumerate(self.px):
            x = 0
            while x < self.w:
                c = row[x]
                if c is None:
                    x += 1
                    continue
                s = x
                while x < self.w and row[x] == c:
                    x += 1
                by.setdefault(c, []).append(f"M{s} {y}h{x - s}v1h-{x - s}z")
        return "".join(f'<path fill="{c}" d="{"".join(d)}"/>' for c, d in by.items())


def layer(rows, key, x=0, y=0):
    """Paths for a small sprite placed at x, y (used for animated overlays)."""
    out = []
    for ch, col in key.items():
        d = runs_path(rows, ch, x, y)
        if d and col:
            out.append(f'<path fill="{col}" d="{d}"/>')
    return "".join(out)


def save(name, svg_text):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write(svg_text)


def wrap(w, h, scale, body, title, desc=""):
    d = f'<desc id="d">{html.escape(desc)}</desc>' if desc else ""
    lab = 't d' if desc else 't'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * scale}" height="{h * scale}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-labelledby="{lab}"><title id="t">{html.escape(title)}</title>{d}'
            f'<g shape-rendering="crispEdges">{body}</g></svg>\n')


# ---------------------------------------------------------------- the hero (same character as the game)
HERO_KEY = {"k": INK, "h": "#2e1f27", "s": "#d58c5d", "R": "#ff004d", "r": "#be1250", "c": "#29adff",
            "C": "#065ab5", "w": "#fff1e8", "j": "#1d2b53", "f": "#fff1e8"}
HEAD = [
    "................",
    "....kkkkkkk.....",
    "...kRRRRRRRk....",
    "..kRhhhhhhhhk...",
    "..kRhhhhhhhhhk..",
    "..krrhhhsssssk..",
    "..krrhhssssksk..",
    "..krrhsssssksk..",
    "...khsssssssk...",
    "....kksssskk....",
]


# ---------------------------------------------------------------- the dev room
def room():
    W, H = 80, 64
    c = Canvas(W, H)
    wall, wall2, base = "#1d2b53", "#22336a", "#151f3d"
    c.rect(0, 0, W, 56, wall)
    for y in range(3, 40, 6):
        for x in range((y // 6) % 2 * 3 + 1, W, 6):
            c.dot(x, y, wall2)
    c.rect(0, 40, W, 16, base)
    c.rect(0, 40, W, 1, "#2a3a70")
    # floor
    c.rect(0, 56, W, 8, "#422136")
    for x in range(0, W, 13):
        c.rect(x, 57, 1, 7, "#2b1a24")
    c.rect(0, 56, W, 1, "#5a2c3e")
    # window with a night city
    c.rect(4, 5, 24, 21, INK)
    c.rect(5, 6, 22, 19, "#5f574f")
    c.rect(6, 7, 20, 17, "#0c1022")
    c.rect(6, 15, 20, 9, "#111d35")
    for x, y in [(8, 9), (12, 12), (18, 8), (9, 15), (23, 13)]:
        c.dot(x, y, "#c2c3c7")
    for dy in range(-3, 4):
        half = int(round((9 - dy * dy) ** 0.5))
        c.rect(21 - half, 10 + dy, half * 2 + 1, 1, "#fff1e8")
    c.dot(20, 9, "#c2c3c7"); c.dot(22, 11, "#c2c3c7")
    for x, h in [(6, 5), (9, 7), (12, 4), (14, 8), (18, 6), (21, 9), (24, 5)]:
        c.rect(x, 24 - h, 3, h, "#0c1022")
    for x, y in [(7, 21), (10, 19), (10, 22), (15, 18), (16, 21), (19, 20), (22, 17), (22, 20), (25, 21)]:
        c.dot(x, y, "#ffec27")
    c.rect(15, 7, 2, 17, "#5f574f")
    c.rect(6, 15, 20, 1, "#5f574f")
    c.rect(3, 25, 26, 2, "#ab5236")
    c.rect(3, 27, 26, 1, "#742f29")
    # a terminal poster
    c.rect(33, 6, 15, 15, "#c2c3c7")
    c.rect(34, 7, 13, 13, "#0c1022")
    c.dot(40, 5, "#ff004d"); c.dot(40, 6, "#ff004d")
    gt = FONT[">"]
    c.sprite(35, 9, gt, {"#": "#00e436"})
    c.rect(41, 15, 4, 1, "#00e436")
    # shelf with books, a floppy and a plant
    c.rect(52, 15, 26, 2, "#ab5236")
    c.rect(52, 17, 26, 1, "#742f29")
    c.rect(54, 18, 1, 2, "#742f29"); c.rect(75, 18, 1, 2, "#742f29")
    for x, h, col in [(53, 8, "#ff004d"), (55, 7, "#29adff"), (57, 9, "#ffec27"), (59, 6, "#00e436"), (61, 8, "#ff77a8")]:
        c.rect(x, 15 - h, 2, h, col)
        c.rect(x, 15 - h, 2, 1, "#fff1e8")
    c.rect(64, 11, 6, 4, "#065ab5"); c.rect(65, 11, 4, 1, "#c2c3c7"); c.rect(65, 13, 4, 2, "#fff1e8")
    c.rect(72, 11, 4, 4, "#ab5236"); c.rect(72, 11, 4, 1, "#d57a4b")
    for x, y in [(73, 8), (74, 7), (72, 9), (75, 9), (74, 10), (73, 10), (71, 8), (76, 8)]:
        c.dot(x, y, "#00e436")
    c.dot(74, 9, "#008751"); c.dot(73, 9, "#008751")
    # desk
    c.rect(30, 43, 50, 2, "#ab5236")
    c.rect(30, 43, 50, 1, "#d57a4b")
    c.rect(31, 45, 48, 11, "#742f29")
    c.rect(31, 45, 48, 1, "#422136")
    c.rect(60, 48, 16, 1, "#422136"); c.rect(67, 50, 3, 1, "#ffa300")
    # monitor (a chunky CRT)
    c.rect(35, 23, 24, 20, INK)
    c.rect(36, 24, 22, 18, "#c2c3c7")
    c.rect(36, 40, 22, 2, "#83769c")
    c.rect(56, 24, 2, 18, "#a7a9b5")
    c.rect(38, 26, 17, 13, INK)
    c.rect(39, 27, 15, 11, "#0c1022")
    c.dot(52, 40, "#00e436")
    c.rect(43, 42, 8, 1, "#83769c")
    # keyboard
    c.rect(37, 43, 19, 2, "#c2c3c7")
    for x in range(38, 55, 2):
        c.dot(x, 43, "#83769c")
    # mug
    c.rect(61, 37, 5, 6, "#fff1e8")
    c.rect(61, 37, 5, 1, "#742f29")
    c.rect(61, 39, 5, 1, "#ff004d")
    c.rect(66, 38, 1, 1, "#fff1e8"); c.rect(67, 39, 1, 2, "#fff1e8"); c.rect(66, 41, 1, 1, "#fff1e8")
    # lamp
    c.rect(70, 41, 6, 2, "#5f574f")
    for i in range(10):
        c.dot(72 - i // 3, 40 - i, "#5f574f")
    c.rect(63, 28, 8, 4, "#ffa300")
    c.rect(63, 28, 8, 1, "#ffec27")
    c.rect(64, 32, 6, 1, "#ab5236")
    # chair
    c.rect(12, 31, 4, 16, "#3a3640")
    c.rect(12, 31, 4, 1, "#5f574f")
    c.rect(14, 46, 17, 2, "#5f574f")
    c.rect(21, 48, 2, 6, "#3a3640")
    c.rect(15, 54, 14, 2, "#3a3640")
    c.dot(15, 56, INK); c.dot(28, 56, INK)
    # the dev, sitting and facing the screen
    c.sprite(15, 28, HEAD, HERO_KEY)
    torso = [
        "...kcccwwccck...",
        "..kccccccccck...",
        "..kCccccccccck..",
        "..kCCCCCCCCCck..",
        "..kjjjjjjjjjjjk.",
        "...kkkkkkkkkkkk.",
    ]
    c.sprite(15, 38, torso, HERO_KEY)
    c.rect(29, 44, 2, 7, "#1d2b53")
    c.rect(28, 51, 4, 2, "#fff1e8")
    base_svg = c.svg()

    # animated bits on top
    # 1. the screen types code, then scrolls
    lines = [
        [(0, 3, "#ff77a8"), (4, 5, "#29adff")],
        [(2, 4, "#fff1e8"), (7, 5, "#00e436")],
        [(2, 6, "#ffec27"), (9, 3, "#fff1e8")],
        [(2, 3, "#ff77a8"), (6, 7, "#00e436")],
        [(0, 2, "#fff1e8")],
        [(0, 4, "#29adff"), (5, 6, "#ffa300")],
    ]
    states = []
    total = sum(len(l) for l in lines)
    for k in range(total + 4):
        segs, n = [], 0
        for li, line in enumerate(lines):
            for (x, w, col) in line:
                if n < k:
                    segs.append(f'<rect x="{40 + x}" y="{28 + li * 2}" width="{w}" height="1" fill="{col}"/>')
                n += 1
        states.append("".join(segs))
    frame_dur = 0.28
    screen = []
    for i, st in enumerate(states):
        vals = [1 if j == i else 0 for j in range(len(states))]
        base = 1 if i == len(states) - 1 else 0
        screen.append(f'<g opacity="{base}">{anim_discrete(vals, frame_dur * len(states))}{st}</g>')
    cursor = (f'<rect x="40" y="38" width="2" height="1" fill="#00e436">'
              f'{anim_discrete([1, 0], 0.8)}</rect>')
    # 2. typing hands
    hands = (f'<g>{anim_discrete([1, 0], 0.36)}<rect x="31" y="41" width="6" height="2" fill="#29adff"/><rect x="37" y="42" width="2" height="1" fill="#d58c5d"/></g>'
             f'<g opacity="0">{anim_discrete([0, 1], 0.36)}<rect x="31" y="41" width="5" height="2" fill="#29adff"/><rect x="36" y="41" width="2" height="2" fill="#d58c5d"/></g>')
    # 3. coffee steam
    steam = ""
    for i, (x, dl) in enumerate([(62, 0), (64, 0.7), (63, 1.4)]):
        steam += (f'<rect x="{x}" y="35" width="1" height="2" fill="#c2c3c7" opacity="0">'
                  f'<animate attributeName="y" values="35;29" dur="2.1s" begin="-{dl}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="0;.9;0" dur="2.1s" begin="-{dl}s" repeatCount="indefinite"/></rect>')
    # 4. twinkling stars
    stars = ""
    for i, (x, y) in enumerate([(8, 9), (12, 12), (18, 8), (23, 13)]):
        stars += f'<rect x="{x}" y="{y}" width="1" height="1" fill="#fff1e8">{anim_discrete([1, 1, 0, 1], 1.6 + i * 0.5, begin=i * 0.4)}</rect>'
    # 5. a cat asleep on the monitor, tail swishing
    cat = Canvas(W, H)
    cat_key = {"k": INK, "o": "#ffa300", "O": "#ab5236", "p": "#ff77a8"}
    cat.sprite(41, 17, [
        "..k...k.......",
        ".kok.kok......",
        ".kooookookk...",
        "kooOoooOoook..",
        "kpoooOooooOok.",
        ".kkkkkkkkkkkk.",
    ], cat_key)
    tail_a = layer(["k.", "ok", "ok", "ok", ".k"], cat_key, 52, 19)
    tail_b = layer(["..k", ".ok", "ok.", "ok.", "k.."], cat_key, 52, 19)
    tail = f'<g>{anim_discrete([1, 0], 1.4)}{tail_a}</g><g opacity="0">{anim_discrete([0, 1], 1.4)}{tail_b}</g>'
    zzz = (f'<g fill="#c2c3c7" opacity="0"><animate attributeName="opacity" values="0;1;0" dur="2.4s" repeatCount="indefinite"/>'
           f'<animateTransform attributeName="transform" type="translate" values="0 0;2 -4" dur="2.4s" repeatCount="indefinite"/>'
           f'<path d="M45 14h3v1h-1v1h-1v1h2v1h-3v-1h1v-1h1v-1h-2z"/></g>')
    # 6. warm lamp light
    light = ('<path d="M64 33L58 43h20L70 33z" fill="#ffec27" opacity=".1">'
             '<animate attributeName="opacity" values=".1;.13;.1" dur="3s" repeatCount="indefinite"/></path>')
    body = base_svg + light + "".join(screen) + cursor + hands + steam + stars + cat.svg() + tail + zzz
    save("room.svg", wrap(W, H, 4, body, "Pixel-art me, coding at night",
                          "A pixel-art developer with red headphones types code on a chunky retro monitor at night; a cat naps on the monitor, coffee steams and the city twinkles outside."))


# ---------------------------------------------------------------- section icons (14x14, drawn at 2x)
def icon_svg(name, rows, key, overlay=""):
    body = sprite_paths(rows, key) + overlay
    return wrap(14, 14, 2, body, name)


def icons():
    k = INK
    sets = {
        "about": ({"k": k, "b": "#c2c3c7", "B": "#83769c", "s": "#0c1022"}, [
            "..............",
            ".kkkkkkkkkkkk.",
            ".kbbbbbbbbbbk.",
            ".kbkkkkkkkkbk.",
            ".kbkssssssbbk.",
            ".kbkssssssbbk.",
            ".kbkssssssbbk.",
            ".kbkssssssbbk.",
            ".kbkssssssbbk.",
            ".kbkkkkkkkkbk.",
            ".kBBBBBBBBBBk.",
            ".kkkkkkkkkkkk.",
            "....kBBBBk....",
            "...kkkkkkkk...",
        ], '<path fill="#00e436" d="M5 5h1v1h-1zM6 6h1v1h-1zM5 7h1v1h-1z"/><rect x="7" y="8" width="2" height="1" fill="#00e436">'
           + anim_discrete([1, 0], 1) + '</rect>'),
        "shipped": ({"k": k, "w": "#fff1e8", "s": "#c2c3c7", "r": "#ff004d", "b": "#29adff"}, [
            "......kk......",
            ".....kwwk.....",
            "....kwwwsk....",
            "....kwbbsk....",
            "....kwbbsk....",
            "....kwwwsk....",
            "....kwwwsk....",
            "...krwwwsrk...",
            "..krrwwwsrrk..",
            "..krkwwwskrk..",
            "..kk.kkkk.kk..",
            "..............",
            "..............",
            "..............",
        ], '<g>' + anim_discrete([1, 0], 0.24) + '<path fill="#ffa300" d="M6 11h2v2h-2z"/><path fill="#ffec27" d="M6 11h2v1h-2z"/></g>'
           '<g opacity="0">' + anim_discrete([0, 1], 0.24) + '<path fill="#ffa300" d="M5 11h4v1h-4zM6 12h2v2h-2z"/><path fill="#ffec27" d="M6 11h2v1h-2z"/></g>'),
        "arcade": ({"k": k, "r": "#ff004d", "w": "#fff1e8", "s": "#5f574f", "b": "#1d2b53", "y": "#ffec27", "g": "#00e436"}, [
            "..............",
            "..............",
            "..............",
            "..............",
            "..............",
            "..............",
            "......kk......",
            "......kk......",
            ".kkkkkkkkkkkk.",
            "kbbbbbbbbbbbbk",
            "kbbbbbbbbykgbk",
            "kbbbbbbbbbbbbk",
            ".kkkkkkkkkkkk.",
            "..............",
        ], '<g><animateTransform attributeName="transform" type="rotate" values="-14 7 8;14 7 8;-14 7 8" dur="1.6s" repeatCount="indefinite"/>'
           '<path fill="#1b1325" d="M6 4h2v5h-2z"/><path fill="#1b1325" d="M5 1h4v1h-4zM4 2h6v3h-6zM5 5h4v1h-4z"/><path fill="#ff004d" d="M5 2h4v3h-4z"/><path fill="#fff1e8" d="M5 2h1v1h-1z"/></g>'),
        "stack": ({"k": k, "r": "#ff004d", "R": "#be1250", "s": "#c2c3c7", "y": "#ffec27"}, [
            "..............",
            "..............",
            ".....kkkk.....",
            "....ks..sk....",
            "....k....k....",
            ".kkkkkkkkkkkk.",
            ".krrrrrrrrrrk.",
            ".krrrryyrrrrk.",
            ".kkkkkkkkkkkk.",
            ".krrrrrrrrrrk.",
            ".kRRRRRRRRRRk.",
            ".kkkkkkkkkkkk.",
            "..............",
            "..............",
        ], ""),
        "projects": ({"k": k, "b": "#065ab5", "B": "#1d2b53", "s": "#c2c3c7", "S": "#5f574f", "w": "#fff1e8", "r": "#ff004d"}, [
            "..............",
            ".kkkkkkkkkkk..",
            ".kbbsssssbbbk.",
            ".kbbsSSssbbbk.",
            ".kbbsSSssbbbk.",
            ".kbbbbbbbbbbk.",
            ".kbwwwwwwwwbk.",
            ".kbwrrrrrrwbk.",
            ".kbwwwwwwwwbk.",
            ".kbwrrrrwwwbk.",
            ".kBwwwwwwwwbk.",
            ".kkkkkkkkkkkk.",
            "..............",
            "..............",
        ], ""),
        "activity": ({"k": k}, ["." * 14] * 14,
                     '<path fill="#1b1325" d="M1 12h12v1h-12z"/>'
                     + "".join(f'<rect x="{x}" y="{12 - h}" width="2" height="{h}" fill="{col}">'
                               f'<animate attributeName="height" values="{h};{h2};{h}" dur="{d}s" repeatCount="indefinite"/>'
                               f'<animate attributeName="y" values="{12 - h};{12 - h2};{12 - h}" dur="{d}s" repeatCount="indefinite"/></rect>'
                               for x, h, h2, col, d in [(2, 4, 6, "#238636", 1.8), (5, 7, 5, "#2ea043", 2.2), (8, 5, 9, "#3fb950", 2.0), (11, 9, 7, "#7ee787", 2.6)])),
        "contact": ({"k": k, "w": "#fff1e8", "s": "#c2c3c7", "r": "#ff004d"}, [
            "..............",
            "..............",
            "..............",
            ".kkkkkkkkkkkk.",
            ".kskwwwwwwksk.",
            ".kwskwwwwkswk.",
            ".kwwskwwkswwk.",
            ".kwwwsrrswwwk.",
            ".kwwwrrrrwwwk.",
            ".kwwwwrrwwwwk.",
            ".kwwwwwwwwwwk.",
            ".kkkkkkkkkkkk.",
            "..............",
            "..............",
        ], ""),
    }
    for name, (key, rows, overlay) in sets.items():
        save(f"icon-{name}.svg", icon_svg(name, rows, key, overlay))


# ---------------------------------------------------------------- the waving avatar for the title
def wave():
    body = sprite_paths(HEAD + ["...kcccwwccck...", "..kccccccccck...", "..kCcccccccCk...", "..kCCCCCCCCk....",
                                "...kjjjkjjjk....", "..kfffk.kfffk..."], HERO_KEY)
    arm_up = '<path fill="#1b1325" d="M12 3h1v1h-1zM14 3h1v1h-1zM12 4h3v1h-3z"/><path fill="#d58c5d" d="M13 3h1v1h-1z"/><path fill="#29adff" d="M12 5h2v5h-2z"/>'
    arm_down = '<path fill="#29adff" d="M12 9h2v3h-2z"/><path fill="#d58c5d" d="M12 12h2v1h-2z"/>'
    over = (f'<g>{anim_discrete([1, 1, 0, 1, 0, 1, 1, 1], 2.4)}{arm_up}</g>'
            f'<g opacity="0">{anim_discrete([0, 0, 1, 0, 1, 0, 0, 0], 2.4)}<path fill="#1b1325" d="M13 2h1v1h-1zM15 2h1v1h-1zM13 3h3v1h-3z"/><path fill="#d58c5d" d="M14 2h1v1h-1z"/><path fill="#29adff" d="M13 4h2v6h-2z"/></g>')
    save("wave.svg", wrap(16, 16, 2, body + over, "Pixel me, waving"))


# ---------------------------------------------------------------- pixel buttons
def button(name, label, icon, accent):
    T = Text("b")
    tw = T.width(label, 2)
    W, H = tw + 46, 30
    body = frame(0, 0, W - 4, H - 4, "#1d2b53", "#000000", shadow="#000000")
    body += f'<rect x="4" y="4" width="18" height="18" fill="{accent}"/>'
    body += icon
    body += T(label, 30, 9, "#fff1e8", 2)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-labelledby="t"><title id="t">{html.escape(label)}</title><defs>{T.defs()}</defs><g shape-rendering="crispEdges">{body}</g></svg>\n')
    save(f"btn-{name}.svg", svg)


def buttons():
    ink = INK
    person = f'<path fill="{ink}" d="M11 7h4v1h1v3h-1v1h-4v-1h-1v-3h1zM9 14h8v1h1v3h-10v-3h1z"/>'
    code = f'<path fill="{ink}" d="M9 9h1v1h-1zM8 10h1v1h-1zM7 11h1v2h-1zM8 13h1v1h-1zM9 14h1v1h-1zM15 8h1v2h-1zM14 10h1v3h-1zM13 13h1v2h-1zM12 15h1v1h-1zM16 9h1v1h-1zM17 10h1v1h-1zM18 11h1v2h-1zM17 13h1v1h-1zM16 14h1v1h-1z"/>'
    play = f'<path fill="{ink}" d="M10 8h1v10h-1zM11 9h1v8h-1zM12 10h1v6h-1zM13 11h1v4h-1zM14 12h1v2h-1z"/>'
    button("linkedin", "LINKEDIN", person, "#29adff")
    button("email", "EMAIL", f'<path fill="{ink}" d="M7 9h12v8h-12z"/><path fill="#fff1e8" d="M8 10h10v6h-10z"/><path fill="{ink}" d="M8 10h1v1h1v1h1v1h1v1h2v-1h1v-1h1v-1h1v-1h1v1h-1v1h-1v1h-1v1h-1v1h-2v-1h-1v-1h-1v-1h-1z"/>', "#ff77a8")
    button("leetcode", "LEETCODE 340+", code, "#ffa300")
    button("play", "PLAY NOW", play, "#00e436")


# ---------------------------------------------------------------- typing intro line
LINES = [
    "> Software Engineer, 2+ years shipping to prod",
    "> serverless, event-driven backends on AWS",
    "> iOS & Android in-app payments, end to end",
    "> RL environments for AI coding agents",
]


def typing(mode):
    color = {"dark": "#7ee787", "light": "#1a7f37"}[mode]
    T = Text("t")
    W, H = 640, 30
    per_char, hold, gap = 0.055, 1.9, 0.25
    spans = []
    t = 0.0
    for line in LINES:
        typed = len(line) * per_char
        spans.append((t, typed, line))
        t += typed + hold + gap
    total = t
    groups = []
    for i, (start, typed, line) in enumerate(spans):
        tw = T.width(line, 2)
        x0 = (W - tw) / 2
        n = len(line)
        # the visible width grows one character at a time
        wv, kt = ["0"], ["0"]
        for k in range(1, n + 1):
            wv.append(f"{k * 12:g}")
            kt.append(f"{(start + k * per_char) / total:.5f}")
        end = start + typed + hold
        wv += [f"{n * 12:g}", "0", "0"]
        kt += [f"{end / total:.5f}", f"{(end + 0.001) / total:.5f}", "1"]
        clip = (f'<clipPath id="c{i}"><rect x="{x0 - 2:g}" y="0" width="{(tw + 4) if i == 0 else 0:g}" height="{H}">'
                f'<animate attributeName="width" calcMode="discrete" values="{";".join(wv)}" keyTimes="{";".join(kt)}" '
                f'dur="{total:.3f}s" repeatCount="indefinite"/></rect></clipPath>')
        cur_x = [f"{x0 + k * 12:g}" for k in range(0, n + 1)]
        cursor = (f'<rect y="7" width="10" height="14" fill="{color}" opacity="0">'
                  f'<animate attributeName="x" calcMode="discrete" values="{";".join([cur_x[0]] + cur_x + [cur_x[-1], cur_x[-1]])}" '
                  f'keyTimes="{";".join(["0"] + [f"{(start + k * per_char) / total:.5f}" for k in range(0, n + 1)] + [f"{end / total:.5f}", "1"])}" '
                  f'dur="{total:.3f}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" calcMode="discrete" values="0;1;0" keyTimes="0;{start / total:.5f};{end / total:.5f}" '
                  f'dur="{total:.3f}s" repeatCount="indefinite"/></rect>')
        groups.append((clip, f'<g clip-path="url(#c{i})">{T(line, x0, 8, color, 2)}</g>{cursor}'))
    defs = T.defs() + "".join(c for c, _ in groups)
    body = "".join(g for _, g in groups)
    alt = " · ".join(l[2:] for l in LINES)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-labelledby="t"><title id="t">{html.escape(alt)}</title><defs>{defs}</defs><g shape-rendering="crispEdges">{body}</g></svg>\n')
    save(f"typing-{mode}.svg", svg)


# ---------------------------------------------------------------- tech stack panel
STACK = [
    ("LANGUAGES", ["TypeScript", "JavaScript", "Python", "C++", "SQL"]),
    ("BACKEND", ["Node.js", "NestJS", "Express", "REST", "GraphQL", "Socket.IO"]),
    ("CLOUD", ["AWS Lambda", "API Gateway", "DynamoDB", "EventBridge", "SQS", "Step Functions", "S3", "Serverless", "GCP Pub/Sub", "Cloudflare"]),
    ("WEB & MOBILE", ["React", "React Native", "Next.js", "Redux", "In-app purchases"]),
    ("DATA & CMS", ["MongoDB", "MySQL", "Prisma", "TypeORM", "Firebase", "Contentful"]),
    ("AI & DEVOPS", ["LangChain", "LLM apps", "RL environments", "Docker", "GitHub Actions", "Jest", "Linux", "Git"]),
]


def stack_svg(W, narrow):
    """The tech stack as pixel chips. Wide: labels on the left. Narrow (phones): each label above its chips."""
    T = Text("s")
    pad, chip_h, gap = (14, 24, 6) if narrow else (22, 24, 8)
    label_w = 0 if narrow else 170
    x_max = W - pad
    rows_svg, y = [], 18 if narrow else 22
    for label, items in STACK:
        rows_svg.append(T(label, pad, y + (2 if narrow else 6), "#7ee787", 2))
        if narrow:
            y += 26
        x = pad + label_w
        line_y = y
        for item in items:
            w = T.width(item, 2) + 20
            if x + w > x_max and x > pad + label_w:
                x = pad + label_w
                line_y += chip_h + gap
            rows_svg.append(
                f'<rect x="{x + 3}" y="{line_y + 3}" width="{w}" height="{chip_h}" fill="#000"/>'
                f'<rect x="{x}" y="{line_y}" width="{w}" height="{chip_h}" fill="#1d2b53"/>'
                f'<rect x="{x}" y="{line_y}" width="{w}" height="2" fill="#2f4380"/>'
                + T(item, x + 10, line_y + 6, "#fff1e8", 2))
            x += w + gap
        y = line_y + chip_h + (16 if narrow else 18)
    H = y + 6
    body = frame(2, 2, W - 10, H - 10, "#0f1629", "#30405f", shadow="#000000") + "".join(rows_svg)
    # a soft shine that sweeps across now and then
    body += (f'<rect x="-120" y="6" width="90" height="{H - 18}" fill="url(#shine)">'
             f'<animate attributeName="x" values="-120;-120;{W};{W}" keyTimes="0;.55;.9;1" dur="7s" repeatCount="indefinite"/></rect>')
    defs = T.defs() + ('<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                       '<stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    alt = "; ".join(f"{label.title()}: {', '.join(items)}" for label, items in STACK)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-labelledby="t"><title id="t">Tech stack. {html.escape(alt)}</title><defs>{defs}</defs><g shape-rendering="crispEdges">{body}</g></svg>\n')


def stack():
    save("stack.svg", stack_svg(860, False))
    save("stack-narrow.svg", stack_svg(360, True))


if __name__ == "__main__":
    room()
    icons()
    wave()
    buttons()
    typing("dark")
    typing("light")
    stack()
    print("wrote", sorted(os.listdir(OUT)))
