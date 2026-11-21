# app structure, agent consistency and language choice

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** process

## Feedback

Organize the repository like a real app instead of flat Python files in the root, with no
compromise on clean software practice: this is an AI product, but it is software. Research
similar products and ideas where agents collaborate with consistent, persistent outputs, and
apply them. Consider optimization, including whether Rust would be better than Python.

## Decision

**Structure:**
- The code is a package, `src/touro_shorts/` (`cli`, `cards`, `models`, `timeline`, `versions`,
  `archive`, plus the brand `fonts/`).
- It is built with `uv_build` and installs one command, `touro-shorts`, replacing
  `python shorts.py`.
- Paths in edits resolve against the working directory like any CLI. The hidden repo-root
  constant is gone.

**Applied from the research on agent consistency:**
- **`AGENTS.md`** is the single shared instruction file. It is the cross-tool convention read by
  Codex, Cursor, Copilot and others. `CLAUDE.md` imports it (`@AGENTS.md`) and adds only
  Claude-specific notes, so collaborators using other agents follow the same rules.
- **Style by tools, not instructions:** ruff (lint + format) runs in CI. Guides note that
  formatters are deterministic and don't consume an agent's instruction budget.
- **Snapshot (golden) tests** of the text animation in `tests/goldens/`, as programmatic-video
  setups use. An accidental visual change fails CI; a deliberate one needs a decision plus
  `UPDATE_GOLDENS=1`.
- **Already in place and kept:** spec-driven development (GitHub Spec Kit's spec → plan →
  tasks) maps onto PRODUCT.md (spec), STYLE.md (rules) and `decisions/` (decision records).

**Language: stay with Python. The data:**
- Profile of the educational render (21.7 s): ~65% in ffmpeg (decoding 4K HEVC iPhone footage,
  cutting, encoding), ~13% piping frames, ~21% Python text drawing.
- The one Python hotspot was algorithmic: every text pop re-scaled the whole 1080×1920 layer.
  It now transforms only the area around the text: 24.0 s → 21.3 s (−11%). It samples the same
  positions; floating-point order changes 0.06% of colour values on glyph edges, invisible, and
  the reference frames still match.
- Rust would not touch the dominant cost (ffmpeg is C either way), and it would add a second
  toolchain that collaborators and agents would have to maintain. Sources consistently say:
  profile first, keep Python for orchestration, and consider native code only for a hot
  per-frame loop that Python can't handle. We don't have one.
- **Future option, not built:** hardware decoding (VideoToolbox) could cut decode time, but
  output can differ between machines, which conflicts with same-inputs-same-output.

**Sources:**
- [AGENTS.md vs CLAUDE.md setup guide](https://dev.to/ahab_indieseek/agentsmd-vs-claudemd-vs-copilot-instructions-a-practical-setup-guide-for-ai-coding-agents-16oo)
- [one AGENTS.md for every agent](https://dev.to/mudassirworks/one-agentsmd-for-every-coding-agent-stop-maintaining-claudemd-and-geminimd-separately-34g4)
- [GitHub Spec Kit](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [Remotion agent skills](https://www.remotion.dev/skills)
- [programmatic video skill (snapshot assertions)](https://www.skills.sh/itallstartedwithaidea/agent-skills/programmatic-video)
- [state of media processing in Rust](https://dev.to/yeauty/the-state-of-media-processing-in-rust-2026-what-each-crate-actually-covers-2k2c)
