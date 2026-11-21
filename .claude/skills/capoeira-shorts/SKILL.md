---
name: capoeira-shorts
description: Make or revise a Simplesmente Capoeira Instagram short (sequence or educational type) from raw clips and text, with cuts, slow motion and movement-timed brand text. Use when given capoeira clips (e.g. in in/) and text, or feedback on a rendered short.
---

# Capoeira shorts

Turn raw capoeira clips plus a little text into a 12–20 s vertical short. The video is cut and
joined by type (`sequence` or `educational`), and its text moves with the body. STYLE.md has the
full rules (§8 for the types). This skill is the working procedure.

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
- No looping motion. Every motion either brings information in or takes it out, or answers
  a move (`beats`: the card pops and the kick underlines the key word again).
- Every multi-clip video opens with a hook (`"hook": true` on the first clip, no card): slow
  motion in a sequence, Touro's real speed in an educational video.

## Procedure

The goal is repeatability. Users bring clips (usually in `in/`) and text. Every decision below
follows a rule in STYLE.md §8, so the same inputs give the same edit. Don't invent a new look;
if something isn't covered, ask, then record the answer in STYLE.md.

0. **Classify.** Look at a full-length contact sheet of every clip:
   `ffmpeg -i <clip> -vf "fps=2,scale=96:-2,tile=21x2" -frames:v 1 sheet.png`. Make sure the
   tile holds every frame (fps × duration ≤ 42), or the sheet silently cuts the end off.
   - One continuous flowing clip → `sequence`.
   - Several "stand, show one move, return" clips → `educational`, one step per clip in
     recording order.
   - Clips that fit neither → ask the user.
   - Check the audio too (`astats`). Silent intros can be cut; speech must not be cut
     without asking.
1. **Find when.** Run `uv run shorts.py peaks "<clip>"` for the strongest motion moments.
2. **Find where.** Peaks say when, not where. They also fire on turns and steps. Confirm every
   move on a 10–15 fps sheet:
   `ffmpeg -ss <t> -t 2.4 -i <clip> -vf "fps=10,scale=108:-2,tile=24x1" -frames:v 1 sheet.png`.
   Note when the upper band is clear and which way each kick sweeps.
3. **Write the edit** in `edits/<yymmdd>-<name>.json` (copy one of the same type). Clip paths are
   repo-relative (`in/...`) or `$SC_CONTENT/...`, never absolute.
   - `sequence`: the hook is the best kick/acrobatic moment, 1–1.5 s at speed 0.5. The body
     runs from the first movement to ~1.5 s after the last spectacular move. Cards follow §8.
     Timeline time = hook length + (source time − body start).
   - `educational`: each step is its finger count (`intro`: from the hand rising to just after
     the count is shown; find it on a zoomed 10 fps crop of the upper body,
     `crop=900:900:600:750` on 2160×3840 iPhone footage) plus its move, cut from peak − 1.4 s
     to peak + 1.7 s. No cards (they're generated and land on the fingers). Add a clip `text`
     only when the user names the step. Check that the count matches the step number.
4. **Check the edit:** run `uv run pytest` (it validates every edit with `models.load` rules).
5. **Render:** run `uv run shorts.py render edits/<file>.json` (output in `out/`).
6. **Look at it.** Extract frames at `in`, `hit`, mid-hold and the exit / kick impact (cropped
   to the top 1100 px and stacked with `hstack`). Check:
   - no letter collisions;
   - text clear of the head and body at rest;
   - the kick impact lands on the foot (±2 frames).
   Fix the timing and render again before showing the user.
7. **Send the render** to the user, with one line per change.
8. **On feedback:** change the constants in `cards.py` or the edit. Update STYLE.md's rules
   **and** add a decision file in `decisions/`. Make new rules checkable (`models.problems` or `tests/`).
9. **Archive only when asked**, with the Drive folder the user gives:
   `uv run shorts.py archive edits/<file>.json "<folder>"`. Report the archive folder it prints.
   Never delete anything from `in/` unless the user asks, and only after the archive succeeded.
