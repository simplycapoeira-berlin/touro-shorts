"""The docs stay true and small: they are checked against the code like the code itself.

Decision files are history and are not checked here (they may name things that no longer exist).
"""

import json
import re
from pathlib import Path

import pytest

from touro_shorts import cli, models

ROOT = Path(__file__).parents[1]
# Line budgets for the living docs. Growing one is a visible change in the pull request: first
# cut what is duplicated or stale. Raising a budget needs a decision (AGENTS.md).
BUDGETS = {
    "README.md": 115,
    "STYLE.md": 155,
    "PRODUCT.md": 90,
    "AGENTS.md": 65,
    "CLAUDE.md": 10,
    "decisions/README.md": 35,
    ".claude/skills/capoeira-shorts/SKILL.md": 50,
    ".claude/skills/coding-principles/SKILL.md": 50,
    ".github/pull_request_template.md": 15,
}
DOCS = {name: (ROOT / name).read_text() for name in BUDGETS}
REPO_PATH = re.compile(r"`((?:src|tests|edits|decisions|docs|\.claude|\.github)/[^`<>*\s]*)`")
LINK = re.compile(r"\]\(([^)#\s]+)")


@pytest.mark.parametrize("name", BUDGETS)
def test_doc_within_budget(name):
    lines = len(DOCS[name].splitlines())
    assert lines <= BUDGETS[name], f"{name} has {lines} lines (budget {BUDGETS[name]}): cut duplication first"


def test_every_living_doc_is_budgeted():
    living = {str(p.relative_to(ROOT)) for p in ROOT.glob("*.md")} | {
        str(p.relative_to(ROOT)) for p in (ROOT / ".claude/skills").glob("*/SKILL.md")
    }
    assert living <= set(BUDGETS), f"add a budget for {sorted(living - set(BUDGETS))}"


@pytest.mark.parametrize("name", BUDGETS)
def test_named_files_exist(name):
    text, base = DOCS[name], (ROOT / name).parent
    links = [base / t for t in LINK.findall(text) if "://" not in t]
    paths = [ROOT / t for t in REPO_PATH.findall(text)]
    missing = [str(p.relative_to(ROOT)) for p in links + paths if not p.exists()]
    assert not missing, f"{name} names files that don't exist: {missing}"


@pytest.mark.parametrize("name", BUDGETS)
def test_named_commands_exist(name):
    used = set(re.findall(r"touro-shorts (\w+)", DOCS[name])) - {"is", "command"}
    assert used <= set(cli.COMMANDS), f"{name} uses unknown commands {sorted(used - set(cli.COMMANDS))}"


def test_example_edits_are_valid():
    blocks = [b for text in DOCS.values() for b in re.findall(r"```json\n(.*?)```", text, re.S)]
    assert blocks, "the README shows an example edit"
    for block in blocks:
        assert models.problems(json.loads(block)) == [], block
