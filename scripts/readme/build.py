"""Render the README's plates into assets/: python scripts/readme/build.py

Every plate is a looping SMIL animation (GitHub plays those inside <img>), cut like the film
on anvinpshibu.com: ink paper, bone type, one signal colour, and a spark that does the work.
"""
import math
import random
from pathlib import Path

from common import (ASH, BLOOD, BONE, DISPLAY, EMBER, GRAPHITE, HOT, INK, INK2, LINE, MONO,
                    MONO_M, SANS, SERIF, SIGNAL, crop_marks, grid, num, spark, svg, wrap)

OUT = Path(__file__).resolve().parents[2] / "assets"
PI = math.pi


def kt(*ts: float, T: float) -> str:
    """keyTimes for a cycle of T seconds."""
    return ";".join(f"{min(max(t / T, 0), 1):.4f}" for t in ts)


# ── HERO: the end card's pen plot, run forwards ──────────────────────────────────────────────
# Same geometry as the site's end card (src/film/scenes/endcard.ts): unit box, y down, cap = 1.
def L(ax, ay, bx, by):
    return ("L", (ax, ay), (bx, by))


def A(cx, cy, r, a0, a1):
    return ("A", (cx, cy), r, a0, a1)


GLYPHS = {
    "A": (0.72, [L(0, 1, 0.36, 0), L(0.36, 0, 0.72, 1), L(0.15, 0.62, 0.57, 0.62)]),
    "N": (0.64, [L(0, 1, 0, 0), L(0, 0, 0.64, 1), L(0.64, 1, 0.64, 0)]),
    "V": (0.72, [L(0, 0, 0.36, 1), L(0.36, 1, 0.72, 0)]),
    "I": (0.08, [L(0.04, 0, 0.04, 1)]),
    "P": (0.56, [L(0, 1, 0, 0), L(0, 0, 0.3, 0), A(0.3, 0.26, 0.26, -PI / 2, PI / 2), L(0.3, 0.52, 0, 0.52)]),
    "S": (0.58, [A(0.29, 0.25, 0.25, -0.08 * PI, -1.5 * PI), A(0.29, 0.75, 0.25, -0.5 * PI, 0.92 * PI)]),
    "H": (0.64, [L(0, 0, 0, 1), L(0.64, 0, 0.64, 1), L(0, 0.5, 0.64, 0.5)]),
    "B": (0.6, [L(0, 1, 0, 0), L(0, 0, 0.3, 0), A(0.3, 0.25, 0.25, -PI / 2, PI / 2), L(0.3, 0.5, 0, 0.5),
                L(0, 0.5, 0.34, 0.5), A(0.34, 0.75, 0.25, -PI / 2, PI / 2), L(0.34, 1, 0, 1)]),
    "U": (0.62, [L(0, 0, 0, 0.69), A(0.31, 0.69, 0.31, PI, 0), L(0.62, 0.69, 0.62, 0)]),
}


def seg_points(seg, ox, oy, cap):
    if seg[0] == "L":
        (ax, ay), (bx, by) = seg[1], seg[2]
        return [(ox + ax * cap, oy + ay * cap), (ox + bx * cap, oy + by * cap)]
    _, (cx, cy), r, a0, a1 = seg
    n = max(8, int(abs(a1 - a0) * 14))
    return [(ox + (cx + math.cos(a0 + (a1 - a0) * i / n) * r) * cap,
             oy + (cy + math.sin(a0 + (a1 - a0) * i / n) * r) * cap) for i in range(n + 1)]


