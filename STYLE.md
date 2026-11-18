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
about 0.6 s after `in` and stays only ~2 s.

1. **Enter once the body clears the band** (`in`). The kicker fades in while its letter-spacing
   tightens from wide to rest (0.35 s).
2. **Swing in the key word.** Its letters travel one by one along a quarter-circle arc (a
   meia-lua), rotating as they go, with a slight overshoot (0.32 s each, 25 ms apart). They come
   from the card's outer edge.
3. **Hit** (`hit`, ≤ 0.8 s after `in`). The letters have landed, and the yellow marker sweeps
   under the key word (0.15 s).
4. **Hold briefly with a slow drift** (16 px). No looping motion, because loops pull the eye away
   from the athlete.
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
export SC_CONTENT=/path/to/sc-content      # edit inputs are "$SC_CONTENT/..."
uv run shorts.py peaks "<clip.mov>"
# write edits/<date>-<name>.json (copy an existing one)
uv run shorts.py render edits/<date>-<name>.json   # -> out/
uv run test_shorts.py
```

Needs `ffmpeg` on PATH (Homebrew). The fonts in `fonts/` were converted once from the site's
woff2 files with fontTools. That is not a runtime dependency.

Output: H.264 CRF 17, AAC 192k, 30 fps, faststart. That is Instagram's preferred upload format.

## 6. Iteration log

Record every round of feedback here: what was asked, and the decision it led to. Newest first.

| Version | Feedback | Decision |
|---|---|---|
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
