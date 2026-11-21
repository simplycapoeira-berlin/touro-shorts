"""Self-check for the layout and timing rules in STYLE.md. Run: uv run test_shorts.py"""
import json
from pathlib import Path

from PIL import Image

import shorts

blank = Image.new("RGBA", (shorts.W, shorts.H))

for edit_path in Path(shorts.ROOT, "edits").glob("*.json"):
    edit = json.loads(edit_path.read_text())
    assert edit.get("type") in shorts.MODELS, f"unknown video type: {edit_path}"
    assert -0.2 <= edit.get("brightness", 0) <= 0.2, f"brightness is a subtle grade, not a fix: {edit_path}"
    assert not any(c["src"].startswith(("/", "~")) for c in edit["clips"]), f"machine-specific clip path: {edit_path}"
    for clip in edit["clips"]:
        assert 0.5 <= clip.get("speed", 1) <= 2, f"speed outside 0.5..2: {clip}"
        assert clip.get("start", 0) < clip.get("end", float("inf")), clip
        if edit["type"] == "educational":
            assert "start" in clip and "end" in clip, f"educational steps are explicit cuts: {clip}"
            intro = clip.get("intro", [0, 0.5])
            assert 0.5 <= intro[1] - intro[0] <= 1.2, f"finger count should last ~0.8-0.9 s: {clip}"
            assert intro[1] <= clip["start"], f"finger count comes before the move: {clip}"
    if edit["type"] == "sequence" and len(edit["clips"]) > 1:
        assert edit["clips"][0].get("speed", 1) < 1, f"a sequence opens with a slow-motion hook: {edit_path}"
    for index, card in enumerate(shorts.edit_cards(edit)):
        g = shorts.compose(card, index)
        assert shorts.MARGIN_X <= g["key_x"] and g["key_x"] + g["key_w"] <= shorts.W - shorts.MARGIN_X + 1, card
        kicker_w = sum(g["kicker_font"].getlength(c) for c in g["lead"]) + shorts.KICKER_SIZE * shorts.KICKER_TRACK * (len(g["lead"]) - 1)
        assert kicker_w <= shorts.SAFE_W, f"kicker wider than safe width: {card}"
        assert len(card["text"].split()) <= 6, f"more than 6 words: {card}"
        assert card["in"] < card["hit"] < card["out"], card
        assert card["hit"] - card["in"] <= 0.8, f"key word lands too late for short attention: {card}"
        assert card.get("kick") in (None, "left", "right"), card
        assert card["hit"] < card.get("shrink", card["hit"] + 1) < card["out"], f"shrink outside hold: {card}"

        def ink_at(t):
            return shorts.overlay_card(blank, g, card, t).getbbox()

        assert ink_at(card["in"] - 0.01) is None, "card visible before in"
        box = ink_at(card["hit"] + 0.05)
        assert box is not None, "card missing while holding"
        assert box[1] >= shorts.TEXT_TOP - 10, f"text above the safe zone: {card}"
        assert ink_at(card["out"] + 1.0) is None, "card still visible 1 s after out"

print("ok")
