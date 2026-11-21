"""End to end on synthetic footage: no real clips needed, so this runs on every machine and in CI."""

import json
import shutil
import subprocess

import pytest

from touro_shorts import cli as shorts

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")


def probe(path):
    out = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,width,height,r_frame_rate:format=duration:format_tags",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return json.loads(out)


@pytest.fixture(scope="module")
def rendered(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("render")
    clip = tmp / "clip.mov"
    # A 4 s portrait 60 fps clip with sound and a fake GPS tag, like an iPhone recording.
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=540x960:rate=60:duration=4",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=4",
            "-shortest",
            "-metadata",
            "location=+52.5200+013.4050/",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(clip),
        ],
        check=True,
    )
    edit = {
        "type": "sequence",
        "clips": [
            {"src": str(clip), "start": 1.0, "end": 1.5, "speed": 0.5, "hook": True},
            {"src": str(clip), "start": 0, "end": 3.0},
        ],
        "output": str(tmp / "out.mp4"),
        "brightness": -0.05,
        "cards": [{"text": "It is not about talent", "in": 0.2, "hit": 0.8, "out": 2.5, "kick": "left"}],
    }
    edit_path = tmp / "260101-synthetic.json"
    edit_path.write_text(json.dumps(edit))
    first = shorts.render(edit_path)
    second = shorts.render(edit_path)
    return first, second


def test_output_format(rendered):
    path = rendered[0]
    info = probe(path)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    assert (video["width"], video["height"], video["r_frame_rate"]) == (1080, 1920, "30/1")
    assert any(s["codec_type"] == "audio" for s in info["streams"])
    assert float(info["format"]["duration"]) == pytest.approx(1.0 + 3.0, abs=0.1)  # 0.5 s hook at 0.5x + 3 s


def test_metadata_carries_type_and_drops_source_tags(rendered):
    tags = probe(rendered[0])["format"]["tags"]
    assert tags["genre"] == "sequence"
    assert json.loads(tags["comment"])["text"] == ["It is not about talent"]
    assert "location" not in json.dumps(tags), "source metadata (GPS) must be stripped"


def test_renders_are_versions_and_identical_renders_are_not_duplicated(rendered):
    first, second = rendered
    assert first.name == "out-v1.mp4", "a render is a new version, never the bare output name"
    assert second == first, "the same edit renders byte-identical, so no duplicate version is stored"
    assert sorted(p.name for p in first.parent.glob("out*.mp4")) == ["out-v1.mp4"]


def test_text_is_drawn(rendered):
    path = rendered[0]

    def mean_dark_top(t):
        raw = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-ss",
                str(t),
                "-i",
                str(path),
                "-frames:v",
                "1",
                "-vf",
                "crop=1080:400:0:280,format=gray",
                "-f",
                "rawvideo",
                "-",
            ],
            capture_output=True,
            check=True,
        ).stdout
        return sum(b < 40 for b in raw) / len(raw)

    assert mean_dark_top(1.5) > mean_dark_top(3.8) + 0.01, "the card's black type should darken the text band"
