"""Card drawing obeys the motion grammar (STYLE.md §3) for every committed edit."""
import json
from pathlib import Path

import pytest
from PIL import Image

import cards
import models

BLANK = Image.new("RGBA", (cards.W, cards.H))
CASES = [(path.name, index, card)
         for path in sorted(Path(models.ROOT, "edits").glob("*.json"))
         for index, card in enumerate(models.edit_cards(json.loads(path.read_text())))]


def ink_at(card, index, t):
    return cards.overlay_card(BLANK, cards.compose(card, index), card, t).getbbox()


@pytest.mark.parametrize("name, index, card", CASES, ids=[f"{n}#{i}" for n, i, _ in CASES])
def test_card_lifecycle(name, index, card):
    assert ink_at(card, index, card["in"] - 0.01) is None, "visible before in"
    box = ink_at(card, index, card["hit"] + 0.05)
    assert box is not None, "missing right after landing"
    assert box[1] >= cards.TEXT_TOP - 10, "above the Instagram safe zone"
    assert ink_at(card, index, card["out"] + 1.0) is None, "still visible 1 s after out"


@pytest.mark.parametrize("index", [0, 1])
def test_key_word_fits_the_safe_width_on_both_sides(index):
    g = cards.compose({"text": "It is about practice"}, index)
    assert cards.MARGIN_X <= g["key_x"] and g["key_x"] + g["key_w"] <= cards.W - cards.MARGIN_X + 1


def test_cards_alternate_sides():
    assert cards.compose({"text": "a b"}, 0)["side"] == 1 and cards.compose({"text": "a b"}, 1)["side"] == -1


def test_shrunk_card_stays_in_its_corner():
    card = {"text": "It is not about talent", "in": 0.0, "hit": 0.6, "shrink": 2.0, "out": 10.0}
    full, small = ink_at(card, 0, 1.5), ink_at(card, 0, 9.0)
    assert small[2] - small[0] < 0.6 * (full[2] - full[0]), "shrink did not shrink"
    assert small[0] >= cards.MARGIN_X - 2 and small[1] >= cards.TEXT_TOP - 10, "shrink left its corner"


def test_kicked_card_scatters_then_disappears():
    card = {"text": "It is about practice", "in": 0.0, "hit": 0.6, "out": 2.0, "kick": "left"}
    assert ink_at(card, 1, 2.2) is not None
    assert ink_at(card, 1, 2.0 + cards.KICK_WAVE + cards.KICK_FADE + 0.01) is None


def test_shrink_snaps_instead_of_fading_down():
    card = {"text": "It is not about talent", "in": 0.0, "hit": 0.6, "shrink": 2.0, "out": 10.0}
    assert cards.card_scale(card, 1.99) == 1.0
    assert cards.card_scale(card, 2.0 + cards.SHRINK_SNAP) == pytest.approx(cards.SHRINK_TO)


def test_beat_pops_the_card_and_redraws_the_underline():
    card = {"text": "It is about practice", "in": 0.0, "hit": 0.6, "beats": [3.0], "out": 6.0}
    g = cards.compose(card, 1)
    assert cards.card_scale(card, 3.0 + cards.BEAT_DUR / 2) == pytest.approx(1 + cards.BEAT_POP)
    assert cards.card_scale(card, 3.0 + cards.BEAT_DUR + 0.01) == 1.0
    width = lambda t: cards.marker_box(g, card, t)[2] - cards.marker_box(g, card, t)[0]
    assert width(3.0 + cards.MARK_SWEEP / 4) < 0.9 * width(2.9), "the move underlines the word again"
    assert width(3.0 + cards.MARK_SWEEP) == pytest.approx(width(2.9))
