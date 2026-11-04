#!/usr/bin/env python3
"""
Nima Kheradi - GitHub profile assets
====================================
Generates the animated SVGs used by README.md.
Pure SVG + CSS: no JavaScript, no external services, nothing that can break later.

    python generate.py        ->  writes ./assets/*.svg

Change the CONFIG block below, run it again, commit the new files.
"""
from itertools import count
from pathlib import Path
from xml.sax.saxutils import escape

# ═══════════════════════════════ CONFIG ═══════════════════════════════
PROMPT_PATH = r"C:\Users\Nima"            # shown before the ">" prompt
USER_HOST = ("nima", "kheradi")           # nima@kheradi
WEBSITE = "nimakheradi.ir"                # typed on the last line

INFO = [                                  # (key, value) - separate items with " · "
    ("role",  "Full-Stack Developer"),
    ("focus", "Real-time web · Streaming · RTL UIs"),
    ("front", "React · Next.js · Vite · Tailwind"),
    ("back",  "Node.js · Express · Socket.IO"),
    ("data",  "MySQL · MariaDB · Prisma · Redis"),
    ("base",  "Tehran"),
]

TREE = [                                  # printed by `tree projects`
    ("OneFa",      "live streaming platform"),
    ("123Bebinim", "virtual cinema · watch together"),
]

PROJECTS = [                              # -> assets/project-<slug>.svg
    dict(slug="onefa", name="OneFa", path="~/projects/onefa",
         desc=["Live streaming platform with real-time",
               "features and a Persian-first RTL UI."],
         tags=["React", "Vite", "Tailwind", "Node.js", "Socket.IO", "MySQL"]),
    dict(slug="123bebinim", name="123Bebinim", path="~/projects/123bebinim",
         desc=["Virtual cinema for watching together,",
               "with synced playback and live chat."],
         tags=["Next.js", "Prisma", "MariaDB", "Redis", "Socket.IO"]),
]

FOOTER_TEXT = "thanks for stopping by"

# ═══════════════════════════ PALETTE & TYPE ═══════════════════════════
BG, BAR, LINE = "#0a0d12", "#11151b", "#262c36"
FG, BRIGHT, MUTED = "#c9d1d9", "#f0f6fc", "#6e7681"
MINT, CYAN, BLUE, VIOLET = "#2ee6a6", "#56d4dd", "#58a6ff", "#bc8cff"
RED, ORANGE, YELLOW, GREEN = "#ff7b72", "#ffa657", "#f2cc60", "#3fb950"
SWATCH = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, VIOLET, BRIGHT]

MONO = ("'Cascadia Mono','SF Mono','JetBrains Mono',Consolas,Menlo,"
        "'DejaVu Sans Mono','Liberation Mono',monospace")
SANS = ("'Segoe UI Variable Text','Segoe UI',system-ui,-apple-system,"
        "'Helvetica Neue',Arial,sans-serif")

FS, CW, LH, GAP = 14, 8.4, 21, 11         # font size, char width, row height, group gap
OUT = Path(__file__).resolve().parent / "assets"


# ═══════════════════════════════ HELPERS ══════════════════════════════
def seg_line(x0, y, parts):
    """Lay parts [(text, css_class)] out on the monospace grid.

    Every segment gets its own <text> with a fixed textLength, so the grid stays
    identical no matter which monospace font the viewer's system picks.
    Whitespace-only parts (class None) just advance the column.
    """
    out, col = [], 0
    for s, cls in parts:
        core = s.strip(" ")
        if not core:
            col += len(s)
            continue
        lead = len(s) - len(s.lstrip(" "))
        col += lead
        out.append(
            f'<text x="{x0 + col * CW:.1f}" y="{y:.1f}" textLength="{len(core) * CW:.1f}" '
            f'lengthAdjust="spacing" class="{cls}">{escape(core)}</text>'
        )
        col += len(core) + (len(s) - lead - len(core))
    return "".join(out), col


