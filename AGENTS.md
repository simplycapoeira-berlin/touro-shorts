# touro-shorts: instructions for AI agents

The shared instructions for every AI coding agent (Claude Code, Codex, Cursor, Copilot, …).
An AI editing assistant for capoeira video editors. Several people change this repo through
agents, each working on their own part, and everything meets on GitHub. Read before working:

- [PRODUCT.md](PRODUCT.md): what this product is, who it is for, its principles and feature map.
- [STYLE.md](STYLE.md): the current design rules. It is the source of truth for taste.
- [decisions/](decisions/): why each rule exists. One file per decision.
- `.claude/skills/capoeira-shorts/SKILL.md`: how to make or revise an edit.
- `.claude/skills/coding-principles/SKILL.md`: how to change the code, and where each kind of change goes.

## Where things live

The app is the package `src/touro_shorts/`, installed by `uv sync` with the command `touro-shorts`.

| Area | File | Change it when… |
|---|---|---|
| Text animation | `src/touro_shorts/cards.py` | the look or motion of text changes |
| Video types and edit rules | `src/touro_shorts/models.py` | a new type, a new edit field, or a new rule |
| Cutting, joining, grading | `src/touro_shorts/timeline.py` | how clips become one timeline |
| Render versions | `src/touro_shorts/versions.py` | how renders are numbered, kept or cleaned |
| Cold storage | `src/touro_shorts/archive.py` | how finished edits are stored |
| Commands | `src/touro_shorts/cli.py` | a new command; it only wires the modules together |
| Brand fonts | `src/touro_shorts/fonts/` | never, unless the brand changes (a decision) |
| Edits | `edits/*.json` | a new video (validated by `models.load`) |
| Tests | `tests/` (reference frames in `tests/goldens/`) | every rule and behaviour |

## Rules that always apply

- **Work on a branch and open a pull request.** `main` is protected: direct pushes are rejected,
  and a pull request merges only when it is up to date and its `checks` pass.
- **The checks are the hooks in `.pre-commit-config.yaml`.** Run `uv run pre-commit install`
  once; then they run on every commit, and CI runs the same hooks on every push. To run them by
  hand: `uv run pre-commit run --all-files`. A red check means stop and fix; never skip a hook
  (`--no-verify`) or weaken a check to get green.
- **Keep it small: each fact lives in one place.** Link to it instead of copying it, because
  copies drift apart. The hooks enforce this (complexity limit, dead code, and
  `tests/test_docs.py` for the docs). If a doc hits its line budget, cut duplication first.
  Lower a limit when you can, never raise one without a decision.
- **Every design or behaviour change** adds a file in `decisions/` (template in
  `decisions/README.md`) and updates the matching STYLE.md section, in the same pull request.
  Never rewrite someone else's decision. Add a new one that replaces it.
- **The look is locked by reference frames** (`tests/test_goldens.py`). Changing how text looks
  or moves needs a decision first, then `UPDATE_GOLDENS=1 uv run pytest tests/test_goldens.py`,
  with the new PNGs committed in the same pull request.
- **Every new rule becomes checkable.** Put it in `models.problems` (edits) or a test (code),
  so the next person can't break it silently.
- **A new kind of video gets a new type**: an entry in `MODELS`, a recipe in STYLE.md §8, a
  decision, and an example edit that passes the tests. Never a one-off edit.
- **Never commit raw clips (`in/`), renders (`out/`) or machine-specific paths.** Clip paths in
  edit files are repo-relative (`in/...`) or use `$SC_CONTENT/...`. The tests reject absolute paths.
- **Renders are versions** (`out/<name>-v<n>.mp4`), never overwritten. Show the user which
  version you made. Deleting versions (`touro-shorts clean`), archiving (`touro-shorts archive`) and
  deleting raw clips in `in/` only happen when a user asks, in that order. Never put their
  Drive path in a committed file.
- **Product changes** (users, scope, principles, features) update PRODUCT.md and add a decision.
- **Verify visually:** extract frames from the render with ffmpeg and look at them before
  claiming an edit is done. Tests prove the pipeline works; only frames prove the edit looks right.
