"""Profile art: a rotating dotted hologram sphere and a 3D contribution skyline.

Writes hologram-{dark,light}.svg and skyline-{dark,light}.svg into OUT_DIR, plus docs/skyline/data.json
for the interactive 3D skyline page (override the path with SKYLINE_DATA, or set it empty to skip).
Contributions come from the public calendar on the profile page (it includes private contribution
counts when the profile shows them), falling back to the GraphQL API, or from a local JSON file.
Usage: python3 profile_art.py OUT_DIR [calendar.json]
"""
import datetime
import json
import math
import os
import re
import sys
import urllib.request

NL = chr(10)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
EASE_OUT = "cubic-bezier(.61,1,.88,1)"
EASE_IN = "cubic-bezier(.12,0,.39,0)"

THEMES = {
    "dark": dict(dot="#b4c4d8", soft="#8b949e", strong="#e6edf3", text="#8b949e"),
    "light": dict(dot="#3d4b5c", soft="#57606a", strong="#1f2328", text="#57606a"),
}


def fetch_days(user, token):
    query = ("{user(login:" + json.dumps(user) + "){contributionsCollection{contributionCalendar"
             "{totalContributions weeks{contributionDays{date contributionCount}}}}}}")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "bearer " + token, "Content-Type": "application/json", "User-Agent": "profile-art"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]
    return sorted(days), cal["totalContributions"]


def fetch_days_calendar(user):
    """Read the same calendar the profile page shows, including private contribution counts."""
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions",
                                 headers={"User-Agent": "profile-art", "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", "replace")
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
    days = sorted((d, c if c is not None else lvl) for d, c, lvl in cells.values())
    if len(days) < 300:
        raise ValueError(f"calendar parse found only {len(days)} days")
    return days, sum(c for _, c in days)