class Scene:
    """Collects the CSS keyframes of one looping SVG (cycle length T seconds)."""

    def __init__(self, T):
        self.T, self.css, self.ids = T, [], count(1)

    def p(self, t):
        s = f"{t / self.T * 100:.3f}".rstrip("0").rstrip(".")
        return s or "0"

    def appear(self, t_on):
        """Hidden -> visible at t_on, stays visible. Returns the css class."""
        n = f"a{next(self.ids)}"
        self.css.append(
            f"@keyframes {n}{{0%,{self.p(t_on)}%{{opacity:0}}"
            f"{self.p(t_on + .02)}%,100%{{opacity:1}}}}"
            f".{n}{{animation:{n} {self.T}s linear infinite}}"
        )
        return n

    def between(self, t_on, t_off):
        """Keyframes only: visible during [t_on, t_off]. Returns the name."""
        n = f"w{next(self.ids)}"
        self.css.append(
            f"@keyframes {n}{{0%,{self.p(t_on)}%{{opacity:0}}"
            f"{self.p(t_on + .02)}%,{self.p(t_off)}%{{opacity:1}}"
            f"{self.p(t_off + .02)}%,100%{{opacity:0}}}}"
        )
        return n

    def typing(self, t_s, t_e, dist, steps):
        """Keyframes only: translateX 0 -> dist in `steps` jumps (one per character)."""
        n = f"m{next(self.ids)}"
        self.css.append(
            f"@keyframes {n}{{0%,{self.p(t_s)}%{{transform:translateX(0px);"
            f"animation-timing-function:steps({steps},end)}}"
            f"{self.p(t_e)}%,100%{{transform:translateX({dist:.1f}px)}}}}"
        )
        return n

    def screen(self, fade_in, out_start, out_end):
        """Whole-screen fade so the loop restarts with a clean 'cls'."""
        self.css.append(
            f"@keyframes scr{{0%{{opacity:0}}{self.p(fade_in)}%,{self.p(out_start)}%{{opacity:1}}"
            f"{self.p(out_end)}%,100%{{opacity:0}}}}"
            f".scr{{animation:scr {self.T}s linear infinite}}"
        )


class Typed:
    """A prompt line whose command is typed character by character."""

    def __init__(self, sc, x0):
        self.sc, self.x0 = sc, x0
        self.cx = x0 + (len(PROMPT_PATH) + 2) * CW

    def prompt(self, base):
        return seg_line(self.x0, base, [(PROMPT_PATH, "pp"), (">", "pg")])[0]

    def command(self, y_top, parts, t_a, final=False, per_char=0.07):
        sc, T = self.sc, self.sc.T
        k = next(sc.ids)
        base = y_top + 15
        n = sum(len(t) for t, _ in parts)
        t_s = t_a + 0.45
        t_e = t_s + n * per_char
        t_h = t_e + 0.35                              # "Enter" pressed
        mv = sc.typing(t_s, t_e, n * CW, n)
        cu = sc.between(t_a, t_e + 0.02 if final else t_h)
        ap = sc.appear(t_a)
        # base state (no animation) = fully typed; keyframes start from "hidden"
        sc.css.append(f".cv{k}{{transform:translateX({n * CW:.1f}px);animation:{mv} {T}s linear infinite}}")
        sc.css.append(f".tc{k}{{opacity:0;animation:{cu} {T}s linear infinite,{mv} {T}s linear infinite}}")
        txt = seg_line(self.cx, base, parts)[0]

        def cursor(cls, x):
            return (f'<rect class="{cls}" x="{x:.1f}" y="{y_top + 1.5}" '
                    f'width="{CW}" height="17" fill="{MINT}"/>')

        svg = (f'<g class="{ap}">{self.prompt(base)}{txt}'
               f'<rect class="cv{k}" x="{self.cx:.1f}" y="{y_top - 1}" width="{n * CW + 6:.1f}" '
               f'height="{LH + 2}" fill="{BG}"/>{cursor(f"tc{k}", self.cx)}</g>')
        if final:                                     # steady blinking cursor at the end
            svg += f'<g class="{sc.appear(t_e)}">{cursor("blink", self.cx + n * CW)}</g>'
        return svg


def base_css(sc):
    return (
        f"text{{font-family:{MONO};font-size:{FS}px;font-variant-ligatures:none}}"
        f".ui{{font-family:{SANS};font-size:12px;fill:{FG}}}"
        f".pp{{fill:{MINT}}}.pg{{fill:{MUTED}}}.cm{{fill:{BRIGHT}}}"
        f".lk{{fill:{BLUE};text-decoration:underline}}"
        f".us{{fill:{MINT};font-weight:700}}.ky{{fill:{MINT}}}.vl{{fill:{FG}}}.sp{{fill:{MUTED}}}"
        f".nm{{fill:{BRIGHT};font-weight:700}}.ds{{fill:{MUTED}}}"
        f".kw{{fill:{VIOLET}}}.cm2{{fill:#8b949e}}"
        f".blink{{animation:blink 1.1s steps(1,end) infinite}}"
        f"@keyframes blink{{0%,50%{{opacity:1}}50.01%,100%{{opacity:0}}}}"
        + "".join(sc.css)
        + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    )


