# real speed hook and kick underline

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** style

## Feedback

The hook in the educational video should not be slow motion: just Touro's real, impressively
fast speed, only that moment at the beginning. And the kicks should add a yellow underline
under the word ("unterschreiben").

## Decision

- **Explicit hooks:** hooks are now marked explicitly with `"hook": true` on the first clip,
  instead of being inferred from slow motion. The speed is a rule per type:
  - a sequence hook plays slowed (speed < 1);
  - an educational hook plays at real speed (no speed change).
- 261120-steps opens with IMG_7017's aú at real speed, 4.5–5.4 s (0.9 s). The video is now
  19.1 s.
- **Kick underline:** each beat now draws a thick yellow underline below the highlight band,
  sweeping in the card's direction, and redraws it on every later beat. This replaces the
  highlight re-sweep from the previous decision, which was too subtle to read as "the kick
  underlines the word". The highlight band sweeps only once, on `hit`.
