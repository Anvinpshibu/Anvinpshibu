"""The commit disposal unit: a laser turret rides the rail and burns every contribution square.

    python scripts/readme/laser.py --user Anvinpshibu --out dist/laser-commits.svg   # GITHUB_TOKEN set
    python scripts/readme/laser.py --demo --out assets/laser-commits.svg             # synthetic year

Run daily by .github/workflows/laser.yml, which publishes the SVG to the `output` branch.
"""
import argparse
import datetime as dt
import json
import os
import random
import urllib.request

from common import (ASH, BONE, EMBER, GRAPHITE, HOT, INK, LINE, MONO, MONO_M, SIGNAL,
                    crop_marks, grid, light, num, spark, svg)

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
FILL = ["#161618", "#4A1A0C", "#8A2A0D", "#D23C10", SIGNAL]
BURNT = "#211210"

QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date weekday contributionCount contributionLevel}}}}}}"""


def fetch(user: str) -> tuple[int, list[list[dict]]]:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[{"row": d["weekday"], "date": d["date"], "n": d["contributionCount"], "lvl": LEVELS[d["contributionLevel"]]}
              for d in w["contributionDays"]] for w in cal["weeks"]]
    return cal["totalContributions"], weeks


def demo() -> tuple[int, list[list[dict]]]:
    rnd = random.Random(7)
    start = dt.date.today() - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)
    weeks, total = [], 0
    for w in range(53):
        days = []
        for r in range(7):
            d = start + dt.timedelta(days=w * 7 + r)
            if d > dt.date.today():
                break
            n = 0 if rnd.random() < 0.35 else int(rnd.expovariate(0.25))
            total += n
            days.append({"row": r, "date": d.isoformat(), "n": n, "lvl": min(4, (n + 2) // 3)})
        weeks.append(days)
    return total, weeks


def render(total: int, weeks: list[list[dict]], user: str) -> str:
    W, H = 1280, 330
    cell, gap = 16, 4
    pitch = cell + gap
    gx = (W - len(weeks) * pitch + gap) / 2
    gy, rail = 122, 74
    cx = lambda c: gx + c * pitch + cell / 2
    cy = lambda r: gy + r * pitch + cell / 2

    targets = [(c, d["row"]) for c, w in enumerate(weeks) for d in w if d["n"] > 0]
    n = max(len(targets), 1)
    dz = min(0.16, 38 / n)  # seconds per zap
    t_start = 1.2
    t_end = t_start + n * dz
    t_restore = t_end + 3.2
    T = t_restore + 1.6
    k = lambda t: f"{min(max(t / T, 0), 1):.5f}"

    body = [grid(W, H, 40, "#121214"), crop_marks(W, H)]
    body.append(MONO_M.text("COMMIT DISPOSAL UNIT", 44, 44, 13, BONE, track=0.24))
    body.append(MONO.text(f"laser-assisted  ·  @{user.lower()}  ·  last 12 months", 44 + MONO_M.width("COMMIT DISPOSAL UNIT", 13, .24) + 24, 44, 12, ASH))
    body.append(MONO.text(f"{total} CONTRIBUTIONS  ·  {len(targets)} DAYS VAPORISED", W - 44, 44, 12, SIGNAL, track=0.16, anchor="end"))

    # the rail the turret rides
    x_a, x_b = gx - 30, gx + len(weeks) * pitch + 10
    body.append(f'<path d="M{num(x_a)} {rail}H{num(x_b)}" stroke="{GRAPHITE}" stroke-width="2"/>')
    body.append(f'<path d="M{num(x_a)} {rail + 6}H{num(x_b)}" stroke="{LINE}" stroke-width="1" stroke-dasharray="2 8"/>')

    # weekday + month labels
    for r, lab in ((1, "MON"), (3, "WED"), (5, "FRI")):
        body.append(MONO.text(lab, gx - 12, cy(r) + 3.5, 9, GRAPHITE, track=0.1, anchor="end"))
    last_month, last_c = None, -9
    for c, w in enumerate(weeks):
        if not w:
            continue
        m = dt.date.fromisoformat(w[0]["date"]).strftime("%b").upper()
        if m != last_month:
            if c - last_c >= 3 and c < len(weeks) - 2:
                body.append(MONO.text(m, gx + c * pitch, gy + 7 * pitch + 16, 10, ASH, track=0.1))
                last_c = c
            last_month = m

    # the squares, and each one's burn
    order = {t: i for i, t in enumerate(targets)}
    cells, burns = [], []
    for c, w in enumerate(weeks):
        for d in w:
            x, y = gx + c * pitch, gy + d["row"] * pitch
            base = FILL[d["lvl"] if d["n"] else 0]
            i = order.get((c, d["row"]))
            if i is None:
                cells.append(f'<rect x="{num(x)}" y="{num(y)}" width="{cell}" height="{cell}" rx="3" fill="{base}"/>')
                continue
            tk = t_start + i * dz
            times = [0, tk, tk + 0.02, tk + 0.2, tk + 0.9, t_restore, t_restore + 0.9, T]
            vals = [base, base, "#FFFFFF", EMBER, BURNT, BURNT, base, base]
            cells.append(f'<rect x="{num(x)}" y="{num(y)}" width="{cell}" height="{cell}" rx="3" fill="{base}">'
                         f'<animate attributeName="fill" values="{";".join(vals)}" keyTimes="{";".join(k(t) for t in times)}" '
                         f'dur="{num(T)}s" repeatCount="indefinite"/></rect>')
            burns.append(f'<circle cx="{num(x + cell / 2)}" cy="{num(y + cell / 2)}" r="0" fill="none" stroke="{HOT}" stroke-width="2" opacity="0">'
                         f'<animate attributeName="r" values="0;0;16;16" keyTimes="0;{k(tk)};{k(tk + .4)};1" dur="{num(T)}s" repeatCount="indefinite"/>'
                         f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{k(tk)};{k(tk + .02)};{k(tk + .4)};1" dur="{num(T)}s" repeatCount="indefinite"/></circle>')
    body.append("".join(cells))
    body.append(f'<g filter="url(#glow)">{"".join(burns)}</g>')

    # turret + beam: one keyframe per zap
    park = x_a + 8
    kts, xs, ys, ops = ["0", k(t_start - .6)], [park, park], [cy(3), cy(3)], ["0", "0"]
    for i, (c, r) in enumerate(targets):
        tk = t_start + i * dz
        kts += [k(tk), k(tk + dz * .45), k(tk + dz * .9)]
        xs += [cx(c)] * 3
        ys += [cy(r)] * 3
        ops += ["1", ".85", "0"]
    kts += [k(t_end + .9), "1"]
    xs += [park, park]
    ys += [cy(3), cy(3)]
    ops += ["0", "0"]
    # keyTimes must not decrease (zaps closer than the rounding collapse onto one another)
    fixed, prev = [], 0.0
    for v in kts:
        prev = max(prev, float(v))
        fixed.append(f"{prev:.5f}")
    kts = ";".join(fixed)
    xv = ";".join(num(v) for v in xs)
    yv = ";".join(num(v) for v in ys)
    ov = ";".join(ops)
    an = lambda attr, vals: f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kts}" dur="{num(T)}s" repeatCount="indefinite"/>'
    beam = f'x1="{num(park)}" y1="{rail + 10}" x2="{num(park)}" y2="{num(cy(3))}"'
    body.append(f'<line {beam} stroke="{SIGNAL}" stroke-width="7" opacity="0" filter="url(#bloom)">{an("x1", xv)}{an("x2", xv)}{an("y2", yv)}{an("opacity", ov)}</line>')
    body.append(f'<line {beam} stroke="{HOT}" stroke-width="1.6" opacity="0">{an("x1", xv)}{an("x2", xv)}{an("y2", yv)}{an("opacity", ov)}</line>')
    turret = (f'<path d="M-15 -11H15L11 6H-11Z" fill="#26231F" stroke="{ASH}" stroke-width="1.2"/>'
              f'<rect x="-4" y="6" width="8" height="5" fill="{GRAPHITE}"/>'
              f'<circle cx="0" cy="11" r="3" fill="{SIGNAL}" filter="url(#glow)"/>')
    tx = ";".join(f"{num(v)} {rail - 1}" for v in xs)
    body.append(f'<g transform="translate({num(park)} {rail - 1})">{turret}'
                f'<animateTransform attributeName="transform" type="translate" values="{tx}" keyTimes="{kts}" dur="{num(T)}s" repeatCount="indefinite"/></g>')
    # muzzle flash, riding with the beam tip at the turret
    body.append(f'<g transform="translate({num(park)} {rail + 10})" opacity="0">{spark(0, 0, 10, pulse=False)}'
                f'<animateTransform attributeName="transform" type="translate" values="{";".join(f"{num(v)} {rail + 10}" for v in xs)}" keyTimes="{kts}" dur="{num(T)}s" repeatCount="indefinite"/>'
                f'{an("opacity", ov)}</g>')

    # legend
    ly = H - 34
    body.append(MONO.text("less", gx, ly + 10, 10, ASH))
    for j, f in enumerate(FILL):
        body.append(f'<rect x="{num(gx + 36 + j * 18)}" y="{ly}" width="13" height="13" rx="2.5" fill="{f}"/>')
    body.append(MONO.text("more", gx + 36 + 5 * 18 + 6, ly + 10, 10, ASH))
    body.append(MONO.text(f"rendered {dt.date.today().isoformat()}  ·  refreshed every 6 h  ·  no commits were harmed permanently",
                          x_b, ly + 10, 10, GRAPHITE, anchor="end"))
    return svg(W, H, "".join(body), f"{total} contributions, burned one by one by a laser turret")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="Anvinpshibu")
    ap.add_argument("--out", default="dist/laser-commits.svg")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    total, weeks = demo() if a.demo else fetch(a.user)
    out = render(total, weeks, a.user)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(out)
    with open(a.out.replace(".svg", "-light.svg"), "w", encoding="utf-8") as f:
        f.write(light(out))
    print(f"{a.out}: {total} contributions, {len(out) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
