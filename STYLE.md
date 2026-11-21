# Simplesmente Capoeira — Shorts style spec

The rules every Instagram short follows. Exact values live once, as constants at the top of
`shorts.py`. This file explains **why** they are what they are. To change the look, change a
constant there and update the reason here.

## 1. Brand (from sc-capoeira.de)

| Choice | Source on the website | Why |
|---|---|---|
| Key word: Archivo 900, lowercase, huge | `.sc-hero__title` | The site's headline voice: heavy, compact, confident. |
| Kicker: Archivo 800, UPPERCASE, tracked 0.18em | `.sc-kicker` | The site's small label above every title. It gives the editorial two-level hierarchy. |
| All type in ink `--sc-black` #111. **No blue.** | body text | Reads on the light gym walls and ceiling. Black + yellow only keeps the palette strong (v3 feedback). |
| Yellow marker `--sc-yellow` #F7E018 over the lower part of the key word | `.sc-mark` | The site's one accent gesture. Only on the key word. |

Fonts are the site's own woff2 files converted to TTF (`fonts/`).

**Footage grade:** the bright gym footage is darkened slightly per edit (`"brightness"`,
e.g. −0.05 ≈ 10% less average brightness). Only the footage is graded, never the type, so black
and yellow stay exact and pop more against the calmer background.

## 2. Composition (1080×1920)

- Every card has two levels: a **kicker** (all words but the last) above a **key word** (the
  last word). The key word is scaled to fill the safe width (max 330 px), so it reads like a
  poster rather than a caption.
- **Call and response:** cards alternate alignment, left then right, like two players answering
  each other in the roda. The right-aligned card mirrors every motion.
- Instagram UI covers about the top 14%, the bottom 35%, and a button rail on the right
  (Meta Reels ad safe-zone guidance). Text starts at y=280 with 72 px side margins.
- **Text never blocks the movement.** A card only appears while the body is clear of the upper
  band (e.g. not during a jump kick), and sits above the head.
- **The movement may remove the text.** When a kick sweeps through the text band, the kick
  knocks the letters off (`"kick": "left"|"right"`), and they scatter in the leg's direction.
  This is the artistic payoff of the type living in the same space as the body.
- At most one card on screen, ≤ 6 words.

## 3. Motion grammar ("follow the spirit of the movement")

Our audience has a short attention span, so information arrives fast. A card is fully readable
about 0.6 s after `in` and is shown full size for only a few seconds. **The text never simply
disappears and leaves a long gap:** if the next card is far away, the current card shrinks
instead (step 4b) and is swapped directly for the next one.

1. **Enter once the body clears the band** (`in`). The kicker fades in while its letter-spacing
   tightens from wide to rest (0.35 s).
2. **Swing in the key word.** Its letters travel one by one along a quarter-circle arc (a
   meia-lua), rotating as they go, with a slight overshoot (0.32 s each, 25 ms apart). They come
   from the card's outer edge.
3. **Hit** (`hit`, ≤ 0.8 s after `in`). The letters have landed, and the yellow marker sweeps
   under the key word (0.15 s).
4. **Hold briefly with a slow drift** (16 px). No looping motion, because loops pull the eye away
   from the athlete.
   - **4b. Shrink to bridge a gap** (`shrink`, ~5 s for a full-size read). The card scales down
     into its aligned top corner, toward 45%, with most of the shrink done in the first ~3 s. The
     sentence stays on screen without competing with the movement. It leaves before the next
     card, preferably knocked out by a kick passing through its corner (`kick`); otherwise it
     slides out ending right as the next card's `in` starts (`out` ≈ next `in` − 0.3 s).
5. **Leave** (`out`). Either a kick knocks the letters away (preferred when a kick passes through
   the band: impact = the frame the foot reaches the text), or the card slides out toward the
   open side with a two-ghost motion trail (0.3 s).

Timings: `python shorts.py peaks <clip>` prints the strongest movement moments (at least 1 s
apart). Then scrub frames to see **where** the body is. Peaks say when, not where. Put the first
card in the first second, right after any opening move clears the band.

## 4. Copy

- 2 cards for a 12–20 s clip. One idea per card, said plainly.
- The **last word is the key word** and carries the meaning ("talent" → "practice"). A pair of
  cards should read as one sentence split across two movements.

## 5. Workflow

```bash
uv sync                                    # once: creates .venv from pyproject.toml + uv.lock
# raw clips go in in/ (or anywhere: "$SC_CONTENT/...", absolute paths stay local); renders go to out/
uv run shorts.py peaks "in/<clip>.MOV"
# write edits/<yymmdd>-<name>.json (copy one of the same type)
uv run shorts.py render edits/<yymmdd>-<name>.json   # -> out/
uv run test_shorts.py
```

`in/` and `out/` are never committed: footage and renders belong to the users who provide them.

Needs `ffmpeg` on PATH (Homebrew). The fonts in `fonts/` were converted once from the site's
woff2 files with fontTools. That is not a runtime dependency.

Output: 1080×1920, 30 fps, H.264 CRF 17, AAC 192k, faststart. That is Instagram's preferred
upload format. Any source works: iPhone 4K/60 fps portrait clips are rotated, scaled and cropped
to fill the frame, and 60 fps sources give smooth 0.5× slow motion. Source metadata (GPS, device)
is always stripped. The output carries `genre=<type>` and a JSON `comment` (type, edit, clips,
texts) instead.

## 6. Iteration log

Record every round of feedback here: what was asked, and the decision it led to. Newest first.

