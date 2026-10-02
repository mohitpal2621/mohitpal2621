"""Contribution skyline: my GitHub contributions as a slowly turning 3D city of pins, one per active day.

Writes
  art/skyline/last-12-months.svg, last-30-days.svg, last-90-days.svg and one SVG per year,
  docs/skyline/data.json (every day since the account was created, for the interactive 3D page),
  and refreshes the "pick a range" list in README.md between the skyline markers.

The rotation uses SMIL animation, which keeps playing even when a device asks websites to reduce motion.
Usage: python3 scripts/skyline.py [calendar.json]   (GH_USER must be set unless a JSON file is given)
"""
import datetime
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retro_kit import P, Text, frame  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/mohitpal2621/mohitpal2621/main"
PAGE = "https://mohitpal2621.github.io/mohitpal2621/skyline/"
DATA_PATH = os.environ.get("SKYLINE_DATA", os.path.join(ROOT, "docs", "skyline", "data.json"))
LEVELS = ["#1f6f3a", "#238636", "#2ea043", "#3fb950", "#7ee787"]  # one green scale, like GitHub: less -> more
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---------------------------------------------------------------- data
def _get(url, accept="text/html", tries=4):
    """GET with a few retries: github.com sometimes answers 502/504 for a moment."""
    headers = {"User-Agent": "skyline", "Accept": accept}
    if url.startswith("https://api.github.com/") and os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            if (exc.code < 500 and exc.code != 429) or attempt == tries - 1:
                raise
            reason = f"HTTP {exc.code}"
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if attempt == tries - 1:
                raise
            reason = str(exc)
        wait = 5 * 2 ** attempt
        print(f"{url}: {reason}, trying again in {wait}s")
        time.sleep(wait)
    raise RuntimeError("unreachable")


def previous_days(path):
    """Day counts from the last good data.json, used for any year that can't be fetched this time."""
    try:
        with open(path, encoding="utf-8") as fh:
            old = json.load(fh)
        start = datetime.date.fromisoformat(old["start"])
        return {(start + datetime.timedelta(days=i)).isoformat(): c for i, c in enumerate(old["counts"])}
    except (OSError, ValueError, KeyError, TypeError):
        return {}


