"""The pixel art for the profile README: a title banner, section title bars, panels for About, experience,
the arcade, the tech stack, side projects and contact, plus pixel buttons.

Every panel with text also comes in a phone-sized version (*-narrow.svg) that the README swaps in on small
screens, so the pixel text never shrinks to an unreadable size.

The look is calm on purpose: one dark navy panel style, cream text, green labels, soft yellow only for a few
key numbers, short lines, and slow, faint animation.

Usage: python3 scripts/retro_art.py   (writes art/pixel/*.svg)
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retro_kit import FONT, Text, frame, runs_path, sprite_paths  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "art", "pixel")

# ---------------------------------------------------------------- palette (kept small and soft)
INK = "#1b1325"
PANEL, EDGE = "#0f1629", "#30405f"
CREAM, MUTED = "#fff1e8", "#9aa3c7"
GREEN, YELLOW = "#7ee787", "#f3ef7d"
NAVY, NAVY_HI = "#1d2b53", "#2f4380"
WIDE, NARROW = 860, 360


# ---------------------------------------------------------------- content (edit the words here)
HERO_TITLE = "HEY, I'M MOHIT"
HERO_ROLE = "FULL-STACK SOFTWARE DEVELOPER"
HERO_LINES = [
    "> building AI chat apps with 20M+ visits a month",
    "> serverless, event-driven backends on AWS",
    "> LLM endpoints, LangChain agents, vector search",
    "> in-app payments on iOS and Android",
    "> 2+ years shipping to production",
]
HERO_LINES_NARROW = [
    "> AI chat apps, 20M+/month",
    "> serverless on AWS",
    "> LLMs, LangChain, agents",
    "> iOS & Android payments",
    "> 2+ years in production",
]

ABOUT_TEXT = ("I build AI chat apps with **20M+** visits a month and **600K+** installs, end to end: "
              "serverless backends on AWS, LLM endpoints, in-app payments and the web and mobile apps on top.")
ABOUT_FACTS = [
    ("NOW", "Software Developer at 4 Way Technologies"),
    ("BUILDING", "SpicyChat AI · PixelChat AI · ChatReal AI"),
    ("STUDIED", "B.Tech CSE, MAIT Delhi (2024) · CGPA 8.7"),
    ("BASED IN", "Gurgaon, India"),
]

JOB = {
    "company": "4 WAY TECHNOLOGIES",
    "when": "AUG 2024 - NOW",
    "role": "Software Developer · Delhi, India",
    "blocks": [
        {"name": "SPICYCHAT AI & PIXELCHAT AI", "sub": "AI character chat platforms, built for NextDay AI",
         "badges": ["20M+ VISITS/MO", "600K+ INSTALLS"],
         "bullets": [
             "Backend and frontend, end to end, on web, iOS and Android",
             "Serverless microservices on AWS Lambda, API Gateway and DynamoDB",
             "Event-driven jobs on EventBridge, SQS and Step Functions",
             "Content moderation and payments features for SpicyChat",
             "Localization in 9 languages, cached on Cloudflare's CDN",
             "Premium content via Contentful + GraphQL, no app release",
         ],
         "short": [
             "Full-stack on web, iOS and Android",
             "Serverless on AWS Lambda and DynamoDB",
             "Async jobs on SQS and Step Functions",
             "Moderation and payments features",
             "Localization in 9 languages",
         ]},
        {"name": "CHATREAL AI", "sub": "In-house AI companion app with 3D characters",
         "badges": ["IOS + ANDROID"],
         "bullets": [
             "In-app purchases and subscriptions, verified server-side",
             "Real-time renewals and cancellations via Google Cloud Pub/Sub",
             "NestJS APIs with rate limits on chat and LLM endpoints",
         ],
         "short": [
             "In-app subscriptions, verified server-side",
             "Real-time renewals via GCP Pub/Sub",
             "Rate-limited chat and LLM APIs",
         ]},
    ],
    "footer": "Private client code, but happy to walk you through the design.",
}

ARCADE_TITLE = "PUSH TO PROD"
ARCADE_TEXT = ("A tiny Mario-style platformer I built from scratch. Stomp bugs, grab coffee and carry "
               "your code from localhost to production.")
ARCADE_NOTE = "Canvas and Web Audio, no libraries. A bot plays every level to prove it can be beaten. Works on phones too."

STACK = [
    ("LANGUAGES", ["TypeScript", "JavaScript", "Python", "SQL", "C++"]),
    ("BACKEND", ["Node.js", "NestJS", "Express", "REST", "GraphQL", "Socket.IO", "Microservices"]),
    ("AI & LLM", ["LLM integration", "LangChain", "Agent workflows", "ChromaDB"]),
    ("CLOUD", ["AWS Lambda", "API Gateway", "DynamoDB", "S3", "SQS", "EventBridge", "Step Functions",
               "CloudWatch", "Serverless", "GCP Pub/Sub", "Cloudflare"]),
    ("WEB & MOBILE", ["React", "React Native", "Next.js", "In-app purchases"]),
    ("DATA & CMS", ["PostgreSQL", "MySQL", "MongoDB", "ClickHouse", "Databricks", "Contentful"]),
    ("DEVOPS", ["Docker", "GitHub Actions", "Jest", "Postman", "Git"]),
]

PROJECTS = [
    ("chat-pulse", "CHAT-PULSE", "chat", "Real-time chat with JWT auth, group chats and read receipts",
     ["React", "Chakra UI", "Node.js", "Express", "Socket.IO", "MongoDB"]),
    ("car-pricing-api", "CAR PRICING API", "car", "NestJS API that prices used cars from approved sale reports",
     ["NestJS", "TypeScript", "TypeORM", "SQLite", "Jest"]),
    ("blogpulse", "BLOGPULSE", "page", "Markdown blog on Next.js with static generation and an API",
     ["Next.js", "React", "MongoDB", "Markdown"]),
    ("expensify", "EXPENSIFY", "coin", "Expense manager with Google sign-in and Firebase sync",
     ["React", "Redux", "Firebase", "Jest", "Webpack"]),
]

CONTACT_TEXT = "Always happy to talk about AI chat backends, serverless on AWS and in-app payments."
CONTACT_NOTE = "mohitpal2621@gmail.com · Gurgaon, India"

SECTIONS = [  # anchor, title, icon
    ("about", "ABOUT ME", "about"),
    ("experience", "WHAT I'VE SHIPPED", "shipped"),
    ("arcade", "ARCADE", "arcade"),
    ("stack", "TECH STACK", "stack"),
    ("projects", "SIDE PROJECTS", "projects"),
    ("activity", "ACTIVITY", "activity"),
    ("contact", "LET'S CONNECT", "contact"),
]
NAV = [("about", "ABOUT"), ("experience", "EXPERIENCE"), ("arcade", "ARCADE"), ("stack", "STACK"),
       ("projects", "PROJECTS"), ("activity", "ACTIVITY"), ("contact", "CONTACT")]


# ---------------------------------------------------------------- small helpers
def save(name, svg_text):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write(svg_text)


def check_text(*strings):
    missing = {c for s in strings for c in s if c != " " and c not in FONT}
    if missing:
        raise ValueError(f"the pixel font has no glyph for {sorted(missing)}")


def doc(W, H, body, defs, title, desc=""):
    d = f'<desc id="d">{html.escape(desc)}</desc>' if desc else ""
    lab = "t d" if desc else "t"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-labelledby="{lab}"><title id="t">{html.escape(title)}</title>{d}<defs>{defs}</defs>'
            f'<g shape-rendering="crispEdges">{body}</g></svg>\n')


def panel(W, H):
    return frame(2, 2, W - 10, H - 10, PANEL, EDGE, shadow="#000000")


SHINE = ('<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
         '<stop offset=".5" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')


def shine(W, H, dur=10):
    """A faint light that glides across a panel every few seconds."""
    return (f'<rect x="-120" y="6" width="90" height="{H - 18}" fill="url(#shine)">'
            f'<animate attributeName="x" values="-120;-120;{W};{W}" keyTimes="0;.62;.9;1" dur="{dur}s" repeatCount="indefinite"/></rect>')


def anim_discrete(values, dur, begin=0, attr="opacity"):
    n = len(values)
    times = ";".join(f"{i / n:.4f}" for i in range(n))
    b = f' begin="{-begin:g}s"' if begin else ""
    return (f'<animate attributeName="{attr}" calcMode="discrete" values="{";".join(map(str, values))}" '
            f'keyTimes="{times}" dur="{dur:g}s"{b} repeatCount="indefinite"/>')


# ---------------------------------------------------------------- rich text: "plain **highlight** plain", wrapped
def segments(text):
    out = []
    for i, part in enumerate(re.split(r"\*\*", text)):
        for tok in re.split(r"( )", part):
            if tok:
                out.append((tok, i % 2 == 1))
    return out


def wrap(text, width):
    lines, cur, n = [], [], 0
    for tok, hl in segments(text):
        if tok == " ":
            if cur:
                cur.append((tok, hl))
                n += 1
            continue
        if n + len(tok) > width and cur:
            while cur and cur[-1][0] == " ":
                cur.pop()
            lines.append(cur)
            cur, n = [], 0
        cur.append((tok, hl))
        n += len(tok)
    while cur and cur[-1][0] == " ":
        cur.pop()
    if cur:
        lines.append(cur)
    return lines


def draw_segs(T, segs, x, y, base, hl, scale=2, anchor="start"):
    n = sum(len(t) for t, _ in segs)
    if anchor == "middle":
        x -= T.width("x" * n, scale) / 2
    elif anchor == "end":
        x -= T.width("x" * n, scale)
    runs = []
    for tok, h in segs:
        if runs and runs[-1][1] == h:
            runs[-1][0] += tok
        else:
            runs.append([tok, h])
    out, pos = [], 0
    for s, h in runs:
        if s.strip():
            out.append(T(s, x + pos * 6 * scale, y, hl if h else base, scale))
        pos += len(s)
    return "".join(out)


def paragraph(T, text, x, y, width, base=CREAM, hl=YELLOW, scale=2, lh=26, anchor="start"):
    check_text(text.replace("**", ""))
    lines = wrap(text, width)
    body = "".join(draw_segs(T, segs, x, y + i * lh, base, hl, scale, anchor) for i, segs in enumerate(lines))
    return body, y + len(lines) * lh


def chip(T, label, x, y, color=CREAM, h=24):
    w = T.width(label, 2) + 20
    return (f'<rect x="{x + 3}" y="{y + 3}" width="{w}" height="{h}" fill="#000"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{NAVY}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="2" fill="{NAVY_HI}"/>'
            + T(label, x + 10, y + (h - 14) // 2 + 1, color, 2)), w


def chip_width(T, label):
    return T.width(label, 2) + 20


def chips(T, items, x, y, x_max, color=CREAM, gap=8, row_gap=6, h=24):
    out, cx, cy = [], x, y
    for it in items:
        w = chip_width(T, it)
        if cx + w > x_max and cx > x:
            cx, cy = x, cy + h + row_gap
        s, _ = chip(T, it, cx, cy, color, h)
        out.append(s)
        cx += w + gap
    return "".join(out), cy + h


# ---------------------------------------------------------------- pixel canvas for the little scenes
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
    out = []
    for ch, col in key.items():
        d = runs_path(rows, ch, x, y)
        if d and col:
            out.append(f'<path fill="{col}" d="{d}"/>')
    return "".join(out)


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
BODY = ["...kcccwwccck...", "..kccccccccck...", "..kCcccccccCk...", "..kCCCCCCCCk....",
        "...kjjjkjjjk....", "..kfffk.kfffk..."]
ARM_UP = '<path fill="#1b1325" d="M12 3h1v1h-1zM14 3h1v1h-1zM12 4h3v1h-3z"/><path fill="#d58c5d" d="M13 3h1v1h-1z"/><path fill="#29adff" d="M12 5h2v5h-2z"/>'
ARM_WAVE = '<path fill="#1b1325" d="M13 2h1v1h-1zM15 2h1v1h-1zM13 3h3v1h-3z"/><path fill="#d58c5d" d="M14 2h1v1h-1z"/><path fill="#29adff" d="M13 4h2v6h-2z"/>'

BLOCK = [
    ".kkkkkkkkkkkkkk.",
    "kyyyyyyyyyyyyyyk",
    "kyoyyyyyyyyyyoYk",
    "kyyyyyyyyyyyyyYk",
    "kyyyykkyyykkyyYk",
    "kyyykyyyyyyykyYk",
    "kyyykyyyyyyykyYk",
    "kyykyyyyyyyyykYk",
    "kyyykyyyyyyykyYk",
    "kyyykyyyyyyykyYk",
    "kyyyykkyyykkyyYk",
    "kyyyyyyyyyyyyyYk",
    "kyyyyyyyyyyyyyYk",
    "kyoyyyyyyyyyyoYk",
    "kYYYYYYYYYYYYYYk",
    ".kkkkkkkkkkkkkk.",
]
BLOCK_KEY = {"k": INK, "y": "#ffec27", "Y": "#ffa300", "o": "#fff1e8"}
COIN = [
    "..kkkk..",
    ".kywwyk.",
    "kywyyyYk",
    "kyyyoyYk",
    "kyyyoyYk",
    "kyyyoyYk",
    "kyyooyYk",
    ".kyyyYk.",
    "..kkkk..",
]
COIN_KEY = {"k": INK, "y": "#ffec27", "Y": "#ffa300", "o": "#ab5236", "w": "#fff1e8"}
GROUND = [
    "gggggggggggggggg",
    "gGgggggGgggggGgg",
    "GdGgGdGGgGGdGgGd",
    "dddGdddddGdddddd",
    "dddddddddddddddd",
    "ddDddddddddDdddd",
    "dddddddddddddddd",
    "ddddddDdddddddDd",
]
GROUND_KEY = {"g": "#00e436", "G": "#008751", "d": "#ab5236", "D": "#742f29"}


def scene(scale):
    """The game's hero waving under a floating code block that pops a coin now and then."""
    W, H = 40, 40
    c = Canvas(W, H)
    for x0 in range(0, W, 16):
        c.sprite(x0, 32, GROUND, GROUND_KEY)
    c.sprite(4, 16, HEAD + BODY, HERO_KEY)
    base = c.svg()
    # the arm waves twice, then rests
    arm = (f'<g>{anim_discrete([1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1], 6)}<g transform="translate(4 16)">{ARM_UP}</g></g>'
           f'<g opacity="0">{anim_discrete([0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0], 6)}<g transform="translate(4 16)">{ARM_WAVE}</g></g>')
    block = (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -2;0 0;0 0" '
             f'keyTimes="0;.5;.53;.58;1" dur="6s" repeatCount="indefinite"/>{layer(BLOCK, BLOCK_KEY, 22, 6)}</g>')
    coin = (f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.5;.51;.62;.68;1" dur="6s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -9;0 -9" keyTimes="0;.5;.64;1" dur="6s" repeatCount="indefinite"/>'
            f'{layer(COIN, COIN_KEY, 26, -2)}</g>')
    return W * scale, H * scale, f'<g transform="scale({scale})">{base}{arm}{block}{coin}</g>'