def hologram(t):
    W, H = 480, 440
    cx, cy, R = 240, 186, 128
    tilt = math.radians(20)
    T = 26.0
    omin = 0.08
    css, dots = [], []
    lats = list(range(-78, 79, 13))
    for k, lat in enumerate(lats):
        phi = math.radians(lat)
        a = R * math.cos(phi)
        b = R * math.cos(phi) * math.sin(tilt)
        y0 = cy - R * math.sin(phi) * math.cos(tilt)
        zc = math.sin(phi) * math.sin(tilt)
        za = math.cos(phi) * math.cos(tilt)

        def op(z):
            return round(omin + (1 - omin) * (z + 1) / 2, 3)

        front, side, back = op(zc + za), op(zc), op(zc - za)
        css.append(
            f"@keyframes x{k}{{0%{{transform:translateX(0);animation-timing-function:{EASE_OUT}}}"
            f"25%{{transform:translateX({a:.1f}px);animation-timing-function:{EASE_IN}}}"
            f"50%{{transform:translateX(0);animation-timing-function:{EASE_OUT}}}"
            f"75%{{transform:translateX({-a:.1f}px);animation-timing-function:{EASE_IN}}}"
            f"100%{{transform:translateX(0)}}}}.x{k}{{animation:x{k} {T}s infinite}}"
        )
        css.append(
            f"@keyframes y{k}{{0%{{transform:translateY({b:.1f}px);opacity:{front};animation-timing-function:{EASE_IN}}}"
            f"25%{{transform:translateY(0);opacity:{side};animation-timing-function:{EASE_OUT}}}"
            f"50%{{transform:translateY({-b:.1f}px);opacity:{back};animation-timing-function:{EASE_IN}}}"
            f"75%{{transform:translateY(0);opacity:{side};animation-timing-function:{EASE_OUT}}}"
            f"100%{{transform:translateY({b:.1f}px);opacity:{front}}}}}.y{k}{{animation:y{k} {T}s infinite}}"
        )
        n = max(6, int(round(2 * math.pi * a / 19)))
        for j in range(n):
            lam = 360.0 * j / n + (k % 2) * 180.0 / n
            th = math.radians(lam)
            delay = -T * lam / 360
            tx, ty = a * math.sin(th), b * math.cos(th)
            o = op(zc + za * math.cos(th))
            dots.append(
                f'<g class="x{k}" style="transform:translateX({tx:.1f}px);animation-delay:{delay:.2f}s">'
                f'<circle class="y{k}" cx="{cx}" cy="{y0:.1f}" r="1.8" '
                f'style="transform:translateY({ty:.1f}px);opacity:{o};animation-delay:{delay:.2f}s"/></g>'
            )

    base_y = cy + R + 74
    particles = []
    for i, (px, dur, dl) in enumerate([(-44, 4.2, 0), (-18, 5.1, -1.3), (6, 3.8, -2.2), (30, 4.7, -0.7),
                                         (52, 5.6, -3.1), (-60, 4.9, -2.8), (18, 3.5, -1.8), (-6, 6.0, -4.0)]):
        particles.append(
            f'<circle class="pt" cx="{cx + px}" cy="{base_y - 6}" r="1.4" fill="{t["dot"]}" '
            f'style="animation-duration:{dur}s;animation-delay:{dl}s"/>'
        )
    css += [
        f".dots circle{{fill:{t['dot']}}}",
        ".orbit{animation:dash 7s linear infinite}.ring{animation:dash 11s linear infinite reverse}",
        "@keyframes dash{to{stroke-dashoffset:-140}}",
        ".scan{animation:scan 5.5s linear infinite}",
        f"@keyframes scan{{from{{transform:translateY(0)}}to{{transform:translateY({2 * R + 40}px)}}}}",
        ".pt{opacity:0;animation:rise 4s ease-in infinite}",
        "@keyframes rise{0%{transform:translateY(0);opacity:0}20%{opacity:.8}100%{transform:translateY(-120px);opacity:0}}",
        ".holo{animation:flick 7s infinite}",
        "@keyframes flick{0%,44%,48%,79%,83%,100%{opacity:1}46%{opacity:.82}81%{opacity:.9}}",
        REDUCED,
    ]
    beam = (f"M{cx - 34} {base_y} L{cx + 34} {base_y} L{cx + R * 0.86:.1f} {cy + R * 0.55:.1f} "
            f"L{cx - R * 0.86:.1f} {cy + R * 0.55:.1f} Z")
    orbit = f"M{cx - R * 1.42:.1f} {cy} a{R * 1.42:.1f} {R * 0.3:.1f} 0 1 0 {R * 2.84:.1f} 0 a{R * 1.42:.1f} {R * 0.3:.1f} 0 1 0 {-R * 2.84:.1f} 0"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="384" viewBox="40 34 400 384" role="img" aria-labelledby="t">
  <title id="t">Rotating dotted hologram sphere</title>
  <style>{NL.join(css)}</style>
  <defs>
    <radialGradient id="rim"><stop offset=".62" stop-color="{t['dot']}" stop-opacity="0"/><stop offset="1" stop-color="{t['dot']}" stop-opacity=".13"/></radialGradient>
    <linearGradient id="beamG" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{t['dot']}" stop-opacity=".16"/><stop offset="1" stop-color="{t['dot']}" stop-opacity="0"/></linearGradient>
    <linearGradient id="scanG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['dot']}" stop-opacity="0"/><stop offset=".5" stop-color="{t['dot']}" stop-opacity=".12"/><stop offset="1" stop-color="{t['dot']}" stop-opacity="0"/></linearGradient>
    <radialGradient id="padG"><stop offset="0" stop-color="{t['dot']}" stop-opacity=".35"/><stop offset="1" stop-color="{t['dot']}" stop-opacity="0"/></radialGradient>
    <clipPath id="ball"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>
  </defs>
  <g class="holo">
    <path d="{beam}" fill="url(#beamG)"/>
    <ellipse cx="{cx}" cy="{base_y}" rx="70" ry="10" fill="url(#padG)"/>
    <ellipse class="ring" cx="{cx}" cy="{base_y}" rx="118" ry="16" fill="none" stroke="{t['soft']}" stroke-opacity=".55" stroke-width="1.2" stroke-dasharray="1.5 6"/>
    <ellipse cx="{cx}" cy="{base_y}" rx="78" ry="10.5" fill="none" stroke="{t['soft']}" stroke-opacity=".35"/>
    <ellipse cx="{cx}" cy="{base_y}" rx="36" ry="5" fill="none" stroke="{t['dot']}" stroke-opacity=".6"/>
    {"".join(particles)}
    <g transform="rotate(-14 {cx} {cy})">
      <path class="orbit" d="{orbit}" fill="none" stroke="{t['soft']}" stroke-opacity=".45" stroke-width="1.2" stroke-dasharray="1.5 7"/>
      <circle r="3" fill="{t['strong']}"><animateMotion dur="9s" repeatCount="indefinite" path="{orbit}"/></circle>
    </g>
    <circle cx="{cx}" cy="{cy}" r="{R + 2}" fill="url(#rim)" stroke="{t['dot']}" stroke-opacity=".16"/>
    <g class="dots">{"".join(dots)}</g>
    <g clip-path="url(#ball)"><rect class="scan" x="{cx - R}" y="{cy - R - 40}" width="{2 * R}" height="34" fill="url(#scanG)"/></g>
  </g>
