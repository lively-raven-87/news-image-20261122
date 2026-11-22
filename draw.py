#!/usr/bin/env python3
"""Render 'The World — 22 November 2026' as a 1024x1024 newspaper page.

Draws the verified 22 Nov 2026 brief (COP31 collapses with no deal in
Antalya leads; Iran strikes Bahrain, a Russian drone hits Dymer, Mexico
captures 'El Chapo Isidro', markets slide into correction) with Pillow
and writes entry.png beside this file.
"""

import os

from PIL import Image, ImageDraw, ImageFont

SIZE = (1024, 1024)
MARGIN = 36
CONTENT_W = SIZE[0] - 2 * MARGIN

PAPER = (248, 244, 233)
INK = (20, 20, 20)
BODY = (60, 58, 50)
FADED = (90, 86, 76)
RED = (176, 30, 30)
RULE_FAINT = (150, 145, 130)
CARD_BG = (255, 253, 245)
BAND_BG = (18, 18, 18)
BAND_FG = (245, 242, 232)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

LEAD_HEAD = "COP31 Collapses With No Deal"
LEAD_DECK = ("The climate summit in Antalya, Turkey, ended without an "
             "agreement, two days past its deadline, as the EU rejected "
             "a final draft that said nothing about fossil fuels.")
LEAD_BODY = ("Negotiators went home empty-handed after days of deadlock. "
             "The revised text weakened or dropped language on phasing "
             "out oil, gas and coal, and the European Union refused to "
             "sign a deal that left fossil fuels unmentioned.")

GLANCE = [
    ("WHERE", "Antalya, Turkey"),
    ("OUTCOME", "No agreement reached"),
    ("DEADLINE", "Missed by two days"),
    ("STICKING POINT", "No mention of fossil fuels"),
]

STORIES = [
    {"kick": "IRAN & THE GULF",
     "head": "Iran strikes Bahrain, hits U.S. base",
     "body": "Iranian missiles and drones hit a U.S. base and industrial "
             "sites in Bahrain, wounding 2. Tehran claims it destroyed "
             "two U.S. Patriot radars and also struck three tankers near "
             "the Strait of Hormuz."},
    {"kick": "WAR IN UKRAINE",
     "head": "Drone strike buries 14 in Dymer apartment",
     "body": "A Russian drone hit an apartment block in Dymer, near Kyiv, "
             "leaving 14 people missing or trapped in the rubble. A "
             "missile on Kryvyi Rih killed 2 — a 7-year-old and a "
             "20-year-old woman — and wounded 60."},
    {"kick": "MEXICO",
     "head": "FBI most-wanted \u201cEl Chapo Isidro\u201d captured",
     "body": "Mexican special forces seized Fausto Isidro Meza Flores in "
             "Sinaloa. He is on the FBI's list of its ten most-wanted "
             "fugitives. Eleven people were killed in the raid, "
             "including four soldiers."},
    {"kick": "MARKETS",
     "head": "Stocks slide into correction territory",
     "body": "S&P 500 fell 3.7% and the Nasdaq 5.3% as the AI sell-off "
             "spread; the Nikkei slid 5.06%. Wall Street's main indexes "
             "are now down 10% or more from their peaks."},
]

TICKER = ("FBI DATABASE HACKED  •  CIKANDE FIRE: 3 DEAD, 36 MISSING  •  "
          "GTA 6 LAUNCH EST. $3.79BN  •  BEPICOLOMBO REACHES MERCURY")
CREDIT = "Sources: AP  •  Reuters  •  Al Jazeera  •  NYT  •  One Turn News"


class Sheet:
    """A 1024x1024 newspaper sheet with text helpers."""

    def __init__(self):
        self.img = Image.new("RGB", SIZE, PAPER)
        self.d = ImageDraw.Draw(self.img)
        self._fonts = {}

    def font(self, path, size):
        key = (path, size)
        if key not in self._fonts:
            try:
                self._fonts[key] = ImageFont.truetype(path, size)
            except OSError:
                self._fonts[key] = ImageFont.load_default()
        return self._fonts[key]

    def wrap(self, text, fnt, width):
        """Greedy wrap on pixel width; returns the lines."""
        lines = []
        for chunk in text.split("\n"):
            words = chunk.split()
            if not words:
                lines.append("")
                continue
            current = words[0]
            for word in words[1:]:
                trial = current + " " + word
                if self.d.textlength(trial, font=fnt) <= width:
                    current = trial
                else:
                    lines.append(current)
                    current = word
            lines.append(current)
        return lines

    def draw_lines(self, lines, x, y, fnt, fill=INK, gap=None, centre=False):
        """Draw lines; returns the y just below the block."""
        step = gap if gap is not None else int(fnt.size * 1.28)
        for line in lines:
            lx = x
            if centre:
                lx = x + (CONTENT_W - self.d.textlength(line, font=fnt)) / 2
            self.d.text((lx, y), line, font=fnt, fill=fill)
            y += step
        return y

    def centred(self, text, y, fnt, fill=INK):
        self.d.text(
            ((SIZE[0] - self.d.textlength(text, font=fnt)) / 2, y),
            text, font=fnt, fill=fill)
        return y + int(fnt.size * 1.3)

    def centred_fit(self, text, y, size, fill, max_w):
        """Centre text, shrinking the font until it fits max_w."""
        while size > 11:
            fnt = self.font(SANS_BOLD, size)
            if self.d.textlength(text, font=fnt) <= max_w:
                break
            size -= 1
        return self.centred(text, y, self.font(SANS_BOLD, size), fill=fill)

    def rule(self, y, thick=2, fill=INK, x0=None, x1=None):
        self.d.line([(x0 or MARGIN, y), (x1 or SIZE[0] - MARGIN, y)],
                    fill=fill, width=thick)
        return y + thick


