---
name: coding-principles
description: How code in this repo is written and changed. Karpathy's LLM-coding guidelines plus Ousterhout's "A Philosophy of Software Design", applied to touro-shorts. Use before any code change.
---

# Coding principles

Two sources, applied here: Karpathy's guidelines against common LLM coding mistakes, and John
Ousterhout's *A Philosophy of Software Design* (the central job is managing complexity).

## Before coding (Karpathy: think first)

- State your assumptions. If a request has two readings, name both and ask, or pick one and say so.
- Push back when a simpler approach exists.
- Turn each request into a check you can verify: a frame that shows it, a rule in
  `models.problems`, or a test in `tests/`.

## Simplicity (Karpathy: simplicity first, surgical changes)

- Write the minimum code for what was asked. No speculative options, config or abstractions.
- Every changed line traces to the request. Don't reformat or refactor neighbours.
- Remove what your change made unused (imports, constants, fonts, dependencies).
- Prefer deleting over adding. Example: the separate `mark` field was removed by making
  "the last word is the key word" a rule.

## Design (Ousterhout)

- **Deep module, simple interface.** The whole interface is `shorts.py render | peaks | archive`. An edit says only *what* and *when* (`text`, `in`, `hit`, `out`, `kick`). All
  layout, easing and compositing stay hidden inside.
- **Pull complexity down.** Hard decisions (alignment alternation, key-word sizing, kick physics)
  are made in code, not pushed to the edit author as options.
- **Define errors out of existence.** For example, an `out` past the clip end simply holds the
  card, and the kicker and key word come from `text` itself, so they can't disagree.
- **No information leakage.** Brand and motion values exist once, as named constants at the top
  of `cards.py` (frame size in `timeline.py`, edit rules in `models.py`). STYLE.md explains *why* and never duplicates the numbers.
- **Design it twice.** For a new effect, consider two approaches and say why you chose one. For
  example, words rising vertically was chosen over sliding horizontally because staggered slides
  collide.
- **Comments say why**, not what. One line. Names are precise (`kicker`, `key`, `hit`, `kick`).

## Verify (Karpathy: goal-driven execution)

- Run `uv run pytest` and render, then look at extracted frames. A change isn't done until
  you have seen it.
- Report honestly what was checked and what was not.

## Collaborating (many people, one repo)

Others change this repo in parallel through Claude. Assume your change meets theirs on `main`.

- **Stay in your area.** Each module owns one area (see the table in CLAUDE.md). A change that
  touches several areas is usually two pull requests.
- **Extend, don't fork.** Where to put common changes:
  - new edit field → `models.py` (`*_KEYS` + `problems`) + the code that uses it + a test in
    `tests/test_validation.py`;
  - new video type → `MODELS` + STYLE.md §8 + a decision + an example edit;
  - new look or motion → a constant or function in `cards.py` + STYLE.md + a decision.
- **Guard what you add.** If breaking it silently is possible, add a test. Never relax an
  existing test or rule to make your change pass. If a rule is wrong, change it explicitly with
  a decision file.
- **Small, reviewable pull requests.** CI must be green. Fill in the pull request checklist.
