#!/usr/bin/env python3
"""Paint the 22 November 2026 front page: 'THE WORLD' in one 1024x1024 PNG.

The page is built from the verified brief for 22 Nov 2026 — the COP31
summit ending with no deal leads, then Bahrain, Dymer, the Sinaloa raid
and the market correction, with a ticker along the bottom. Pillow does
the drawing; running this file writes entry.png next to it.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
SIDE = 36
INNER = W - 2 * SIDE

BG = (248, 244, 233)
FG = (20, 20, 20)
TEXT = (60, 58, 50)
SOFT = (90, 86, 76)
ACCENT = (176, 30, 30)
HAIRLINE = (150, 145, 130)
PANEL = (255, 253, 245)
STRIP = (18, 18, 18)
STRIP_FG = (245, 242, 232)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def f(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


HEADLINE = "COP31 Collapses With No Deal"
STANDOFF = (
    "The climate summit in Antalya, Turkey, ended without an agreement, "
    "two days past its deadline, as the EU rejected a final draft that "
    "said nothing about fossil fuels.")
LEAD_COPY = (
    "Negotiators went home empty-handed after days of deadlock. The "
    "revised text weakened or dropped language on phasing out oil, gas "
    "and coal, and the European Union refused to sign a deal that left "
    "fossil fuels unmentioned.")

FACTS = [
    ("WHERE", "Antalya, Turkey"),
    ("OUTCOME", "No agreement reached"),
    ("DEADLINE", "Missed by two days"),
    ("STICKING POINT", "No mention of fossil fuels"),
]

# (kicker, headline, body) for the four second stories.
STORIES = [
    ("IRAN & THE GULF",
     "Iran strikes Bahrain, hits U.S. base",
     "Iranian missiles and drones hit a U.S. base and industrial sites "
     "in Bahrain, wounding 2. Tehran claims it destroyed two U.S. "
     "Patriot radars and also struck three tankers near the Strait of "
     "Hormuz."),
    ("WAR IN UKRAINE",
     "Drone strike buries 14 in Dymer apartment",
     "A Russian drone hit an apartment block in Dymer, near Kyiv, "
     "leaving 14 people missing or trapped in the rubble. A missile on "
     "Kryvyi Rih killed 2 — a 7-year-old and a 20-year-old woman — and "
     "wounded 60."),
    ("MEXICO",
     "FBI most-wanted \u201cEl Chapo Isidro\u201d captured",
     "Mexican special forces seized Fausto Isidro Meza Flores in "
     "Sinaloa. He is on the FBI's list of its ten most-wanted fugitives. "
     "Eleven people were killed in the raid, including four soldiers."),
    ("MARKETS",
     "Stocks slide into correction territory",
     "S&P 500 fell 3.7% and the Nasdaq 5.3% as the AI sell-off spread; "
     "the Nikkei slid 5.06%. Wall Street's main indexes are now down "
     "10% or more from their peaks."),
]

TICKER = (
    "FBI DATABASE HACKED  •  CIKANDE FIRE: 3 DEAD, 36 MISSING  •  "
    "GTA 6 LAUNCH EST. $3.79BN  •  BEPICOLOMBO REACHES MERCURY")
SOURCES = "Sources: AP  •  Reuters  •  Al Jazeera  •  NYT  •  One Turn News"


class FrontPage:
    """The sheet plus the small drawing vocabulary used across it."""

    def __init__(self):
        self.img = Image.new("RGB", (W, H), BG)
        self.d = ImageDraw.Draw(self.img)

    def measure(self, text, font):
        return self.d.textlength(text, font=font)

    def split_lines(self, text, font, width):
        """Wrap text to the pixel width, one word at a time."""
        result = []
        for piece in text.split("\n"):
            words = piece.split()
            if not words:
                result.append("")
                continue
            current = ""
            for word in words:
                trial = word if not current else current + " " + word
                if self.measure(trial, font) <= width:
                    current = trial
                else:
                    result.append(current)
                    current = word
            result.append(current)
        return result

    def write_block(self, lines, x, y, font, fill=FG, leading=None,
                    centred=False):
        step = leading if leading is not None else int(font.size * 1.28)
        for line in lines:
            lx = x
            if centred:
                lx = x + (INNER - self.measure(line, font)) / 2
            self.d.text((lx, y), line, font=font, fill=fill)
            y += step
        return y

    def write_centred(self, text, y, font, fill=FG):
        self.d.text(((W - self.measure(text, font)) / 2, y),
                    text, font=font, fill=fill)
        return y + int(font.size * 1.3)

    def write_centred_fit(self, text, y, size, fill, max_w):
        """Centre text, stepping the size down until it fits max_w."""
        while size > 11:
            font = f(SANS_B, size)
            if self.measure(text, font) <= max_w:
                break
            size -= 1
        return self.write_centred(text, y, f(SANS_B, size), fill=fill)

    def draw_rule(self, y, thick=2, fill=FG, x0=None, x1=None):
        self.d.line([(x0 if x0 is not None else SIDE, y),
                     (x1 if x1 is not None else W - SIDE, y)],
                    fill=fill, width=thick)
        return y + thick


def draw_glance(page, x, y, width):
    """Fact panel at the side of the lead story; returns its bottom edge."""
    label_font = f(SANS_B, 15)
    value_font = f(SERIF, 16)
    value_w = width - 16 - 132 - 16
    rows = []
    for label, value in FACTS:
        rows.append((label, page.split_lines(value, value_font, value_w)))
    value_lines = sum(len(v) for _, v in rows)
    top = y - 4
    height = 12 + 26 + 10 + value_lines * 22 + 8 + 18 + 12
    page.d.rectangle([x, top, x + width, top + height], fill=PANEL,
                     outline=FG, width=2)
    ix = x + 16
    iy = top + 12
    page.d.text((ix, iy), "AT A GLANCE", font=f(SANS_B, 16), fill=ACCENT)
    iy += 26
    page.d.line([(ix, iy), (x + width - 16, iy)], fill=HAIRLINE, width=1)
    iy += 10
    for label, vlines in rows:
        page.d.text((ix, iy), label, font=label_font, fill=ACCENT)
        vy = iy
        for vline in vlines:
            page.d.text((ix + 132, vy - 1), vline, font=value_font, fill=FG)
            vy += 22
        iy = vy
    iy += 6
    page.d.text((ix, iy), "Sources: One Turn News, WPXI/AP",
                font=f(SERIF_I, 14), fill=SOFT)
    return top + height


def draw_story(page, kick, head, body, x, y, width):
    """One second story: red kicker, bold headline, body copy."""
    page.d.text((x, y), kick, font=f(SANS_B, 15), fill=ACCENT)
    hy = y + 22
    head_font = f(SERIF_B, 23)
    hy = page.write_block(page.split_lines(head, head_font, width),
                          x, hy, head_font, leading=26)
    body_font = f(SERIF, 17)
    page.write_block(page.split_lines(body, body_font, width),
                     x, hy + 2, body_font, leading=21)


def draw_masthead(page):
    page.write_centred("SUNDAY EDITION  •  VOL. 2026 — NO. 326", 18,
                       f(SANS, 15), fill=SOFT)
    page.write_centred("THE WORLD", 40, f(SERIF_B, 88))
    page.draw_rule(156)
    page.draw_rule(160, thick=1)
    page.write_centred("22 NOVEMBER 2026", 168, f(SANS_B, 21))
    page.draw_rule(200)


def draw_lead(page):
    d = page.d
    y = 214
    d.text((SIDE, y), "LEAD STORY  —  CLIMATE",
           font=f(SANS_B, 19), fill=ACCENT)
    y += 28
    head_font = f(SERIF_B, 42)
    y = page.write_block(page.split_lines(HEADLINE, head_font, INNER),
                         SIDE, y, head_font, leading=48)
    y += 4
    deck_font = f(SERIF_I, 21)
    y = page.write_block(page.split_lines(STANDOFF, deck_font, INNER),
                         SIDE, y, deck_font, fill=TEXT, leading=28)
    y += 8

    body_w = 520
    panel_x = SIDE + body_w + 26
    panel_w = W - SIDE - panel_x
    body_font = f(SERIF, 20)
    body_end = page.write_block(
        page.split_lines(LEAD_COPY, body_font, body_w),
        SIDE, y, body_font, leading=26)
    panel_end = draw_glance(page, panel_x, y, panel_w)
    return max(body_end, panel_end) + 14


def draw_grid(page, y):
    page.draw_rule(y)
    y += 12
    col = (INNER - 28) // 2
    row_h = 148
    for i, (kick, head, body) in enumerate(STORIES):
        cx = SIDE + (i % 2) * (col + 28)
        cy = y + (i // 2) * (row_h + 12)
        draw_story(page, kick, head, body, cx, cy, col)
        if i % 2 == 0:
            page.d.line([(cx + col + 14, cy),
                         (cx + col + 14, cy + row_h)],
                        fill=HAIRLINE, width=1)
    y = y + 2 * row_h + 10 + 6
    page.draw_rule(y)
    return y + 10


def draw_ticker(page, y):
    strip_h = 36
    page.d.rectangle([SIDE, y, W - SIDE, y + strip_h], fill=STRIP)
    page.write_centred_fit(TICKER, y + 10, 15, STRIP_FG, INNER - 16)
    page.write_centred(SOURCES, y + strip_h + 10, f(SANS, 13), fill=SOFT)


def render():
    page = FrontPage()
    draw_masthead(page)
    y = draw_lead(page)
    y = draw_grid(page, y)
    draw_ticker(page, y)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    page.img.save(out, format="PNG", optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    render()
