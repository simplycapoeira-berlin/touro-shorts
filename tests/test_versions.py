"""Renders are versions: never overwritten, deleted only on request, nothing else touched."""
import pytest

import versions


def test_versions_count_up_and_ignore_other_files(tmp_path):
    out = tmp_path / "edit.mp4"
    assert versions.latest(out) is None and versions.next_path(out).name == "edit.v1.mp4"
    for name in ["edit.v1.mp4", "edit.v2.mp4", "edit.v10.mp4", "edit.v2.timeline.mp4", "edit-other.v3.mp4", "edit.mp4"]:
        (tmp_path / name).write_bytes(b"x")
    assert [p.name for p in versions.all_versions(out)] == ["edit.v1.mp4", "edit.v2.mp4", "edit.v10.mp4"]
    assert versions.next_path(out).name == "edit.v11.mp4"


def test_prune_keeps_the_chosen_version_and_nothing_else_is_touched(tmp_path):
    out = tmp_path / "edit.mp4"
    for name in ["edit.v1.mp4", "edit.v2.mp4", "edit.v3.mp4", "notes.txt"]:
        (tmp_path / name).write_bytes(b"x")
    assert versions.prune(out, keep=2).name == "edit.v2.mp4"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["edit.v2.mp4", "notes.txt"]
    assert versions.prune(out).name == "edit.v2.mp4", "default keeps the latest"


def test_prune_refuses_an_unknown_version_and_deletes_nothing(tmp_path):
    out = tmp_path / "edit.mp4"
    (tmp_path / "edit.v1.mp4").write_bytes(b"x")
    with pytest.raises(SystemExit):
        versions.prune(out, keep=7)
    assert (tmp_path / "edit.v1.mp4").exists()