def typing(T, lines, x, y, color, cursor_color, W, anchor="start", idp="c"):
    """Lines typed one after another, each held for a moment; the first one shows when nothing animates."""
    per_char, hold, gap = 0.06, 2.2, 0.3
    spans, t = [], 0.0
    for line in lines:
        typed = len(line) * per_char
        spans.append((t, typed, line))
        t += typed + hold + gap
    total = t
    defs, body = [], []
    for i, (start, typed, line) in enumerate(spans):
        tw = T.width(line, 2)
        x0 = x - tw / 2 if anchor == "middle" else x
        n = len(line)
        wv, kt = ["0"], ["0"]
        for k in range(1, n + 1):
            wv.append(f"{k * 12:g}")
            kt.append(f"{(start + k * per_char) / total:.5f}")
        end = start + typed + hold
        wv += [f"{n * 12:g}", "0", "0"]
        kt += [f"{end / total:.5f}", f"{(end + 0.001) / total:.5f}", "1"]
        defs.append(f'<clipPath id="{idp}{i}"><rect x="{x0 - 2:g}" y="{y - 4}" width="{(tw + 4) if i == 0 else 0:g}" height="26">'
                    f'<animate attributeName="width" calcMode="discrete" values="{";".join(wv)}" keyTimes="{";".join(kt)}" '
                    f'dur="{total:.3f}s" repeatCount="indefinite"/></rect></clipPath>')
        cur_x = [f"{x0 + k * 12:g}" for k in range(0, n + 1)]
        cursor = (f'<rect y="{y - 1}" width="10" height="16" fill="{cursor_color}" opacity="0">'
                  f'<animate attributeName="x" calcMode="discrete" values="{";".join([cur_x[0]] + cur_x + [cur_x[-1], cur_x[-1]])}" '
                  f'keyTimes="{";".join(["0"] + [f"{(start + k * per_char) / total:.5f}" for k in range(0, n + 1)] + [f"{end / total:.5f}", "1"])}" '
                  f'dur="{total:.3f}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" calcMode="discrete" values="0;1;0" keyTimes="0;{start / total:.5f};{end / total:.5f}" '
                  f'dur="{total:.3f}s" repeatCount="indefinite"/></rect>')
        prompt = T(line[:1], x0, y, cursor_color, 2)
        rest = T(line[1:], x0 + 12, y, color, 2)
        body.append(f'<g clip-path="url(#{idp}{i})">{prompt}{rest}</g>{cursor}')
    return "".join(defs), "".join(body)


