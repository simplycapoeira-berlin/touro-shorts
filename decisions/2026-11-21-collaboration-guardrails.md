# collaboration guardrails

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** process

## Feedback

Different people will work on different parts of this repo through Claude and push to GitHub.
They may break things. We need tests, limitations, and a structure where decisions keep
accumulating in an extendable way.

## Decision

- **Modules by area:**
  - `cards.py`: text animation;
  - `models.py`: video types, edit rules and validation;
  - `timeline.py`: cutting and joining;
  - `archive.py`: cold storage;
  - `shorts.py`: CLI only.

  People working on different areas rarely touch the same file.
- **One gate for edits:** `models.load` validates every edit before anything runs. Unknown keys
  (typos), wrong types and broken timing rules are all listed at once.
- **Decisions as files:** STYLE.md's single iteration-log table became `decisions/`, one file
  per decision, so parallel changes don't conflict. STYLE.md keeps the current rules.
- **Tests:** `uv run pytest` covers every committed edit, the validation rules, card rendering,
  the archive, the decision files, and an end-to-end render of synthetic footage (format,
  metadata, privacy, determinism). It needs no real clips, so it runs anywhere.
- **CI:** GitHub Actions runs the tests on every push and pull request. Work happens on
  branches and reaches `main` through pull requests.
