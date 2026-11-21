# playful text and educational hook

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** style

## Feedback

Start the educational video with a hook too: the last great, catchy move from Touro, then the
steps. Make "talent" less present and more playful. It shrinks too slowly and feels detached
from the video; it should move with the moment. Kicks should keep knocking text away, and kicks
could also underline the yellow-marked word.

## Decision

- **Shrink snaps:** `shrink` is now a 0.35 s springy snap to 45%, not a slow fade-down. This
  applies to every edit; the touro edit re-renders with the snap too.
- **Beats:** a new card field `beats` (times of kicks/moves). On each beat, the card pops 12%
  for 0.3 s and the yellow marker sweeps under the key word again, so the kick underlines the
  word. Educational step cards get their move's peak as a beat automatically.
- **Educational hook:** every type may now open with a slow-motion hook (first clip speed < 1),
  and the rule requires it when there are several clips. The hook gets no card.
  - 261120-steps opens with IMG_7017's aú (4.55–5.35 s at 0.5×).
  - Move cuts are now peak −1.4/+1.4 s, keeping the video at 19.8 s.
- **261120-sequence re-timed:**
  - "talent" snaps small at 3.0 s, is underlined by the 9.0 s kick and kicked out at 9.6 s;
  - "practice" enters at 10.2 s, is underlined by the armada (12.95 s) and the high kick
    (13.6 s), and is kicked out by the aú (16.1 s).

  Total text-free gap: ~0.6 s instead of ~4.4 s.
