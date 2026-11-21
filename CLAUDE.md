# touro-shorts

Text-animation pipeline for Simplesmente Capoeira Instagram shorts. Read before working:

- [STYLE.md](STYLE.md): the design spec and its iteration log. It is the source of truth for taste.
- `.claude/skills/capoeira-shorts`: how to make or revise an edit.
- `.claude/skills/coding-principles`: how to change the code.

Rules that always apply:

- Every design change updates STYLE.md in the same change: the rule section, plus a new row in
  the iteration log (feedback → decision, newest first). Keep `test_shorts.py` in sync with the rules.
- Never commit raw clips (`in/`), renders (`out/`) or machine-specific paths. Clip paths in
  edit files are repo-relative (`in/...`) or use `$SC_CONTENT/...`.
- Every edit declares a video `type` from `MODELS` in `shorts.py`, recipe in STYLE.md §8.
  A new kind of video gets a new type (code + §8 + iteration log), never a one-off edit.
- Verify visually: extract frames from the render with ffmpeg and look at them before
  claiming an edit is done.