def stars(W, H, n, seed, area_h):
    """A few faint pixel stars; some twinkle slowly."""
    import random
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.randrange(14, W - 18), rnd.randrange(12, area_h)
        size = 2 if rnd.random() < 0.8 else 4
        op = rnd.choice([".25", ".35", ".5"])
        tw = anim_discrete([1, 1, 0, 1], round(2.5 + rnd.random() * 3, 1), begin=round(rnd.random() * 3, 1)) if i % 3 == 0 else ""
        out.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{CREAM}" opacity="{op}">{tw}</rect>')
    return "".join(out)


# ---------------------------------------------------------------- title banner
def hero(narrow):
    T = Text("g")
    check_text(HERO_TITLE, HERO_ROLE, *HERO_LINES, *HERO_LINES_NARROW)
    if not narrow:
        W = WIDE
        sw, sh, sc = scene(4)
        H = sh + 36
        body = panel(W, H) + stars(W, H, 22, 7, H - 40)
        body += f'<g transform="translate(30 14)">{sc}</g>'
        x = 30 + sw + 34
        body += T(HERO_TITLE, x, 38 + 4, "#000000", 4) + T(HERO_TITLE, x, 38, CREAM, 4)
        body += T(HERO_ROLE, x, 92, GREEN, 2)
        tdefs, tbody = typing(T, HERO_LINES, x, 130, CREAM, GREEN, W)
        body += tbody + shine(W, H, 11)
    else:
        W = NARROW
        sw, sh, sc = scene(3)
        cx = W // 2 - 2
        y = 14
        body = ""
        body += f'<g transform="translate({cx - sw // 2} {y})">{sc}</g>'
        y += sh + 18
        body += T(HERO_TITLE, cx, y + 3, "#000000", 3, "middle") + T(HERO_TITLE, cx, y, CREAM, 3, "middle")
        y += 21 + 18
        for part in ("FULL-STACK SOFTWARE", "DEVELOPER"):
            body += T(part, cx, y, GREEN, 2, "middle")
            y += 24
        y += 12
        tdefs, tbody = typing(T, HERO_LINES_NARROW, cx, y, CREAM, GREEN, W, anchor="middle")
        y += 24 + 18
        H = y
        body = panel(W, H) + stars(W, H, 12, 9, 120) + body + tbody + shine(W, H, 11)
    alt = f"Hey, I'm Mohit. {HERO_ROLE.title()}. " + " · ".join(l[2:] for l in HERO_LINES)
    return doc(W, H, body, T.defs() + SHINE + tdefs, alt)


