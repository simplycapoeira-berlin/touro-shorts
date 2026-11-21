"""Cold archive: verified copy, idempotent re-run, never overwrites, never deletes."""

import json

import pytest

from touro_shorts import archive


def test_archive_copies_verifies_and_is_idempotent(tmp_path):
    src, dest = tmp_path / "src", tmp_path / "drive" / "edit"
    src.mkdir()
    (src / "clip.mov").write_bytes(b"raw footage")
    first = archive.archive([src / "clip.mov", src / "clip.mov"], dest)
    assert list(first) == ["clip.mov"] and (dest / "clip.mov").read_bytes() == b"raw footage"
    assert json.loads((dest / "manifest.json").read_text()) == first
    assert archive.archive([src / "clip.mov"], dest) == first, "re-archiving must be a no-op"
    assert not list(dest.glob("*.part")), "no partial files left behind"


def test_archive_never_overwrites_and_never_deletes(tmp_path):
    src, dest = tmp_path / "src", tmp_path / "drive"
    src.mkdir()
    (src / "clip.mov").write_bytes(b"raw footage")
    archive.archive([src / "clip.mov"], dest)
    (src / "clip.mov").write_bytes(b"other footage")
    with pytest.raises(SystemExit):
        archive.archive([src / "clip.mov"], dest)
    assert (dest / "clip.mov").read_bytes() == b"raw footage"
    assert (src / "clip.mov").exists()
