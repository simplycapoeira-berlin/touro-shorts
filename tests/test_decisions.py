"""Decision files follow the template in decisions/README.md, so the history stays readable."""

import re
from pathlib import Path

import pytest

DECISIONS = sorted(p for p in (Path(__file__).parents[1] / "decisions").glob("*.md") if p.name != "README.md")
AREAS = {"style", "video-type", "pipeline", "archive", "process"}


def test_there_is_a_history():
    assert DECISIONS


@pytest.mark.parametrize("path", DECISIONS, ids=[p.name for p in DECISIONS])
def test_decision_format(path):
    text = path.read_text()
    assert re.match(r"\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$", path.name), "name: <yyyy-mm-dd>-<slug>.md"
    assert f"- **Date:** {path.name[:10]}" in text, "the Date line matches the file name"
    assert "- **Requested by:**" in text
    area = re.search(r"- \*\*Area:\*\* (\S+)", text)
    assert area and area.group(1) in AREAS, f"Area is one of {sorted(AREAS)}"
    assert "## Feedback" in text and "## Decision" in text