def poly_len(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def hero():
    W, H, T = 1280, 500, 16.0
    cap, gap, space = 108, 0.2, 0.42
    name = "ANVIN P SHIBU"
    widths = [space if c == " " else GLYPHS[c][0] for c in name]
    total = (sum(widths) + gap * sum(1 for i in range(len(name) - 1) if name[i] != " " and name[i + 1] != " ")) * cap
    x0, y0 = (W - total) / 2, 168
    segs, x = [], x0
    for i, c in enumerate(name):
        if c == " ":
            x += space * cap
            continue
        for s in GLYPHS[c][1]:
            segs.append(seg_points(s, x, y0, cap))
        x += GLYPHS[c][0] * cap + (gap * cap if i + 1 < len(name) and name[i + 1] != " " else 0)
    x1 = x
    stop = (x1 + 14, y0 + cap - 2)  # the full stop the spark comes to rest on

    t0, t1 = 1.0, 7.2
    lens = [poly_len(p) for p in segs]
    tot = sum(lens)
    body = [grid(W, H), crop_marks(W, H)]

    # the code that "asked" for the drawing, typed in
    code = ['% eval: "Draw Anvin P Shibu in TikZ."', r"\begin{tikzpicture}",
            r"\draw[pen=spark] (A) -- (N) -- (V) -- (I) -- (N);",
            r"\draw[pen=spark] (P) (S) -- (H) -- (I) -- (B) -- (U);", r"\end{tikzpicture}"]
    for i, line in enumerate(code):
        ta = 0.1 + i * 0.16
        body.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" '
                    f'keyTimes="{kt(0, ta, ta + .05, 14.6, 15.4, T, T=T)}" dur="{T}s" repeatCount="indefinite"/>'
                    + MONO.text(line, 40, 46 + i * 17, 12, BONE if i == 0 else ASH) + "</g>")
    body.append(MONO.text("SHEET 1 OF 6  ·  START OF REEL", W - 40, 46, 11, ASH, track=0.18, anchor="end"))

    # construction: dimension line + guides
    dim_y = y0 - 34
    lbl = f"{(x1 - x0) / cap:.2f} × 1.00"
    lw = MONO.width(lbl, 12) + 20
    body.append(f'<g stroke="{GRAPHITE}" stroke-width="1" fill="none"><path d="M{num(x0)} {dim_y}H{num((x0 + x1 - lw) / 2)}'
                f'M{num((x0 + x1 + lw) / 2)} {dim_y}H{num(x1)}M{num(x0)} {dim_y-6}v12M{num(x1)} {dim_y-6}v12"/>'
                f'<path d="M{num(x0 - 30)} {y0}H{num(x1 + 40)}M{num(x0 - 30)} {y0 + cap}H{num(x1 + 40)}" stroke-dasharray="4 7"/></g>')
    body.append(MONO.text(lbl, (x0 + x1) / 2, dim_y + 4, 12, ASH, anchor="middle"))

    # the horizon, lit on the drop
    hy = y0 + cap + 34
    body.append(f'<path d="M0 {hy}H{W}" stroke="{SIGNAL}" stroke-width="1.2" pathLength="1" stroke-dasharray="1" '
                f'stroke-dashoffset="1" opacity=".85"><animate attributeName="stroke-dashoffset" values="1;1;0;0;1" '
                f'keyTimes="{kt(0, .3, 1.4, 15.4, T, T=T)}" dur="{T}s" repeatCount="indefinite"/></path>')

    # the name: each stroke plotted in order, at the spark's speed
    strokes, glow, motion, acc = [], [], [], 0.0
    for pts, ln in zip(segs, lens):
        a = t0 + (t1 - t0) * acc / tot
        acc += ln
        b = t0 + (t1 - t0) * acc / tot
        d = "M" + "L".join(f"{num(px)} {num(py)}" for px, py in pts)
        motion.append(d)
        anim = (f'<animate attributeName="stroke-dashoffset" values="1;1;0;0;1" keyTimes="{kt(0, a, b, 15.5, T, T=T)}" '
                f'dur="{T}s" repeatCount="indefinite"/>')
        strokes.append(f'<path d="{d}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">{anim}</path>')
        glow.append(f'<path d="{d}"/>')
    fade = (f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="{kt(0, 14.6, 15.4, T, T=T)}" '
            f'dur="{T}s" repeatCount="indefinite"/>')
    # the name heats as the pen lifts
    body.append(f'<g fill="none" stroke="{SIGNAL}" stroke-width="7" stroke-linecap="round" filter="url(#bloom)" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;.75;.35;.35;0;0" keyTimes="{kt(0, t1 - .3, t1 + .4, t1 + 2, 14.4, 15.2, T, T=T)}" '
                f'dur="{T}s" repeatCount="indefinite"/>{"".join(glow)}</g>')
    body.append(f'<g fill="none" stroke="{BONE}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">'
                f'{fade}{"".join(strokes)}</g>')

    # the spark: rides the pen, then rests on the full stop
    glide = math.dist(segs[-1][-1], stop)
    mpath = "".join(motion) + f"L{num(stop[0])} {num(stop[1])}"
    k_end = tot / (tot + glide)
    body.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt(0, t0 - .3, t0, 14.6, 15.4, T, T=T)}" '
                f'dur="{T}s" repeatCount="indefinite"/>'
                f'<g>{spark(0, 0, 18)}<animateMotion path="{mpath}" keyPoints="0;0;{k_end:.4f};1;1" keyTimes="{kt(0, t0, t1, t1 + .6, T, T=T)}" '
                f'calcMode="linear" dur="{T}s" repeatCount="indefinite"/></g></g>')
    body.append(f'<circle cx="{num(stop[0])}" cy="{num(stop[1])}" r="3.6" fill="{BONE}" opacity="0"><animate attributeName="opacity" '
                f'values="0;0;1;1;0;0" keyTimes="{kt(0, t1 + .55, t1 + .6, 14.6, 15.4, T, T=T)}" dur="{T}s" repeatCount="indefinite"/></circle>')

    # title + contact, typed beneath
    def typed(el, y, h, ta, tb, x_from=0, x_to=W):
        cid = f"c{int(y)}"
        return (f'<clipPath id="{cid}"><rect x="{x_from}" y="{y - h}" width="0" height="{h + 8}">'
                f'<animate attributeName="width" values="0;0;{x_to - x_from};{x_to - x_from};0" keyTimes="{kt(0, ta, tb, 15.4, T, T=T)}" '
                f'dur="{T}s" repeatCount="indefinite"/></rect></clipPath><g clip-path="url(#{cid})">{el}</g>')

    sub = "SI ENGINEER   ·   ML   ·   AI"
    sw = MONO_M.width(sub, 21, 0.32)
    body.append(typed(MONO_M.text(sub, W / 2, hy + 52, 21, SIGNAL, track=0.32, anchor="middle"),
                      hy + 52, 24, t1 + .3, t1 + 1.4, W / 2 - sw / 2, W / 2 + sw / 2))
    contact = "anvinpshibu@gmail.com   ·   Alappuzha, Kerala   ·   anvinpshibu.com"
    cw = MONO.width(contact, 15)
    body.append(typed(MONO.text(contact, W / 2, hy + 88, 15, BONE, anchor="middle"),
                      hy + 88, 18, t1 + 1.2, t1 + 2.4, W / 2 - cw / 2, W / 2 + cw / 2))
    body.append(MONO.text("TECHNICAL CO-FOUNDER & CEO  ·  ARASKOVA LABS", 40, H - 30, 11, GRAPHITE, track=0.16))
    body.append(SERIF.text("reel one.", W - 40, H - 26, 28, ASH, anchor="end"))
    return svg(W, H, "".join(body), "Anvin P Shibu — SI engineer · ML · AI")