| Version | Feedback | Decision |
|---|---|---|
| v7 (2026-11-21) | New raw clips in `in/`. Two edits: one like before (an attention-heavy movement first, then the sequence with our type, same text for now), and one educational step-by-step video with cuts. Classify the target videos as models (types) and keep them as output metadata. Later, users only bring videos and text and everything runs reliably and repeatably. | Two video types (§8): `sequence` and `educational`. New `clips` timeline (cut, slow motion, join, rotate/scale any source) replaces the single `input`. `in/` and `out/` are git-ignored. 261120-sequence: 0.5× hook of IMG_7011's armada and high kick, then the sequence; "talent" lands during the hook and is kicked out by the armada at 12.95 s; "practice" is kicked out by the aú at 16.1 s; the calm ginga tail is trimmed (17.8 s total). 261120-steps: IMG_7013–7017 cut to their move (peak −1.7 s / +1.9 s), with automatic STEP 1–5 cards (18 s). Confirmed: plain step numbers are the default; names only when the user gives them. Outputs carry the type in their metadata, and GPS is stripped. |
| v6 (2026-11-20) | The video is great; make it look a little darker. | New edit-level `brightness` (ffmpeg eq), applied to the footage before the text is drawn. Touro edit: −0.05 (mean brightness 158.6 → 143.1). Text and timings unchanged. |
| v5 (2026-11-20) | v4 is good. After second 15, the kick should throw the first sentence out; everything else stays the same. | The shrunken "talent" now gets `"kick": "left"` with its impact at 15.9 s, the frame the foot sweeps right to left through the top-left corner. "practice" is unchanged (17.6 s, armada at 19.6 s). Both sentences now leave by a kick. |
| v4 (2026-11-20) | Good design overall, but the first sentence disappears and the gap to the second is too long. Keep the first sentence's start as it is; after 5 s it should shrink until the second sentence replaces it. | New optional `shrink` time: the card scales into its top corner (to 45%, ease-out) and stays until it's swapped. Touro edit: "talent" from 0.6 s, shrinking from 5.0 s, out at 17.3 s, ending as "practice" enters at 17.6 s. The kick exit is unchanged. |
| v3 (2026-11-18) | Shorten text durations. The audience has short attention, so give the information faster. Sizes are good. No blue. Text must not block the movement, but the movement may remove the text (e.g. the last armada). | Enter/land timings roughly halved (readable ~0.6 s after `in`). Cards stay ~2 s. Kicker now ink. Cards appear only when the body is clear of the text band. New `kick` exit: the final armada knocks "practice" off screen. Touro edit: card 1 at 0.6–3.4 s (after the opening jump kick), card 2 at 17.6 s, kicked at 19.6 s. Confirmed: a payoff kick-off beats delivering card 2 earlier, even with a ~14 s text-free middle. |
| v2 | Bring the texts closer to the beginning. Make alignment and animations more artistic. | Two-level editorial card (small tracked kicker + poster-size key word). Left/right call-and-response alignment. Meia-lua arc letter swing, marker sweep, motion-trail exit. First card in the first second. |
| v1 | Initial brief: 12–20 s capoeira shorts, website fonts/style, text during movement passes. | Archivo + site colors. Word-by-word rise, yellow marker on the key word timed to motion peaks. |

## 7. References consulted

- Meta/Instagram Reels safe zones (14% top, 35% bottom, right rail): hopperhq.com/blog/instagram-reel-size,
  trymypost.com/blog/instagram-reels-safe-zones-text-placement-2026
- Kinetic type for sports: tie entries to real moments in the action, keep layers few, avoid
  looping motion, and keep motion direction consistent: capcut.com/features/how-to-make-kinetic-typography-capcut-workflow,
  linearity.io/blog/kinetic-typography
- Token-driven video pipelines (brand tokens defined once, motion layer shared):
  chuk-motion (Remotion + design tokens), Inkeep motion-video skill (`brand.ts` single source).
  We follow the same pattern without the Node/Remotion stack, because one Python file is enough.

## 8. Video types (models)

Every edit declares a `type`. The type is the model of the output: it fixes the structure, the
text behaviour and how the edit is derived from raw clips, and it is written into the output's
metadata. The goal is that a user only brings clips and text, and the same inputs always produce
the same video. So each type below is a recipe with no free choices left except the inputs.

### `sequence`: one flowing movement sequence

- **Input:** one continuous clip of a sequence (plus the text).
- **Structure:** a **hook**, then the sequence.
  - Hook: the most spectacular 1–1.5 s of the clip (the strongest motion peak that is a kick
    or acrobatic move, checked on frames) at 0.5× speed, from a 60 fps source.
  - Sequence: from the first movement (skip standing still) to ~1.5 s after the last
    spectacular move. Cut calm tails.
  - Total 12–20 s.
- **Text:** two cards (the sentence split in two, as in §4).
  - Card 1 lands its key word on the hook's peak, shrinks from 5 s (§3, 4b), and is kicked out
    by a real kick later in the sequence.
  - Card 2 enters ~1 s after that and is kicked out by the last spectacular move.
  - Every kick time must be checked on frames. Motion peaks also fire on steps and turns.

### `educational`: step-by-step techniques

- **Input:** one clip per technique, filmed as "stand, show, return".
- **Structure:** one cut per step, in recording order.
  - Each cut runs from 1.7 s before the move's peak to 1.9 s after it (3.6 s): lead-in, move,
    recovery.
  - Standing and explaining parts are dropped (they're silent).
  - Hard cuts between steps.
- **Text:** generated, not hand-timed.
  - Each step opens with a card: kicker "STEP", key word = the step number (or the clip's
    `text`, whose last word becomes the key word).
  - The card lands 0.8 s into its cut and leaves 0.35 s before the cut ends.
  - Cards alternate left/right, so consecutive steps answer each other.

Shared by all types: brand (§1), composition (§2), motion grammar (§3), house grade −0.05
brightness, 1080×1920/30 fps output.
