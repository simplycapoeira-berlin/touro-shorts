"""Text cards: brand-styled, movement-timed typography drawn onto video frames.

A card is {"text", "in", "hit", "out", optional "kick", "shrink"} (see models.py and STYLE.md
§3). The last word is the key word, set huge with the yellow marker; the words before it form
the small kicker above. Cards alternate left / right alignment by their index. Everything here
is pure drawing: no ffmpeg, no file I/O beyond the bundled fonts.
"""
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import timeline

FONTS = Path(__file__).parent / "fonts"

# Brand tokens, taken from sc-capoeira.de (css: --sc-black, --sc-yellow, Archivo).
INK = (17, 17, 17)
MARK = (247, 224, 24)
KEY_FONT = FONTS / "archivo-900.ttf"     # .sc-hero__title weight
KICKER_FONT = FONTS / "archivo-800.ttf"  # .sc-kicker weight

# Frame and Instagram safe zone (UI covers ~14% top, ~35% bottom, rail on the right).
W, H = timeline.W, timeline.H
MARGIN_X = 72
SAFE_W = W - 2 * MARGIN_X
TEXT_TOP = 280

# Typography: small tracked kicker over a key word fitted to the safe width.
KICKER_SIZE = 56
KICKER_TRACK = 0.18       # em, .sc-kicker letter-spacing
KEY_MAX = 330             # px cap so short key words don't become absurd
GAP = 10                  # px between kicker baseline and key word cap height

# Motion grammar (see STYLE.md §3). Times in seconds, distances in px. Kept short:
# a card is fully readable ~0.6 s after `in`.
KICKER_IN = 0.35          # kicker fades in while its tracking tightens from wide to rest
KICKER_TRACK_FROM = 0.6   # em, starting letter-spacing
LETTER_IN = 0.32          # one key-word letter swinging in along its arc
LETTER_STAGGER = 0.025
ARC_R = 200               # radius of the meia-lua arc the letters travel
MARK_SWEEP = 0.15         # marker sweep, ends exactly on `hit`
DRIFT = 16                # slow drift while holding, keeps the card alive without looping
EXIT = 0.3                # normal exit: slide toward the open side with a motion trail
TRAVEL = 320
TRAIL = ((2, 0.15), (1, 0.3))  # (step, opacity) ghost copies while leaving
TRAIL_STEP = 60
KICK_WAVE = 0.12          # s for the leg to sweep across the full frame width
KICK_SPEED = 2600         # px/s sideways
KICK_LIFT = 1100          # px/s upward at impact
GRAVITY = 5000            # px/s^2
KICK_SPIN = 520           # deg/s
KICK_FADE = 0.45          # s for a struck letter to fade out
SHRINK_TO = 0.45          # scale of a shrunk card
SHRINK_SNAP = 0.35        # s: the card snaps small with a springy overshoot, not a slow fade-down
BEAT_POP = 0.12           # a beat (a kick or move) punches the card 12% bigger...
BEAT_DUR = 0.3            # ...for this long, and re-sweeps the yellow marker under the key word


@dataclass
class Glyph:
    ch: str
    font: ImageFont.FreeTypeFont
    x: float      # left of the baseline
    y: float      # baseline
    alpha: float = 1.0
    angle: float = 0.0  # degrees, counter-clockwise around (x, y)


def ease_out_back(p):
    c = 1.70158
    return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2


def ease_out_cubic(p):
    return 1 - (1 - p) ** 3


def clamp01(x):
    return min(max(x, 0.0), 1.0)


