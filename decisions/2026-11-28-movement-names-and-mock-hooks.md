# movement names, mock-ginga hooks, hook card snaps small

- **Date:** 2026-11-28
- **Requested by:** project owner
- **Area:** video-type

## Feedback

Two new step-by-step videos, one per movement: Martelo de chão and Ginga, hook first as before,
but now with the movement's name. For the Ginga, a correct, clean ginga matters (not a flat
one), so a friend recorded mock (wrong) gingas: make try-out versions with them.

## Decision

- **Name:** the hook card shows the movement's name huge (the hook clip's `text`: "Martelo de
  chão", "A clean ginga"). The step cards stay STEP 1, 2, 3… (chosen by the owner).
- **Mock hooks:** a try-out version opens with a mock ginga that ends on Touro's "no-no" finger
  wag, with the text "Not like this", followed by the clean steps. Three mock takes, so three
  try-out edits (`261128-ginga-mock1..3`) next to the clean one (`261128-ginga`).
- **The hook card snaps small at 1.3 s** (`HOOK_SHRINK`, the existing snap from STYLE §3 4b).
  In the Ginga footage Touro stands close, so a full-size hook card covered his face and the
  finger wag for the whole hook. Hooks shorter than ~1.6 s keep the full-size card. This also
  changes earlier educational edits when they are rendered again.
- **Step 4 of the Ginga** comes from the second half of IMG_7071 (a hand count read as four
  fingers at ~29 s, then the full, wide ginga), cut 4 s long instead of 2.7 s, because a ginga
  needs more than one cycle to read.
- **The Martelo de chão hook kicks its name away** (follow-up feedback: keep v1's full-size
  card, and let the kick get rid of the text, as in the sequence videos). The hook clip may now
  set `kick` and `kick_at` (educational edits only): the card stays big and is knocked off at
  the impact instead of snapping small. Martelo: the foot reaches "chão" at 1.0 s, sweeping
  right (v3).
- **Correction (same day, owner):** the count at ~29 s of IMG_7071 shows five fingers: it is
  step 5, not 4. The real step 4 (four fingers at ~14 s, then a wide side ginga, peak ~20.2 s)
  was added. To stay ≤ 20 s with five steps, every move uses the standard 2.7 s cut (step 5
  too) and every hook is 2.1 s (the mock hooks keep the end of the wrong ginga and the wag).