def svg_doc(w, h, title, desc, defs, css, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-labelledby="t d">\n'
        f'<title id="t">{escape(title)}</title>\n<desc id="d">{escape(desc)}</desc>\n'
        f'<defs>{defs}</defs>\n<style>{css}</style>\n{body}\n</svg>\n'
    )


def titlebar(WX, WY, WW):
    """Windows-Terminal style tab strip: tab, +, chevron and window controls."""
    top, tx, cy, ctl = WY + 40, WX + 12, WY + 24, "#8b949e"
    return (
        f'<rect x="{WX}" y="{WY}" width="{WW}" height="40" fill="{BAR}"/>'
        f'<path d="M{tx},{top} V{WY + 16} a8,8 0 0 1 8,-8 H{tx + 162} a8,8 0 0 1 8,8 V{top} Z" fill="{BG}"/>'
        f'<rect x="{tx + 12}" y="{cy - 8}" width="16" height="16" rx="3.5" fill="#1b2028" stroke="#3a424d"/>'
        f'<path d="M{tx + 16.5},{cy - 3.5} l3.5,3.5 l-3.5,3.5 M{tx + 22},{cy + 3.5} h3.5" fill="none" '
        f'stroke="{MINT}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<text x="{tx + 36}" y="{cy + 4.2}" class="ui">Command Prompt</text>'
        f'<path d="M{tx + 145},{cy - 3.5} l7,7 M{tx + 152},{cy - 3.5} l-7,7" stroke="{MUTED}" '
        f'stroke-width="1.1" stroke-linecap="round"/>'
        f'<path d="M{tx + 193},{cy} h10 M{tx + 198},{cy - 5} v10" stroke="{ctl}" stroke-width="1.1" stroke-linecap="round"/>'
        f'<path d="M{tx + 219},{cy - 2} l4,4 l4,-4" fill="none" stroke="{ctl}" stroke-width="1.1" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M{WX + WW - 115},{cy} h10" stroke="{ctl}" stroke-width="1"/>'
        f'<rect x="{WX + WW - 75.5}" y="{cy - 5.5}" width="10" height="10" rx="1.5" fill="none" stroke="{ctl}"/>'
        f'<path d="M{WX + WW - 35},{cy - 5} l10,10 M{WX + WW - 25},{cy - 5} l-10,10" stroke="{ctl}" '
        f'stroke-width="1" stroke-linecap="round"/>'
    )