# ── PLATES: the film's chapters, as section headers ──────────────────────────────────────────
PLATES = [
    ("01", "SPARKS", "ABOUT", "Builds and ships end-to-end AI systems.", "I ship sparks of AI to the edge"),
    ("02", "SINGULARITY", "EXPERIENCE", "Two stable internships, then two startups.", "There was a sudden drop in your training loss"),
    ("03", "ASCENT", "PROJECTS", "Sixteen shipped, from vision to production.", "SHIP it to production"),
    ("04", "LEFT TURN", "ROUTE", "B.E., then data, ML and AI. Next: SI.", "Sharp left turn, and here I am"),
    ("05", "SKILLS", "ARSENAL", "Six groups, 53 skills, one root.", "53 tools in one room"),
    ("06", "NEXT", "TELEMETRY", "Every commit, accounted for. Then vaporised.", "Real-time, thirty FPS"),
    ("07", "FIN", "CONTACT", "Building what comes next. Say hello, I reply.", "What am I training next? You'll see"),
]


def plate(num_, chapter, title, lede, lyric, i):
    W, H, T = 1280, 160, 9.0
    body = [grid(W, H, 32, "#121214"), crop_marks(W, H, 10, 12)]
    tag = f"PLATE {num_}  ·  "
    body.append(MONO.text(tag, 44, 46, 12, ASH, track=0.28))
    body.append(MONO_M.text(chapter, 44 + MONO.width(tag, 12, 0.28) + 12 * 0.28, 46, 12, SIGNAL, track=0.28))
    body.append(DISPLAY.text(title, 40, 116, 66, BONE, track=0.01))
    body.append(SERIF.text(lede, W - 44, 82, 27, "#B9B3A8", anchor="end"))
    note = "♪" if 0x266A in MONO.cmap else "//"
    body.append(MONO.text(f"{note}  {lyric}", W - 44, 114, 12, GRAPHITE, track=0.06, anchor="end"))
    y = 136
    body.append(f'<path d="M44 {y}H{W - 44}" stroke="{LINE}" stroke-width="1"/>')
    body.append(f'<path d="M44 {y}H{W - 44}" stroke="{SIGNAL}" stroke-width="1.6" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
                f'<animate attributeName="stroke-dashoffset" values="1;1;0;0;1" keyTimes="{kt(0, .2, 2.2, 8.4, T, T=T)}" dur="{T}s" repeatCount="indefinite"/></path>')
    body.append(f'<g>{spark(0, 0, 13)}<animateMotion path="M44 {y}H{W - 44}" keyPoints="0;0;1;1" keyTimes="{kt(0, .2, 2.2, T, T=T)}" '
                f'calcMode="linear" dur="{T}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="{kt(0, .2, 8.2, 8.6, T, T=T)}" dur="{T}s" repeatCount="indefinite"/></g>')
    # a scanning laser, sweeping the plate
    body.append(f'<g opacity=".55"><rect x="-6" y="8" width="3" height="{H - 16}" fill="{SIGNAL}" filter="url(#glow)"/>'
                f'<rect x="-40" y="8" width="40" height="{H - 16}" fill="url(#trail)"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;{W + 50} 0" dur="{T}s" '
                f'begin="{2.4 + i * 0.35}s" repeatCount="indefinite"/></g>')
    trail = (f'<linearGradient id="trail"><stop offset="0" stop-color="{SIGNAL}" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{SIGNAL}" stop-opacity=".35"/></linearGradient>')
    return svg(W, H, "".join(body), f"{num_} · {title}", trail)


