# plain type, no underline

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** style

## Feedback

The "unterschreiben" underline that kicks drew under the words (still visible in the steps
video) isn't wanted. Remove that style completely and keep our type plain, with no extra
underscore.

## Decision

This replaces the kick-underline part of `2026-11-21-real-speed-hook-and-kick-underline.md`.

- The kick-drawn underline is removed from the code (`underline_box` and its constant are gone).
- Beats now only make the card pop. The type keeps exactly one yellow element, the highlight
  band that sweeps in on `hit`, as on the website.
- STYLE.md §3 says explicitly: no underlines or other extra decoration.
- A test renders a card after a kick and fails if any yellow appears below the highlight band,
  so the style can't come back unnoticed.
- 261120-steps re-rendered as v3. The sequence video picks up the change on its next render.