def compose(card, index):
    """Rest geometry of one card. side=+1: left-aligned, leaves to the right; -1 mirrors it."""
    side = 1 if index % 2 == 0 else -1
    lead, key = card["text"].rsplit(" ", 1)
    probe = ImageFont.truetype(str(KEY_FONT), KEY_MAX)
    key_font = ImageFont.truetype(str(KEY_FONT), min(KEY_MAX, int(KEY_MAX * SAFE_W / probe.getlength(key))))
    key_w = key_font.getlength(key)
    key_x = MARGIN_X if side > 0 else W - MARGIN_X - key_w
    kicker_base = TEXT_TOP + KICKER_SIZE
    key_base = kicker_base + GAP - key_font.getbbox(key, anchor="ls")[1]
    letters = [(ch, key_x + key_font.getlength(key[:i])) for i, ch in enumerate(key)]
    if side < 0:
        letters.reverse()  # letters land from the card's outer edge inward
    return dict(side=side, lead=lead.upper(), key=key, key_font=key_font, key_x=key_x, key_w=key_w,
                kicker_base=kicker_base, key_base=key_base, letters=letters,
                kicker_font=ImageFont.truetype(str(KICKER_FONT), KICKER_SIZE))


def entering_glyphs(g, card, t):
    """Kicker and key-word glyphs at time t, animated in but not yet leaving."""
    glyphs = []
    p = clamp01((t - card["in"]) / KICKER_IN)
    if p > 0:
        font = g["kicker_font"]
        track = KICKER_SIZE * (KICKER_TRACK_FROM + (KICKER_TRACK - KICKER_TRACK_FROM) * ease_out_cubic(p))
        widths = [font.getlength(ch) for ch in g["lead"]]
        x = MARGIN_X if g["side"] > 0 else W - MARGIN_X - (sum(widths) + track * (len(widths) - 1))
        for ch, w in zip(g["lead"], widths):
            glyphs.append(Glyph(ch, font, x, g["kicker_base"], clamp01(p * 2)))
            x += w + track

    start = card["hit"] - MARK_SWEEP - LETTER_IN - LETTER_STAGGER * (len(g["letters"]) - 1)
    for i, (ch, x) in enumerate(g["letters"]):
        p = clamp01((t - start - i * LETTER_STAGGER) / LETTER_IN)
        if p <= 0:
            continue
        a = (1 - ease_out_back(p)) * math.pi / 2  # arc angle: 90deg away -> 0 at rest, overshoots slightly
        glyphs.append(Glyph(ch, g["key_font"], x - g["side"] * ARC_R * math.sin(a),
                            g["key_base"] + ARC_R * (1 - math.cos(a)), clamp01(p * 3),
                            g["side"] * math.degrees(a) * 0.6))
    return glyphs


def marker_box(g, card, t):
    """Yellow highlighter band over the lower part of the key word, like .sc-mark; None before it
    starts. Each beat redraws it from scratch, so the move underlines the word again."""
    last_beat = max((b for b in card.get("beats", []) if b <= t), default=None)
    sweep = (clamp01((t - last_beat) / MARK_SWEEP) if last_beat is not None
             else clamp01((t - card["hit"] + MARK_SWEEP) / MARK_SWEEP))
    if sweep <= 0:
        return None
    size = g["key_font"].size
    left, right = g["key_x"] - 10, g["key_x"] + g["key_w"] + 10
    span = (right - left) * ease_out_cubic(sweep)
    x0, x1 = (left, left + span) if g["side"] > 0 else (right - span, right)
    return [x0, g["key_base"] - 0.30 * size, x1, g["key_base"] + 0.06 * size]


def kick(glyphs, card, t):
    """Knock glyphs away as a leg sweeps across the frame in direction card['kick'] starting at `out`.

    The leg enters from the opposite side, so glyphs on that side are struck first. Each glyph
    gets its own lift and spin (deterministic, from its index) so the letters scatter, not slide.
    """
    d = 1 if card["kick"] == "right" else -1
    for i, gl in enumerate(glyphs):
        reach = (gl.x if d > 0 else W - gl.x) / W
        s = t - card["out"] - KICK_WAVE * reach
        if s <= 0:
            continue
        r = (i * 7919 % 13) / 13
        gl.x += d * KICK_SPEED * (0.7 + 0.6 * r) * s
        gl.y += -KICK_LIFT * (0.5 + r) * s + 0.5 * GRAVITY * s * s
        gl.angle -= d * KICK_SPIN * (0.5 + r) * s
        gl.alpha *= 1 - clamp01(s / KICK_FADE)