# ── TRAINING RUN: experience as a loss curve ─────────────────────────────────────────────────
CKPTS = [
    # (year, _, tag, org, role, label anchor, label offset from the point)
    (2023.5, 0.86, "ckpt 01", "BUMBLEBEE INC.", "Data Science Intern · 2023", "start", -64),
    (2024.1, 0.52, "ckpt 02", "NEXORIS", "Founder & AI Lead · 2024 →", "end", 46),
    (2024.45, 0.43, "ckpt 03", "BUMBLEBEE INC.", "Data Analyst Intern · 2024", "start", 46),
    (2026.55, 0.17, "ckpt 04", "ARASKOVA LABS", "Technical Co-founder & CEO · 2026 →", "end", -74),
]


def training_run():
    W, H, T = 1280, 440, 14.0
    X0, X1, Y0, Y1 = 96, 1100, 90, 360
    yr0, yr1 = 2023.0, 2027.0
    sx = lambda yr: X0 + (yr - yr0) / (yr1 - yr0) * (X1 - X0)
    sy = lambda v: Y1 - v * (Y1 - Y0)

    def loss(yr):
        base = 1.0 - 0.28 * (yr - 2023) ** 0.8
        if yr > 2024.0:  # the sudden drop: the first startup
            base -= 0.24 * min((yr - 2024.0) / 0.12, 1)
        if yr > 2026.4:
            base -= 0.06 * min((yr - 2026.4) / 0.2, 1)
        return max(base, 0.12)

    rnd = random.Random(2026)
    pts, yr = [], yr0
    while yr <= 2026.62:
        v = loss(yr) + rnd.gauss(0, 0.022) * (1.1 - (yr - 2023) / 4)
        pts.append((sx(yr), sy(v)))
        yr += 0.012
    d = "M" + "L".join(f"{num(x)} {num(y)}" for x, y in pts)
    t0, t1 = 0.6, 6.0
    body = [grid(W, H, 40, "#121214"), crop_marks(W, H)]
    body.append(MONO_M.text("TRAINING RUN", 44, 46, 13, BONE, track=0.24))
    body.append(MONO.text("loss vs. steps  ·  lr: aggressive  ·  batch: everything", 44 + MONO_M.width("TRAINING RUN", 13, .24) + 24, 46, 12, ASH))
    body.append(MONO.text("4 CHECKPOINTS  ·  NEXT: SI", W - 44, 46, 12, SIGNAL, track=0.2, anchor="end"))
    # axes
    ax = [f'<path d="M{X0} {Y0 - 10}V{Y1}H{X1 + 120}" stroke="{GRAPHITE}" fill="none"/>']
    for v in (0.25, 0.5, 0.75, 1.0):
        ax.append(f'<path d="M{X0} {num(sy(v))}H{X1 + 120}" stroke="#1C1B1A" stroke-dasharray="2 6"/>')
        ax.append(MONO.text(f"{v:.2f}", X0 - 12, sy(v) + 4, 11, GRAPHITE, anchor="end"))
    for y_ in range(2023, 2028):
        ax.append(f'<path d="M{num(sx(y_))} {Y1}v6" stroke="{GRAPHITE}"/>')
        ax.append(MONO.text(str(y_), sx(y_), Y1 + 24, 11, ASH, anchor="middle"))
    ax.append(MONO.text("loss", X0, Y0 - 20, 11, ASH, anchor="middle"))
    ax.append(MONO.text("steps →", X1 + 120, Y1 + 24, 11, ASH, anchor="end"))
    body += ax
    # the curve, with a glow under it
    draw = (f'<animate attributeName="stroke-dashoffset" values="1;1;0;0;1" keyTimes="{kt(0, t0, t1, 13.4, T, T=T)}" '
            f'dur="{T}s" repeatCount="indefinite"/>')
    body.append(f'<path d="{d}" fill="none" stroke="{SIGNAL}" stroke-width="6" opacity=".35" filter="url(#bloom)" pathLength="1" '
                f'stroke-dasharray="1" stroke-dashoffset="1">{draw}</path>')
    body.append(f'<path d="{d}" fill="none" stroke="{SIGNAL}" stroke-width="2" stroke-linejoin="round" pathLength="1" '
                f'stroke-dasharray="1" stroke-dashoffset="1">{draw}</path>')
    body.append(f'<g>{spark(0, 0, 14)}<animateMotion path="{d}" keyPoints="0;0;1;1" keyTimes="{kt(0, t0, t1, T, T=T)}" '
                f'calcMode="linear" dur="{T}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt(0, t0 - .1, t0, 13.2, 13.6, T, T=T)}" dur="{T}s" repeatCount="indefinite"/></g>')
    # the sudden drop, annotated
    dx = sx(2024.06)
    body.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="{kt(0, 1.9, 2.3, 13.4, T, T=T)}" dur="{T}s" repeatCount="indefinite"/>'
                f'<path d="M{num(dx + 16)} {num(sy(0.78))}l-10 0" stroke="{ASH}"/>'
                + SERIF.text("a sudden drop in the training loss", dx + 24, sy(0.78) + 6, 21, BONE) + "</g>")
    # checkpoints pop as the curve reaches them
    for yr, v, ck, org, role, anchor, off in CKPTS:
        x, y = sx(yr), sy(loss(yr))
        ta = t0 + (t1 - t0) * (x - pts[0][0]) / (pts[-1][0] - pts[0][0])
        ly = y + off
        lx = x + (12 if anchor == "start" else -12)
        g = (f'<path d="M{num(x)} {num(y)}V{num(ly - 16 if off > 0 else ly + 34)}" stroke="{GRAPHITE}" stroke-dasharray="2 3"/>'
             f'<circle cx="{num(x)}" cy="{num(y)}" r="5.5" fill="{INK}" stroke="{BONE}" stroke-width="2"/>'
             + MONO.text(ck.upper(), lx, ly - 2, 10, SIGNAL, track=0.2, anchor=anchor)
             + MONO_M.text(org, lx, ly + 14, 13, BONE, track=0.06, anchor=anchor)
             + MONO.text(role, lx, ly + 29, 11, ASH, anchor=anchor))
        body.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="{kt(0, ta, ta + .3, 13.4, T, T=T)}" '
                    f'dur="{T}s" repeatCount="indefinite"/>{g}</g>')
    # extrapolation to the next checkpoint
    ex0, ey0 = pts[-1]
    sx1, sy1 = sx(2027.0) + 70, sy(0.03)
    body.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="{kt(0, t1, t1 + .5, 13.4, T, T=T)}" '
                f'dur="{T}s" repeatCount="indefinite"/>'
                f'<path d="M{num(ex0)} {num(ey0)}Q{num(sx(2026.9))} {num(sy(0.05))} {num(sx1)} {num(sy1)}" fill="none" stroke="{SIGNAL}" '
                f'stroke-width="1.6" stroke-dasharray="5 6"><animate attributeName="stroke-dashoffset" values="0;-22" dur="1s" repeatCount="indefinite"/></path>'
                f'<g transform="translate({num(sx1)} {num(sy1)})"><path d="M0 -11L11 0L0 11L-11 0Z" fill="{SIGNAL}" filter="url(#glow)">'
                f'<animateTransform attributeName="transform" type="scale" values="1;1.25;1" dur="1.2s" repeatCount="indefinite"/></path></g>'
                + MONO_M.text("NEXT CHECKPOINT", sx1, sy1 - 46, 11, SIGNAL, track=0.2, anchor="end")
                + DISPLAY.text("SI", sx1, sy1 - 18, 26, BONE, anchor="end") + "</g>")
    return svg(W, H, "".join(body), "Training run: experience as a loss curve, next checkpoint SI")