# ═══════════════════════════════ TERMINAL ═════════════════════════════
def terminal():
    T = 23.0
    sc = Scene(T)
    W = 760
    WX, WY = 24, 18
    WW = W - 2 * WX
    TOP = WY + 40
    X0 = WX + 24
    ty = Typed(sc, X0)
    body = []

    def out(y_top, parts, t_on, x=X0):
        body.append(f'<g class="{sc.appear(t_on)}">{seg_line(x, y_top + 15, parts)[0]}</g>')

    y = TOP + 20

    # 1 - fastfetch ---------------------------------------------------
    t_a1 = 0.6
    body.append(ty.command(y, [("fastfetch", "cm")], t_a1))
    y += LH
    t_fetch = t_a1 + 0.45 + 9 * 0.07 + 0.35 + 0.1

    IX = X0 + 26 * CW                                  # info column
    cell, blk = 16, 14                                 # pixel-logo geometry
    ly = y + 30
    N = ["X...X", "XX..X", "X.X.X", "X..XX", "X...X", "X...X", "X...X"]
    K = ["X...X", "X..X.", "X.X..", "XX...", "X.X..", "X..X.", "X...X"]
    main, shadow = [], []
    for r in range(7):
        for gi, glyph in enumerate((N, K)):
            for c in range(5):
                if glyph[r][c] == "X":
                    gx, gy = X0 + (gi * 6 + c) * cell, ly + r * cell
                    main.append(f'<rect x="{gx}" y="{gy}" width="{blk}" height="{blk}" rx="2.5"/>')
                    shadow.append(f'<rect x="{gx + 4}" y="{gy + 4}" width="{blk}" height="{blk}" rx="2.5"/>')
    body.append(
        f'<g class="{sc.appear(t_fetch)}"><g fill="#0c4a3a" opacity=".85">{"".join(shadow)}</g>'
        f'<g fill="url(#lg)">{"".join(main)}</g></g>'
    )

    u, h = USER_HOST
    rows = [[(u, "us"), ("@", "pg"), (h, "us")], [("\u2500" * (len(u) + 1 + len(h)), "pg")]]
    for key, val in INFO:
        parts = [(key, "ky"), (" " * (8 - len(key)), None)]
        for i, tok in enumerate(val.split(" \u00b7 ")):
            if i:
                parts += [(" ", None), ("\u00b7", "sp"), (" ", None)]
            parts.append((tok, "vl"))
        rows.append(parts)
    for i, parts in enumerate(rows):
        out(y + i * LH, parts, t_fetch + 0.09 * i, x=IX)

    cb_y = y + len(rows) * LH + 6
    sw = "".join(
        f'<rect x="{IX + i * 20:.1f}" y="{cb_y}" width="14" height="14" rx="3" fill="{c}"/>'
        for i, c in enumerate(SWATCH)
    )
    body.append(f'<g class="{sc.appear(t_fetch + 0.09 * len(rows))}">{sw}</g>')
    y = cb_y + 14 + 12

    # 2 - tree projects ------------------------------------------------
    t_a2 = 4.4
    body.append(ty.command(y, [("tree", "cm"), (" ", None), ("projects", "cm")], t_a2))
    y += LH
    t_tree = t_a2 + 0.45 + 13 * 0.07 + 0.35 + 0.08
    for i, (name, desc) in enumerate(TREE):
        con = "\u2514\u2500\u2500" if i == len(TREE) - 1 else "\u251c\u2500\u2500"
        out(y, [(con, "pg"), (" ", None), (name, "nm"), (" " * (13 - len(name)), None), (desc, "ds")],
            t_tree + i * 0.12)
        y += LH
    y += GAP

    # 3 - start <website> (cursor keeps blinking here) -----------------
    body.append(ty.command(y, [("start", "cm"), (" ", None), (WEBSITE, "lk")], 7.7, final=True))
    y += LH

    WH = (y + 22) - WY
    H = WY + WH + 20
    sc.screen(0.35, 21.6, 22.3)

    defs = (
        '<filter id="sh" x="-10%" y="-10%" width="120%" height="130%" color-interpolation-filters="sRGB">'
        '<feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000" flood-opacity=".32"/></filter>'
        f'<clipPath id="win"><rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" rx="12"/></clipPath>'
        f'<linearGradient id="lg" gradientUnits="userSpaceOnUse" x1="0" y1="{ly}" x2="0" y2="{ly + 7 * cell}">'
        f'<stop offset="0" stop-color="{MINT}"/><stop offset=".55" stop-color="{CYAN}"/>'
        f'<stop offset="1" stop-color="{BLUE}"/></linearGradient>'
    )
    shell = (
        f'<g filter="url(#sh)"><rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" rx="12" fill="#000"/></g>\n'
        f'<rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" rx="12" fill="{BG}"/>\n'
        f'<g clip-path="url(#win)">{titlebar(WX, WY, WW)}\n'
        f'<rect x="{WX + WW - 11}" y="{TOP + 10}" width="4" height="96" rx="2" fill="#1b212a"/>\n'
        f'<g class="scr">{"".join(body)}</g></g>\n'
        f'<rect x="{WX + .5}" y="{WY + .5}" width="{WW - 1}" height="{WH - 1}" rx="11.5" fill="none" stroke="{LINE}"/>'
    )
    return svg_doc(
        W, H, "Nima Kheradi - command prompt",
        f"Animated Windows-style command prompt: a fastfetch card, a tree of projects and a link to {WEBSITE}.",
        defs, base_css(sc), shell,
    )


# ═══════════════════════════════ FOOTER ═══════════════════════════════
def footer():
    T = 12.0
    sc = Scene(T)
    W, H = 760, 77
    WX, WY, WW, WH = 24, 21, 712, 48
    ty = Typed(sc, WX + 24)
    row = ty.command(WY + (WH - LH) / 2, [("rem", "kw"), (" ", None), (FOOTER_TEXT, "cm2")],
                     0.5, final=True, per_char=0.06)
    sc.screen(0.3, 10.4, 11.2)
    shell = (
        f'<rect x="{WX + .5}" y="{WY + .5}" width="{WW - 1}" height="{WH - 1}" rx="12" fill="{BG}" stroke="{LINE}"/>\n'
        f'<g class="scr">{row}</g>'
    )
    return svg_doc(W, H, "Thanks for stopping by", f"C:\\Users\\Nima> rem {FOOTER_TEXT}",
                   "", base_css(sc), shell)


# ═════════════════════════════ PROJECT CARDS ══════════════════════════
# Two cards sit side by side under the terminal. Each image is 360px wide with a 6px
# transparent inset, so the pair lines up exactly with the 712px terminal window above.
CARD_W, CARD_INSET, CARD_PX = 360, 6, 28
PILL_Y0, PILL_ROW = 142, 28


def pill_w(tag):
    return len(tag) * 6.3 + 14


