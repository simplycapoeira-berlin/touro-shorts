# v4: shrink instead of gap

- **Date:** 2026-11-20
- **Requested by:** project owner
- **Area:** style

## Feedback

Good design overall, but the first sentence disappears and the gap to the second is too long. Keep the first sentence's start as it is; after 5 s it should shrink until the second sentence replaces it.

## Decision

New optional `shrink` time: the card scales into its top corner (to 45%, ease-out) and stays until it's swapped. Touro edit: "talent" from 0.6 s, shrinking from 5.0 s, out at 17.3 s, ending as "practice" enters at 17.6 s. The kick exit is unchanged.