# ---------------------------------------------------------------- section icons (14x14)
def icon_parts():
    k = INK
    return {
        "about": ({"k": k, "b": "#c2c3c7", "B": "#83769c", "s": "#0c1022"}, [
            "..............", ".kkkkkkkkkkkk.", ".kbbbbbbbbbbk.", ".kbkkkkkkkkbk.", ".kbkssssssbbk.",
            ".kbkssssssbbk.", ".kbkssssssbbk.", ".kbkssssssbbk.", ".kbkssssssbbk.", ".kbkkkkkkkkbk.",
            ".kBBBBBBBBBBk.", ".kkkkkkkkkkkk.", "....kBBBBk....", "...kkkkkkkk..."],
            '<path fill="#00e436" d="M5 5h1v1h-1zM6 6h1v1h-1zM5 7h1v1h-1z"/><rect x="7" y="8" width="2" height="1" fill="#00e436">'
            + anim_discrete([1, 0], 1.2) + '</rect>'),
        "shipped": ({"k": k, "w": "#fff1e8", "s": "#c2c3c7", "r": "#ff004d", "b": "#29adff"}, [
            "......kk......", ".....kwwk.....", "....kwwwsk....", "....kwbbsk....", "....kwbbsk....",
            "....kwwwsk....", "....kwwwsk....", "...krwwwsrk...", "..krrwwwsrrk..", "..krkwwwskrk..",
            "..kk.kkkk.kk..", "..............", "..............", ".............."],
            '<g>' + anim_discrete([1, 0], 0.3) + '<path fill="#ffa300" d="M6 11h2v2h-2z"/><path fill="#ffec27" d="M6 11h2v1h-2z"/></g>'
            '<g opacity="0">' + anim_discrete([0, 1], 0.3) + '<path fill="#ffa300" d="M5 11h4v1h-4zM6 12h2v2h-2z"/><path fill="#ffec27" d="M6 11h2v1h-2z"/></g>'),
        "arcade": ({"k": k, "b": "#1d2b53", "y": "#ffec27", "g": "#00e436"}, [
            "..............", "..............", "..............", "..............", "..............",
            "..............", "......kk......", "......kk......", ".kkkkkkkkkkkk.", "kbbbbbbbbbbbbk",
            "kbbbbbbbbykgbk", "kbbbbbbbbbbbbk", ".kkkkkkkkkkkk.", ".............."],
            '<g><animateTransform attributeName="transform" type="rotate" values="-12 7 8;12 7 8;-12 7 8" dur="2.4s" repeatCount="indefinite"/>'
            '<path fill="#1b1325" d="M6 4h2v5h-2z"/><path fill="#1b1325" d="M5 1h4v1h-4zM4 2h6v3h-6zM5 5h4v1h-4z"/><path fill="#ff004d" d="M5 2h4v3h-4z"/><path fill="#fff1e8" d="M5 2h1v1h-1z"/></g>'),
        "stack": ({"k": k, "r": "#ff004d", "R": "#be1250", "s": "#c2c3c7", "y": "#ffec27"}, [
            "..............", "..............", ".....kkkk.....", "....ks..sk....", "....k....k....",
            ".kkkkkkkkkkkk.", ".krrrrrrrrrrk.", ".krrrryyrrrrk.", ".kkkkkkkkkkkk.", ".krrrrrrrrrrk.",
            ".kRRRRRRRRRRk.", ".kkkkkkkkkkkk.", "..............", ".............."], ""),
        "projects": ({"k": k, "b": "#065ab5", "B": "#1d2b53", "s": "#c2c3c7", "S": "#5f574f", "w": "#fff1e8", "r": "#ff004d"}, [
            "..............", ".kkkkkkkkkkk..", ".kbbsssssbbbk.", ".kbbsSSssbbbk.", ".kbbsSSssbbbk.",
            ".kbbbbbbbbbbk.", ".kbwwwwwwwwbk.", ".kbwrrrrrrwbk.", ".kbwwwwwwwwbk.", ".kbwrrrrwwwbk.",
            ".kBwwwwwwwwbk.", ".kkkkkkkkkkkk.", "..............", ".............."], ""),
        "activity": ({"k": k}, ["." * 14] * 14,
                     '<path fill="#1b1325" d="M1 12h12v1h-12z"/>'
                     + "".join(f'<rect x="{x}" y="{12 - h}" width="2" height="{h}" fill="{col}">'
                               f'<animate attributeName="height" values="{h};{h2};{h}" dur="{d}s" repeatCount="indefinite"/>'
                               f'<animate attributeName="y" values="{12 - h};{12 - h2};{12 - h}" dur="{d}s" repeatCount="indefinite"/></rect>'
                               for x, h, h2, col, d in [(2, 4, 6, "#238636", 2.4), (5, 7, 5, "#2ea043", 2.8),
                                                        (8, 5, 9, "#3fb950", 2.6), (11, 9, 7, "#7ee787", 3.2)])),
        "contact": ({"k": k, "w": "#fff1e8", "s": "#c2c3c7", "r": "#ff004d"}, [
            "..............", "..............", "..............", ".kkkkkkkkkkkk.", ".kskwwwwwwksk.",
            ".kwskwwwwkswk.", ".kwwskwwkswwk.", ".kwwwsrrswwwk.", ".kwwwrrrrwwwk.", ".kwwwwrrwwwwk.",
            ".kwwwwwwwwwwk.", ".kkkkkkkkkkkk.", "..............", ".............."], ""),
        # project icons
        "chat": ({"k": k, "w": "#fff1e8", "b": "#29adff", "B": "#065ab5"}, [
            "..............", ".kkkkkkkkkkk..", "kbbbbbbbbbbbk.", "kbwwbwwwbwwbk.", "kbbbbbbbbbbbk.",
            "kbwwwwbwwwbbk.", "kbbbbbbbbbbbk.", ".kkkBkkkkkkk..", "...kBk........", "...kk.........",
            "..............", "..............", "..............", ".............."], ""),
        "car": ({"k": k, "r": "#ff004d", "R": "#be1250", "w": "#c2e6ff", "s": "#5f574f", "y": "#ffec27"}, [
            "..............", "..............", "..............", "....kkkkk.....", "...krwwwrk....",
            "..krrwwwrrk...", ".krrrrrrrrrrk.", ".kyrrrrrrrrRk.", ".kRRRRRRRRRRk.", "..kssk..kssk..",
            "...kk....kk...", "..............", "..............", ".............."], ""),
        "page": ({"k": k, "w": "#fff1e8", "s": "#c2c3c7", "g": "#00e436", "G": "#008751"}, [
            "..............", "..kkkkkkkk....", "..kwwwwwwkk...", "..kwggggwwsk..", "..kwwwwwwwwk..",
            "..kwssssswwk..", "..kwwwwwwwwk..", "..kwsssssswk..", "..kwwwwwwwwk..", "..kwssssswwk..",
            "..kwwwwwwwwk..", "..kkkkkkkkkk..", "..............", ".............."], ""),
        "coin": ({"k": k, "y": "#ffec27", "Y": "#ffa300", "o": "#ab5236"}, [
            "..............", "....kkkkk.....", "...kyyyyyk....", "..kyyoooyyk...", "..kyyoyyyYk...",
            "..kyyoooyYk...", "..kyyyyoyYk...", "..kyyoooyYk...", "...kyyyyYk....", "....kkkkk.....",
            "..............", "..............", "..............", ".............."], ""),
    }


