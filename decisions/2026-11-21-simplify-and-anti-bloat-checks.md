# simplify the docs and add checks against bloat

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** process

## Feedback

Scan the repository for unnecessary, duplicated and overly verbose content and make it simpler.
Add a mechanism that keeps the repository from getting sloppy, based on existing solutions, and
be very safe.

## Decision

**What the scan found:** the code was clean (no dead code; one function at complexity 12), but
the docs repeated each other, and the copies had drifted:
- the README's example edits failed validation (no hook), it named renders `out/<name>.mp4`
  (they are `-v<n>`), and it linked a font license path that no longer existed;
- STYLE.md and the editing skill each gave a different educational move cut (+1.4 s, +1.7 s);
  the real cut, since the hook-research decision, is −1.4 s / +1.3 s (2.7 s);
- the skill said to shrink a card ~5 s in, where STYLE.md says ~1.5 s after `hit`;
- the field reference existed three times (README, `cli.py`, `models.py`), and the area table
  three times (README, AGENTS.md, a skill pointing to CLAUDE.md).

**Simplified:** each fact now lives in one place, and the others link to it:
- the edit fields live in the README; `cli.py` and `models.py` only point there;
- the taste rules and type recipes live in STYLE.md; the editing skill is the procedure only;
- the collaboration rules live in AGENTS.md;
- the README went from 179 to 112 lines.

Code, rendering and look are unchanged: the reference frames and all edits pass as before.
Names (repo, package, commands, modules) were already short and are kept.

**Checks against bloat (tools, not instructions):** these follow the common practice of
executable documentation (README examples run as tests, as doctest and pytest-codeblocks do)
and of complexity and dead-code gates for AI-written code.
- `tests/test_docs.py`:
  - every file a doc links to or names exists;
  - every `touro-shorts` command a doc names exists;
  - every JSON example edit passes validation;
  - every living doc stays within a line budget set just above its current size.
- ruff `C90`: no function may be more complex than today's maximum (12).
- vulture (dead code, confidence ≥ 80) in CI.

A limit may be lowered at any time; raising one needs a decision. Decision files are history and
are not checked.