# ── PROJECT CARDS ────────────────────────────────────────────────────────────────────────────
PROJECTS = [
    ("001", "VIGIL", "Real-time CV quality control", "N100", "edge inference",
     "EfficientAD anomaly detection for cashew-kernel inspection: per-item anomaly scores from a live webcam feed, "
     "client-server, deployed on an Intel N100 with ONNX Runtime.", ["EfficientAD", "ONNX Runtime", "OpenCV", "Intel N100"]),
    ("002", "CERBERUS", "Autonomous AI security guardrail", "--fix", "patches on disk",
     "Headless security reviewer for terminals and CI: reads git diffs, flags vulnerabilities where they happen, "
     "patches them in place and generates dynamic security tests.", ["Rust", "LLMs", "CI/CD", "npm + cargo"]),
    ("003", "ARGUS", "Sports AI coach · biomechanics", "−70%", "labelling cost",
     "Real-time cricket coaching: pose estimation, multi-person tracking and XGBoost + LSTM risk scoring. "
     "ONNX + TensorRT on-device, so raw video never leaves the edge.", ["YOLOv8-Pose", "ByteTrack", "LSTM", "TensorRT"]),
    ("004", "TRIAGE-X", "Clinical decision support", "93%", "AUC-ROC · <2 s",
     "Multi-model triage ensemble (XGBoost + Transformer + LLM) with SHAP explainability; RAG report summaries "
     "with hallucination checks. SNS National Hackathon finalist.", ["XGBoost", "Transformer", "RAG", "pgvector"]),
    ("005", "RETINA-Q", "Quantum-classical retinal diagnosis", "8", "qubit circuits",
     "PennyLane circuits + EfficientNet-B0 for OCT / fundus classification, U-Net macular segmentation, "
     "Grad-CAM explainability, MLflow model registry.", ["PennyLane", "PyTorch", "U-Net", "MLflow"]),
    ("006", "SPECTER", "Security for LLM coding agents", "22", "guardrails",
     "Zero-dependency framework that installs 18 security skills and 22 enforceable guardrails into "
     "LLM coding agents across 8 platforms. npm i specter-kit", ["TypeScript", "Node.js", "OWASP", "npm"]),
    ("007", "TESSERIN", "Agentic knowledge studio", "4", "agents",
     "Summariser, linker, critic and retriever agents with scoped tools turn notes into a queryable "
     "knowledge graph over ChromaDB, Pinecone and PostgreSQL.", ["LangChain", "ChromaDB", "Pinecone", "Postgres"]),
    ("008", "EDGESHIELD", "Privacy-preserving on-device inference", "INT8", "quantised",
     "Quantised CV models on Raspberry Pi 4 and Jetson Nano, fully local. Benchmarked ONNX Runtime vs TensorRT "
     "vs OpenVINO; differential privacy at the feature layer.", ["OpenVINO", "TensorRT", "Jetson", "FastAPI"]),
]


