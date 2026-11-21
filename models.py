"""Video types and edit files: what an edit may say, and what it means.

An edit file (edits/*.json) declares:
    "type"        one of MODELS (the model of the output; recipe in STYLE.md §8)
    "clips"       [{"src", "start", "end", "speed", "intro", "text"}] in play order (timeline.py)
    "output"      where the render goes, e.g. "out/<name>.mp4"
    "brightness"  optional footage grade, -0.2..0.2
    "cards"       text cards (cards.py); educational edits may omit them and get step cards

`load` is the one way to read an edit. It rejects any edit that breaks a rule and lists every
problem at once, so a typo or a broken edit from any collaborator fails before rendering.
Extending: a new field must be added to the *_KEYS sets and to `problems`, with a test.
"""
import json
import sys
from pathlib import Path

import cards
import timeline

ROOT = Path(__file__).parent

# Video types (STYLE.md §8). The key goes into every output's metadata; the description is the
# structure an edit of that type follows. A new kind of video is a new entry here.
MODELS = {
    "sequence": "one continuous movement sequence, opened by a slow-motion hook of its most "
                "spectacular move; hand-timed cards ride and get kicked by the movement",
    "educational": "step by step: per technique the finger count, then the move; an automatic "
                   "numbered step card lands on the fingers",
}
STEP_IN, STEP_HIT, STEP_GAP = 0.1, 0.6, 0.35  # step card timing inside its step; hit lands on the finger count

EDIT_KEYS = {"type", "clips", "output", "brightness", "cards"}
CLIP_KEYS = {"src", "start", "end", "speed", "intro", "text"}
CARD_KEYS = {"text", "in", "hit", "out", "kick", "shrink"}


def play_clips(edit):
    """Clips in play order. A clip's optional "intro" [start, end] (an educational step's finger
    count) is cut from the same source and plays right before the clip itself."""
    clips = []
    for clip in edit["clips"]:
        if "intro" in clip:
            clips.append({"src": clip["src"], "start": clip["intro"][0], "end": clip["intro"][1]})
        clips.append({k: v for k, v in clip.items() if k not in ("intro", "text")})
    return clips


def edit_cards(edit):
    """The edit's text cards: explicit "cards", or for educational edits one step card per step
    (a step = its intro + its move)."""
    if "cards" in edit:
        return edit["cards"]
    if edit["type"] != "educational":
        return []
    spans = iter(timeline.segments(play_clips(edit), ROOT))
    steps = []
    for n, clip in enumerate(edit["clips"], 1):
        start, end = next(spans)
        if "intro" in clip:
            end = next(spans)[1]
        steps.append({"text": clip.get("text", f"Step {n}"), "in": start + STEP_IN, "hit": start + STEP_HIT,
                      "out": end - STEP_GAP})
    return steps


def problems(edit):
    """Every rule the edit breaks, as readable messages. Empty means it can be rendered."""
    found = []

    def require(ok, message):
        if not ok:
            found.append(message)

    kind = edit.get("type")
    require(kind in MODELS, f'"type" must be one of {sorted(MODELS)}, got {kind!r}')
    require(not set(edit) - EDIT_KEYS, f"unknown edit keys {sorted(set(edit) - EDIT_KEYS)} (allowed: {sorted(EDIT_KEYS)})")
    require("clips" in edit and "output" in edit, 'an edit needs "clips" and "output"')
    require(-0.2 <= edit.get("brightness", 0) <= 0.2, "brightness is a subtle grade: keep it within -0.2..0.2")
    for clip in edit.get("clips", []):
        require(not set(clip) - CLIP_KEYS, f"unknown clip keys {sorted(set(clip) - CLIP_KEYS)} in {clip}")
        require("src" in clip, f'clip without "src": {clip}')
        require(0.5 <= clip.get("speed", 1) <= 2, f"speed must be 0.5..2: {clip}")
        require(clip.get("start", 0) < clip.get("end", float("inf")), f"start must be before end: {clip}")
        if kind == "educational":
            require("start" in clip and "end" in clip, f"educational steps are explicit cuts (start, end): {clip}")
            intro = clip.get("intro", [0, 0.5])
            require(0.5 <= intro[1] - intro[0] <= 1.2, f"finger count (intro) should last 0.5..1.2 s: {clip}")
            require(intro[1] <= clip.get("start", 0), f"finger count (intro) comes before the move: {clip}")
    if kind == "sequence" and len(edit.get("clips", [])) > 1:
        require(edit["clips"][0].get("speed", 1) < 1, "a sequence opens with a slow-motion hook (first clip speed < 1)")
    if found:
        return found  # card checks below assume a well-formed edit

    for index, card in enumerate(edit_cards(edit)):
        require(not set(card) - CARD_KEYS, f"unknown card keys {sorted(set(card) - CARD_KEYS)} in {card}")
        words = card.get("text", "").split()
        require(2 <= len(words) <= 6, f"a card has 2..6 words (kicker + key word): {card}")
        require(card.get("in", 0) < card.get("hit", -1) < card.get("out", -1), f"in < hit < out: {card}")
        require(card.get("hit", 0) - card.get("in", 0) <= 0.8, f"key word lands too late for short attention (hit - in <= 0.8): {card}")
        require(card.get("kick") in (None, "left", "right"), f'kick is "left" or "right": {card}')
        require(card.get("hit", 0) < card.get("shrink", card.get("hit", 0) + 1) < card.get("out", 0),
                f"shrink must fall between hit and out: {card}")
        if len(words) >= 2:
            require(cards.kicker_width(cards.compose(card, index)) <= cards.SAFE_W, f"kicker wider than the safe width: {card}")
    return found


def load(edit_path):
    """Read an edit file; exit listing every broken rule instead of rendering a broken edit."""
    edit = json.loads(Path(edit_path).read_text())
    found = problems(edit)
    if found:
        sys.exit(f"{edit_path} breaks {len(found)} rule(s):\n- " + "\n- ".join(found))
    return edit
