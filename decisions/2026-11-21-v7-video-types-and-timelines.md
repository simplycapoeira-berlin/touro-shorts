# v7: video types and timelines

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** style

## Feedback

New raw clips in `in/`. Two edits: one like before (an attention-heavy movement first, then the sequence with our type, same text for now), and one educational step-by-step video with cuts. Classify the target videos as models (types) and keep them as output metadata. Later, users only bring videos and text and everything runs reliably and repeatably.

## Decision

Two video types (§8): `sequence` and `educational`. New `clips` timeline (cut, slow motion, join, rotate/scale any source) replaces the single `input`. `in/` and `out/` are git-ignored. 261120-sequence: 0.5× hook of IMG_7011's armada and high kick, then the sequence; "talent" lands during the hook and is kicked out by the armada at 12.95 s; "practice" is kicked out by the aú at 16.1 s; the calm ginga tail is trimmed (17.8 s total). 261120-steps: IMG_7013–7017 cut to their move (peak −1.7 s / +1.9 s), with automatic STEP 1–5 cards (18 s). Confirmed: plain step numbers are the default; names only when the user gives them. Outputs carry the type in their metadata, and GPS is stripped.