def card(pn, name, sub, metric, mlabel, desc, stack, i):
    W, H, T = 620, 272, 7.0
    body = [grid(W, H, 31, "#121214"),
            f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="10" fill="none" stroke="{LINE}" stroke-width="1.5"/>',
            crop_marks(W, H, 10, 10, "#3A3835")]
    body.append(MONO.text("P/N ", 28, 40, 11, ASH, track=0.24))
    body.append(MONO_M.text(pn, 28 + MONO.width("P/N ", 11, .24) + 11 * .24, 40, 11, SIGNAL, track=0.24))
    body.append(DISPLAY.text(name, 28, 88, 38, BONE, track=0.01))
    body.append(MONO.text(sub.upper(), 28, 112, 11, ASH, track=0.14))
    # the metric, hot
    body.append(DISPLAY.text(metric, W - 28, 88, 38, SIGNAL, anchor="end", extra='filter="url(#glow)"'))
    body.append(MONO.text(mlabel.upper(), W - 28, 112, 10, ASH, track=0.16, anchor="end"))
    body.append(f'<path d="M28 128H{W - 28}" stroke="{LINE}"/>')
    for j, line in enumerate(wrap(desc, 74)[:4]):
        body.append(MONO.text(line, 28, 152 + j * 19, 12.2, "#CFC9BE"))
    x = 28
    for s in stack:
        w = MONO.width(s, 11) + 18
        body.append(f'<rect x="{num(x)}" y="{H - 48}" width="{num(w)}" height="24" rx="3" fill="{INK2}" stroke="#34312E"/>')
        body.append(MONO.text(s, x + 9, H - 32, 11, BONE))
        x += w + 8
    # a laser sweeps the card, top to bottom
    body.append(f'<g opacity="0"><rect x="8" y="-2" width="{W - 16}" height="2" fill="{SIGNAL}" filter="url(#glow)"/>'
                f'<rect x="8" y="-34" width="{W - 16}" height="32" fill="url(#sweep)"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 {H}" keyTimes="0;.55;1" dur="{T}s" '
                f'begin="{i * 0.6}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0;.8;.8;0" keyTimes="0;.55;.6;.95;1" dur="{T}s" begin="{i * 0.6}s" repeatCount="indefinite"/></g>')
    sweep = (f'<linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SIGNAL}" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{SIGNAL}" stop-opacity=".22"/></linearGradient>')
    return svg(W, H, "".join(body), f"{name} — {sub}", sweep)


