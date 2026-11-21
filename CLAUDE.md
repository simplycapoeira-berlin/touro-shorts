# touro-shorts

Video pipeline for Simplesmente Capoeira Instagram shorts. Several people change this repo
through Claude, each working on their own part, and everything meets on GitHub. Read before
working:

- [STYLE.md](STYLE.md): the current design rules. It is the source of truth for taste.
- [decisions/](decisions/): why each rule exists. One file per decision.
- `.claude/skills/capoeira-shorts`: how to make or revise an edit.
- `.claude/skills/coding-principles`: how to change the code, and where each kind of change goes.

## Where things live

| Area | File | Change it when… |
|---|---|---|
| Text animation | `cards.py` | the look or motion of text changes |
| Video types and edit rules | `models.py` | a new type, a new edit field, or a new rule |
| Cutting, joining, grading | `timeline.py` | how clips become one timeline |
| Cold storage | `archive.py` | how finished edits are stored |
| Commands | `shorts.py` | a new command; it only wires the modules together |
| Edits | `edits/*.json` | a new video (validated by `models.load`) |

## Rules that always apply

- **Work on a branch and open a pull request.** `main` is protected: direct pushes are rejected,
  and a pull request merges only with green CI and up to date with `main`. CI runs
  `uv run pytest` on every push; run it yourself before committing. A red test means stop and
  fix; never delete or weaken a test to get green.
- **Every design or behaviour change** adds a file in `decisions/` (template in
  `decisions/README.md`) and updates the matching STYLE.md section, in the same pull request.
  Never rewrite someone else's decision. Add a new one that replaces it.
- **Every new rule becomes checkable.** Put it in `models.problems` (edits) or a test (code),
  so the next person can't break it silently.
- **A new kind of video gets a new type**: an entry in `MODELS`, a recipe in STYLE.md §8, a
  decision, and an example edit that passes the tests. Never a one-off edit.
- **Never commit raw clips (`in/`), renders (`out/`) or machine-specific paths.** Clip paths in
  edit files are repo-relative (`in/...`) or use `$SC_CONTENT/...`. The tests reject absolute paths.
- **Cold archiving** (`shorts.py archive`) only runs when a user asks and gives the destination
  folder. Never put their Drive path in a committed file.
- **Verify visually:** extract frames from the render with ffmpeg and look at them before
  claiming an edit is done. Tests prove the pipeline works; only frames prove the edit looks right.
