"""Turn raw capoeira clips into a finished vertical short: cut, join, grade, then animate
brand-styled, movement-timed text cards on top.

Usage:
    uv run shorts.py peaks <clip>        # print motion peaks, to pick cuts and card timings
    uv run shorts.py render <edit.json>  # render the edit described in the JSON

An edit file declares its video "type" (see MODELS), its "clips" (timeline.py), an "output"
path, an optional "brightness", and its text cards. Educational edits may omit "cards": each
clip then gets a numbered step card automatically (its optional "text", or "Step <n>").
The type and the sources are written into the output's metadata.

Text cards: the last word of each card is its key word. The last word of each card is its key word: it is set huge
and marked in yellow; the words before it form the small kicker line above. Each card is timed
to the movement:
    {"text": "It is not about talent", "in": s, "hit": s, "out": s, "kick": "left"}
  in   - the kicker starts entering (once the body has cleared the text band)
  hit  - the key word has landed and the yellow marker is complete
  out  - the card starts leaving; past the clip end = hold to the end
  kick - optional, "left" or "right": at `out` a kick sweeping in that direction knocks the
         letters off screen instead of the normal slide-out
  shrink - optional time: from here the card shrinks toward its aligned top corner, staying
         readable but out of the movement's way until `out` (bridges a long gap to the next card)
Cards alternate left / right alignment. Design rules behind every constant: STYLE.md.

Clip and output paths may use environment variables (e.g. "$SC_CONTENT/...") or be relative to
the repo (e.g. "in/IMG_7011.MOV"), so edit files never contain a machine-specific (or private)
path. "brightness" (ffmpeg eq, -1..1, default 0) grades the footage only, so the type keeps its
exact brand colors.
"""
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import timeline

ROOT = Path(__file__).parent

# Video types (STYLE.md §8). The key goes into every output's metadata; the description is the
# structure an edit of that type follows.
MODELS = {
    "sequence": "one continuous movement sequence, opened by a slow-motion hook of its most "
                "spectacular move; hand-timed cards ride and get kicked by the movement",
    "educational": "step by step: per technique the finger count, then the move; an automatic "
                   "numbered step card lands on the fingers",
}
STEP_IN, STEP_HIT, STEP_GAP = 0.1, 0.6, 0.35  # step card timing inside its step; hit lands on the finger count

# Brand tokens, taken from sc-capoeira.de (css: --sc-black, --sc-yellow, Archivo).
INK = (17, 17, 17)
MARK = (247, 224, 24)
KEY_FONT = ROOT / "fonts" / "archivo-900.ttf"     # .sc-hero__title weight
KICKER_FONT = ROOT / "fonts" / "archivo-800.ttf"  # .sc-kicker weight

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
SHRINK_TO = 0.45          # final scale of a shrinking card; mostly reached in its first ~3 s


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
    """Yellow highlighter band over the lower part of the key word, like .sc-mark; None before it starts."""
    sweep = clamp01((t - card["hit"] + MARK_SWEEP) / MARK_SWEEP)
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
    if "shrink" in card:
        p = clamp01((min(t, card["out"]) - card["shrink"]) / (card["out"] - card["shrink"]))
        layer = scaled(layer, 1 - (1 - SHRINK_TO) * ease_out_cubic(p), g["side"])
    if card.get("kick"):
        return Image.alpha_composite(frame, layer)

    p_out = clamp01((t - card["out"]) / EXIT)
    dx = g["side"] * TRAVEL * p_out**2
    copies = [(k * TRAIL_STEP * p_out, o) for k, o in TRAIL] if p_out > 0 else []
    for lag, opacity in copies + [(0, 1.0)]:
        frame = Image.alpha_composite(frame, shifted(layer, dx - g["side"] * lag, opacity * (1 - p_out)))
    return frame


def scaled(layer, s, side):
    """Scale the card layer by s around its aligned top corner, so it shrinks into that corner."""
    if s >= 1:
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