def glance(sheet, x, y, width):
    """The 'AT A GLANCE' fact box; returns its bottom y."""
    lab_f = sheet.font(SANS_BOLD, 15)
    val_f = sheet.font(SERIF, 16)
    val_w = width - 16 - 132 - 16
    rows = [(lab, sheet.wrap(val, val_f, val_w)) for lab, val in GLANCE]
    n_val = sum(len(v) for _, v in rows)
    top = y - 4
    tall = 12 + 26 + 10 + n_val * 22 + 8 + 18 + 12
    sheet.d.rectangle([x, top, x + width, top + tall], fill=CARD_BG,
                      outline=INK, width=2)
    bx, by = x + 16, top + 12
    sheet.d.text((bx, by), "AT A GLANCE",
                 font=sheet.font(SANS_BOLD, 16), fill=RED)
    by += 26
    sheet.d.line([(bx, by), (x + width - 16, by)], fill=RULE_FAINT, width=1)
    by += 10
    for lab, vlines in rows:
        sheet.d.text((bx, by), lab, font=lab_f, fill=RED)
        vy = by
        for vline in vlines:
            sheet.d.text((bx + 132, vy - 1), vline, font=val_f, fill=INK)
            vy += 22
        by = vy
    by += 6
    sheet.d.text((bx, by), "Sources: One Turn News, WPXI/AP",
                 font=sheet.font(SERIF_ITALIC, 14), fill=FADED)
    return top + tall


def story_card(sheet, story, x, y, width):
    """One secondary story: kicker, headline, body."""
    sheet.d.text((x, y), story["kick"], font=sheet.font(SANS_BOLD, 15),
                 fill=RED)
    hy = y + 22
    head_f = sheet.font(SERIF_BOLD, 23)
    hy = sheet.draw_lines(sheet.wrap(story["head"], head_f, width), x, hy,
                          head_f, gap=26)
    body_f = sheet.font(SERIF, 17)
    sheet.draw_lines(sheet.wrap(story["body"], body_f, width), x, hy + 2,
                     body_f, gap=21)


def masthead(sheet):
    sheet.centred("SUNDAY EDITION  •  VOL. 2026 — NO. 326", 18,
                  sheet.font(SANS, 15), fill=FADED)
    sheet.centred("THE WORLD", 40, sheet.font(SERIF_BOLD, 88))
    sheet.rule(156)
    sheet.rule(160, thick=1)
    sheet.centred("22 NOVEMBER 2026", 168, sheet.font(SANS_BOLD, 21))
    sheet.rule(200)


def lead_story(sheet):
    d = sheet.d
    y = 214
    d.text((MARGIN, y), "LEAD STORY  —  CLIMATE",
           font=sheet.font(SANS_BOLD, 19), fill=RED)
    y += 28
    head_f = sheet.font(SERIF_BOLD, 42)
    y = sheet.draw_lines(sheet.wrap(LEAD_HEAD, head_f, CONTENT_W),
                         MARGIN, y, head_f, gap=48)
    y += 4
    deck_f = sheet.font(SERIF_ITALIC, 21)
    y = sheet.draw_lines(sheet.wrap(LEAD_DECK, deck_f, CONTENT_W),
                         MARGIN, y, deck_f, fill=BODY, gap=28)
    y += 8

    body_w = 520
    box_x = MARGIN + body_w + 26
    box_w = SIZE[0] - MARGIN - box_x
    body_f = sheet.font(SERIF, 20)
    body_end = sheet.draw_lines(sheet.wrap(LEAD_BODY, body_f, body_w),
                                MARGIN, y, body_f, gap=26)
    box_end = glance(sheet, box_x, y, box_w)
    return max(body_end, box_end) + 14


def story_grid(sheet, y):
    sheet.rule(y)
    y += 12
    col = (CONTENT_W - 28) // 2
    row_h = 148
    for i, story in enumerate(STORIES):
        cx = MARGIN + (i % 2) * (col + 28)
        cy = y + (i // 2) * (row_h + 12)
        story_card(sheet, story, cx, cy, col)
        if i % 2 == 0:
            sheet.d.line([(cx + col + 14, cy),
                          (cx + col + 14, cy + row_h)],
                         fill=RULE_FAINT, width=1)
    y = y + 2 * row_h + 10 + 6
    sheet.rule(y)
    return y + 10


def ticker_band(sheet, y):
    band_h = 36
    sheet.d.rectangle([MARGIN, y, SIZE[0] - MARGIN, y + band_h], fill=BAND_BG)
    sheet.centred_fit(TICKER, y + 10, 15, BAND_FG, CONTENT_W - 16)
    sheet.centred(CREDIT, y + band_h + 10, sheet.font(SANS, 13), fill=FADED)


def build():
    sheet = Sheet()
    masthead(sheet)
    y = lead_story(sheet)
    y = story_grid(sheet, y)
    ticker_band(sheet, y)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    sheet.img.save(out, format="PNG", optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    build()
