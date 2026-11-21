# versioned renders

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** pipeline

## Feedback

Every render should create a new version of the video instead of overwriting it. When the
users are finished, they tell Claude whether to delete the previous versions and archive the
inputs. This is our storage management feature.

## Decision

- **Never overwrite:** a render of an edit with `"output": "out/<name>.mp4"` writes
  `out/<name>-v<n>.mp4`, one above the highest existing version (`versions.py`).
- **No duplicates:** renders are deterministic, so a render byte-identical to the latest version
  is not stored again; the command reports "unchanged".
- **Clean on request:** `shorts.py clean <edit.json> [version]` keeps one version (default: the
  latest) and deletes the others. It only touches files named `<name>-v<n>.mp4` and refuses an
  unknown version without deleting anything. It runs only when a user asks.
- **Archive the kept version:** `shorts.py archive` stores the latest version (run `clean` first
  to choose it) together with the inputs and the edit file.
- **Raw clips:** deleting raw clips in `in/` is a separate, explicit user instruction, given
  after the archive succeeded.
