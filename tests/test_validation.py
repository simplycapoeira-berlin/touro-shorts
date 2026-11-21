"""The rules in models.problems catch the mistakes collaborators are likely to make."""

import copy

import pytest

from touro_shorts import models

GOOD = {
    "type": "sequence",
    "clips": [
        {"src": "in/a.mov", "start": 1.0, "end": 2.0, "speed": 0.5, "hook": True},
        {"src": "in/a.mov", "start": 0, "end": 10},
    ],
    "output": "out/a.mp4",
    "cards": [{"text": "It is not about talent", "in": 0.5, "hit": 1.1, "out": 4.0, "kick": "left"}],
}


def broken(change):
    edit = copy.deepcopy(GOOD)
    change(edit)
    return models.problems(edit)


def test_good_edit_passes():
    assert models.problems(GOOD) == []


@pytest.mark.parametrize(
    "change, expected",
    [
        (lambda e: e.update(type="vlog"), '"type" must be one of'),
        (lambda e: e.update(brightnes=-0.1), "unknown edit keys"),
        (lambda e: e.update(brightness=-0.5), "subtle grade"),
        (lambda e: e.pop("output"), 'needs "clips" and "output"'),
        (lambda e: e["clips"][0].update(sped=0.5), "unknown clip keys"),
        (lambda e: e["clips"][0].update(speed=0.25), "speed must be 0.5..2"),
        (lambda e: e["clips"][1].update(start=12), "start must be before end"),
        (lambda e: e["clips"][0].pop("hook"), "opens with a hook"),
        (lambda e: e["clips"][0].update(speed=1), "sequence hook plays in slow motion"),
        (lambda e: e["clips"][1].update(hook=True), "only the first clip"),
        (lambda e: e["cards"][0].update(kik="left"), "unknown card keys"),
        (lambda e: e["cards"][0].update(text="talent"), "2..6 words"),
        (lambda e: e["cards"][0].update(hit=0.4), "in < hit < out"),
        (lambda e: e["cards"][0].update(hit=2.0), "lands too late"),
        (lambda e: e["cards"][0].update(kick="up"), 'kick is "left" or "right"'),
        (lambda e: e["cards"][0].update(shrink=9.0), "shrink must fall between"),
        (lambda e: e["cards"][0].update(beats=[3.0, 2.0]), "beats are move moments"),
        (lambda e: e["cards"][0].update(beats=[0.2]), "beats are move moments"),
        (
            lambda e: e["cards"][0].update(
                text="Supercalifragilistic extraordinarily ridiculously long kicker words here"
            ),
            "safe width",
        ),
    ],
)
def test_rule_is_enforced(change, expected):
    found = broken(change)
    assert any(expected in message for message in found), found


def test_educational_steps_need_explicit_cuts_and_a_short_finger_count():
    edit = {
        "type": "educational",
        "output": "out/s.mp4",
        "clips": [{"src": "in/a.mov", "intro": [0.2, 3.0], "start": 4.0}],
    }
    found = " ".join(models.problems(edit))
    assert "explicit cuts" in found and "finger count" in found


def test_educational_cards_are_generated_per_step():
    edit = {
        "type": "educational",
        "output": "out/s.mp4",
        "clips": [
            {"src": "in/a.mov", "start": 4.0, "end": 5.5, "hook": True},
            {"src": "in/a.mov", "intro": [1.0, 1.8], "start": 3.0, "end": 6.0},
            {"src": "in/b.mov", "start": 2.0, "end": 5.0, "text": "Step 2 aú"},
        ],
    }
    steps = models.edit_cards(edit)
    assert [s["text"] for s in steps] == ["In 2 steps", "Step 1", "Step 2 aú"]
    assert steps[1]["in"] == pytest.approx(1.5 + models.STEP_IN)  # after the 1.5 s hook
    assert steps[2]["in"] == pytest.approx(1.5 + 0.8 + 3.0 + models.STEP_IN)  # after step 1's intro + move
    assert models.problems(edit) == []


def test_load_lists_every_problem_and_exits(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"type": "vlog", "clip": []}')
    with pytest.raises(SystemExit) as stop:
        models.load(path)
    assert "rule(s)" in str(stop.value) and '"type"' in str(stop.value) and "unknown edit keys" in str(stop.value)


def test_educational_hook_gets_a_first_frame_card_and_steps_get_their_peak_as_beat():
    edit = {
        "type": "educational",
        "output": "out/s.mp4",
        "clips": [
            {"src": "in/a.mov", "start": 4.0, "end": 6.0, "hook": True},
            {"src": "in/a.mov", "intro": [1.0, 1.8], "start": 3.0, "end": 5.8},
        ],
    }
    hook_card, step = models.edit_cards(edit)
    assert hook_card["text"] == "In 1 steps" and hook_card["in"] == 0.0, "text from the first frame"
    assert step["text"] == "Step 1" and step["in"] == pytest.approx(2.0 + models.STEP_IN)
    assert step["beats"] == [pytest.approx(2.0 + 0.8 + models.PEAK_LEAD)]  # hook + intro + lead to the peak
    assert models.problems(edit) == []


def test_educational_hook_keeps_real_speed():
    edit = {
        "type": "educational",
        "output": "out/s.mp4",
        "clips": [
            {"src": "in/a.mov", "start": 4.0, "end": 5.0, "speed": 0.5, "hook": True},
            {"src": "in/a.mov", "intro": [1.0, 1.8], "start": 3.0, "end": 5.8},
        ],
    }
    assert any("real speed" in m for m in models.problems(edit))
