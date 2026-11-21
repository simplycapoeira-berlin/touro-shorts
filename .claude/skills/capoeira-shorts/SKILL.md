---
name: capoeira-shorts
description: Make or revise a Simplesmente Capoeira Instagram short (sequence or educational type) from raw clips and text, with cuts, slow motion and movement-timed brand text. Use when given capoeira clips (e.g. in in/) and text, or feedback on a rendered short.
---

# Capoeira shorts

The working procedure for turning raw clips plus a little text into a short. **Read STYLE.md
first:** it holds every taste rule (§1–4) and the recipe of each video type (§8). This skill
never repeats them. The edit fields are in the README. Don't invent a new look: if something
isn't covered, ask, then record the answer (STYLE.md + a decision).

## Procedure

0. **Classify.** Look at a full-length contact sheet of every clip:
   `ffmpeg -i <clip> -vf "fps=2,scale=96:-2,tile=21x2" -frames:v 1 sheet.png`. Make sure the
   tile holds every frame (fps × duration ≤ 42), or the sheet silently cuts the end off.
   - One continuous flowing clip → `sequence`.
   - Several "stand, show one move, return" clips → `educational`, one step per clip in
     recording order.
   - Clips that fit neither → ask the user.
   - Check the audio too (`astats`). Silent intros can be cut; speech must not be cut
     without asking.
1. **Find when.** `uv run touro-shorts peaks "<clip>"` prints the strongest motion moments.
2. **Find where.** Peaks say when, not where, and they also fire on turns and steps. Confirm
   every move on a 10–15 fps sheet:
   `ffmpeg -ss <t> -t 2.4 -i <clip> -vf "fps=10,scale=108:-2,tile=24x1" -frames:v 1 sheet.png`.
   Note when the upper band is clear and which way each kick sweeps. For a finger count, use a
   zoomed crop of the upper body (`crop=900:900:600:750` on 2160×3840 iPhone footage).
3. **Write the edit** in `edits/<yymmdd>-<name>.json`, copied from one of the same type, with
   cuts and cards following STYLE.md §8. In a sequence, timeline time = hook length + (source
   time − body start).
4. **Check it:** `uv run pytest` validates every edit.
5. **Render:** `uv run touro-shorts render edits/<file>.json` prints the new version
   (`out/<name>-v<n>.mp4`), or "unchanged".
6. **Look at it.** Extract frames at `in`, `hit`, mid-hold and the exit or kick impact (cropped
   to the top 1100 px, stacked with `hstack`). Check:
   - no letter collisions;
   - text clear of the head and body at rest, and of the raised fingers;
   - the kick impact lands on the foot (±2 frames).
   Fix and render again before showing the user.
7. **Send the render** to the user, naming its version, with one line per change.
8. **On feedback:** change the edit, or a constant in `src/touro_shorts/cards.py`. A rule change
   updates STYLE.md and adds a decision (see AGENTS.md).
9. **Finish only when asked**, in this order: `touro-shorts clean`, then `touro-shorts archive`
   with the folder the user gives. Delete raw clips in `in/` only if the user asks, and only
   after the archive succeeded.
