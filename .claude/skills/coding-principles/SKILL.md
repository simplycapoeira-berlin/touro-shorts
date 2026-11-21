---
name: coding-principles
description: How code in this repo is written and changed. Karpathy's LLM-coding guidelines plus Ousterhout's "A Philosophy of Software Design", applied to touro-shorts. Use before any code change.
---

# Coding principles

Two sources, applied here: Karpathy's guidelines against common LLM coding mistakes, and John
Ousterhout's *A Philosophy of Software Design* (the central job is managing complexity). Where
each kind of change goes, and the rules CI enforces, are in AGENTS.md.

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

- **Deep module, simple interface.** The whole interface is `touro-shorts render | peaks | clean | archive`.
  An edit says only *what* and *when* (`text`, `in`, `hit`, `out`, `kick`). All layout, easing
  and compositing stay hidden inside.
- **Pull complexity down.** Hard decisions (alignment alternation, key-word sizing, kick physics)
  are made in code, not pushed to the edit author as options.
- **Define errors out of existence.** For example, an `out` past the clip end simply holds the
  card, and the kicker and key word come from `text` itself, so they can't disagree.
- **No information leakage.** Each fact lives in one place. Values are named constants at the top
  of their module; docs explain *why* and link instead of copying.
- **Design it twice.** For a new effect, consider two approaches and say why you chose one.
- **Comments say why**, not what. One line. Names are precise (`kicker`, `key`, `hit`, `kick`).

## Verify (Karpathy: goal-driven execution)

- Run the checks in AGENTS.md, render, then look at extracted frames. A change isn't done until
  you have seen it.
- Measure before optimizing (`cProfile`). Most render time is ffmpeg decoding 4K footage.
- Report honestly what was checked and what was not.