</svg>
"""


def skyline(days, total, t):
    """The last year as a 3D platform of days with a glowing pin on every active day.

    The floor is drawn top-down, squashed into perspective and swayed with a CSS rotation; every pin
    and label sits in a counter-rotated group, so it stays upright while it rides on the moving floor.
    """
    W, H = 900, 340
    first = datetime.date.fromisoformat(days[0][0])
    offset = (first.weekday() + 1) % 7
    cells = [((i + offset) // 7, (i + offset) % 7, c, ds) for i, (ds, c) in enumerate(days)]
    nweeks = cells[-1][0] + 1
    maxc = max([c for _, _, c, _ in cells] + [1])
    sp = min(13.0, 690.0 / max(nweeks - 1, 1))   # floor spacing between weeks and between weekdays
    squash = 0.42                                 # sine of the camera pitch: how flat the floor looks
    cx, cy = 452, 238                             # middle of the floor on screen
    sway = (-15, 9)                               # degrees the floor swings between
    scan = 9.0                                    # seconds per light sweep along the year

    def fx(w):
        return (w - (nweeks - 1) / 2) * sp

    def fz(d):
        return (d - 3) * sp

    def upright(inner):
        return f'<g class="un"><g transform="scale(1 {1 / squash:.4f})">{inner}</g></g>'

    x_first, x_last = fx(0), fx(nweeks - 1)
    edge = fz(6) + 0.85 * sp
    floor, ticks, labels, pins = [], [], [], []
    last_month = None
    for w in range(nweeks):
        wk = [c for c in cells if c[0] == w]
        if not wk:
            continue
        sunday = datetime.date.fromisoformat(wk[0][3]) - datetime.timedelta(days=wk[0][1])
        if sunday.month != last_month and w < nweeks - 2 and (last_month is not None or sunday.day <= 7):
            ticks.append(f"M{fx(w):.1f} {edge:.1f}v{0.45 * sp:.1f}")
            text = f'<text class="lbl" y="13">{sunday.strftime("%b")}</text>'
            labels.append(f'<g transform="translate({fx(w):.1f} {edge + 0.55 * sp:.1f})">{upright(text)}</g>')
        last_month = sunday.month

    mid = math.radians(sum(sway) / 2)
    order = sorted(cells, key=lambda c: fx(c[0]) * math.sin(mid) + fz(c[1]) * math.cos(mid))
    for w, d, c, ds in order:
        px, pz = fx(w), fz(d)
        if c == 0:
            floor.append(f'<circle cx="{px:.1f}" cy="{pz:.1f}" r="1.8"/>')
            continue
        h = 14 + 112 * (c / maxc) ** 0.55
        grow = w * 0.022 + (6 - d) * 0.01
        flash = scan * (0.10 + 0.50 * (px - x_first) / max(x_last - x_first, 1)) - scan
        pins.append(
            f'<g transform="translate({px:.1f} {pz:.1f})"><title>{c} contribution{"s" if c != 1 else ""} on {ds}</title>'
            f'<circle r="4.4" fill="{t["dot"]}" fill-opacity=".28"/>'
            + upright(
                f'<rect class="bar" x="-1.5" y="{-h:.1f}" width="3" height="{h:.1f}" fill="url(#barG)" style="animation-delay:{grow:.2f}s"/>'
                f'<g class="cap" style="animation-delay:{grow + 0.9:.2f}s"><circle class="glow" cy="{-h:.1f}" r="6.5" fill="{t["dot"]}" style="animation-delay:{flash:.2f}s"/></g>'
                f'<circle class="cap" cy="{-h:.1f}" r="2.4" fill="{t["strong"]}" style="animation-delay:{grow + 0.9:.2f}s"/>'
            )
            + "</g>"
        )

    plate_x, plate_z = x_first - 0.9 * sp, fz(0) - 0.9 * sp
    plate_w, plate_h = x_last - x_first + 1.8 * sp, 6 * sp + 1.8 * sp
    css = [
        f".lbl{{font-family:{MONO};font-size:10.5px;fill:{t['text']};text-anchor:middle}}",
        f".hdr{{font-family:{MONO};font-size:12px;fill:{t['text']}}}",
        f".cta{{font-family:{MONO};font-size:11px;fill:{t['soft']};text-anchor:end;opacity:.8}}",
        f".spin{{animation:yaw 11s ease-in-out infinite alternate}}.un{{animation:unyaw 11s ease-in-out infinite alternate}}",
        f"@keyframes yaw{{from{{transform:rotate({sway[0]}deg)}}to{{transform:rotate({sway[1]}deg)}}}}",
        f"@keyframes unyaw{{from{{transform:rotate({-sway[0]}deg)}}to{{transform:rotate({-sway[1]}deg)}}}}",
        ".bar{transform-box:fill-box;transform-origin:50% 100%;animation:grow 1.3s cubic-bezier(.2,.8,.2,1) both}",
        "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}",
        ".cap{animation:capin .5s ease-out both}@keyframes capin{from{opacity:0}to{opacity:1}}",
        f".glow{{opacity:.16;animation:pulse {scan:g}s linear infinite}}",
        "@keyframes pulse{0%{opacity:.75}7%,100%{opacity:.16}}",
        f".scan{{opacity:0;animation:scan {scan:g}s linear infinite}}",
        f"@keyframes scan{{0%,10%{{transform:translateX({x_first:.1f}px);opacity:0}}13%,57%{{opacity:1}}"
        f"60%,100%{{transform:translateX({x_last:.1f}px);opacity:0}}}}",
        REDUCED,
    ]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
  <title id="t">{total} contributions in the last year, drawn as a slowly turning 3D skyline</title>
  <style>{NL.join(css)}</style>
  <defs>
    <linearGradient id="barG" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{t['dot']}" stop-opacity=".05"/><stop offset="1" stop-color="{t['dot']}" stop-opacity=".95"/></linearGradient>
    <linearGradient id="scanG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['dot']}" stop-opacity="0"/><stop offset=".5" stop-color="{t['dot']}" stop-opacity=".2"/><stop offset="1" stop-color="{t['dot']}" stop-opacity="0"/></linearGradient>
  </defs>
  <text class="hdr" x="46" y="30">{total} contributions in the last year</text>
  <text class="cta" x="{W - 46}" y="30">open in 3D &#8250;</text>
  <g transform="translate({cx} {cy}) scale(1 {squash})">
    <g class="spin">
      <rect x="{plate_x:.1f}" y="{plate_z:.1f}" width="{plate_w:.1f}" height="{plate_h:.1f}" rx="{0.5 * sp:.1f}" fill="{t['dot']}" fill-opacity=".03" stroke="{t['soft']}" stroke-opacity=".22" vector-effect="non-scaling-stroke"/>
      <g fill="{t['soft']}" fill-opacity=".34">{"".join(floor)}</g>
      <path d="{"".join(ticks)}" stroke="{t['soft']}" stroke-opacity=".45" vector-effect="non-scaling-stroke"/>
      <rect class="scan" x="{-1.3 * sp:.1f}" y="{plate_z:.1f}" width="{2.6 * sp:.1f}" height="{plate_h:.1f}" fill="url(#scanG)"/>
      {"".join(pins)}
      {"".join(labels)}
    </g>
  </g>
</svg>
"""


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "dist"
    os.makedirs(out, exist_ok=True)
    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding="utf-8") as fh:
            data = json.load(fh)
        days, total = [(d["date"], d["count"]) for d in data["days"]], data["total"]
    else:
        try:
            days, total = fetch_days_calendar(os.environ["GH_USER"])
        except Exception as exc:  # fall back to GraphQL (public contributions only)
            print("calendar page unavailable, using GraphQL:", exc)
            days, total = fetch_days(os.environ["GH_USER"], os.environ["GITHUB_TOKEN"])
    for mode, theme in THEMES.items():
        for name, svg in (("hologram", hologram(theme)), ("skyline", skyline(days, total, theme))):
            with open(os.path.join(out, f"{name}-{mode}.svg"), "w", encoding="utf-8") as fh:
                fh.write(svg)
    # the interactive 3D page (docs/skyline) reads the same numbers
    data_path = os.environ.get("SKYLINE_DATA", os.path.join(ROOT, "docs", "skyline", "data.json"))
    if data_path:
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        data = {"user": os.environ.get("GH_USER", ""), "updated": days[-1][0], "total": total,
                "start": days[0][0], "counts": [c for _, c in days]}
        with open(data_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, separators=(",", ":"))
            fh.write(NL)
    print("wrote profile art for", len(days), "days,", total, "contributions")


if __name__ == "__main__":
    main()
