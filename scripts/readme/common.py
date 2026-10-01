"""Shared bits for the README plates: the film's palette and text set as SVG paths.

GitHub serves README images through a proxy that blocks web fonts, so every word is
converted to outlines from the same fonts anvinpshibu.com uses (Archivo, IBM Plex Mono,
Cormorant). All fonts are SIL OFL.
"""
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
FONTS = HERE / "fonts"

# The whole film lives in a restrained palette: ink, bone, and one signal colour.
INK = "#0A0A0B"
INK2 = "#151517"
LINE = "#2A2826"
GRAPHITE = "#5E5B57"
ASH = "#9C978F"
BONE = "#EEE9DF"
SIGNAL = "#FF4D12"
EMBER = "#FF8A3D"
BLOOD = "#C21D0B"
HOT = "#FFE2C4"


def num(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Font:
    def __init__(self, file: str):
        self.tt = TTFont(FONTS / file)
        self.glyphs = self.tt.getGlyphSet()
        self.cmap = self.tt.getBestCmap()
        self.upm = self.tt["head"].unitsPerEm
        self.hmtx = self.tt["hmtx"]

    def _gname(self, ch: str) -> str:
        return self.cmap.get(ord(ch)) or self.cmap.get(ord("?"))

    def width(self, text: str, size: float, track: float = 0) -> float:
        k = size / self.upm
        adv = sum(self.hmtx[self._gname(c)][0] for c in text) * k
        return adv + track * size * max(len(text) - 1, 0)

    def path(self, text: str, x: float, y: float, size: float, track: float = 0, anchor: str = "start") -> str:
        """Outline `text` with its baseline at y. track is extra spacing in em."""
        w = self.width(text, size, track)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        k = size / self.upm
        pen = SVGPathPen(self.glyphs, ntos=num)
        cx = x
        for c in text:
            g = self._gname(c)
            self.glyphs[g].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
            cx += self.hmtx[g][0] * k + track * size
        return pen.getCommands()

    def text(self, text: str, x: float, y: float, size: float, fill: str, track: float = 0,
             anchor: str = "start", extra: str = "") -> str:
        d = self.path(text, x, y, size, track, anchor)
        return f'<path d="{d}" fill="{fill}" {extra}><title>{escape(text)}</title></path>' if d else ""


DISPLAY = Font("Archivo-w1125-900.ttf")  # the film's shouting voice
SANS = Font("Archivo-w1000-500.ttf")
MONO = Font("IBMPlexMono-Regular.ttf")  # the credits
MONO_M = Font("IBMPlexMono-Medium.ttf")
SERIF = Font("CormorantItalic-400.ttf")  # the liner-note ledes


def svg(w: int, h: int, body: str, title: str, extra_defs: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
        f"<defs>{GLOW_DEFS}{extra_defs}</defs>"
        f'<rect width="{w}" height="{h}" rx="10" fill="{INK}"/>{body}</svg>'
    )


GLOW_DEFS = (
    '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
    '<feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    '<filter id="bloom" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>'
    f'<radialGradient id="spark"><stop offset="0" stop-color="#fff"/><stop offset=".25" stop-color="{HOT}"/>'
    f'<stop offset=".55" stop-color="{SIGNAL}" stop-opacity=".55"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/></radialGradient>'
)


def grid(w: int, h: int, step: int = 40, color: str = "#141416") -> str:
    xs = "".join(f"M{x} 0V{h}" for x in range(step, w, step))
    ys = "".join(f"M0 {y}H{w}" for y in range(step, h, step))
    return f'<path d="{xs}{ys}" stroke="{color}" stroke-width="1" fill="none"/>'


def crop_marks(w: int, h: int, m: int = 14, L: int = 18, color: str = GRAPHITE) -> str:
    d = (f"M{m} {m+L}V{m}H{m+L}M{w-m-L} {m}H{w-m}V{m+L}"
         f"M{w-m} {h-m-L}V{h-m}H{w-m-L}M{m+L} {h-m}H{m}V{h-m-L}")
    return f'<path d="{d}" stroke="{color}" stroke-width="1.5" fill="none"/>'


def spark(cx: float, cy: float, r: float = 16, pulse: bool = True) -> str:
    anim = (f'<animate attributeName="r" values="{r};{r*1.5};{r}" dur="1.6s" repeatCount="indefinite"/>'
            if pulse else "")
    star = (f'<path d="M{cx} {cy-r*0.9}L{cx+1.4} {cy-1.4}L{cx+r*0.9} {cy}L{cx+1.4} {cy+1.4}L{cx} {cy+r*0.9}'
            f'L{cx-1.4} {cy+1.4}L{cx-r*0.9} {cy}L{cx-1.4} {cy-1.4}Z" fill="#fff" opacity=".9"/>')
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#spark)">{anim}</circle>{star}'


def wrap(text: str, chars: int) -> list[str]:
    out, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > chars:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out
