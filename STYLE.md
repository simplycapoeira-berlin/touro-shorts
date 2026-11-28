# Simplesmente Capoeira — Shorts style spec

The rules every Instagram short follows. Exact values live once, as constants at the top of
`src/touro_shorts/cards.py`. This file explains **why** they are what they are. To change the look, change a
constant there and update the reason here.

## 1. Brand (from sc-capoeira.de)

| Choice | Source on the website | Why |
|---|---|---|
| Key word: Archivo 900, lowercase, huge | `.sc-hero__title` | The site's headline voice: heavy, compact, confident. |
| Kicker: Archivo 800, UPPERCASE, tracked 0.18em | `.sc-kicker` | The site's small label above every title. It gives the editorial two-level hierarchy. |
| All type in ink `--sc-black` #111. **No blue.** | body text | Reads on the light gym walls and ceiling. Black + yellow only keeps the palette strong (v3 feedback). |
| Yellow marker `--sc-yellow` #F7E018 over the lower part of the key word | `.sc-mark` | The site's one accent gesture. Only on the key word. |

Fonts are the site's own woff2 files, converted once to TTF (`src/touro_shorts/fonts/`).

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
  This is the artistic payoff of the type living in the same space as the body, and it is
  worth a short stretch without text.
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
   - **4b. Shrink to bridge a gap** (`shrink`, ~1.5 s after `hit`). The card **snaps** into its
     aligned top corner at 45% in 0.35 s, with a springy overshoot. It never fades down slowly:
     slow shrinking felt detached from the movement. The sentence stays on screen without
     competing with the movement. It leaves before the next card, preferably knocked out by a
     kick passing through its corner (`kick`); otherwise it slides out ending right as the next
     card's `in` starts (`out` ≈ next `in` − 0.3 s).
   - **4c. Beats: the movement plays with the text** (`beats`, list of times). On every beat (a
     kick or a big move, checked on frames), the card pops 12% for 0.3 s. That's all: the type
     stays plain, with only the one yellow highlight band from `hit`. **No underlines or other
     extra decoration**; a kick-drawn underline was tried and rejected.
5. **Leave** (`out`). Either a kick knocks the letters away (preferred when a kick passes through
   the band: impact = the frame the foot reaches the text), or the card slides out toward the
   open side with a two-ghost motion trail (0.3 s).

Timings: `uv run touro-shorts peaks <clip>` prints the strongest movement moments (at least 1 s
apart). Then scrub frames to see **where** the body is. Peaks say when, not where. Put the first
card in the first second, right after any opening move clears the band.

## 4. Copy

- 2 cards for a 12–20 s clip. One idea per card, said plainly.
- The **last word is the key word** and carries the meaning ("talent" → "practice"). A pair of
  cards should read as one sentence split across two movements.

## 5. Output

Commands are in the [README](README.md). Output: 1080×1920, 30 fps, H.264 CRF 17, AAC 192k, faststart. That is Instagram's preferred
upload format. Any source works: iPhone 4K/60 fps portrait clips are rotated, scaled and cropped
to fill the frame, and 60 fps sources give smooth 0.5× slow motion. Source metadata (GPS, device)
is always stripped. The output carries `genre=<type>` and a JSON `comment` (type, edit, clips,
texts) instead.

## 6. Decisions

Every round of feedback becomes one file in [`decisions/`](decisions/): what was asked, by whom,
and the decision it led to. One file per decision means collaborators never conflict over a
shared table. The sections above always hold the *current* rules; the decision files hold the
history and the reasons. See [decisions/README.md](decisions/README.md) for the template.

## 7. References consulted

- Meta/Instagram Reels safe zones (14% top, 35% bottom, right rail): hopperhq.com/blog/instagram-reel-size,
  trymypost.com/blog/instagram-reels-safe-zones-text-placement-2026
- Kinetic type for sports: tie entries to real moments in the action, keep layers few, avoid
  looping motion, and keep motion direction consistent: capcut.com/features/how-to-make-kinetic-typography-capcut-workflow,
  linearity.io/blog/kinetic-typography
- Token-driven video pipelines (brand tokens defined once, motion layer shared):
  chuk-motion (Remotion + design tokens), Inkeep motion-video skill (`brand.ts` single source).
  We follow the same pattern without the Node/Remotion stack: one small Python package is enough.

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
  - Card 1 lands its key word on the hook's peak, snaps small ~1.5 s later (§3, 4b), gets a beat
    on the next kick, and is kicked out by the kick after that. Keep its total time short.
  - Card 2 enters ~0.6 s after that, gets beats on the big moves while it holds, and is kicked
    out by the last spectacular move.
  - Every kick time must be checked on frames. Motion peaks also fire on steps and turns.

### `educational`: step-by-step techniques

- **Input:** one clip per technique, filmed as "stand and **show the step number with the
  fingers**, show the move, return".
- **Hook:** the video opens with the most impressive move of the material (usually the last
  step's acrobatic move) at **real speed**, never slowed. It starts mid-action, with the move's
  peak at ~1 s, then ~1 s of landing (~2 s). From the first frame, a card shows the movement's
  name (hook clip `text`, else "In <n> steps"). It lands, then snaps small (§3, 4b) to keep the
  face clear, unless the hook's kick sweeps through it first and knocks it away (`kick`,
  `kick_at`). A hook may show a wrong version of the move instead, as "Not like this".
- **Structure:** each step is two cuts from its clip, in recording order, with hard cuts
  everywhere. Total ≤ 20 s.
  - **Finger count** (`intro`, ~0.8–0.9 s): from the hand rising to just after the fingers are
    clearly shown. Confirm it on a zoomed 10 fps crop of the upper body. The count must match
    the step number.
  - **Move:** from 1.4 s before the move's peak to 1.3 s after it (2.7 s): lead-in, move,
    recovery. The fixed lead puts the peak at a known time, which is the step card's beat.
  - Everything else (standing, walking into position) is dropped. It's silent.
- **Text:** generated, not hand-timed.
  - Each step opens with a card: kicker "STEP", key word = the step number (or the clip's
    `text`, whose last word becomes the key word).
  - The card lands 0.6 s into the step, while the fingers are up, so the number and the hand
    say the same thing. On the move's peak the number pops (an automatic beat). It leaves 0.35 s before the step ends.
  - Cards alternate left/right. The card sits on the opposite side from the raised hand; check
    that it never covers the fingers.

Shared by all types: brand (§1), composition (§2), motion grammar (§3), house grade −0.05
brightness, 1080×1920/30 fps output.