def play_clips(edit):
    """Clips in play order. A clip's optional "intro" [start, end] (an educational step's finger
    count) is cut from the same source and plays right before the clip itself."""
    clips = []
    for clip in edit["clips"]:
        if "intro" in clip:
            clips.append({"src": clip["src"], "start": clip["intro"][0], "end": clip["intro"][1]})
        clips.append({k: v for k, v in clip.items() if k != "intro"})
    return clips


def edit_cards(edit):
    """The edit's text cards: explicit "cards", or for educational edits one step card per step
    (a step = its intro + its move)."""
    if "cards" in edit:
        return edit["cards"]
    if edit["type"] != "educational":
        return []
    spans = iter(timeline.segments(play_clips(edit), ROOT))
    cards = []
    for n, clip in enumerate(edit["clips"], 1):
        start, end = next(spans)
        if "intro" in clip:
            end = next(spans)[1]
        cards.append({"text": clip.get("text", f"Step {n}"), "in": start + STEP_IN, "hit": start + STEP_HIT,
                      "out": end - STEP_GAP})
    return cards


def render(edit_path):
    edit = json.loads(Path(edit_path).read_text())
    if edit.get("type") not in MODELS:
        sys.exit(f'"type" must be one of {sorted(MODELS)}')
    dst = timeline.source(ROOT, edit["output"])
    dst.parent.mkdir(parents=True, exist_ok=True)
    cut = dst.with_suffix(".timeline.mp4")
    timeline.assemble(play_clips(edit), edit.get("brightness", 0), ROOT, cut)
    cards = [(compose(c, i), c) for i, c in enumerate(edit_cards(edit))]
    fps = timeline.FPS
    metadata = json.dumps({"type": edit["type"], "edit": Path(edit_path).name,
                           "clips": [Path(c["src"]).name for c in edit["clips"]],
                           "text": [c["text"] for _, c in cards]})

    decode = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(cut), "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
                              stdout=subprocess.PIPE)
    encode = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
         "-r", str(fps), "-i", "-", "-i", str(cut), "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
         "-map_metadata", "-1", "-metadata", f"genre={edit['type']}", "-metadata", f"comment={metadata}",
         str(dst)],
        stdin=subprocess.PIPE)

    frame_bytes, index = W * H * 4, 0
    while chunk := decode.stdout.read(frame_bytes):
        if len(chunk) < frame_bytes:
            break
        frame = Image.frombuffer("RGBA", (W, H), chunk)
        for g, card in cards:
            frame = overlay_card(frame, g, card, index / fps)
        encode.stdin.write(frame.tobytes())
        index += 1
    encode.stdin.close()
    if encode.wait() != 0:
        sys.exit("ffmpeg encode failed")
    cut.unlink()
    print(f"{dst}  ({index} frames, {edit['type']})")


def peaks(clip, top=6):
    """Print the strongest motion moments: mean frame difference, smoothed over 0.3 s."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(clip), "-vf", "scale=90:160,fps=30,format=gray",
         "-f", "rawvideo", "-"], capture_output=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, 160, 90).astype(np.float32)
    energy = np.convolve(np.abs(np.diff(frames, axis=0)).mean((1, 2)), np.ones(9) / 9, "same")
    chosen = []  # strongest frames first, at least 1 s apart so one pass is reported once
    for i in np.argsort(-energy):
        if all(abs(i - j) >= 30 for j in chosen):
            chosen.append(i)
        if len(chosen) == top:
            break
    for i in sorted(chosen):
        print(f"{i / 30:5.2f}s  {'#' * int(energy[i] * 4)}")


if __name__ == "__main__":
    commands = {"render": render, "peaks": peaks}
    if len(sys.argv) != 3 or sys.argv[1] not in commands:
        sys.exit(__doc__)
    commands[sys.argv[1]](sys.argv[2])
