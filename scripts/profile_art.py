"""Profile art: a rotating dotted hologram sphere and a 3D contribution skyline.

Writes hologram-{dark,light}.svg and skyline-{dark,light}.svg into OUT_DIR.
Contributions come from the GitHub GraphQL API (GITHUB_TOKEN, GH_USER) or a local JSON file.
Usage: python3 profile_art.py OUT_DIR [calendar.json]
"""
import datetime
import json
import math
import os
import sys
import urllib.request

NL = chr(10)
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
    W, H = 900, 300
    first = datetime.date.fromisoformat(days[0][0])
    offset = (first.weekday() + 1) % 7
    cells = []
    for i, (ds, c) in enumerate(days):
        idx = i + offset
        cells.append((idx // 7, idx % 7, c, ds))
    nweeks = cells[-1][0] + 1
    maxc = max([c for _, _, c, _ in cells] + [1])
    ew = (min(14.4, 760.0 / nweeks), 0.9)
    ed = (6.6, -6.4)
    x0, y0 = 46, 222

    def pos(w, d):
        return x0 + w * ew[0] + (6 - d) * ed[0], y0 + w * ew[1] + (6 - d) * ed[1]

    floor, bars, labels = [], [], []
    sweep = 3.2
    last_month = None
    for w in range(nweeks):
        wk = [c for c in cells if c[0] == w]
        if wk:
            sunday = datetime.date.fromisoformat(wk[0][3]) - datetime.timedelta(days=wk[0][1])
            if sunday.month != last_month and w < nweeks - 2 and (last_month is not None or sunday.day <= 7):
                lx, ly = pos(w, 6)
                labels.append(f'<text class="lbl" x="{lx:.1f}" y="{ly + 20:.1f}">{sunday.strftime("%b")}</text>')
            last_month = sunday.month
    for d in range(7):
        for w, dd, c, ds in cells:
            if dd != d:
                continue
            px, py = pos(w, d)
            if c == 0:
                floor.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.3" fill="{t["soft"]}" fill-opacity=".3"/>')
                continue
            h = 14 + 136 * (c / maxc) ** 0.55
            grow = w * 0.022 + (6 - d) * 0.01
            pulse = 1.0 + (px - x0) / 780.0 * sweep
            bars.append(
                f'<g><title>{c} contribution{"s" if c != 1 else ""} on {ds}</title>'
                f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="4.5" ry="2" fill="{t["dot"]}" fill-opacity=".28"/>'
                f'<rect class="bar" x="{px - 1.5:.1f}" y="{py - h:.1f}" width="3" height="{h:.1f}" fill="url(#barG)" style="animation-delay:{grow:.2f}s"/>'
                f'<g class="cap" style="animation-delay:{grow + 0.9:.2f}s"><circle class="glow" cx="{px:.1f}" cy="{py - h:.1f}" r="6.5" fill="{t["dot"]}" style="animation-delay:{pulse:.2f}s"/></g>'
                f'<circle class="cap" cx="{px:.1f}" cy="{py - h:.1f}" r="2.4" fill="{t["strong"]}" style="animation-delay:{grow + 0.9:.2f}s"/></g>'
            )
    css = [
        f".lbl{{font-family:{MONO};font-size:10.5px;fill:{t['text']}}}",
        f".hdr{{font-family:{MONO};font-size:12px;fill:{t['text']}}}",
        ".bar{transform-box:fill-box;transform-origin:50% 100%;animation:grow 1.3s cubic-bezier(.2,.8,.2,1) both}",
        "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}",
        ".cap{animation:capin .5s ease-out both}",
        "@keyframes capin{from{opacity:0}to{opacity:1}}",
        ".glow{opacity:.16;animation:pulse 9s ease-out infinite}",
        "@keyframes pulse{0%,12%,100%{opacity:.16}3%{opacity:.6}}",
        f".beam{{animation:beam 9s linear infinite}}",
        f"@keyframes beam{{0%,11%{{transform:translateX(0)}}46%,100%{{transform:translateX({W + 160}px)}}}}",
        REDUCED,
    ]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
  <title id="t">{total} contributions in the last year, drawn as a 3D skyline</title>
  <style>{NL.join(css)}</style>
  <defs>
    <linearGradient id="barG" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{t['dot']}" stop-opacity=".05"/><stop offset="1" stop-color="{t['dot']}" stop-opacity=".95"/></linearGradient>
    <linearGradient id="beamG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['dot']}" stop-opacity="0"/><stop offset=".5" stop-color="{t['dot']}" stop-opacity=".09"/><stop offset="1" stop-color="{t['dot']}" stop-opacity="0"/></linearGradient>
  </defs>
  <text class="hdr" x="{x0}" y="30">{total} contributions in the last year</text>
  {"".join(floor)}
  {"".join(labels)}
  {"".join(bars)}
  <rect class="beam" x="-160" y="40" width="120" height="{H - 50}" fill="url(#beamG)"/>
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
        days, total = fetch_days(os.environ["GH_USER"], os.environ["GITHUB_TOKEN"])
    for mode, theme in THEMES.items():
        for name, svg in (("hologram", hologram(theme)), ("skyline", skyline(days, total, theme))):
            with open(os.path.join(out, f"{name}-{mode}.svg"), "w", encoding="utf-8") as fh:
                fh.write(svg)
    print("wrote profile art for", len(days), "days,", total, "contributions")


if __name__ == "__main__":
    main()
