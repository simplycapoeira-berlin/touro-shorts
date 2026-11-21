"""Visual regression: the text animation must look exactly like the committed reference frames.

Any change to how cards look or move fails here, so nobody changes the look by accident. To
change it on purpose: record a decision, then run `UPDATE_GOLDENS=1 uv run pytest
tests/test_goldens.py` and commit the new PNGs together with the decision.
"""

import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from touro_shorts import cards

GOLDENS = Path(__file__).parent / "goldens"
BAND = (0, 200, cards.W, 900)  # the text band: everything a card draws happens here
CARD = {"text": "It is not about talent", "in": 0.0, "hit": 0.6, "shrink": 2.0, "beats": [3.0], "out": 4.0}
KICKED = {**CARD, "kick": "left"}
STATES = {
    "swing-in": (CARD, 0, 0.35),
    "landed-left": (CARD, 0, 1.0),
    "landed-right": (CARD, 1, 1.0),
    "shrunk": (CARD, 0, 2.6),
    "beat-pop": (CARD, 0, 3.0 + cards.BEAT_DUR / 2),
    "kicked": (KICKED, 0, 4.12),
}


def render(card, index, t):
    blank = Image.new("RGBA", (cards.W, cards.H))
    return cards.overlay_card(blank, cards.compose(card, index), card, t).crop(BAND)


@pytest.mark.parametrize("name", STATES)
def test_card_matches_golden(name):
    frame, path = render(*STATES[name]), GOLDENS / f"{name}.png"
    if os.environ.get("UPDATE_GOLDENS"):
        GOLDENS.mkdir(exist_ok=True)
        frame.save(path, optimize=True)
    assert path.exists(), f"missing golden {path.name}: run with UPDATE_GOLDENS=1 to create it"
    # Tolerance only for font rasterisation noise between platforms, far below any visible change.
    diff = np.abs(np.asarray(frame, np.int16) - np.asarray(Image.open(path), np.int16))
    assert diff.mean() < 0.3, f"{name} looks different from its golden (mean pixel diff {diff.mean():.2f})"
