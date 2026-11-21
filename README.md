<p align="center">
  <a href="https://www.youtube.com/@Tourocapoeira"><img src="docs/touro-logo.jpg" alt="TOURO capoeira logo" width="200"></a>
</p>

<h1 align="center">touro-shorts</h1>

<p align="center">
  <b>Text that moves like capoeira.</b><br>
  Words land on the peak of a movement, and a kick can knock them off screen.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/format-1080×1920%20·%2012–20s-111111?style=flat-square" alt="format">
  <img src="https://img.shields.io/badge/python-3.13-F7E018?style=flat-square&labelColor=111111" alt="python 3.13">
  <img src="https://img.shields.io/badge/uv-managed-F7E018?style=flat-square&labelColor=111111" alt="uv">
  <img src="https://img.shields.io/badge/font-Archivo-F7E018?style=flat-square&labelColor=111111" alt="Archivo">
</p>

<p align="center">
  <a href="https://www.youtube.com/@Tourocapoeira">TOURO on YouTube</a> ·
  <a href="https://sc-capoeira.de/">Simplesmente Capoeira</a> ·
  <a href="STYLE.md">Style spec</a>
</p>

---

An AI editing assistant for capoeira video editors: bring raw clips and a few words, talk to
Claude, get brand-consistent [Simplesmente Capoeira](https://sc-capoeira.de/) Instagram shorts
(12–20 s, 1080×1920) whose text moves with the capoeira.
- What the product is and why: [PRODUCT.md](PRODUCT.md).
- The visual rules: [STYLE.md](STYLE.md).
- Every decision along the way: [decisions/](decisions/).

## Setup

Needs [uv](https://docs.astral.sh/uv/) and `ffmpeg` on PATH (`brew install uv ffmpeg`).

```bash
uv sync
mkdir -p in out   # raw clips go in in/, renders land in out/ (both stay local, never pushed)
```

Clips can also live anywhere else: edit paths may be absolute on your machine or use
environment variables like `$SC_CONTENT/...`.

## Video types

Every edit declares a `type`, the model of the output. It's stored in the output's metadata
(`genre` and a JSON `comment`). The full recipes are in [STYLE.md §8](STYLE.md).

| Type | Input | Output |
|---|---|---|
| `sequence` | one continuous movement clip and a sentence | a 0.5× slow-motion hook of the best move, then the sequence; two text cards that the kicks knock away |
| `educational` | one clip per technique, opened by a finger count | per step: the finger count, then the move, with an automatic STEP 1, 2, 3… card landing on the fingers |

## Make a short

```bash
uv run shorts.py peaks in/<clip>.MOV            # when the strongest moves happen
cp edits/261120-sequence.json edits/<yymmdd>-<name>.json   # copy an edit of the same type
uv run shorts.py render edits/<yymmdd>-<name>.json         # -> out/<name>.mp4
uv run pytest                                   # checks every edit, rule and the pipeline
```

A sequence edit:

```json
{
  "type": "sequence",
  "clips": [
    {"src": "in/IMG_7011.MOV", "start": 11.6, "end": 12.7, "speed": 0.5},
    {"src": "in/IMG_7011.MOV", "start": 1.0, "end": 16.6}
  ],
  "output": "out/261120-sequence.mp4",
  "brightness": -0.05,
  "cards": [
    {"text": "It is not about talent", "in": 0.9, "hit": 1.55, "shrink": 5.0, "out": 12.95, "kick": "left"},
    {"text": "It is about practice", "in": 13.9, "hit": 14.55, "out": 16.1, "kick": "left"}
  ]
}
```

An educational edit needs no cards. Each clip becomes one step: its finger count (`intro`)
followed by its move:

```json
{
  "type": "educational",
  "clips": [
    {"src": "in/IMG_7013.MOV", "intro": [2.5, 3.4], "start": 7.3, "end": 10.4},
    {"src": "in/IMG_7014.MOV", "intro": [1.1, 1.9], "start": 5.2, "end": 8.3, "text": "Step 2 aú"}
  ],
  "output": "out/261120-steps.mp4"
}
```

- **Clips:** the first clip of a multi-clip edit is the hook (`"hook": true`): slow motion in
  a sequence, real speed in an educational video. `start`/`end` cut a clip (seconds in the source). `speed` 0.5–2 re-times it (0.5 =
  slow motion). `intro` [start, end] plays a second cut of the same source first (the finger
  count). Clips are joined in order with hard cuts.
- **Cards:** the last word of each card is its key word, set huge with the yellow marker.
  - `in`: the card starts appearing. `hit`: the key word has landed. `out`: the card starts
    leaving. Times are on the final timeline.
  - `kick` (optional, `left`/`right`): at `out`, a kick knocks the letters away in that direction.
  - `shrink` (optional time): the card snaps small into its corner and stays until `out`,
    bridging a long gap to the next card.
  - `beats` (optional list of times): kicks or big moves. Each one pops the card and underlines
    the key word again.
- **`brightness`** (optional, −1..1): darkens or brightens the footage only, never the text.

## Versions

Every render is a new version: `out/<name>-v1.mp4`, `-v2.mp4`, … Nothing is overwritten, so
you can compare iterations. A render identical to the latest version isn't stored twice. When
you're done:

```bash
uv run shorts.py clean edits/261120-steps.json      # keep the latest version, delete the others
uv run shorts.py clean edits/261120-steps.json 2    # or keep version 2
```

## Cold archive (e.g. Google Drive)

Once an edit is finished, store its raw inputs, the render and the edit file away from the laptop:

```bash
uv run shorts.py archive edits/261120-steps.json "<your Google Drive folder>"
```

This creates `<folder>/261120-steps/` with `inputs/` (the original clips, unchanged), the render
and the edit file. Point it at a folder inside Google Drive for desktop and Drive uploads it.

- Every copy is checked with sha256 and listed in a `manifest.json`.
- Re-running it is safe: identical files are skipped, and a different file with the same name
  stops the run instead of being overwritten.
- The folder must already exist, so a mistyped path fails instead of silently writing locally.
- Nothing in `in/` is deleted. Once the archive has synced, clearing `in/` is up to you.

## Working together (through Claude)

Several people change this repo through Claude, each on their own part. Changes meet on GitHub:

1. **Branch and pull request.** Start a branch, let Claude make the change, open a pull request.
   Nobody pushes to `main` directly.
2. **Tests guard everyone's work.** GitHub Actions runs `uv run pytest` on every push. The tests
   need no footage:
   - every committed edit is validated;
   - every rule in `models.py` has a test that breaks it on purpose;
   - text drawing follows the motion grammar;
   - the archive never overwrites or deletes;
   - a synthetic clip is rendered end to end (format, metadata, GPS stripped, byte-identical
     re-renders).
3. **Edits are validated before rendering.** `models.load` lists every broken rule at once, so a
   typo like `"kik"` fails with a clear message instead of a wrong video.
4. **Decisions accumulate.** Each design change adds one file in [decisions/](decisions/)
   (feedback → decision, who asked). [STYLE.md](STYLE.md) always shows the current rules.

| Area | File |
|---|---|
| Text look and motion | `cards.py` |
| Video types, edit fields, rules | `models.py` |
| Cutting, slow motion, joining | `timeline.py` |
| Render versions | `versions.py` |
| Cold storage | `archive.py` |
| Commands | `shorts.py` |

Claude reads [CLAUDE.md](CLAUDE.md) and the project skills in `.claude/skills/`:
`capoeira-shorts` (making an edit) and `coding-principles` (changing the code, and where each
kind of change goes).

## Fonts

`fonts/` holds Archivo (from sc-capoeira.de), licensed under the SIL Open Font License 1.1.
See [fonts/OFL.txt](fonts/OFL.txt).

The TOURO logo (`docs/touro-logo.jpg`) belongs to [TOURO](https://www.youtube.com/@Tourocapoeira)
and isn't covered by the code in this repository.
