# Product design

**touro-shorts is an AI editing assistant for capoeira video editors.** An editor brings raw clips
and a few words. They describe what they want in plain language, and Claude produces finished,
brand-consistent Instagram shorts in which the text moves with the capoeira. The same inputs
always give the same video.

This file describes *what* the product is and *why*. [STYLE.md](STYLE.md) holds the current
visual rules, [decisions/](decisions/) the history of every choice, and the code how it works.

## Who it is for

- **Capoeira groups and schools** (first: Simplesmente Capoeira) that post short movement videos
  and want them to look like their brand, every time.
- **Editors** in those groups: people who know capoeira but not video tools. They talk to Claude
  instead of learning an editor.
- **Players on camera** (first: Touro). Their movement is the content. The product's job is to
  frame it, never to cover it.
- **Developers and contributors** who extend the product through Claude, in parallel, on GitHub.

## What a user does

1. **Bring footage.** Put raw clips in `in/` (or point to them, e.g. `$SC_CONTENT/...`).
2. **Say what you want.** For example: "a sequence with *it is not about talent / it is about
   practice*", or "an educational video of these five steps".
3. **Get a version.** Claude classifies the clips into a video type, finds the moves, cuts,
   times the text to the kicks, checks the frames, and renders `out/<edit>-v1.mp4`.
4. **Give feedback, get the next version.** Each round adds a new version (`-v2`, `-v3`, …); nothing
   is overwritten. Each round's design choice is written down as a decision.
5. **Finish.** The user names the version to keep; Claude deletes the others and, if asked,
   archives inputs + kept version + edit (e.g. to Google Drive). Raw clips are deleted only on
   the user's explicit instruction, after the archive succeeded.
6. **Schedule.** "Post it Tuesday at 6 pm on Instagram and TikTok": Claude confirms version,
   time, channels and caption, then our own Postiz publishes it.

## Core concepts

| Concept | What it is | Where |
|---|---|---|
| **Video type** (model) | The kind of video and its recipe: `sequence` (hook + flowing sequence) or `educational` (hook + finger-count steps). Stored in every output's metadata. | `models.py`, STYLE.md §8 |
| **Edit** | One video, described as data: type, clips, text cards, grade. Validated before anything runs. | `edits/*.json`, `models.py` |
| **Clip / hook / intro** | Cuts from raw footage. The first clip of a multi-clip video is the hook. An intro is a step's finger count. | `timeline.py` |
| **Card** | A sentence on screen: a small kicker and a huge key word with the yellow marker. | `cards.py` |
| **Beat / kick** | A real movement moment. A beat makes the card pop; a kick knocks the text away. | `cards.py` |
| **Style spec** | The current brand and motion rules, derived from the website and user feedback. | STYLE.md |
| **Decision** | One file per design choice: what was asked, by whom, what was decided. | `decisions/` |
| **Version** | Every render is a new file; identical renders aren't duplicated. | `versions.py` |
| **Archive** | Verified cold storage of a finished edit. | `archive.py` |

## Product principles

1. **The movement leads.** Text appears when the body leaves space, reacts to kicks (beats),
   and is knocked away by them. It never blocks the player.
2. **Short attention.** Information arrives fast: readable within ~0.6 s, the first card in the
   first second, total 12–20 s.
3. **One brand, every time.** Archivo, black and yellow, from sc-capoeira.de. No ad-hoc styles.
4. **Repeatable.** Every choice is a rule, a type recipe or a decision. The same inputs render
   byte-identical outputs.
5. **Nothing is lost by accident.**
   - Renders are versions, never overwritten.
   - Deleting versions or raw clips and archiving only happen when a user asks.
   - Archives are checksum-verified.
6. **Private by default.** Footage and renders never go to GitHub. A render leaves the laptop only
   when a user schedules it to post. GPS, device data and personal paths are never shared.
7. **Built to be extended by many people.** Modules are split by area, edits are validated, and
   tests run in CI. `main` changes only through pull requests with green tests.

## Feature map

| Feature | Status |
|---|---|
| Brand text cards (kicker + key word, marker, arc swing) | built |
| Motion grammar: snap shrink, beats (pop), kick exits | built |
| Video types `sequence` and `educational`, recorded in output metadata | built |
| Cutting, joining, slow-motion hooks, grading, any iPhone source | built |
| Educational steps: finger count + move, automatic numbered cards | built |
| Motion peaks to find moves (`peaks`) | built, confirmed by eye on frames |
| Versioned renders and cleanup on request (`clean`) | built |
| Cold archive to a Google Drive folder (`archive`) | built, not yet used on a real Drive |
| Collaboration: validation, decisions, tests, CI, protected `main` | built |
| Fully automatic cut and kick detection (no frame check by Claude) | next: peaks fire on turns too, so frames are still checked |
| More video types (e.g. roda highlights, music-synced) | later: each one is a new type with a recipe |
| Named steps (e.g. "aú") instead of numbers | ready: a clip's `text`, when users give names |
| Scheduled posting to Instagram, TikTok and more (`schedule`, through Postiz in `deploy/postiz/`) | built, runs locally; Instagram needs R2 storage, TikTok a server |

## Not in scope (for now)

- Music, voice-over or subtitles of speech.
- Brands other than Simplesmente Capoeira. The style is one brand. A second brand would be a
  product decision, not an edit option.
