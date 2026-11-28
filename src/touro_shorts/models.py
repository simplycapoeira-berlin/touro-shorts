"""Video types and edit files: what an edit may say, and what it means.

The fields are documented in the README. `load` is the one way to read an edit: it lists every
broken rule at once, so a typo from any collaborator fails before rendering. A new field goes
into the *_KEYS sets and `problems`, with a test.
"""

import json
import sys
from pathlib import Path

from . import cards, timeline

# Video types (STYLE.md §8). The key goes into every output's metadata; the description is the
# structure an edit of that type follows. A new kind of video is a new entry here.
MODELS = {
    "sequence": "one continuous movement sequence, opened by a slow-motion hook of its most "
    "spectacular move; hand-timed cards ride and get kicked by the movement",
    "educational": "opened by the most impressive move at real speed, then step by step: per "
    "technique the finger count, then the move; an automatic numbered step card "
    "lands on the fingers and pops on the move",
}
STEP_IN, STEP_HIT, STEP_GAP = 0.1, 0.6, 0.35  # step card timing inside its step; hit lands on the finger count
PEAK_LEAD = 1.4  # an educational move cut starts this long before the move's peak (STYLE.md §8)
HOOK_HIT, HOOK_GAP = 0.5, 0.3  # educational hook card: lands by 0.5 s, gone as the hook ends
HOOK_SHRINK = 1.3  # then snaps small into its corner, so the hook move (and the face) stay clear

EDIT_KEYS = {"type", "clips", "output", "brightness", "cards"}
CLIP_KEYS = {"src", "start", "end", "speed", "intro", "text", "hook"}
CARD_KEYS = {"text", "in", "hit", "out", "kick", "shrink", "beats"}


def has_hook(edit):
    """Every video with several clips opens with a hook: its first clip, marked "hook": true."""
    return bool(edit["clips"]) and edit["clips"][0].get("hook", False)


def play_clips(edit):
    """Clips in play order. A clip's optional "intro" [start, end] (an educational step's finger
    count) is cut from the same source and plays right before the clip itself."""
    clips = []
    for clip in edit["clips"]:
        if "intro" in clip:
            clips.append({"src": clip["src"], "start": clip["intro"][0], "end": clip["intro"][1]})
        clips.append({k: v for k, v in clip.items() if k not in ("intro", "text", "hook")})
    return clips


def edit_cards(edit):
    """The edit's text cards: explicit "cards", or for educational edits one step card per step
    (a step = its intro + its move), opened by a hook card ("In <n> steps", or the hook clip's
    "text"). A move's peak is its step card's beat, so the number pops on the move."""
    if "cards" in edit:
        return edit["cards"]
    if edit["type"] != "educational":
        return []
    spans = iter(timeline.segments(play_clips(edit)))
    steps = []
    if has_hook(edit):  # text from the very first frame: muted scrollers decide in ~1-3 s
        hook, (_, hook_end) = edit["clips"][0], next(spans)
        card = {"text": hook.get("text", f"In {len(edit['clips']) - 1} steps"), "in": 0.0, "hit": HOOK_HIT}
        card["out"] = hook_end - HOOK_GAP
        if card["out"] > HOOK_SHRINK:  # a very short hook has no time to sit small
            card["shrink"] = HOOK_SHRINK
        steps.append(card)
    for n, clip in enumerate(edit["clips"][has_hook(edit) :], 1):
        start, end = next(spans)
        move_start = start
        if "intro" in clip:
            move_start, end = next(spans)
        steps.append(
            {
                "text": clip.get("text", f"Step {n}"),
                "in": start + STEP_IN,
                "hit": start + STEP_HIT,
                "out": end - STEP_GAP,
                "beats": [move_start + PEAK_LEAD],
            }
        )
    return steps


def problems(edit):
    """Every rule the edit breaks, as readable messages. Empty means it can be rendered."""
    found = []

    def require(ok, message):
        if not ok:
            found.append(message)

    kind = edit.get("type")
    require(kind in MODELS, f'"type" must be one of {sorted(MODELS)}, got {kind!r}')
    require(
        not set(edit) - EDIT_KEYS, f"unknown edit keys {sorted(set(edit) - EDIT_KEYS)} (allowed: {sorted(EDIT_KEYS)})"
    )
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
    clips = edit.get("clips", [])
    if len(clips) > 1:
        require(clips[0].get("hook", False), 'a video with several clips opens with a hook (first clip "hook": true)')
    require(not any(c.get("hook") for c in clips[1:]), "only the first clip can be the hook")
    if clips and clips[0].get("hook"):
        if kind == "sequence":
            require(clips[0].get("speed", 1) < 1, "a sequence hook plays in slow motion (speed < 1)")
        if kind == "educational":
            require(clips[0].get("speed", 1) == 1, "an educational hook plays at Touro's real speed (no speed change)")
    if found:
        return found  # card checks below assume a well-formed edit

    for index, card in enumerate(edit_cards(edit)):
        require(not set(card) - CARD_KEYS, f"unknown card keys {sorted(set(card) - CARD_KEYS)} in {card}")
        words = card.get("text", "").split()
        require(2 <= len(words) <= 6, f"a card has 2..6 words (kicker + key word): {card}")
        require(card.get("in", 0) < card.get("hit", -1) < card.get("out", -1), f"in < hit < out: {card}")
        require(
            card.get("hit", 0) - card.get("in", 0) <= 0.8,
            f"key word lands too late for short attention (hit - in <= 0.8): {card}",
        )
        require(card.get("kick") in (None, "left", "right"), f'kick is "left" or "right": {card}')
        require(
            "shrink" not in card or card.get("hit", 0) < card["shrink"] < card.get("out", 0),
            f"shrink must fall between hit and out: {card}",
        )
        beats = card.get("beats", [])
        require(
            beats == sorted(beats) and all(card.get("hit", 0) < b <= card.get("out", 0) for b in beats),
            f"beats are move moments in order, between hit and out: {card}",
        )
        if len(words) >= 2:
            require(
                cards.kicker_width(cards.compose(card, index)) <= cards.SAFE_W,
                f"kicker wider than the safe width: {card}",
            )
    return found


def load(edit_path):
    """Read an edit file; exit listing every broken rule instead of rendering a broken edit."""
    edit = json.loads(Path(edit_path).read_text())
    found = problems(edit)
    if found:
        sys.exit(f"{edit_path} breaks {len(found)} rule(s):\n- " + "\n- ".join(found))
    return edit
