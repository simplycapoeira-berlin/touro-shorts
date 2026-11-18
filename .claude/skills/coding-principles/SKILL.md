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
- Turn each request into a check you can verify: a frame that shows it, or an assert in
  `test_shorts.py`.

## Simplicity (Karpathy: simplicity first, surgical changes)

- Write the minimum code for what was asked. No speculative options, config or abstractions.
- Every changed line traces to the request. Don't reformat or refactor neighbours.
- Remove what your change made unused (imports, constants, fonts, dependencies).
- Prefer deleting over adding. Example: the separate `mark` field was removed by making
  "the last word is the key word" a rule.

## Design (Ousterhout)

- **Deep module, simple interface.** The whole interface is `shorts.py render <edit.json>` and
  `peaks <clip>`. An edit says only *what* and *when* (`text`, `in`, `hit`, `out`, `kick`). All
  layout, easing and compositing stay hidden inside.
- **Pull complexity down.** Hard decisions (alignment alternation, key-word sizing, kick physics)
  are made in code, not pushed to the edit author as options.
- **Define errors out of existence.** For example, an `out` past the clip end simply holds the
  card, and the kicker and key word come from `text` itself, so they can't disagree.
- **No information leakage.** Brand and motion values exist once, as named constants at the top
  of `shorts.py`. STYLE.md explains *why* and never duplicates the numbers.
- **Design it twice.** For a new effect, consider two approaches and say why you chose one. For
  example, words rising vertically was chosen over sliding horizontally because staggered slides
  collide.
- **Comments say why**, not what. One line. Names are precise (`kicker`, `key`, `hit`, `kick`).

## Verify (Karpathy: goal-driven execution)

- Run `uv run test_shorts.py` and render, then look at extracted frames. A change isn't done until
  you have seen it.
- Report honestly what was checked and what was not.
