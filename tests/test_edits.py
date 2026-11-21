"""Every committed edit must pass the rules and must be safe to publish."""
import json
from pathlib import Path

import pytest

import models

EDITS = sorted(Path(models.ROOT, "edits").glob("*.json"))


@pytest.mark.parametrize("path", EDITS, ids=[p.name for p in EDITS])
def test_edit_follows_the_rules(path):
    assert models.problems(json.loads(path.read_text())) == []


@pytest.mark.parametrize("path", EDITS, ids=[p.name for p in EDITS])
def test_edit_has_no_machine_specific_paths(path):
    # Edits are public: absolute or home paths leak a collaborator's folders (and e.g. their email).
    edit = json.loads(path.read_text())
    paths = [c["src"] for c in edit["clips"]] + [edit["output"]]
    assert not [p for p in paths if p.startswith(("/", "~"))], "use in/..., out/... or $SC_CONTENT/..."


@pytest.mark.parametrize("path", EDITS, ids=[p.name for p in EDITS])
def test_edit_name_and_output(path):
    edit = json.loads(path.read_text())
    assert path.stem[:6].isdigit(), "edit files are named <yymmdd>-<name>.json"
    assert edit["output"].startswith("out/"), "renders go to out/ (git-ignored)"