def paint(layer, glyphs, marker, marker_alpha):
    draw = ImageDraw.Draw(layer)
    if marker and marker_alpha > 0:
        draw.rectangle(marker, fill=MARK + (int(255 * marker_alpha),))
    for gl in glyphs:
        if gl.alpha <= 0:
            continue
        fill = INK + (int(255 * gl.alpha),)
        if abs(gl.angle) < 0.5:
            draw.text((gl.x, gl.y), gl.ch, font=gl.font, fill=fill, anchor="ls")
            continue
        size = gl.font.size
        tile = Image.new("RGBA", (2 * size, 2 * size))
        ImageDraw.Draw(tile).text((size, size), gl.ch, font=gl.font, fill=fill, anchor="ls")
        tile = tile.rotate(gl.angle, resample=Image.BICUBIC, center=(size, size))
        layer.paste(tile, (round(gl.x - size), round(gl.y - size)), tile)


def overlay_card(frame, g, card, t):
    """Composite one card onto the frame at time t; returns the frame untouched outside the card's life."""
    leave = KICK_WAVE + KICK_FADE if card.get("kick") else EXIT
    if not card["in"] <= t <= card["out"] + leave:
        return frame
    glyphs, marker = entering_glyphs(g, card, t), marker_box(g, card, t)
    hold = clamp01((min(t, card["out"]) - card["hit"]) / max(card["out"] - card["hit"], 1e-6))
    for gl in glyphs:
        gl.x += g["side"] * DRIFT * hold
    if marker:
        marker[0] += g["side"] * DRIFT * hold
        marker[2] += g["side"] * DRIFT * hold

    layer = Image.new("RGBA", (W, H))
    if card.get("kick"):
        kick(glyphs, card, t)
    paint(layer, glyphs, marker, 1 - clamp01((t - card["out"]) / 0.1) if card.get("kick") else 1.0)
    layer = scaled(layer, card_scale(card, min(t, card["out"])), g["side"])
    if card.get("kick"):
        return Image.alpha_composite(frame, layer)

    p_out = clamp01((t - card["out"]) / EXIT)
    dx = g["side"] * TRAVEL * p_out**2
    copies = [(k * TRAIL_STEP * p_out, o) for k, o in TRAIL] if p_out > 0 else []
    for lag, opacity in copies + [(0, 1.0)]:
        frame = Image.alpha_composite(frame, shifted(layer, dx - g["side"] * lag, opacity * (1 - p_out)))
    return frame


def card_scale(card, t):
    """Scale of the whole card at t: a springy snap down at `shrink`, times a pop on every beat."""
    s = 1.0
    if "shrink" in card and t > card["shrink"]:  # before it, stay exactly 1: no resampling blur
        s -= (1 - SHRINK_TO) * ease_out_back(clamp01((t - card["shrink"]) / SHRINK_SNAP))
    for beat in card.get("beats", []):
        if 0 <= t - beat <= BEAT_DUR:
            s *= 1 + BEAT_POP * math.sin(math.pi * (t - beat) / BEAT_DUR)
    return s


def scaled(layer, s, side):
    """Scale the card layer by s around its aligned top corner, so it shrinks into (or pops out of) that corner."""
    if s == 1:
        return layer
    ax, ay = (MARGIN_X if side > 0 else W - MARGIN_X), TEXT_TOP
    return layer.transform(layer.size, Image.AFFINE, (1 / s, 0, ax - ax / s, 0, 1 / s, ay - ay / s),
                           resample=Image.BICUBIC)


def shifted(layer, dx, opacity):
    if dx == 0 and opacity == 1:
        return layer
    out = Image.new("RGBA", layer.size)
    out.paste(layer, (round(dx), 0))
    if opacity < 1:
        out.putalpha(out.getchannel("A").point(lambda a: int(a * opacity)))
    return out


def kicker_width(g):
    """Width of the kicker line at rest, to check it fits the safe width."""
    return sum(g["kicker_font"].getlength(c) for c in g["lead"]) + KICKER_SIZE * KICKER_TRACK * (len(g["lead"]) - 1)