# ── END CARD ─────────────────────────────────────────────────────────────────────────────────
def endcard():
    W, H, T = 1280, 330, 8.0
    body = [grid(W, H), crop_marks(W, H)]
    body.append(MONO.text("SHEET 6 OF 6  ·  END OF REEL", W - 44, 48, 11, ASH, track=0.18, anchor="end"))
    body.append(MONO.text("> what am I training next?", 44, 48, 12, ASH))
    body.append(DISPLAY.text("NEXT CHECKPOINT:", 44, 150, 64, BONE))
    sw = DISPLAY.width("NEXT CHECKPOINT: ", 64)
    body.append(DISPLAY.text("SI.", 44 + sw, 150, 64, SIGNAL, extra='filter="url(#glow)"'))
    cx = 44 + sw + DISPLAY.width("SI.", 64) + 10
    body.append(f'<rect x="{num(cx)}" y="100" width="26" height="52" fill="{SIGNAL}"><animate attributeName="opacity" '
                f'values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/></rect>')
    body.append(SERIF.text("Stay tuned.", 46, 196, 34, "#B9B3A8"))
    # P(doom) meter, upping it
    mx, my, n = 44, 250, 40
    body.append(MONO_M.text("P(doom)", mx, my + 14, 13, BONE, track=0.1))
    bx = mx + 96
    for k in range(n):
        x = bx + k * 15
        on = k / n
        col = SIGNAL if k < n * 0.75 else BLOOD
        body.append(f'<rect x="{x}" y="{my}" width="11" height="18" fill="{INK2}" stroke="#2E2B28"/>'
                    f'<rect x="{x}" y="{my}" width="11" height="18" fill="{col}" opacity="0"><animate attributeName="opacity" '
                    f'values="0;0;1;1;0" keyTimes="0;{on * .6:.3f};{on * .6 + .02:.3f};.92;1" dur="{T}s" repeatCount="indefinite"/></rect>')
    body.append(MONO.text("upping it", bx + n * 15 + 14, my + 14, 12, ASH))
    body.append(MONO.text("anvinpshibu.com  ·  anvinpshibu@gmail.com  ·  linkedin.com/in/anvin141", 44, H - 30, 12, ASH, track=0.04))
    body.append(SERIF.text("fin.", W - 44, H - 26, 40, BONE, anchor="end"))
    body.append(f'<g transform="translate({W - 34} {H - 36})">{spark(0, 0, 12)}</g>')
    return svg(W, H, "".join(body), "Next checkpoint: SI. Stay tuned.")


def main():
    OUT.mkdir(exist_ok=True)
    files = {"hero.svg": hero(), "training-run.svg": training_run(), "endcard.svg": endcard()}
    for i, p in enumerate(PLATES):
        files[f"plate-{p[0]}.svg"] = plate(*p, i)
    for i, p in enumerate(PROJECTS):
        files[f"card-{p[1].lower()}.svg"] = card(*p, i)
    for f, s in files.items():
        (OUT / f).write_text(s, encoding="utf-8")
        print(f"{f:24s} {len(s) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