ICONS = icon_parts()


def icon(name, x, y, scale=2):
    key, rows, overlay = ICONS[name]
    return f'<g transform="translate({x} {y}) scale({scale})">{sprite_paths(rows, key)}{overlay}</g>'


# ---------------------------------------------------------------- section title bars
def title_bar(n, title, icon_name, narrow):
    T = Text("g")
    check_text(title)
    W = NARROW if narrow else WIDE
    scale = 2 if narrow else 3
    th = 7 * scale
    tab_h = 40 if not narrow else 34
    tab_w = 12 + 28 + 12 + T.width(title, scale) + 16
    body = frame(0, 0, tab_w, tab_h, NAVY, "#000000", shadow="#000000")
    body += f'<rect x="2" y="2" width="{tab_w - 4}" height="2" fill="{NAVY_HI}"/>'
    body += icon(icon_name, 12, (tab_h - 28) // 2)
    body += T(title, 52, (tab_h - th) // 2 + 1, CREAM, scale)
    num = f"{n:02d}"
    nw = T.width(num, 2) + 16
    nx = W - nw - 6
    rule_y = tab_h // 2 - 1
    if nx - (tab_w + 14) > 20:
        body += f'<rect x="{tab_w + 14}" y="{rule_y}" width="{nx - tab_w - 26}" height="2" fill="{EDGE}"/>'
    body += frame(nx, rule_y - 12, nw, 26, NAVY, "#000000", shadow="#000000")
    body += T(num, nx + 8, rule_y - 6, GREEN, 2)
    H = tab_h + 6
    return doc(W, H, body, T.defs(), title.title())


# ---------------------------------------------------------------- nav and buttons
def nav_button(label):
    T = Text("g")
    check_text(label)
    w = T.width(label, 2) + 24
    H = 30
    body = frame(0, 0, w, 26, NAVY, "#000000", shadow="#000000")
    body += f'<rect x="2" y="2" width="{w - 4}" height="2" fill="{NAVY_HI}"/>'
    body += T(label, 12, 7, CREAM, 2)
    return doc(w + 4, H, body, T.defs(), label.title())


def button(label, icon_svg, accent, glyph=None):
    T = Text("g")
    check_text(label, glyph or "")
    tw = T.width(label, 2)
    W, H = tw + 46, 30
    body = frame(0, 0, W - 4, H - 4, NAVY, "#000000", shadow="#000000")
    body += f'<rect x="4" y="4" width="18" height="18" fill="{accent}"/>'
    body += icon_svg or ""
    if glyph:
        body += T(glyph, 8, 6, INK, 2)
    body += T(label, 30, 9, CREAM, 2)
    return doc(W, H, body, T.defs(), label.title())


def buttons():
    ink = INK
    person = f'<path fill="{ink}" d="M11 7h4v1h1v3h-1v1h-4v-1h-1v-3h1zM9 14h8v1h1v3h-10v-3h1z"/>'
    code = f'<path fill="{ink}" d="M9 9h1v1h-1zM8 10h1v1h-1zM7 11h1v2h-1zM8 13h1v1h-1zM9 14h1v1h-1zM15 8h1v2h-1zM14 10h1v3h-1zM13 13h1v2h-1zM12 15h1v1h-1zM16 9h1v1h-1zM17 10h1v1h-1zM18 11h1v2h-1zM17 13h1v1h-1zM16 14h1v1h-1z"/>'
    play = f'<path fill="{ink}" d="M10 8h1v10h-1zM11 9h1v8h-1zM12 10h1v6h-1zM13 11h1v4h-1zM14 12h1v2h-1z"/>'
    mail = (f'<path fill="{ink}" d="M7 9h12v8h-12z"/><path fill="#fff1e8" d="M8 10h10v6h-10z"/>'
            f'<path fill="{ink}" d="M8 10h1v1h1v1h1v1h1v1h2v-1h1v-1h1v-1h1v-1h1v1h-1v1h-1v1h-1v1h-1v1h-2v-1h-1v-1h-1v-1h-1z"/>')
    save("btn-linkedin.svg", button("LINKEDIN", person, "#29adff"))
    save("btn-email.svg", button("EMAIL", mail, "#ff77a8"))
    save("btn-leetcode.svg", button("LEETCODE 340+", code, "#ffa300"))
    save("btn-play.svg", button("PLAY NOW", play, "#00e436"))
    save("btn-more.svg", button("MORE PROJECTS ON GITHUB", None, GREEN, "▶"))
    save("btn-3d.svg", button("OPEN IN 3D · PICK ANY DATES", None, GREEN, "▶"))
    save("btn-top.svg", button("BACK TO TOP", None, GREEN, "▲"))


# ---------------------------------------------------------------- the dev room (embedded in About)
def room_body():
    W, H = 80, 64
    c = Canvas(W, H)
    wall, wall2, base = "#1d2b53", "#22336a", "#151f3d"
    c.rect(0, 0, W, 56, wall)
    for y in range(3, 40, 6):
        for x in range((y // 6) % 2 * 3 + 1, W, 6):
            c.dot(x, y, wall2)
    c.rect(0, 40, W, 16, base)
    c.rect(0, 40, W, 1, "#2a3a70")
    c.rect(0, 56, W, 8, "#422136")
    for x in range(0, W, 13):
        c.rect(x, 57, 1, 7, "#2b1a24")
    c.rect(0, 56, W, 1, "#5a2c3e")
    c.rect(4, 5, 24, 21, INK)
    c.rect(5, 6, 22, 19, "#5f574f")
    c.rect(6, 7, 20, 17, "#0c1022")
    c.rect(6, 15, 20, 9, "#111d35")
    for x, y in [(8, 9), (12, 12), (18, 8), (9, 15), (23, 13)]:
        c.dot(x, y, "#c2c3c7")
    for dy in range(-3, 4):
        half = int(round((9 - dy * dy) ** 0.5))
        c.rect(21 - half, 10 + dy, half * 2 + 1, 1, "#fff1e8")
    c.dot(20, 9, "#c2c3c7")
    c.dot(22, 11, "#c2c3c7")
    for x, h in [(6, 5), (9, 7), (12, 4), (14, 8), (18, 6), (21, 9), (24, 5)]:
        c.rect(x, 24 - h, 3, h, "#0c1022")
    for x, y in [(7, 21), (10, 19), (10, 22), (15, 18), (16, 21), (19, 20), (22, 17), (22, 20), (25, 21)]:
        c.dot(x, y, "#ffec27")
    c.rect(15, 7, 2, 17, "#5f574f")
    c.rect(6, 15, 20, 1, "#5f574f")
    c.rect(3, 25, 26, 2, "#ab5236")
    c.rect(3, 27, 26, 1, "#742f29")
    c.rect(33, 6, 15, 15, "#c2c3c7")
    c.rect(34, 7, 13, 13, "#0c1022")
    c.dot(40, 5, "#ff004d")
    c.dot(40, 6, "#ff004d")
    c.sprite(35, 9, FONT[">"], {"#": "#00e436"})
    c.rect(41, 15, 4, 1, "#00e436")
    c.rect(52, 15, 26, 2, "#ab5236")
    c.rect(52, 17, 26, 1, "#742f29")
    c.rect(54, 18, 1, 2, "#742f29")
    c.rect(75, 18, 1, 2, "#742f29")
    for x, h, col in [(53, 8, "#ff004d"), (55, 7, "#29adff"), (57, 9, "#ffec27"), (59, 6, "#00e436"), (61, 8, "#ff77a8")]:
        c.rect(x, 15 - h, 2, h, col)
        c.rect(x, 15 - h, 2, 1, "#fff1e8")
    c.rect(64, 11, 6, 4, "#065ab5")
    c.rect(65, 11, 4, 1, "#c2c3c7")
    c.rect(65, 13, 4, 2, "#fff1e8")
    c.rect(72, 11, 4, 4, "#ab5236")
    c.rect(72, 11, 4, 1, "#d57a4b")
    for x, y in [(73, 8), (74, 7), (72, 9), (75, 9), (74, 10), (73, 10), (71, 8), (76, 8)]:
        c.dot(x, y, "#00e436")
    c.dot(74, 9, "#008751")
    c.dot(73, 9, "#008751")
    c.rect(30, 43, 50, 2, "#ab5236")
    c.rect(30, 43, 50, 1, "#d57a4b")
    c.rect(31, 45, 48, 11, "#742f29")
    c.rect(31, 45, 48, 1, "#422136")
    c.rect(60, 48, 16, 1, "#422136")
    c.rect(67, 50, 3, 1, "#ffa300")
    c.rect(35, 23, 24, 20, INK)
    c.rect(36, 24, 22, 18, "#c2c3c7")
    c.rect(36, 40, 22, 2, "#83769c")
    c.rect(56, 24, 2, 18, "#a7a9b5")
    c.rect(38, 26, 17, 13, INK)
    c.rect(39, 27, 15, 11, "#0c1022")
    c.dot(52, 40, "#00e436")
    c.rect(43, 42, 8, 1, "#83769c")
    c.rect(37, 43, 19, 2, "#c2c3c7")
    for x in range(38, 55, 2):
        c.dot(x, 43, "#83769c")
    c.rect(61, 37, 5, 6, "#fff1e8")
    c.rect(61, 37, 5, 1, "#742f29")
    c.rect(61, 39, 5, 1, "#ff004d")
    c.rect(66, 38, 1, 1, "#fff1e8")
    c.rect(67, 39, 1, 2, "#fff1e8")
    c.rect(66, 41, 1, 1, "#fff1e8")
    c.rect(70, 41, 6, 2, "#5f574f")
    for i in range(10):
        c.dot(72 - i // 3, 40 - i, "#5f574f")
    c.rect(63, 28, 8, 4, "#ffa300")
    c.rect(63, 28, 8, 1, "#ffec27")
    c.rect(64, 32, 6, 1, "#ab5236")
    c.rect(12, 31, 4, 16, "#3a3640")
    c.rect(12, 31, 4, 1, "#5f574f")
    c.rect(14, 46, 17, 2, "#5f574f")
    c.rect(21, 48, 2, 6, "#3a3640")
    c.rect(15, 54, 14, 2, "#3a3640")
    c.dot(15, 56, INK)
    c.dot(28, 56, INK)
    c.sprite(15, 28, HEAD, HERO_KEY)
    torso = ["...kcccwwccck...", "..kccccccccck...", "..kCccccccccck..", "..kCCCCCCCCCck..",
             "..kjjjjjjjjjjjk.", "...kkkkkkkkkkkk."]
    c.sprite(15, 38, torso, HERO_KEY)
    c.rect(29, 44, 2, 7, "#1d2b53")
    c.rect(28, 51, 4, 2, "#fff1e8")
    base_svg = c.svg()
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
    frame_dur = 0.32
    screen = []
    for i, st in enumerate(states):
        vals = [1 if j == i else 0 for j in range(len(states))]
        base = 1 if i == len(states) - 1 else 0
        screen.append(f'<g opacity="{base}">{anim_discrete(vals, frame_dur * len(states))}{st}</g>')
    cursor = f'<rect x="40" y="38" width="2" height="1" fill="#00e436">{anim_discrete([1, 0], 1)}</rect>'
    hands = (f'<g>{anim_discrete([1, 0], 0.4)}<rect x="31" y="41" width="6" height="2" fill="#29adff"/><rect x="37" y="42" width="2" height="1" fill="#d58c5d"/></g>'
             f'<g opacity="0">{anim_discrete([0, 1], 0.4)}<rect x="31" y="41" width="5" height="2" fill="#29adff"/><rect x="36" y="41" width="2" height="2" fill="#d58c5d"/></g>')
    steam = ""
    for x, dl in [(62, 0), (64, 0.8), (63, 1.6)]:
        steam += (f'<rect x="{x}" y="35" width="1" height="2" fill="#c2c3c7" opacity="0">'
                  f'<animate attributeName="y" values="35;29" dur="2.4s" begin="-{dl}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="0;.8;0" dur="2.4s" begin="-{dl}s" repeatCount="indefinite"/></rect>')
    twinkle = ""
    for i, (x, y) in enumerate([(8, 9), (12, 12), (18, 8), (23, 13)]):
        twinkle += f'<rect x="{x}" y="{y}" width="1" height="1" fill="#fff1e8">{anim_discrete([1, 1, 0, 1], 2 + i * 0.6, begin=i * 0.5)}</rect>'
    cat = Canvas(W, H)
    cat_key = {"k": INK, "o": "#ffa300", "O": "#ab5236", "p": "#ff77a8"}
    cat.sprite(41, 17, ["..k...k.......", ".kok.kok......", ".kooookookk...", "kooOoooOoook..",
                        "kpoooOooooOok.", ".kkkkkkkkkkkk."], cat_key)
    tail_a = layer(["k.", "ok", "ok", "ok", ".k"], cat_key, 52, 19)
    tail_b = layer(["..k", ".ok", "ok.", "ok.", "k.."], cat_key, 52, 19)
    tail = f'<g>{anim_discrete([1, 0], 1.6)}{tail_a}</g><g opacity="0">{anim_discrete([0, 1], 1.6)}{tail_b}</g>'
    zzz = (f'<g fill="#c2c3c7" opacity="0"><animate attributeName="opacity" values="0;1;0" dur="2.8s" repeatCount="indefinite"/>'
           f'<animateTransform attributeName="transform" type="translate" values="0 0;2 -4" dur="2.8s" repeatCount="indefinite"/>'
           f'<path d="M45 14h3v1h-1v1h-1v1h2v1h-3v-1h1v-1h1v-1h-2z"/></g>')
    light = ('<path d="M64 33L58 43h20L70 33z" fill="#ffec27" opacity=".1">'
             '<animate attributeName="opacity" values=".1;.13;.1" dur="3s" repeatCount="indefinite"/></path>')
    return base_svg + light + "".join(screen) + cursor + hands + steam + twinkle + cat.svg() + tail + zzz


# ---------------------------------------------------------------- About
def facts(T, x, y, label_w, width_chars, narrow):
    out = ""
    for label, value in ABOUT_FACTS:
        check_text(label, value)
        if narrow:
            out += T(label, x, y, GREEN, 2)
            y += 24
            b, y = paragraph(T, value, x, y, width_chars, CREAM, YELLOW, lh=24)
            out += b
            y += 10
        else:
            out += T(label, x, y, GREEN, 2) + T(value, x + label_w, y, CREAM, 2)
            y += 30
    return out, y


def about(narrow):
    T = Text("g")
    if not narrow:
        W = WIDE
        body = f'<g transform="translate(26 26) scale(4)">{room_body()}</g>'
        x = 26 + 320 + 30
        body += T("> whoami", x, 30, GREEN, 2)
        b, _ = paragraph(T, ABOUT_TEXT, x, 68, (WIDE - 34 - x) // 12, CREAM, YELLOW)
        body += b
        f, y = facts(T, 30, 26 + 256 + 30, 132, 0, False)
        body += f
        H = y + 10
    else:
        W = NARROW
        body = f'<g transform="translate(18 18) scale(4)">{room_body()}</g>'
        y = 18 + 256 + 24
        body += T("> whoami", 20, y, GREEN, 2)
        b, y = paragraph(T, ABOUT_TEXT, 20, y + 36, 26, CREAM, YELLOW, lh=24)
        body += b
        f, y = facts(T, 20, y + 18, 0, 26, True)
        body += f
        H = y + 10
    alt = ("About me. Full-stack software developer. " + ABOUT_TEXT.replace("**", "") + " "
           + " ".join(f"{l.title()}: {v}." for l, v in ABOUT_FACTS))
    return doc(W, H, panel(W, H) + body + shine(W, H, 12), T.defs() + SHINE, alt,
               "Pixel art: me coding at night on a chunky retro monitor while a cat naps on top of it.")


# ---------------------------------------------------------------- experience
def experience(narrow):
    T = Text("g")
    W = NARROW if narrow else WIDE
    x0, x1 = (20, W - 30) if narrow else (30, W - 36)
    width = (x1 - x0) // 12
    y = 26
    body = ""
    if not narrow:
        body += T(JOB["company"], x0, y, CREAM, 3)
        body += T(JOB["when"], x1, y + 4, GREEN, 2, "end")
        y += 21 + 16
        body += T(JOB["role"], x0, y, MUTED, 2)
        y += 30
    else:
        body += T("4 WAY", x0, y, CREAM, 3) + T("TECHNOLOGIES", x0, y + 30, CREAM, 3)
        y += 30 + 21 + 14
        body += T(JOB["when"], x0, y, GREEN, 2)
        y += 24
        b, y = paragraph(T, JOB["role"], x0, y, width, MUTED, MUTED, lh=24)
        body += b
        y += 6
    for blk in JOB["blocks"]:
        check_text(blk["name"], blk["sub"], *blk["badges"], *blk["bullets"])
        body += f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="2" fill="{EDGE}"/>'
        y += 20
        if not narrow:
            bw = sum(chip_width(T, b) for b in blk["badges"]) + 8 * (len(blk["badges"]) - 1)
            cx = x1 - bw
            for b in blk["badges"]:
                s, w = chip(T, b, cx, y - 4, YELLOW)
                body += s
                cx += w + 8
            body += T(blk["name"], x0, y + 1, GREEN, 2)
            y += 32
            b, y = paragraph(T, blk["sub"], x0, y, width, MUTED, MUTED)
        else:
            b, y = paragraph(T, blk["name"], x0, y, width, GREEN, GREEN, lh=24)
            body += b
            s, y = chips(T, blk["badges"], x0, y + 4, x1, YELLOW)
            body += s
            y += 14
            b, y = paragraph(T, blk["sub"], x0, y, width, MUTED, MUTED, lh=24)
        body += b
        y += 8
        for item in (blk["short"] if narrow else blk["bullets"]):
            body += T("•", x0 + 4, y, GREEN, 2)
            b, y = paragraph(T, item, x0 + 28, y, width - 2, CREAM, YELLOW, lh=24 if narrow else 26)
            body += b
            y += 4 if narrow else 2
        y += 12
    body += f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="2" fill="{EDGE}"/>'
    y += 20
    b, y = paragraph(T, JOB["footer"], x0, y, width, MUTED, MUTED, lh=24)
    body += b
    H = y + 14
    alt = (f"What I've shipped. Software Developer at 4 Way Technologies, Delhi, Aug 2024 to now. "
           + " ".join(f"{blk['name'].title()} ({', '.join(blk['badges'])}): {blk['sub']}. " + " ".join(i + "." for i in blk["bullets"])
                      for blk in JOB["blocks"]) + " " + JOB["footer"])
    return doc(W, H, panel(W, H) + body + shine(W, H, 13), T.defs() + SHINE, alt)


# ---------------------------------------------------------------- arcade blurb
def arcade_info(narrow):
    T = Text("g")
    check_text(ARCADE_TITLE)
    W = NARROW if narrow else WIDE
    x0, x1 = (20, W - 30) if narrow else (30, W - 36)
    width = (x1 - x0) // 12
    y = 26
    body = T(ARCADE_TITLE, x0, y, YELLOW, 3)
    y += 21 + 18
    b, y = paragraph(T, ARCADE_TEXT, x0, y, width, CREAM, YELLOW, lh=24 if narrow else 26)
    body += b
    y += 8
    b, y = paragraph(T, ARCADE_NOTE, x0, y, width, MUTED, MUTED, lh=24)
    body += b
    H = y + 14
    alt = f"{ARCADE_TITLE}: {ARCADE_TEXT} {ARCADE_NOTE}"
    return doc(W, H, panel(W, H) + body + shine(W, H, 14), T.defs() + SHINE, alt)


# ---------------------------------------------------------------- tech stack
def stack_svg(narrow):
    T = Text("s")
    W = NARROW if narrow else WIDE
    pad, chip_h, gap = (14, 24, 6) if narrow else (22, 24, 8)
    label_w = 0 if narrow else 170
    x_max = W - pad
    rows_svg, y = [], 18 if narrow else 22
    for label, items in STACK:
        check_text(label, *items)
        rows_svg.append(T(label, pad, y + (2 if narrow else 6), GREEN, 2))
        if narrow:
            y += 26
        x = pad + label_w
        line_y = y
        for item in items:
            w = chip_width(T, item)
            if x + w > x_max and x > pad + label_w:
                x = pad + label_w
                line_y += chip_h + gap
            s, _ = chip(T, item, x, line_y)
            rows_svg.append(s)
            x += w + gap
        y = line_y + chip_h + (16 if narrow else 18)
    H = y + 6
    body = panel(W, H) + "".join(rows_svg) + shine(W, H, 10)
    alt = "; ".join(f"{label.title()}: {', '.join(items)}" for label, items in STACK)
    return doc(W, H, body, T.defs() + SHINE, f"Tech stack. {alt}")


# ---------------------------------------------------------------- project cards
def project(name, title, icon_name, desc, tech, narrow):
    T = Text("g")
    check_text(title, desc, *tech)
    W = NARROW if narrow else WIDE
    x0, x1 = (20, W - 30) if narrow else (30, W - 36)
    width = (x1 - x0) // 12
    body = icon(icon_name, x0 - 2, 20)
    tscale = 3 if (not narrow or T.width(title, 3) <= x1 - x0 - 40) else 2
    body += T(title, x0 + 40, 24 if tscale == 3 else 27, CREAM, tscale)
    if not narrow:
        body += T("VIEW CODE ▶", x1, 28, GREEN, 2, "end")
        b, y = paragraph(T, desc, x0 + 40, 62, width - 3, MUTED, MUTED)
        body += b
        s, y = chips(T, tech, x0 + 40, y + 6, x1)
    else:
        b, y = paragraph(T, desc, x0, 62, width, MUTED, MUTED, lh=24)
        body += b
        s, y = chips(T, tech, x0, y + 8, x1)
        body += T("VIEW CODE ▶", x1, y + 16, GREEN, 2, "end")
        y += 16 + 14
    body += s
    H = y + 22
    alt = f"{title.title()}: {desc}. Built with {', '.join(tech)}. Opens the code on GitHub."
    return doc(W, H, panel(W, H) + body, T.defs(), alt)


# ---------------------------------------------------------------- contact
def contact(narrow):
    T = Text("g")
    W = NARROW if narrow else WIDE
    x0, x1 = (20, W - 30) if narrow else (30, W - 36)
    width = (x1 - x0) // 12
    b, y = paragraph(T, CONTACT_TEXT, x0, 26, width, CREAM, YELLOW, lh=24 if narrow else 26)
    body = b
    y += 6
    b, y = paragraph(T, CONTACT_NOTE, x0, y, width, GREEN, GREEN, lh=24)
    body += b
    H = y + 14
    return doc(W, H, panel(W, H) + body, T.defs(), f"{CONTACT_TEXT} {CONTACT_NOTE}")


# ---------------------------------------------------------------- everything
def main():
    for narrow in (False, True):
        sfx = "-narrow" if narrow else ""
        save(f"hero{sfx}.svg", hero(narrow))
        save(f"about{sfx}.svg", about(narrow))
        save(f"experience{sfx}.svg", experience(narrow))
        save(f"arcade{sfx}.svg", arcade_info(narrow))
        save(f"stack{sfx}.svg", stack_svg(narrow))
        save(f"contact{sfx}.svg", contact(narrow))
        for n, (key, title, ic) in enumerate(SECTIONS, 1):
            save(f"title-{key}{sfx}.svg", title_bar(n, title, ic, narrow))
        for name, title, ic, desc, tech in PROJECTS:
            save(f"project-{name}{sfx}.svg", project(name, title, ic, desc, tech, narrow))
    for key, label in NAV:
        save(f"nav-{key}.svg", nav_button(label))
    buttons()
    print("wrote", len(os.listdir(OUT)), "files to", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
