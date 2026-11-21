# license: CC BY 4.0

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** process

## Feedback

Add a Creative Commons 4.0 license to the repository, if it is compatible with the licenses we
already have (the font license).

## Decision

The repository is licensed under **CC BY 4.0** (`LICENSE`, `license = "CC-BY-4.0"` in
`pyproject.toml`). Anyone may use, change and share it, commercially too, with credit. The
owner chose BY over BY-SA and the non-commercial variants.

**Compatibility:**
- **Fonts:** the Archivo fonts stay under the SIL Open Font License 1.1, which allows bundling
  them with software under any license as long as the fonts keep the OFL. `LICENSE` excludes
  `src/touro_shorts/fonts/`, and `OFL.txt` ships in the package next to `LICENSE`.
- **Logo:** the TOURO logo is not ours to license, so it is excluded (all rights reserved by
  TOURO).
- **Footage and renders** are never in the repository, so they are not covered.

**Known trade-off:** Creative Commons recommends against CC licenses for software, because they
don't address patents or source code distribution. The owner kept CC BY knowing this; a
software license (e.g. MIT) for the code would be a new decision.
