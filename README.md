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

Animated, brand-styled text for [Simplesmente Capoeira](https://sc-capoeira.de/) Instagram
shorts (12–20 s, 1080×1920). One Python file, one JSON file per edit. The design rules live in
[STYLE.md](STYLE.md).

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
| `educational` | one clip per technique | one cut per move with automatic STEP 1, 2, 3… cards |

## Make a short

```bash
uv run shorts.py peaks in/<clip>.MOV            # when the strongest moves happen
cp edits/261120-sequence.json edits/<yymmdd>-<name>.json   # copy an edit of the same type
uv run shorts.py render edits/<yymmdd>-<name>.json         # -> out/<name>.mp4
uv run test_shorts.py                           # checks every edit against STYLE.md
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

An educational edit needs no cards. Each clip becomes one step:

```json
{
  "type": "educational",
  "clips": [
    {"src": "in/IMG_7013.MOV", "start": 7.5, "end": 11.1},
    {"src": "in/IMG_7014.MOV", "start": 4.9, "end": 8.5, "text": "Step 2 aú"}
  ],
  "output": "out/261120-steps.mp4"
}
```

- **Clips:** `start`/`end` cut a clip (seconds in the source). `speed` 0.5–2 re-times it (0.5 =
  slow motion). Clips are joined in order with hard cuts.
- **Cards:** the last word of each card is its key word, set huge with the yellow marker.
  - `in`: the card starts appearing. `hit`: the key word has landed. `out`: the card starts
    leaving. Times are on the final timeline.
  - `kick` (optional, `left`/`right`): at `out`, a kick knocks the letters away in that direction.
  - `shrink` (optional time): the card shrinks into its corner from here until `out`, bridging a
    long gap to the next card.
- **`brightness`** (optional, −1..1): darkens or brightens the footage only, never the text.

## Working with Claude Code

This repo has project skills in `.claude/skills/`:

- `capoeira-shorts`: the end-to-end workflow and design taste for a new edit.
- `coding-principles`: how code in this repo is written (simple, deep modules, verified).

## Fonts

`fonts/` holds Archivo (from sc-capoeira.de), licensed under the SIL Open Font License 1.1.
See [fonts/OFL.txt](fonts/OFL.txt).

The TOURO logo (`docs/touro-logo.jpg`) belongs to [TOURO](https://www.youtube.com/@Tourocapoeira)
and isn't covered by the code in this repository.
