# cold archive

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** archive

## Feedback

After edits, users should be able to give their Google Drive path and have the edited inputs
pushed there as cold storage. Build the feature now; don't run it yet.

## Decision

`shorts.py archive <edit.json> <folder>` copies the raw inputs (`inputs/`), the render and the
edit file into `<folder>/<edit name>/`. A Google Drive for desktop folder syncs this without
any API or login.

- Every copy is sha256-verified into `manifest.json`.
- Identical files are skipped, and a different file under the same name stops the run.
- The folder must already exist, so a typo can't write locally by mistake.
- Nothing in `in/` is deleted.
- It only runs when a user asks and gives the destination folder.
