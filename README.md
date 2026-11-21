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

An AI editing assistant for capoeira video editors. Bring raw clips and a few words, talk to
Claude, and get brand-consistent [Simplesmente Capoeira](https://sc-capoeira.de/) shorts
(12–20 s, 1080×1920). The same inputs always give the same video.

- [PRODUCT.md](PRODUCT.md): what the product is and why.
- [STYLE.md](STYLE.md): the visual rules and the two video types (`sequence`, `educational`).
- [decisions/](decisions/): why each rule exists.
- [AGENTS.md](AGENTS.md): how to change this repo (for people and AI agents).

## Setup

Needs [uv](https://docs.astral.sh/uv/) and `ffmpeg` (`brew install uv ffmpeg`).

```bash
uv sync
mkdir -p in out   # raw clips go in in/, renders in out/; both stay on your machine
```

## Make a short

```bash
uv run touro-shorts peaks in/<clip>.MOV                 # when the strongest moves happen
cp edits/261120-sequence.json edits/<yymmdd>-<name>.json  # start from an edit of the same type
uv run touro-shorts render edits/<yymmdd>-<name>.json   # -> out/<name>-v<n>.mp4
```

Every render is a new version (`-v1`, `-v2`, …). Nothing is overwritten, and a render identical
to the latest version isn't stored twice.

## The edit file

An edit describes one video as data. It is checked before anything renders, and every broken
rule is listed at once:

```json
{
  "type": "sequence",
  "clips": [
    {"src": "in/IMG_7011.MOV", "start": 11.6, "end": 12.7, "speed": 0.5, "hook": true},
    {"src": "in/IMG_7011.MOV", "start": 1.0, "end": 16.6}
  ],
  "output": "out/261120-sequence.mp4",
  "brightness": -0.05,
  "cards": [
    {"text": "It is not about talent", "in": 0.9, "hit": 1.55, "shrink": 3.0, "beats": [9.0], "out": 9.6, "kick": "left"},
    {"text": "It is about practice", "in": 10.2, "hit": 10.85, "out": 16.1, "kick": "left"}
  ]
}
```

- **`type`:** `sequence` or `educational` (recipes in [STYLE.md §8](STYLE.md)). It is written
  into the output's metadata.
- **`clips`:** played in order with hard cuts.
  - `start`/`end` are seconds in the source; `speed` is 0.5–2 (0.5 = slow motion).
  - A multi-clip video opens with a hook: the first clip, marked `"hook": true`.
  - `intro` [start, end] plays a second cut of the same source first (an educational step's
    finger count). `text` names a step.
  - Paths are repo-relative (`in/...`) or use variables (`$SC_CONTENT/...`), never personal paths.
- **`cards`:** the last word is the key word, set huge with the yellow marker. Times are on the
  final timeline.
  - `in`: the card starts appearing. `hit`: the key word has landed. `out`: it starts leaving.
  - `kick` (`left`/`right`): at `out`, a kick knocks the letters away.
  - `shrink`: the card snaps small into its corner and stays until `out`.
  - `beats`: kicks or big moves; each one makes the card pop.
  - Educational edits leave out `cards`: the step cards are generated.
- **`brightness`** (−0.2..0.2): grades the footage only, never the text.

## Finish

Only when you are done, and only on request:

```bash
uv run touro-shorts clean edits/<file>.json [n]              # keep version n (default: latest), delete the others
uv run touro-shorts archive edits/<file>.json "<Drive folder>"  # copy inputs, render and edit to cold storage
```

`archive` writes `<folder>/<edit name>/` and checks every copy with sha256 (`manifest.json`). It
never overwrites or deletes anything, and the folder must already exist, so a mistyped path
fails. Clearing `in/` afterwards is up to you.

## License

The fonts in [src/touro_shorts/fonts/](src/touro_shorts/fonts/) are Archivo, under the
[SIL Open Font License 1.1](src/touro_shorts/fonts/OFL.txt). The TOURO logo
(`docs/touro-logo.jpg`) belongs to [TOURO](https://www.youtube.com/@Tourocapoeira) and isn't
covered by the code's license.
