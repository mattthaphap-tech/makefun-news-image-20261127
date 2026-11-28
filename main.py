#!/usr/bin/env python3
"""make.fun news-image-20261127 entry (v2 revision).

Renders the Friday 27 November 2026 front page in code (PIL) and writes
it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png),
verifying it with validate_png() (genuine, fully decodable PNG, exactly
1024x1024). A copy next to this file (entry.png) is written only on a
best-effort basis: the grader mounts the repository read-only, so that
copy must never fail the run. Runs with no network. Deterministic: same
bytes every run.

v2 applies the winner study of the 26 Nov edition
(~/workspace/makefun-news-image-20261126/winner-study-26nov.md):
full-day research (round 2, after the UTC day ended), 41 stories across
11 regions, the winners' frame (giant coloured number strip, region chips,
UTC timeline, world map with numbered pins, trust legend with coloured
pill badges, red serif-italic subhead naming the 3 leads, WHY IT MATTERS
lines, full-scene lead illustrations with data badges inside the picture).
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_LOCAL = os.path.join(HERE, "entry.png")
# The grader sets MAKEFUN_OUTPUT_DIR=/output and mounts the repository
# read-only, so the output must go here, never to the script directory.
DST_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DST = os.path.join(DST_DIR, "entry.png")
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024

# ---------------------------------------------------------------- colours
PAPER = (246, 241, 229)
INK = (25, 25, 25)
RED = (185, 28, 28)
RED_LT = (248, 113, 113)
NAVY = (22, 35, 63)
NAVY_BG = (30, 58, 95)
GOLD = (245, 158, 11)
TEAL = (45, 212, 191)
GREEN = (21, 128, 61)
BLUE = (29, 78, 216)
ORANGE = (234, 88, 12)
GREY = (87, 83, 78)
LINE = (25, 25, 25)
SEA = (220, 231, 236)
LAND = (183, 196, 168)
LAND_EDGE = (120, 135, 110)

REGION_COLORS = {
    "EUROPE": (29, 78, 216),
    "UKRAINE WAR": (153, 27, 27),
    "MIDDLE EAST": (180, 83, 9),
    "N. AFRICA": (15, 118, 110),
    "SUB-SAHARAN AFRICA": (21, 128, 61),
    "S. ASIA": (126, 34, 206),
    "E. ASIA": (220, 38, 38),
    "SE ASIA": (234, 88, 12),
    "OCEANIA": (8, 145, 178),
    "AMERICAS": (30, 58, 95),
    "GLOBAL": (87, 83, 78),
}
TRUST_COLORS = {
    "OFFICIAL": (29, 78, 216),
    "CONFIRMED": (21, 128, 61),
    "REPORTED": (234, 88, 12),
    "CLAIM": (220, 38, 38),
}

TITLE = "Friday 27 November 2026 — 41 stories, 11 regions: EU summit ends with no deal, Gaza toll rises, Asian shares rally"
SUBHEAD = ("EU summit ends with no budget deal and the \u20ac45bn Ukraine loan on hold"
           " \u00b7 Gaza toll rises as ceasefire frays"
           " \u00b7 Asian shares rally on China stimulus")

NUMBERS = [
    ("\u20ac45bn", "Ukraine loan on hold", GOLD),
    ("961,000", "without power", (255, 255, 255)),
    ("155", "drones at Ukraine", RED_LT),
    ("+4.2%", "Kospi", TEAL),
    ("19", "killed in Gaza", (255, 255, 255)),
    ("$97.71", "Brent crude", GOLD),
]

REGIONS = [
    ("EUROPE", 4), ("UKRAINE WAR", 2), ("MIDDLE EAST", 3), ("N. AFRICA", 1),
    ("SUB-SAHARAN AFRICA", 8), ("S. ASIA", 5), ("E. ASIA", 3), ("SE ASIA", 4),
    ("OCEANIA", 1), ("AMERICAS", 9), ("GLOBAL", 1),
]

TIMELINE = [
    ("00:30", "Storm peak: 961,000 without power"),
    ("01:30", "EU summit ends, no deal"),
    ("02:10", "Nvidia halt reported"),
    ("08:03", "Jazan refinery strike reported"),
    ("13:30", "F1 practice opens, Lusail"),
    ("14:30", "US markets reopen"),
]

# ------------------------------------------------------------------- data
# Leads: full scenes, headline, 3-4 line summary, WHY IT MATTERS line.
LEADS = [
    {
        "num": 1, "region": "EUROPE", "badge": "OFFICIAL",
        "source": "CONSILIUM",
        "headline": "EU summit ends with no deal; de Cos to lead the ECB",
        "summary": ("No deal on the 2028\u20132034 budget (\u20ac1.78tn) and no final "
                    "decision on a \u20ac45bn loan for Ukraine in 2027; 24 of 27 "
                    "states backed the loan, but Germany ties budget backing "
                    "to all 27 sharing it."),
        "wim": "Europe's money for Ukraine \u2014 and its own budget \u2014 now both wait until December.",
        "scene": "eu",
        "badges": [("NO DEAL", RED), ("\u20ac45BN ON HOLD", GOLD)],
    },
    {
        "num": 2, "region": "MIDDLE EAST", "badge": "CONFIRMED",
        "source": "ANADOLU",
        "headline": "Gaza toll rises despite ceasefire",
        "summary": ("19 Palestinians killed, 48 injured in Israeli strikes, the "
                    "Gaza health ministry said in a 48-hour toll reported "
                    "Friday; 10 were killed on Thursday, including senior "
                    "Hamas official Khaled Abu Nada."),
        "wim": "The ceasefire is fraying days after it began.",
        "scene": "gaza",
        "badges": [("19 KILLED", RED), ("48 INJURED", (255, 255, 255))],
    },
    {
        "num": 3, "region": "E. ASIA", "badge": "CONFIRMED",
        "source": "REUTERS",
        "headline": "Asian shares rally on Friday",
        "summary": ("Nikkei +2.0%, Kospi +4.2%, Hang Seng +2.1%, Shanghai +3.2% "
                    "as China rolled out more capital-market support; Tokyo "
                    "core CPI rose 2.9% in November, its fastest since July "
                    "2025."),
        "wim": "Asia's best day in weeks as Beijing opens the taps again.",
        "scene": "asia",
        "badges": [("+4.2% KOSPI", GOLD), ("NIKKEI +2.0%", (255, 255, 255))],
    },
]

# Minis: small scenes + headline + source line.
MINIS = [
    {"num": 4, "region": "MIDDLE EAST", "badge": "CONFIRMED", "source": "REUTERS",
     "headline": "Houthis hit Saudi refinery; 50 targets struck in reply",
     "scene": "yemen"},
    {"num": 5, "region": "UKRAINE WAR", "badge": "REPORTED", "source": "KYIV POST",
     "headline": "Russia fires 155 drones at Ukraine overnight; 110 downed",
     "scene": "drones"},
    {"num": 6, "region": "AMERICAS", "badge": "CONFIRMED", "source": "NWS",
     "headline": "Thanksgiving storm: 961,000 without power at its peak",
     "scene": "storm"},
    {"num": 7, "region": "OCEANIA", "badge": "OFFICIAL", "source": "REUTERS",
     "headline": "NZ count: coalition one seat short; kingmaker holds seven",
     "scene": "nz"},
    {"num": 8, "region": "SE ASIA", "badge": "REPORTED", "source": "CNA",
     "headline": "Nvidia reportedly halts chip shipments to four SE Asian states",
     "scene": "chip"},
    {"num": 9, "region": "MIDDLE EAST", "badge": "OFFICIAL", "source": "FORMULA 1",
     "headline": "F1 Qatar: Antonelli sweeps Friday practice for Mercedes",
     "scene": "f1"},
    {"num": 10, "region": "EUROPE", "badge": "CONFIRMED", "source": "REUTERS",
     "headline": "Drone violates Latvian airspace; NATO jets scrambled",
     "scene": "latvia"},
    {"num": 11, "region": "S. ASIA", "badge": "REPORTED", "source": "THE HINDU",
     "headline": "Lok Sabha seats may rise by half under delimitation plan",
     "scene": "parliament"},
    {"num": 12, "region": "AMERICAS", "badge": "CONFIRMED", "source": "MARKETS",
     "headline": "US markets reopen; Wall Street heads for best week in a year",
     "scene": "markets"},
    {"num": 13, "region": "UKRAINE WAR", "badge": "CLAIM", "source": "AJP",
     "headline": "Ukraine downs jet drone with a laser, first time",
     "scene": "laser"},
    {"num": 14, "region": "S. ASIA", "badge": "CONFIRMED", "source": "ESPNCRICINFO",
     "headline": "India\u2013NZ 2nd Test begins at Christchurch",
     "scene": "cricket"},
    {"num": 15, "region": "AMERICAS", "badge": "CONFIRMED", "source": "RETAILERS",
     "headline": "Black Friday sales open across the US",
     "scene": "blackfriday"},
]

# Briefs: (number, region, headline, source)
BRIEFS = [
    (16, "EUROPE", "Finland: Stubb signs border closure extension today", "VALTIONEUVOSTO"),
    (17, "EUROPE", "Spain concludes general election campaign; votes Sunday", "AP"),
    (18, "S. ASIA", "Chandrayaan-5 / LUPEX rover prototype unveiled", "THE HINDU"),
    (19, "S. ASIA", "India, UAE to speed up joint next-gen defence gear", "THE HINDU"),
    (20, "S. ASIA", "India top court: PMLA benches need a judicial member", "IQMIA"),
    (21, "SE ASIA", "StarHub was 'only realistic merger partner' for M1", "CNA"),
    (22, "SE ASIA", "Singapore median income rises to S$6,021", "CNA"),
    (23, "SE ASIA", "Laos leaves UN development list after 55 years", "CNA"),
    (24, "AMERICAS", "Canada's US tariff talks could extend into January", "THE INDEPENDENT SG"),
    (25, "AMERICAS", "Canada top court largely upholds Quebec secularism law", "AJP"),
    (26, "AMERICAS", "US Army deploys first hypersonic weapon battery", "AJP"),
    (27, "AMERICAS", "Venezuela considers easing curbs on opposition figures", "OPEN CHRONICLE"),
    (28, "AMERICAS", "College football Black Friday: 13 FBS games", "ESPN"),
    (29, "N. AFRICA", "Morocco to invest $222m in tourism in 2027", "AJP"),
    (30, "SUB-SAHARAN AFRICA", "South Sudan's Kiir lifts emergency in four states", "WISDOM GENERAL"),
    (31, "SUB-SAHARAN AFRICA", "Atiku, Obi, Makinde meet Monday as 2027 lines form", "PUNCH"),
    (32, "SUB-SAHARAN AFRICA", "17 victims of Plateau attack get mass burial", "PUNCH"),
    (33, "SUB-SAHARAN AFRICA", "Kwara jailbreak: three inmates die, two escape", "PUNCH"),
    (34, "SUB-SAHARAN AFRICA", "FG clears pension backlog accumulated since 2013", "PUNCH"),
    (35, "SUB-SAHARAN AFRICA", "INEC, NSA read riot act to violence sponsors", "PUNCH"),
    (36, "SUB-SAHARAN AFRICA", "NHI deterring foreign investors, says Life Healthcare CEO", "NEWS24"),
    (37, "SUB-SAHARAN AFRICA", "Mahama hands over three aircraft to Ghana Air Force", "DAILY GRAPHIC"),
    (38, "GLOBAL", "UN names 16 hunger hotspots", "OPEN CHRONICLE"),
    (39, "E. ASIA", "Taiwan holds local elections Saturday", "AJP"),
    (40, "E. ASIA", "China issues five-year plan to expand defence education", "AJP"),
    (41, "AMERICAS", "Trump rewrites NATO statement to add Ukraine", "POLITICO"),
]

DATE_CHECK = ("Left out on purpose \u2014 earlier news: Kuwait drone kills 2 Italians "
              "(26 Nov) \u00b7 Bangkok refinery blast (26 Nov) \u00b7 Ebola 12,021 cases "
              "(26 Nov data) \u00b7 Pete Edochie died 25 Nov \u00b7 COP31 ended 22 Nov "
              "\u00b7 Trump \u201cpull back\u201d post (26 Nov).")

FOOTER_SOURCES = ("Sources: Reuters \u00b7 Consilium \u00b7 Xinhua \u00b7 AP \u00b7 CNA \u00b7 "
                  "The Hindu \u00b7 Anadolu \u00b7 Punch \u00b7 News24 \u00b7 ESPNcricinfo \u00b7 "
                  "NCC \u00b7 MOM \u00b7 F1 \u00b7 CNN \u00b7 Rigzone \u00b7 Kyiv Post \u00b7 Politico.")

# ------------------------------------------------------------------- fonts
FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/noto",
]


def _find_font(names):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.isfile(p):
                return p
    return None


def _truetype_or_default(p, size):
    """Load a TrueType font, falling back to PIL's default on any failure.

    A font file that exists but cannot be read must never fail the run
    (the grader image may ship different fonts); the fallback only
    changes output when truetype() itself raises.
    """
    if p:
        try:
            return ImageFont.truetype(p, size)
        except Exception as exc:  # unreadable or corrupt font file
            print(f"warning: cannot load font {p}: {exc}; using default",
                  file=sys.stderr)
    return ImageFont.load_default(size)


def font_serif_bold(size):
    p = _find_font(["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf",
                    "NotoSerif-Bold.ttf"])
    return _truetype_or_default(p, size)


def font_serif(size):
    p = _find_font(["DejaVuSerif.ttf", "LiberationSerif-Regular.ttf",
                    "NotoSerif-Regular.ttf"])
    return _truetype_or_default(p, size)


def font_serif_italic(size):
    p = _find_font(["NotoSerif-SemiBoldItalic.ttf", "NotoSerif-Italic.ttf",
                    "LiberationSerif-Italic.ttf", "DejaVuSerif.ttf"])
    return _truetype_or_default(p, size)


def font_sans_bold(size):
    p = _find_font(["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf",
                    "NotoSans-Bold.ttf"])
    return _truetype_or_default(p, size)


def font_sans(size):
    p = _find_font(["DejaVuSans.ttf", "LiberationSans-Regular.ttf",
                    "NotoSans-Regular.ttf"])
    return _truetype_or_default(p, size)


# ------------------------------------------------------------------ helpers
def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines fitting width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, width, fill, spacing=3, max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap(draw, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def pill(draw, x, y, text, fnt, bg, fg=(255, 255, 255), pad_x=6, pad_y=2):
    """Coloured rounded pill with centred text; returns width used."""
    w = int(text_w(draw, text, fnt)) + 2 * pad_x
    h = fnt.size + 2 * pad_y
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    draw.text((x + pad_x, y + pad_y - 1), text, font=fnt, fill=fg)
    return w


def num_badge(draw, x, y, n, color, r=9):
    draw.ellipse([x, y, x + 2 * r, y + 2 * r], fill=color)
    f = font_sans_bold(11 if n < 10 else 10)
    t = str(n)
    tw = text_w(draw, t, f)
    draw.text((x + r - tw / 2, y + r - 7), t, font=f, fill=(255, 255, 255))
    return 2 * r

# ------------------------------------------------------------- scene art
# Every picture is drawn in code (PIL shapes), not photos. Lead scenes
# are full dramatic scenes; mini scenes are small illustrated panels.


def _stars(draw, box, n, seed=7):
    import random
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x = rnd.randint(x0 + 2, x1 - 2)
        y = rnd.randint(y0 + 2, y1 - 2)
        r = rnd.choice([1, 1, 2])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 220))


def _skyline(draw, box, color, seed=3):
    import random
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    x = x0
    while x < x1:
        w = rnd.randint(14, 30)
        h = rnd.randint(12, y1 - y0 - 6)
        draw.rectangle([x, y1 - h, x + w, y1], fill=color)
        for wy in range(y1 - h + 4, y1 - 4, 7):
            for wx in range(x + 3, x + w - 3, 7):
                if rnd.random() < 0.5:
                    draw.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 220, 120))
        x += w + 2


def paint_lead_scene(draw, kind, box):
    """Draw the lead illustration inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if kind == "eu":
        draw.rectangle(box, fill=(16, 24, 48))
        _stars(draw, (x0, y0, x1, y0 + h // 2), 26, seed=11)
        draw.ellipse([x1 - 52, y0 + 8, x1 - 22, y0 + 38], fill=(245, 200, 90))
        # council building: round-topped block with lit windows
        draw.rounded_rectangle([x0 + 18, y0 + 42, x1 - 18, y1], radius=10,
                               fill=(52, 68, 104))
        draw.rounded_rectangle([x0 + 18, y0 + 42, x1 - 18, y0 + 56], radius=8,
                               fill=(70, 88, 130))
        for r in range(3):
            for c in range(9):
                wx = x0 + 30 + c * 28
                wy = y0 + 62 + r * 13
                draw.rectangle([wx, wy, wx + 14, wy + 8],
                               fill=(255, 220, 120) if (r + c) % 3 else (90, 110, 150))
        # EU stars circle
        import math
        cx, cy = x0 + 52, y0 + 26
        for k in range(12):
            a = 2 * math.pi * k / 12 - math.pi / 2
            sx = cx + 15 * math.cos(a)
            sy = cy + 11 * math.sin(a)
            draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(245, 200, 90))
    elif kind == "gaza":
        draw.rectangle(box, fill=(43, 32, 26))
        _stars(draw, (x0, y0, x1, y0 + h // 3), 14, seed=21)
        # smoke columns
        for sx, sw in ((x0 + 40, 26), (x0 + 150, 34), (x0 + 250, 22)):
            for i in range(4):
                yy = y0 + 8 + i * 12
                draw.ellipse([sx + (i % 2) * 6 - sw // 2, yy, sx + (i % 2) * 6 + sw // 2,
                              yy + 16], fill=(120, 110, 100))
        # fires
        for fx in (x0 + 60, x0 + 180, x0 + 265):
            draw.polygon([(fx, y1 - 46), (fx + 12, y1 - 18), (fx + 24, y1 - 46)],
                         fill=(234, 88, 12))
            draw.polygon([(fx + 5, y1 - 38), (fx + 12, y1 - 22), (fx + 19, y1 - 38)],
                         fill=(245, 158, 11))
        _skyline(draw, (x0, y1 - 26, x1, y1), (20, 16, 14), seed=5)
    elif kind == "asia":
        draw.rectangle(box, fill=(8, 60, 52))
        _skyline(draw, (x0, y1 - 34, x1, y1), (6, 40, 36), seed=9)
        # rising market line with dots
        pts = [(x0 + 10, y1 - 26), (x0 + 70, y1 - 44), (x0 + 120, y1 - 36),
               (x0 + 180, y1 - 58), (x0 + 240, y1 - 50), (x0 + 300, y1 - 76)]
        draw.line(pts, fill=(45, 212, 191), width=4)
        for px, py in pts:
            draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 255, 255))
        draw.polygon([(x0 + 300, y1 - 76), (x0 + 288, y1 - 70), (x0 + 300, y1 - 62)],
                     fill=(45, 212, 191))


def paint_mini_scene(draw, kind, box):
    """Draw a small illustrated panel inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if kind == "yemen":
        draw.rectangle(box, fill=(40, 26, 20))
        for tx in (x0 + 26, x0 + 96, x0 + 166):
            draw.rectangle([tx, y0 + 14, tx + 22, y1 - 8], fill=(90, 80, 70))
            draw.rectangle([tx + 6, y0 + 6, tx + 16, y0 + 14], fill=(120, 110, 100))
        draw.polygon([(x0 + 200, y0 + 30), (x0 + 208, y0 + 10), (x0 + 216, y0 + 30)],
                     fill=(245, 158, 11))
        draw.polygon([(x0 + 204, y0 + 30), (x0 + 208, y0 + 18), (x0 + 212, y0 + 30)],
                     fill=(234, 88, 12))
    elif kind == "drones":
        draw.rectangle(box, fill=(16, 24, 48))
        _stars(draw, box, 10, seed=31)
        for dx, dy in ((x0 + 40, y0 + 12), (x0 + 110, y0 + 22), (x0 + 180, y0 + 10)):
            draw.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(255, 255, 255))
            draw.line([dx - 8, dy, dx + 8, dy], fill=(200, 200, 200), width=1)
        draw.ellipse([x0 + 130, y0 + 26, x0 + 150, y0 + 42], fill=(248, 113, 113))
        for a in range(8):
            import math
            ang = 2 * math.pi * a / 8
            draw.line([x0 + 140 + 10 * math.cos(ang), y0 + 34 + 8 * math.sin(ang),
                       x0 + 140 + 16 * math.cos(ang), y0 + 34 + 12 * math.sin(ang)],
                      fill=(248, 113, 113), width=2)
    elif kind == "storm":
        draw.rectangle(box, fill=(51, 65, 85))
        for cx in (x0 + 40, x0 + 120, x0 + 190):
            draw.ellipse([cx - 26, y0 + 6, cx + 26, y0 + 24], fill=(30, 41, 59))
        draw.polygon([(x0 + 108, y0 + 22), (x0 + 96, y0 + 40), (x0 + 106, y0 + 40),
                      (x0 + 98, y0 + 52), (x0 + 118, y0 + 30), (x0 + 108, y0 + 30)],
                     fill=(245, 200, 90))
        for rx in range(x0 + 10, x1 - 6, 14):
            draw.line([rx, y0 + 30, rx - 3, y0 + 40], fill=(147, 197, 253), width=1)
    elif kind == "nz":
        draw.rectangle(box, fill=(8, 90, 90))
        draw.rounded_rectangle([x0 + 90, y0 + 8, x0 + 150, y1 - 6], radius=12,
                               fill=(220, 230, 230))
        for wy in range(y0 + 14, y1 - 10, 8):
            draw.line([x0 + 98, wy, x0 + 142, wy], fill=(120, 140, 140), width=1)
        draw.rectangle([x0 + 20, y0 + 26, x0 + 70, y1 - 6], fill=(255, 255, 255))
        draw.polygon([(x0 + 20, y0 + 26), (x0 + 45, y0 + 12), (x0 + 70, y0 + 26)],
                     fill=(200, 30, 30))
    elif kind == "chip":
        draw.rectangle(box, fill=(10, 30, 20))
        draw.rounded_rectangle([x0 + 80, y0 + 10, x0 + 160, y1 - 10], radius=6,
                               fill=(21, 128, 61), outline=(45, 212, 191), width=2)
        for px in range(x0 + 88, x0 + 156, 12):
            draw.line([px, y0 + 4, px, y0 + 10], fill=(45, 212, 191), width=2)
            draw.line([px, y1 - 10, px, y1 - 4], fill=(45, 212, 191), width=2)
        f = font_sans_bold(13)
        draw.text((x0 + 108, y0 + 16), "AI", font=f, fill=(255, 255, 255))
    elif kind == "f1":
        draw.rectangle(box, fill=(12, 12, 18))
        draw.arc([x0 + 10, y0 - 30, x1 + 60, y1 + 30], start=200, end=340,
                 fill=(200, 200, 200), width=5)
        draw.rectangle([x0 + 150, y0 + 16, x0 + 178, y0 + 28], fill=(220, 38, 38))
        draw.rectangle([x0 + 158, y0 + 10, x0 + 170, y0 + 16], fill=(255, 255, 255))
        for i in range(4):
            c = (255, 255, 255) if i % 2 == 0 else (0, 0, 0)
            draw.rectangle([x0 + 200 + i * 8, y0 + 6, x0 + 208 + i * 8, y0 + 14],
                           fill=c)
    elif kind == "latvia":
        draw.rectangle(box, fill=(70, 90, 120))
        for r in (10, 20, 30):
            draw.arc([x0 + 110 - r, y0 + 34 - r, x0 + 110 + r, y0 + 34 + r],
                     start=300, end=60, fill=(255, 255, 255), width=2)
        draw.rectangle([x0 + 100, y0 + 14, x0 + 120, y0 + 20], fill=(30, 30, 30))
        for ox, oy in ((x0 + 96, y0 + 10), (x0 + 124, y0 + 10), (x0 + 96, y0 + 20),
                       (x0 + 124, y0 + 20)):
            draw.ellipse([ox - 4, oy - 2, ox + 4, oy + 2], fill=(30, 30, 30))
    elif kind == "parliament":
        draw.rectangle(box, fill=(180, 83, 9))
        draw.rectangle([x0 + 30, y0 + 22, x0 + 210, y1 - 6], fill=(255, 240, 200))
        draw.pieslice([x0 + 95, y0 + 2, x0 + 145, y0 + 26], start=180, end=360,
                      fill=(255, 240, 200))
        for cx in range(x0 + 44, x0 + 200, 26):
            draw.rectangle([cx, y0 + 28, cx + 8, y1 - 6], fill=(180, 83, 9))
    elif kind == "markets":
        draw.rectangle(box, fill=(8, 60, 40))
        pts = [(x0 + 8, y1 - 12), (x0 + 60, y1 - 24), (x0 + 110, y1 - 18),
               (x0 + 160, y1 - 34), (x0 + 210, y1 - 26), (x0 + 232, y1 - 40)]
        draw.line(pts, fill=(74, 222, 128), width=3)
        for px, py in pts:
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255))
    elif kind == "laser":
        draw.rectangle(box, fill=(10, 16, 40))
        _stars(draw, box, 12, seed=41)
        draw.line([x0 + 10, y1 - 10, x0 + 190, y0 + 12], fill=(34, 211, 238), width=3)
        draw.ellipse([x0 + 186, y0 + 8, x0 + 198, y0 + 20], fill=(255, 255, 255))
        draw.line([x0 + 182, y0 + 14, x0 + 202, y0 + 14], fill=(200, 200, 200), width=1)
    elif kind == "cricket":
        draw.rectangle(box, fill=(34, 120, 60))
        draw.rectangle([x0 + 90, y0 + 6, x0 + 150, y1 - 6], fill=(210, 180, 130))
        draw.ellipse([x0 + 170, y0 + 20, x0 + 178, y0 + 28], fill=(185, 28, 28))
        draw.rectangle([x0 + 40, y0 + 30, x0 + 52, y0 + 34], fill=(120, 70, 30))
    elif kind == "blackfriday":
        draw.rectangle(box, fill=(120, 20, 20))
        draw.rectangle([x0 + 95, y0 + 14, x0 + 145, y1 - 8], fill=(255, 255, 255))
        draw.arc([x0 + 105, y0 + 2, x0 + 135, y0 + 20], start=180, end=360,
                 fill=(255, 255, 255), width=3)
        draw.polygon([(x0 + 150, y0 + 26), (x0 + 168, y0 + 20), (x0 + 168, y0 + 34)],
                     fill=(245, 158, 11))
        f = font_sans_bold(11)
        draw.text((x0 + 104, y0 + 24), "SALE", font=f, fill=(185, 28, 28))
    else:
        draw.rectangle(box, fill=(200, 200, 200))


# ------------------------------------------------------------- world map
# Simplified equirectangular continents (lon, lat) polygons.
CONTINENTS = [
    [(-168, 66), (-150, 70), (-130, 71), (-110, 72), (-95, 80), (-85, 69),
     (-78, 71), (-72, 62), (-68, 48), (-74, 38), (-80, 26), (-86, 30),
     (-90, 21), (-96, 17), (-102, 19), (-110, 24), (-116, 30), (-122, 37),
     (-126, 46), (-134, 56), (-152, 59), (-165, 61)],
    [(-55, 60), (-42, 61), (-32, 68), (-24, 70), (-34, 76), (-55, 76),
     (-60, 70)],
    [(-80, 9), (-76, 4), (-70, 11), (-61, 6), (-51, 1), (-42, -4),
     (-35, -9), (-40, -20), (-48, -28), (-58, -35), (-66, -45),
     (-70, -52), (-72, -36), (-76, -20), (-80, -4)],
    [(-10, 36), (-4, 44), (-1, 46), (4, 52), (8, 57), (14, 58), (21, 60),
     (26, 66), (32, 70), (42, 68), (44, 60), (38, 55), (30, 50), (26, 45),
     (20, 40), (14, 38), (8, 37), (0, 36)],
    [(-6, 50), (-3, 53), (-5, 57), (-2, 58), (0, 52)],
    [(-10, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (40, 15),
     (48, 11), (51, 11), (45, 1), (40, -10), (35, -20), (30, -29),
     (20, -35), (15, -30), (11, -20), (8, -5), (5, 5), (-5, 5), (-10, 15),
     (-15, 25)],
    [(30, 70), (45, 68), (60, 69), (75, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (168, 66), (176, 62), (160, 56), (150, 46), (140, 40),
     (130, 34), (122, 30), (114, 23), (108, 18), (104, 9), (99, 8), (95, 15),
     (90, 22), (85, 20), (80, 14), (76, 8), (72, 22), (64, 25), (57, 28),
     (52, 33), (46, 39), (40, 44), (34, 50), (28, 60)],
    [(113, -22), (120, -15), (130, -12), (140, -17), (146, -20), (150, -26),
     (150, -35), (140, -38), (130, -32), (120, -33), (113, -30)],
    [(130, -2), (140, -5), (148, -8), (142, -8), (135, -4)],
]
# (number, lon, lat)
PINS = [
    (1, 4.35, 50.85), (2, 34.47, 31.5), (3, 139.7, 35.7), (4, 42.55, 16.9),
    (5, 30.5, 50.45), (6, -75.0, 39.0), (7, 174.8, -41.3), (8, 103.8, 1.35),
    (9, 51.5, 25.4), (10, 24.1, 56.95), (11, 77.2, 28.6), (12, -74.0, 40.7),
    (13, 33.5, 48.0), (14, 172.6, -43.5), (15, -71.0, 42.0),
]


def paint_map(draw, box):
    """Stylised world map with numbered pins for stories 1-15."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=SEA)
    def proj(lon, lat):
        return (x0 + (lon + 170) / 360.0 * w, y0 + (75 - lat) / 130.0 * h)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    f = font_sans_bold(8)
    for n, lon, lat in PINS:
        px, py = proj(lon, lat)
        r = 7
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        t = str(n)
        tw = text_w(draw, t, f)
        draw.text((px - tw / 2, py - 5.5), t, font=f, fill=(255, 255, 255))

# ------------------------------------------------------------------ layout
W, H = 1024, 1024
MX = 22
CW = W - 2 * MX


def _rich_wrap(draw, segments, fnt_bold, fnt, width):
    """Wrap [(text, bold), ...] words; returns list of [(text, bold)] lines."""
    words = []
    for text, bold in segments:
        for w_ in text.split(" "):
            if w_:
                words.append((w_, bold))
    lines, cur, cur_w = [], [], 0
    space_w = text_w(draw, " ", fnt)
    for w_, bold in words:
        ww = text_w(draw, w_, fnt_bold if bold else fnt)
        add = ww if not cur else ww + space_w
        if cur and cur_w + add > width:
            lines.append(cur)
            cur, cur_w = [(w_, bold)], ww
        else:
            cur.append((w_, bold))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def _draw_rich_line(draw, x, y, line, fnt_bold, fnt, fill):
    cx = x
    for i, (w_, bold) in enumerate(line):
        f = fnt_bold if bold else fnt
        draw.text((cx, y), w_, font=f, fill=fill)
        cx += text_w(draw, w_, f)
        if i < len(line) - 1:
            cx += text_w(draw, " ", fnt)
    return cx


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 8

    # ---- kicker + rule + title + subhead
    f_kick = font_sans_bold(14)
    f_kick_r = font_sans_bold(12)
    d.text((MX, y), "THE WORLD IN ONE DAY", font=f_kick, fill=RED)
    rt = "41 STORIES \u00b7 11 REGIONS \u00b7 ALL FROM THIS FRIDAY"
    d.text((W - MX - text_w(d, rt, f_kick_r), y + 1), rt, font=f_kick_r, fill=INK)
    y += 20
    d.line([MX, y, W - MX, y], fill=LINE, width=2)
    y += 6
    f_title = font_serif_bold(50)
    d.text((MX, y), "Friday 27 November 2026", font=f_title, fill=INK)
    y += 54
    f_sub = font_serif_italic(18)
    y = draw_wrapped(d, MX, y, SUBHEAD, f_sub, CW, RED, spacing=2)
    y += 2

    # ---- giant coloured numbers strip
    f_num = font_sans_bold(24)
    f_num_l = font_sans(10)
    strip_h = 46
    d.rectangle([MX, y, W - MX, y + strip_h], fill=NAVY)
    cell = CW / len(NUMBERS)
    for i, (num, label, col) in enumerate(NUMBERS):
        cx = MX + i * cell
        if i:
            d.line([cx, y + 8, cx, y + strip_h - 8], fill=(90, 110, 150), width=1)
        nw = text_w(d, num, f_num)
        d.text((cx + (cell - nw) / 2, y + 4), num, font=f_num, fill=col)
        lw = text_w(d, label, f_num_l)
        d.text((cx + (cell - lw) / 2, y + 30), label, font=f_num_l,
               fill=(200, 210, 225))
    y += strip_h + 4

    # ---- region chips bar
    f_chip = font_sans_bold(10)
    chips = [(f"{name} {n}", REGION_COLORS[name]) for name, n in REGIONS]
    total = sum(text_w(d, t, f_chip) + 12 for t, _ in chips) + 5 * (len(chips) - 1)
    if total > CW:  # shrink once if needed
        f_chip = font_sans_bold(9)
        total = sum(text_w(d, t, f_chip) + 12 for t, _ in chips) + 5 * (len(chips) - 1)
    cx = MX + (CW - total) / 2
    for text, col in chips:
        wch = pill(d, int(cx), y, text, f_chip, col, pad_x=6, pad_y=3)
        cx += wch + 5
    y += 20

    # ---- UTC timeline strip (two rows of three milestones)
    f_tl = font_sans_bold(11)
    f_tl_b = font_sans_bold(11)
    d.text((MX, y), "THE DAY IN UTC", font=f_tl, fill=RED)
    tx = MX + text_w(d, "THE DAY IN UTC  ", f_tl)
    for row in (TIMELINE[:3], TIMELINE[3:]):
        cx = tx
        for tm, what in row:
            seg = f"{tm} {what}   \u00b7   "
            d.text((cx, y), tm, font=f_tl_b, fill=INK)
            cx += text_w(d, tm + " ", f_tl_b)
            d.text((cx, y), what + "   \u00b7   ", font=f_tl, fill=INK)
            cx += text_w(d, what + "   \u00b7   ", f_tl)
        y += 13
    y += 1

    # ---- leads (3 columns, full scenes)
    col_w = (CW - 20) // 3
    lead_top = y
    lead_h = 0
    f_lead_k = font_sans_bold(11)
    f_head = font_serif_bold(18)
    f_sum = font_sans(11)
    f_wim = font_sans_bold(11)
    f_src = font_sans_bold(9)
    for i, lead in enumerate(LEADS):
        lx = MX + i * (col_w + 10)
        ly = lead_top
        paint_lead_scene(d, lead["scene"], (lx, ly, lx + col_w, ly + 72))
        # data badges inside the picture
        bx = lx + 6
        by = ly + 72 - 22
        for btext, bcol in lead["badges"]:
            bw = pill(d, bx, by, btext, font_sans_bold(10), bcol,
                      fg=(25, 25, 25) if bcol in (GOLD, (255, 255, 255))
                      else (255, 255, 255),
                      pad_x=6, pad_y=2)
            bx += bw + 5
        ly += 76
        # kicker: number + region + trust pill + source
        num_badge(d, lx, ly, lead["num"], REGION_COLORS[lead["region"]])
        d.text((lx + 22, ly + 2), lead["region"], font=f_lead_k,
               fill=REGION_COLORS[lead["region"]])
        px = lx + 22 + text_w(d, lead["region"], f_lead_k) + 8
        pill(d, int(px), ly + 1, lead["badge"], font_sans_bold(9),
             TRUST_COLORS[lead["badge"]], pad_x=5, pad_y=1)
        d.text((lx + col_w - text_w(d, lead["source"], f_src), ly + 3),
               lead["source"], font=f_src, fill=GREY)
        ly += 19
        ly = draw_wrapped(d, lx, ly, lead["headline"], f_head, col_w, INK,
                          spacing=1, max_lines=2)
        ly += 2
        ly = draw_wrapped(d, lx, ly, lead["summary"], f_sum, col_w, INK,
                          spacing=2, max_lines=4)
        ly += 2
        segs = [("WHY IT MATTERS: ", True), (lead["wim"], False)]
        for ln in _rich_wrap(d, segs, f_wim, f_sum, col_w):
            _draw_rich_line(d, lx, ly, ln, f_wim, f_sum, RED)
            ly += 13
        lead_h = max(lead_h, ly - lead_top)
    y = lead_top + lead_h + 6

    # ---- minis grid (4 cols x 3 rows, small scenes)
    mini_w = (CW - 3 * 8) // 4
    mini_h = 76
    f_mini_h = font_serif_bold(12)
    f_mini_s = font_sans(9)
    for r in range(3):
        for c in range(4):
            m = MINIS[r * 4 + c]
            mx = MX + c * (mini_w + 8)
            my = y + r * (mini_h + 5)
            paint_mini_scene(d, m["scene"], (mx, my, mx + mini_w, my + 36))
            num_badge(d, mx + 4, my + 36 - 22, m["num"],
                      REGION_COLORS[m["region"]], r=8)
            hy = my + 39
            hy = draw_wrapped(d, mx, hy, m["headline"], f_mini_h, mini_w, INK,
                              spacing=3, max_lines=2)
            d.text((mx, hy + 1),
                   f"{m['region']} \u00b7 {m['badge']} \u00b7 {m['source']}",
                   font=f_mini_s, fill=GREY)
    y += 3 * mini_h + 2 * 5 + 4

    # ---- map band + trust legend (right column)
    f_map_t = font_sans_bold(12)
    d.text((MX, y), "WHERE IT HAPPENED \u2014 stories 1\u201315", font=f_map_t, fill=RED)
    map_y = y + 13
    map_h = 92
    paint_map(d, (MX, map_y, MX + 620, map_y + map_h))
    lx0 = MX + 632
    lw_ = W - MX - lx0
    f_leg_t = font_sans_bold(11)
    f_leg = font_sans(9)
    d.text((lx0, map_y), "HOW SURE", font=f_leg_t, fill=RED)
    ly = map_y + 15
    for name, desc in (("OFFICIAL", "government or institution statement"),
                       ("CONFIRMED", "two sources or primary data"),
                       ("REPORTED", "one credible report"),
                       ("CLAIM", "asserted, not verified")):
        pw = pill(d, lx0, ly, name, font_sans_bold(8), TRUST_COLORS[name],
                  pad_x=5, pad_y=1)
        d.text((lx0 + pw + 6, ly + 1), desc, font=f_leg, fill=INK)
        ly += 14
    d.text((lx0, ly + 2), "Pictures drawn in code,", font=f_leg, fill=GREY)
    d.text((lx0, ly + 13), "not photos.", font=f_leg, fill=GREY)
    y = map_y + map_h + 6

    # ---- briefs (two columns, 13 rows each)
    f_br_t = font_sans_bold(12)
    d.text((MX, y), "ALSO ON FRIDAY 27 NOVEMBER", font=f_br_t, fill=RED)
    y += 13
    f_br_n = font_sans_bold(10)
    f_br_r = font_sans_bold(9)
    f_br = font_serif(10)
    f_br_s = font_sans(8)
    br_col_w = (CW - 16) // 2
    row_h = 11
    for ci in range(2):
        bx = MX + ci * (br_col_w + 16)
        for ri in range(13):
            b = BRIEFS[ci * 13 + ri]
            by = y + ri * row_h
            num, region, headline, source = b
            d.text((bx, by), str(num), font=f_br_n, fill=RED)
            nx = bx + 20
            rw = text_w(d, region + "  ", f_br_r)
            d.text((nx, by + 0.5), region, font=f_br_r,
                   fill=REGION_COLORS[region])
            hx = nx + rw
            # headline + source must fit the column; trim words if needed
            words = headline.split(" ")
            while words:
                trial = " ".join(words) + f"  ({source})"
                if text_w(d, trial, f_br) <= br_col_w - (hx - bx):
                    break
                words = words[:-1]
            d.text((hx, by), " ".join(words), font=f_br, fill=INK)
            sx = hx + text_w(d, " ".join(words) + "  ", f_br)
            d.text((sx, by + 0.5), f"({source})", font=f_br_s, fill=GREY)
    y += 13 * row_h + 4

    # ---- date check + footer
    f_dc = font_sans_bold(10)
    f_dc_t = font_sans(10)
    dc_label_w = text_w(d, "DATE CHECK  ", f_dc)
    dc_lines = wrap(d, DATE_CHECK, f_dc_t, CW - 16 - dc_label_w)
    dc_h = 6 + len(dc_lines) * 13 + 5
    d.rectangle([MX, y, W - MX, y + dc_h], outline=RED, width=2)
    dy = y + 5
    d.text((MX + 8, dy), "DATE CHECK", font=f_dc, fill=RED)
    dx = MX + 8 + text_w(d, "DATE CHECK  ", f_dc)
    for ln in dc_lines:
        d.text((dx, dy), ln, font=f_dc_t, fill=INK)
        dy += 13
    y += dc_h + 4
    f_ft = font_sans(9)
    d.text((MX, y), FOOTER_SOURCES, font=f_ft, fill=GREY)
    y += 11
    d.text((MX, y), ("Every story here happened, or was first reported, on Friday "
                     "27 November 2026; claims are attributed."),
           font=f_ft, fill=GREY)
    y += 11
    return img, y


# ---------------------------------------------------------------- validation
def sha256_of(path):
    hsh = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            hsh.update(chunk)
    return hsh.hexdigest()


def validate_png(path):
    """Check path is a genuine, fully decodable PNG of the expected size.

    Exits loudly on any failure: not a PNG, truncated or corrupt image
    data, or dimensions other than EXPECTED_WIDTH x EXPECTED_HEIGHT.
    Returns (format, (width, height)) on success.
    """
    try:
        with Image.open(path) as img:
            fmt = img.format
            size = img.size
            img.load()  # decode every scanline: catches truncated data
    except Exception as exc:  # corrupt file, unreadable header, bad CRC
        print(f"error: {path} is not a readable PNG: {exc}", file=sys.stderr)
        sys.exit(1)
    if fmt != "PNG":
        print(f"error: {path} is {fmt}, not a PNG", file=sys.stderr)
        sys.exit(1)
    if size != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        print(f"error: {path} is {size[0]}x{size[1]}, expected "
              f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}", file=sys.stderr)
        sys.exit(1)
    return fmt, size


def main():
    img, bottom = render()
    print(f"layout bottom y: {bottom} (canvas {EXPECTED_HEIGHT})")
    if bottom > EXPECTED_HEIGHT:
        print(f"error: layout overflows by {bottom - EXPECTED_HEIGHT}px",
              file=sys.stderr)
        sys.exit(1)
    # The only required output: $MAKEFUN_OUTPUT_DIR/entry.png. The
    # grader mounts the repository read-only, so writing next to this
    # file must never fail the run.
    os.makedirs(DST_DIR, exist_ok=True)
    img.save(DST, format="PNG", optimize=True)
    fmt, (w, h) = validate_png(DST)
    print(f"output: {DST}")
    print(f"  format: {fmt} {w}x{h}")
    print(f"  size: {os.path.getsize(DST)} bytes")
    print(f"  sha256: {sha256_of(DST)}")

    # Best-effort local copy for development only: warn and continue
    # when the script directory is not writable (grader: read-only).
    try:
        img.save(OUT_LOCAL, format="PNG", optimize=True)
        print(f"local copy: {OUT_LOCAL}")
    except Exception as exc:
        print(f"warning: could not write local copy {OUT_LOCAL}: {exc}",
              file=sys.stderr)
    print(f"verified: {DST} ({fmt})")


if __name__ == "__main__":
    main()