def pill_rows(tags, avail, gap=6):
    """One row if the tags fit, otherwise the most evenly balanced two rows."""
    width = lambda ts: sum(pill_w(t) for t in ts) + gap * (len(ts) - 1)
    if width(tags) <= avail:
        return [tags]
    _, k = min((max(width(tags[:k]), width(tags[k:])), k) for k in range(1, len(tags)))
    return [tags[:k], tags[k:]]


def card_height(rows):
    return PILL_Y0 + PILL_ROW * rows - 6 + 20


def card(p, rows, H):
    W, A, PX = CARD_W, CARD_INSET, CARD_PX
    R = W - PX                                   # right edge of the text area
    pills = []
    for r, row in enumerate(rows):
        x, y = PX, PILL_Y0 + r * PILL_ROW
        for t in row:
            w = pill_w(t)
            pills.append(
                f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="22" rx="11" fill="{BAR}" stroke="{LINE}"/>'
                f'<text x="{x + 7:.1f}" y="{y + 15}" textLength="{len(t) * 6.3:.1f}" lengthAdjust="spacing" '
                f'class="pt">{escape(t)}</text>'
            )
            x += w + 6
    status, sw = "in development", 14 * 6.6
    css = (
        f".lb,.st{{font-family:{MONO};font-size:11px}}.lb{{fill:{MUTED}}}.st{{fill:#8b949e}}"
        f".tt{{font-family:{SANS};font-size:26px;font-weight:700;letter-spacing:-.4px;fill:{BRIGHT}}}"
        f".dd{{font-family:{SANS};font-size:13.5px;fill:#9da7b3}}"
        f".pt{{font-family:{MONO};font-size:10.5px;fill:#9da7b3}}"
        f".dot{{animation:pl 2.2s ease-in-out infinite}}"
        f".ring{{transform-box:fill-box;transform-origin:center;animation:ping 2.2s ease-out infinite}}"
        "@keyframes pl{0%,100%{opacity:1}50%{opacity:.35}}"
        "@keyframes ping{0%{transform:scale(1);opacity:.7}75%,100%{transform:scale(3);opacity:0}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}.ring{opacity:0}}"
    )
    defs = (
        f'<radialGradient id="gl" gradientUnits="userSpaceOnUse" cx="{A + 40}" cy="0" r="250">'
        f'<stop offset="0" stop-color="{MINT}" stop-opacity=".14"/>'
        f'<stop offset="1" stop-color="{MINT}" stop-opacity="0"/></radialGradient>'
    )
    frame = f'x="{A + .5}" y=".5" width="{W - 2 * A - 1}" height="{H - 1}" rx="14"'
    body = (
        f'<rect {frame} fill="{BG}" stroke="{LINE}"/>\n<rect {frame} fill="url(#gl)"/>\n'
        f'<text x="{PX}" y="34" textLength="{len(p["path"]) * 6.6:.1f}" lengthAdjust="spacing" '
        f'class="lb">{escape(p["path"])}</text>\n'
        f'<circle class="ring" cx="{R - sw - 12:.1f}" cy="30" r="3.5" fill="none" stroke="{MINT}"/>'
        f'<circle class="dot" cx="{R - sw - 12:.1f}" cy="30" r="3.5" fill="{MINT}"/>'
        f'<text x="{R - sw:.1f}" y="34" textLength="{sw:.1f}" lengthAdjust="spacing" class="st">{status}</text>\n'
        f'<text x="{PX}" y="78" class="tt">{escape(p["name"])}</text>\n'
        f'<text x="{PX}" y="104" class="dd">{escape(p["desc"][0])}</text>\n'
        f'<text x="{PX}" y="124" class="dd">{escape(p["desc"][1])}</text>\n' + "".join(pills)
    )
    return svg_doc(W, H, f'{p["name"]} - project', " ".join(p["desc"]), defs, css, body)


# ═════════════════════════════════ MAIN ═══════════════════════════════
def main():
    OUT.mkdir(exist_ok=True)
    files = {"terminal.svg": terminal(), "footer.svg": footer()}
    avail = CARD_W - 2 * CARD_PX
    rows = {p["slug"]: pill_rows(p["tags"], avail) for p in PROJECTS}
    H = max(card_height(len(r)) for r in rows.values())      # equal heights keep the pair aligned
    for p in PROJECTS:
        files[f'project-{p["slug"]}.svg'] = card(p, rows[p["slug"]], H)
    for name, svg in files.items():
        (OUT / name).write_text(svg, encoding="utf-8")
        print(f"wrote assets/{name}  ({len(svg) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
