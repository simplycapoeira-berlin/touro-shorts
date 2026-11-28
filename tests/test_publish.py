"""Sharing through Postiz: nothing is booked by accident, at the wrong time, or on the wrong channel."""

from datetime import UTC, datetime

import pytest

from touro_shorts import models, publish

NOW = datetime(2026, 11, 28, 12, 0, tzinfo=UTC)
CONNECTED = [
    {"id": "ig-1", "identifier": "instagram", "name": "simplycapoeira"},
    {"id": "yt-1", "identifier": "youtube", "name": "TOURO"},
    {"id": "tt-old", "identifier": "tiktok", "name": "old", "disabled": True},
]


def test_time_needs_a_zone_and_the_future():
    assert publish.when("2026-12-02T18:00+01:00", NOW) == "2026-12-02T17:00:00.000Z"
    with pytest.raises(ValueError, match="time zone"):
        publish.when("2026-12-02T18:00", NOW)
    with pytest.raises(ValueError, match="past"):
        publish.when("2026-11-01T18:00+01:00", NOW)


def test_each_channel_must_be_connected_exactly_once():
    assert [c["id"] for c in publish.pick(CONNECTED, ["instagram", "youtube"])] == ["ig-1", "yt-1"]
    with pytest.raises(ValueError, match="0 connected 'tiktok'"):
        publish.pick(CONNECTED, ["tiktok"])  # the only TikTok channel is disabled


def test_book_uploads_once_and_schedules_every_channel(monkeypatch, tmp_path):
    calls = []
    answers = {"/integrations": CONNECTED, "/upload": {"id": "v1", "path": "https://media/v1.mp4"}, "/posts": [{}]}

    def fake_request(method, path, body=None, **_):
        calls.append((method, path, body))
        return answers[path]

    monkeypatch.setattr(publish, "_request", fake_request)
    video = tmp_path / "short-v2.mp4"
    video.write_bytes(b"mp4")
    publish.book(video, "2026-12-02T17:00:00.000Z", "Martelo de chão\n#capoeira", ["instagram", "youtube"])

    assert [c[1] for c in calls] == ["/integrations", "/upload", "/posts"]
    body = calls[2][2]
    assert body["type"] == "schedule" and body["date"] == "2026-12-02T17:00:00.000Z"
    assert [p["integration"]["id"] for p in body["posts"]] == ["ig-1", "yt-1"]
    assert all(p["value"][0]["image"] == [{"id": "v1", "path": "https://media/v1.mp4"}] for p in body["posts"])
    assert body["posts"][1]["settings"]["title"] == "Martelo de chão", "YouTube needs a title: the first line"


def test_caption_lives_in_the_edit_and_is_checked():
    edit = {"type": "sequence", "clips": [{"src": "in/a.mov"}], "output": "out/a.mp4", "cards": []}
    assert models.problems({**edit, "post": {"caption": "Martelo de chão #capoeira"}}) == []
    assert any("1..2200" in m for m in models.problems({**edit, "post": {"caption": ""}}))
    assert any("only a" in m for m in models.problems({**edit, "post": {"caption": "x", "at": "monday"}}))
    assert any("only a" in m for m in models.problems({**edit, "post": "just text"}))
