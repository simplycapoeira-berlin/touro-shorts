"""Cold archive: copy files into a folder (typically a Google Drive for desktop folder, which then
syncs them to the cloud) and prove every copy is intact.

Copies are verified by sha256 and recorded in the folder's manifest.json. Archiving is
idempotent: identical files already there are skipped, and a *different* file with the same name
stops the run instead of being overwritten. Nothing is ever deleted from the source.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def archive(files, dest):
    """Copy files into dest (created if missing); returns the manifest {name: sha256}."""
    dest.mkdir(parents=True, exist_ok=True)
    manifest_path = dest / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for src in dict.fromkeys(Path(f).resolve() for f in files):  # same clip used twice = one copy
        target, digest = dest / src.name, sha256(src)
        if target.exists():
            if sha256(target) != digest:
                sys.exit(f"not overwriting {target}: a different file with that name is already archived")
        else:
            part = target.with_name(target.name + ".part")  # a crash never leaves a half file under the real name
            shutil.copy2(src, part)
            if sha256(part) != digest:
                part.unlink()
                sys.exit(f"copy of {src.name} is corrupt; nothing was archived under its name")
            part.rename(target)
        manifest[src.name] = digest
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest
