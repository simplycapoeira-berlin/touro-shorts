"""Output versions: every render becomes a new file, never an overwrite.

An edit's "output": "out/<name>.mp4" is stored as out/<name>-v1.mp4, -v2.mp4, ... so users can
compare iterations and go back. Versions are deleted only when a user asks (`prune`), after
they have picked the one to keep. Only files matching <name>-v<n>.mp4 are ever touched.
"""

import re
from pathlib import Path


def all_versions(output):
    """Existing versions of an output, oldest first."""
    output = Path(output)
    pattern = re.compile(rf"^{re.escape(output.stem)}-v(\d+){re.escape(output.suffix)}$")
    found = [
        (int(m.group(1)), p)
        for p in output.parent.glob(f"{output.stem}-v*{output.suffix}")
        if (m := pattern.match(p.name))
    ]
    return [p for _, p in sorted(found)]


def latest(output):
    found = all_versions(output)
    return found[-1] if found else None


def number(path):
    return int(re.search(r"-v(\d+)\.[^.]+$", Path(path).name).group(1))


def next_path(output):
    """Where the next render goes: one above the highest existing version."""
    output, last = Path(output), latest(output)
    return output.with_name(f"{output.stem}-v{number(last) + 1 if last else 1}{output.suffix}")


def prune(output, keep=None):
    """Delete every version except `keep` (a version number; default the latest). Returns the
    kept path. Exits without deleting anything if the version to keep doesn't exist."""
    found = all_versions(output)
    kept = latest(output) if keep is None else next((p for p in found if number(p) == int(keep)), None)
    if kept is None:
        raise SystemExit(f"no version {keep or ''} of {Path(output).name} to keep; nothing deleted")
    for path in found:
        if path != kept:
            path.unlink()
    return kept
