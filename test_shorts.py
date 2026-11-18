"""Self-check for the layout and timing rules in STYLE.md. Run: uv run test_shorts.py"""
import json
from pathlib import Path

from PIL import Image

import shorts

blank = Image.new("RGBA", (shorts.W, shorts.H))

for edit_path in Path(shorts.ROOT, "edits").glob("*.json"):
    for index, card in enumerate(json.loads(edit_path.read_text())["cards"]):
        g = shorts.compose(card, index)
        assert shorts.MARGIN_X <= g["key_x"] and g["key_x"] + g["key_w"] <= shorts.W - shorts.MARGIN_X + 1, card
        kicker_w = sum(g["kicker_font"].getlength(c) for c in g["lead"]) + shorts.KICKER_SIZE * shorts.KICKER_TRACK * (len(g["lead"]) - 1)
        assert kicker_w <= shorts.SAFE_W, f"kicker wider than safe width: {card}"
        assert len(card["text"].split()) <= 6, f"more than 6 words: {card}"
        assert card["in"] < card["hit"] < card["out"], card
        assert card["hit"] - card["in"] <= 0.8, f"key word lands too late for short attention: {card}"
        assert card.get("kick") in (None, "left", "right"), card

        def ink_at(t):
            return shorts.overlay_card(blank, g, card, t).getbbox()

        assert ink_at(card["in"] - 0.01) is None, "card visible before in"
        box = ink_at(card["hit"] + 0.05)
        assert box is not None, "card missing while holding"
        assert box[1] >= shorts.TEXT_TOP - 10, f"text above the safe zone: {card}"
        assert ink_at(card["out"] + 1.0) is None, "card still visible 1 s after out"

print("ok")
