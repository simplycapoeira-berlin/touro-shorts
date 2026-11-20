---
name: capoeira-shorts
description: Make or revise a Simplesmente Capoeira Instagram short with movement-timed brand text. Use when given a capoeira clip and text lines, or feedback on a rendered short.
---

# Capoeira shorts

Turn a 12–20 s vertical capoeira clip plus one to three short lines into a short whose text moves
with the body. STYLE.md has the full rules. This skill is the working procedure.

## Taste (settled through feedback; details and history in STYLE.md)

- Website look only: Archivo, black `#111` type, and a yellow `#F7E018` marker on the key word.
  **No blue or other colors.**
- Each card has two levels: a small UPPERCASE tracked kicker, then the last word as a huge key word
  sized to the safe width. Cards alternate left / right alignment (call and response).
- **The audience has a short attention span.** A card is readable about 0.6 s after `in`
  (`hit - in ≤ 0.8`) and is shown full size for a few seconds. Put the first card in the first second.
- **No long gaps between sentences.** If the next card is far away, don't let the current one
  vanish: set `shrink` (about 5 s into the clip) so it shrinks into its corner, and set its `out`
  to the next card's `in` − 0.3 s so they swap cleanly.
- **Text never blocks the movement.** Show a card only while the body is clear of the upper
  band (y ≈ 280–620).
- **The movement may remove the text.** When a kick sweeps through the band, use
  `"kick": "left"|"right"` with `out` = the frame the foot reaches the letters. A payoff kick
  is worth a quiet stretch with no text.
- No looping motion. Every motion either brings information in or takes it out.

## Procedure

1. **Find when.** Run `uv run shorts.py peaks "<clip>"` for the strongest motion moments.
2. **Find where.** Peaks say when, not where. Look at the body with a contact sheet:
   `ffmpeg -ss <t> -t 5.6 -i <clip> -vf "fps=5,scale=180:320,tile=14x2" -frames:v 1 sheet.png`.
   Note when the upper band is clear, and which way each kick sweeps through it.
3. **Write the edit** in `edits/<yymmdd>-<name>.json` (copy an existing one). The input path
   starts with `$SC_CONTENT/`.
4. **Check the edit:** run `uv run test_shorts.py`.
5. **Render:** run `uv run shorts.py render edits/<file>.json` (output in `out/`).
6. **Look at it.** Extract frames at `in`, `hit`, mid-hold and the exit / kick impact (cropped
   to the top 1100 px and stacked with `hstack`). Check:
   - no letter collisions;
   - text clear of the head and body at rest;
   - the kick impact lands on the foot (±2 frames).
   Fix the timing and render again before showing the user.
7. **Send the render** to the user, with one line per change.
8. **On feedback:** change the constants in `shorts.py` or the edit. Update STYLE.md's rules
   **and** add a row to its iteration log. Update `test_shorts.py` if a rule became checkable.