def parse_calendar(html):
    """Day counts from the contribution calendar HTML (includes private counts when the profile shows them)."""
    cells = {}
    for tag in re.findall(r"<td\b[^>]*>", html):
        date = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        cid = re.search(r'\bid="([^"]+)"', tag)
        level = re.search(r'data-level="(\d)"', tag)
        if date and cid:
            cells[cid.group(1)] = [date.group(1), None, int(level.group(1)) if level else 0]
    for cid, text in re.findall(r'<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        if cid in cells:
            m = re.match(r"\s*(\d+) contributions?", text)
            cells[cid][1] = int(m.group(1)) if m else 0
    return {d: (c if c is not None else lvl) for d, c, lvl in cells.values()}


def fetch_all(user, previous=None):
    """Every day from the start of the account's first year up to today."""
    base = f"https://github.com/users/{user}/contributions"
    latest = parse_calendar(_get(base))
    if len(latest) < 300:
        raise ValueError(f"calendar parse found only {len(latest)} days")
    today = max(latest)
    first_year = int(today[:4]) - 4
    try:
        created = json.loads(_get(f"https://api.github.com/users/{user}", "application/vnd.github+json"))["created_at"]
        first_year = int(created[:4])
    except Exception as exc:  # the API is optional; fall back to a few years back
        print("could not read the account creation date:", exc)
    days = {}
    for year in range(first_year, int(today[:4]) + 1):
        try:
            got = parse_calendar(_get(f"{base}?from={year}-01-01&to={year}-12-31"))
            days.update({d: c for d, c in got.items() if d.startswith(str(year))})
        except Exception as exc:
            print("year", year, "failed:", exc, "- keeping its previous numbers")
            days.update({d: c for d, c in (previous or {}).items() if d.startswith(str(year))})
    days.update(latest)
    return {d: c for d, c in days.items() if d <= today}, today


def series(days, start, end):
    """[(date, count)] for every day in [start, end]."""
    out, d = [], start
    while d <= end:
        k = d.isoformat()
        out.append((k, days.get(k, 0)))
        d += datetime.timedelta(days=1)
    return out


def stats(rows):
    total = sum(c for _, c in rows)
    active = sum(1 for _, c in rows if c)
    best = run = 0
    for _, c in rows:
        run = run + 1 if c else 0
        best = max(best, run)
    top = max(rows, key=lambda r: r[1]) if rows else ("", 0)
    return {"total": total, "active": active, "streak": best, "top": top}


def nice_day(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{MONTHS[d.month - 1]} {d.day}"


# ---------------------------------------------------------------- drawing
def level_of(c, maxc):
    if c <= 0:
        return -1
    return min(4, int(math.ceil(c / maxc * 5)) - 1)


def render(rows, heading, note):
    """One rotating skyline panel for the given days."""
    W, H = 900, 400
    T = Text("g")
    st = stats(rows)
    first = datetime.date.fromisoformat(rows[0][0])
    offset = (first.weekday() + 1) % 7                     # weeks start on Sunday, like GitHub
    cells = [((i + offset) // 7, (i + offset) % 7, c, ds) for i, (ds, c) in enumerate(rows)]
    nweeks = cells[-1][0] + 1
    maxc = max([c for *_, c, _ in cells] + [1])
    small = nweeks <= 16
    sp = min(46.0, 640.0 / max(nweeks - 1, 1))
    sz = sp if small else sp * 1.5          # a deeper floor reads better in 3D for long ranges
    squash = 0.44
    cx, cy = 450, 262 if small else 256
    sway = (-26, 18) if small else (-13, 9)
    dur = 16

    def fx(w):
        return (w - (nweeks - 1) / 2) * sp

    def fz(d):
        return (d - 3) * sz

    spline = '.45 0 .55 1;.45 0 .55 1'

    def turning(inner, sign=1):
        a, b = sway[0] * sign, sway[1] * sign
        return (f'<g><animateTransform attributeName="transform" type="rotate" values="{a};{b};{a}" keyTimes="0;.5;1" '
                f'calcMode="spline" keySplines="{spline}" dur="{dur}s" repeatCount="indefinite"/>{inner}</g>')

    def upright(inner):
        return turning(f'<g transform="scale(1 {1 / squash:.4f})">{inner}</g>', -1)

    tile = max(3.0, min(sp * 0.42, 12.0))
    floor_empty, floor_lit, pins, labels, ticks = [], [], [], [], []
    # month labels on the front edge, at least three weeks apart so they never crowd
    marks, last_month = [], None
    for w in range(nweeks):
        wk = [c for c in cells if c[0] == w]
        if not wk:
            continue
        month = datetime.date.fromisoformat(wk[-1][3]).month
        if month != last_month:
            marks.append((w, month))
        last_month = month
    if len(marks) > 1 and marks[1][0] - marks[0][0] < 3:
        marks = marks[1:]
    kept = []
    for w, m in marks:
        if not kept or w - kept[-1][0] >= 3:
            kept.append((w, m))
    for w, m in kept:
        x, z = fx(w), fz(6) + 0.8 * sz
        ticks.append(f"M{x:.1f} {z - 0.3 * sz:.1f}v{0.3 * sz:.1f}")
        labels.append(f'<g transform="translate({x:.1f} {z:.1f})">{upright(T(MONTHS[m - 1], 0, 2, P["silver"], 2, "middle"))}</g>')

    mid = math.radians(sum(sway) / 2)
    order = sorted(cells, key=lambda c: fx(c[0]) * math.sin(mid) + fz(c[1]) * math.cos(mid))
    grow0 = 0.4
    for w, d, c, ds in order:
        x, z = fx(w), fz(d)
        if c == 0:
            floor_empty.append(f"M{x - 1.5:.1f} {z - 1.5:.1f}h3v3h-3z")
            continue
        lv = level_of(c, maxc)
        col = LEVELS[lv]
        floor_lit.append(f'<rect x="{x - tile / 2:.1f}" y="{z - tile / 2:.1f}" width="{tile:.1f}" height="{tile:.1f}" fill="{col}" fill-opacity=".55"/>')
        h = 12 + (118 if not small else 104) * (c / maxc) ** 0.6
        begin = grow0 + w * (0.03 if not small else 0.12) + (6 - d) * 0.01
        kb = begin / (begin + 0.9)
        grow = f'dur="{begin + 0.9:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;{kb:.3f};1" keySplines="0 0 1 1;.2 .8 .2 1"'
        bar = (f'<rect x="-1.5" y="{-h:.1f}" width="3" height="{h:.1f}" fill="url(#bar{lv})">'
               f'<animate attributeName="height" values="0;0;{h:.1f}" {grow}/>'
               f'<animate attributeName="y" values="0;0;{-h:.1f}" {grow}/></rect>')
        kc = (begin + 0.7) / (begin + 0.9)
        cap = (f'<g><animate attributeName="opacity" values="0;0;1" keyTimes="0;{kc:.3f};1" dur="{begin + 0.9:.2f}s" fill="freeze"/>'
               f'<rect x="-6" y="{-h - 6:.1f}" width="12" height="12" fill="{col}" fill-opacity=".22"/>'
               f'<rect x="-3.5" y="{-h - 3.5:.1f}" width="7" height="7" fill="{col}"/>'
               f'<rect x="-3.5" y="{-h - 3.5:.1f}" width="3" height="2" fill="{P["white"]}" fill-opacity=".85"/></g>')
        tip = f'<title>{c} contribution{"s" if c != 1 else ""} on {nice_day(ds)}, {ds[:4]}</title>'
        pins.append(f'<g transform="translate({x:.1f} {z:.1f})">{tip}{upright(bar + cap)}</g>')

    px0, pz0 = fx(0) - 0.8 * sp, fz(0) - 0.8 * sz
    pw, pd = fx(nweeks - 1) - fx(0) + 1.6 * sp, 6 * sz + 1.6 * sz
    sweep_from, sweep_to = fx(0) - sp, fx(nweeks - 1) + sp
    world = (
        f'<rect x="{px0:.1f}" y="{pz0:.1f}" width="{pw:.1f}" height="{pd:.1f}" fill="#16213d" stroke="#3d4f75" stroke-opacity=".9" stroke-width="2" vector-effect="non-scaling-stroke"/>'
        f'<path d="{"".join(floor_empty)}" fill="#5a6b8f" fill-opacity=".5"/>'
        + "".join(floor_lit)
        + f'<path d="{"".join(ticks)}" stroke="{P["silver"]}" stroke-opacity=".6" stroke-width="2" vector-effect="non-scaling-stroke"/>'
        f'<clipPath id="floor"><rect x="{px0:.1f}" y="{pz0:.1f}" width="{pw:.1f}" height="{pd:.1f}"/></clipPath>'
        f'<g clip-path="url(#floor)"><rect x="{-1.2 * sp:.1f}" y="{pz0:.1f}" width="{2.4 * sp:.1f}" height="{pd:.1f}" fill="url(#sweep)" opacity="0">'
        f'<animateTransform attributeName="transform" type="translate" values="{sweep_from:.1f} 0;{sweep_from:.1f} 0;{sweep_to:.1f} 0;{sweep_to:.1f} 0" keyTimes="0;.1;.6;1" dur="9s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.1;.14;.56;.6;1" dur="9s" repeatCount="indefinite"/></rect></g>'
        + "".join(pins) + "".join(labels)
    )
    # header, stats and legend
    num = f"{st['total']:,}"
    hx = 30
    head = T(num, hx, 22, "#7ee787", 3)
    head += T(f"contribution{'s' if st['total'] != 1 else ''} {heading}", hx + T.width(num, 3) + 14, 29, P["white"], 2)
    bits = [f"{st['active']} active day{'s' if st['active'] != 1 else ''}",
            f"best streak {st['streak']} day{'s' if st['streak'] != 1 else ''}"]
    if st["top"][1]:
        bits.append(f"busiest {nice_day(st['top'][0])} ({st['top'][1]})")
    head += T("  ·  ".join(bits), hx, 58, P["silver"], 2)
    lx = W - 30 - (T.width("less", 2) + 5 * 16 + T.width("more", 2) + 20)
    legend = T("less", lx, H - 34, P["silver"], 2)
    for i, col in enumerate(LEVELS):
        legend += f'<rect x="{lx + T.width("less", 2) + 10 + i * 16}" y="{H - 35}" width="12" height="12" fill="{col}"/>'
    legend += T("more", lx + T.width("less", 2) + 10 + 5 * 16 + 4, H - 34, P["silver"], 2)
    hint = T(note, 30, H - 34, "#8b949e", 2)
    defs = (T.defs()
            + "".join(f'<linearGradient id="bar{i}" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{c}" stop-opacity=".15"/>'
                      f'<stop offset="1" stop-color="{c}"/></linearGradient>' for i, c in enumerate(LEVELS))
            + f'<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{P["white"]}" stop-opacity="0"/>'
              f'<stop offset=".5" stop-color="{P["white"]}" stop-opacity=".16"/><stop offset="1" stop-color="{P["white"]}" stop-opacity="0"/></linearGradient>')
    body = (frame(2, 2, W - 10, H - 10, "#0f1629", "#30405f", shadow=P["black"])
            + head
            + f'<g transform="translate({cx} {cy}) scale(1 {squash})">{turning(world)}</g>'
            + legend + hint)
    title = f"{st['total']} contributions {heading}"
    desc = (f"A slowly turning 3D skyline of my GitHub contributions {heading}: {st['active']} active days, "
            f"best streak {st['streak']} days.")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-labelledby="t d"><title id="t">{title}</title><desc id="d">{desc}</desc><defs>{defs}</defs>'
            f'<g shape-rendering="crispEdges">{body}</g></svg>\n'), st


# ---------------------------------------------------------------- outputs
def ranges(days, today_iso):
    today = datetime.date.fromisoformat(today_iso)
    out = [
        ("last-12-months", "in the last 12 months", series(days, today - datetime.timedelta(days=364), today)),
        ("last-30-days", "in the last 30 days", series(days, today - datetime.timedelta(days=29), today)),
        ("last-90-days", "in the last 90 days", series(days, today - datetime.timedelta(days=89), today)),
    ]
    years = sorted({int(d[:4]) for d in days})
    for y in reversed(years):
        start, end = datetime.date(y, 1, 1), min(datetime.date(y, 12, 31), today)
        rows = series(days, start, end)
        if y < today.year and not any(c for _, c in rows):
            continue
        label = f"in {y}" if y < today.year else f"in {y} so far"
        out.append((str(y), label, rows))
    return out


def readme_block(made):
    labels = {"last-30-days": "Last 30 days", "last-90-days": "Last 90 days"}
    lines = ["<!-- skyline:start -->", '<p align="center">',
             f'  <a href="{PAGE}" title="Open it in 3D: rotate, zoom and pick any dates"><img src="{RAW}/art/skyline/last-12-months.svg" '
             f'alt="{made[0][2]["total"]} contributions in the last 12 months as a slowly turning 3D skyline: one green pin per active day, taller and brighter on busier days" width="100%" /></a>',
             "</p>", "",
             f'<p align="center"><sub>One pin per day I contributed, taller and brighter means busier · refreshed every 6 hours · '
             f'<a href="{PAGE}"><b>open in 3D</b></a> to rotate it yourself or pick any dates</sub></p>', "",
             "**See another range** (click one to open it):", ""]
    for key, heading, st in made[1:]:
        name = labels.get(key, key + (" so far" if "so far" in heading else ""))
        lines += [f'<details name="skyline-range">',
                  f'<summary><b>📅 {name}</b> · {st["total"]:,} contribution{"s" if st["total"] != 1 else ""}</summary>',
                  '<br />', '<p align="center">',
                  f'  <img src="{RAW}/art/skyline/{key}.svg" alt="{st["total"]} contributions {heading} as a 3D skyline" width="100%" />',
                  "</p>", "</details>", ""]
    lines.append("<!-- skyline:end -->")
    return "\n".join(lines)


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as fh:
            data = json.load(fh)
        days = {d["date"]: d["count"] for d in data["days"]} if "days" in data else {
            (datetime.date.fromisoformat(data["start"]) + datetime.timedelta(days=i)).isoformat(): c
            for i, c in enumerate(data["counts"])}
        today = max(days)
    else:
        days, today = fetch_all(os.environ["GH_USER"], previous_days(DATA_PATH))
    out_dir = os.path.join(ROOT, "art", "skyline")
    os.makedirs(out_dir, exist_ok=True)
    made = []
    for key, heading, rows in ranges(days, today):
        note = "click to rotate it yourself" if key == "last-12-months" else "open in 3D for any dates"
        svg, st = render(rows, heading, note)
        with open(os.path.join(out_dir, f"{key}.svg"), "w", encoding="utf-8") as fh:
            fh.write(svg)
        made.append((key, heading, st))
        print(f"{key}: {st['total']} contributions, {st['active']} active days")
    # data for the interactive page
    start = min(days)
    span = (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(start)).days + 1
    counts = [days.get((datetime.date.fromisoformat(start) + datetime.timedelta(days=i)).isoformat(), 0) for i in range(span)]
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as fh:
        json.dump({"user": os.environ.get("GH_USER", "mohitpal2621"), "updated": today, "start": start,
                   "total": sum(counts), "counts": counts}, fh, separators=(",", ":"))
        fh.write("\n")
    # keep the README range list current
    readme = os.environ.get("README", os.path.join(ROOT, "README.md"))
    if os.path.exists(readme):
        text = open(readme, encoding="utf-8").read()
        new, n = re.subn(r"<!-- skyline:start -->.*?<!-- skyline:end -->", lambda m: readme_block(made), text, flags=re.S)
        if n and new != text:
            with open(readme, "w", encoding="utf-8") as fh:
                fh.write(new)
            print("README range list updated")


if __name__ == "__main__":
    main()
