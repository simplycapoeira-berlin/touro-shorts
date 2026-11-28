"""touro-shorts: turn raw capoeira clips into a finished vertical short.

Usage:
    touro-shorts peaks <clip>                  # strongest motion moments, to time cuts and cards
    touro-shorts render <edit.json>            # render a new version: out/<name>-v<n>.mp4
    touro-shorts clean <edit.json> [version]   # keep one version (default: latest), delete the others
    touro-shorts archive <edit.json> <folder>  # copy inputs, kept render and edit to <folder>/<edit name>/
    touro-shorts schedule <edit.json> <time> <channels> [--yes]
        # book the latest render through Postiz, e.g. 2026-12-02T18:00+01:00 instagram,tiktok;
        # without --yes it only shows the plan: a post is public, so the user confirms first

The edit file format is in the README; the design rules behind it are in STYLE.md.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from . import archive, cards, models, publish, timeline, versions

W, H = cards.W, cards.H


def render(edit_path):
    edit = models.load(edit_path)
    output = timeline.source(edit["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    previous, dst = versions.latest(output), versions.next_path(output)
    cut = dst.with_suffix(".timeline.mp4")
    timeline.assemble(models.play_clips(edit), edit.get("brightness", 0), cut)
    placed = [(cards.compose(c, i), c) for i, c in enumerate(models.edit_cards(edit))]
    fps = timeline.FPS
    metadata = json.dumps(
        {
            "type": edit["type"],
            "edit": Path(edit_path).name,
            "clips": [Path(c["src"]).name for c in edit["clips"]],
            "text": [c["text"] for _, c in placed],
        }
    )

    decode = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", str(cut), "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE
    )
    encode = subprocess.Popen(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgba",
            "-s",
            f"{W}x{H}",
            "-r",
            str(fps),
            "-i",
            "-",
            "-i",
            str(cut),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "libx264",
            "-crf",
            "17",
            "-preset",
            "medium",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            "-map_metadata",
            "-1",
            "-metadata",
            f"genre={edit['type']}",
            "-metadata",
            f"comment={metadata}",
            str(dst),
        ],
        stdin=subprocess.PIPE,
    )

    frame_bytes, index = W * H * 4, 0
    while chunk := decode.stdout.read(frame_bytes):
        if len(chunk) < frame_bytes:
            break
        frame = Image.frombuffer("RGBA", (W, H), chunk)
        for g, card in placed:
            frame = cards.overlay_card(frame, g, card, index / fps)
        encode.stdin.write(frame.tobytes())
        index += 1
    encode.stdin.close()
    if encode.wait() != 0:
        sys.exit("ffmpeg encode failed")
    cut.unlink()
    if previous and previous.read_bytes() == dst.read_bytes():
        dst.unlink()  # deterministic: an unchanged edit would only duplicate the latest version
        print(f"{previous}  (unchanged, no new version)")
        return previous
    print(f"{dst}  ({index} frames, {edit['type']})")
    return dst


def peaks(clip, top=6):
    """Print the strongest motion moments: mean frame difference, smoothed over 0.3 s."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(clip), "-vf", "scale=90:160,fps=30,format=gray", "-f", "rawvideo", "-"],
        capture_output=True,
    ).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, 160, 90).astype(np.float32)
    energy = np.convolve(np.abs(np.diff(frames, axis=0)).mean((1, 2)), np.ones(9) / 9, "same")
    chosen = []  # strongest frames first, at least 1 s apart so one pass is reported once
    for i in np.argsort(-energy):
        if all(abs(i - j) >= 30 for j in chosen):
            chosen.append(i)
        if len(chosen) == top:
            break
    for i in sorted(chosen):
        print(f"{i / 30:5.2f}s  {'#' * int(energy[i] * 4)}")


def clean(edit_path, keep=None):
    """Keep one version of the edit's render (default: the latest) and delete the others."""
    output = timeline.source(models.load(edit_path)["output"])
    before = versions.all_versions(output)
    kept = versions.prune(output, keep)
    print(f"kept {kept.name}; deleted {len(before) - 1} other version(s)")


def archive_edit(edit_path, folder):
    """Archive a rendered edit to <folder>/<edit name>/: raw source clips in inputs/, plus the
    render and the edit file. The folder must already exist (e.g. a synced Google Drive folder),
    so a mistyped path fails instead of silently creating a local copy."""
    root = timeline.source(folder)
    if not root.is_dir():
        sys.exit(f"archive folder not found: {root} (is Google Drive for desktop running?)")
    edit = models.load(edit_path)
    render_path = versions.latest(timeline.source(edit["output"]))
    if render_path is None:
        sys.exit(f"render {edit['output']} first: the archive keeps inputs and output together")
    dest = root / Path(edit_path).stem
    clips = archive.archive([timeline.source(c["src"]) for c in edit["clips"]], dest / "inputs")
    files = archive.archive([render_path, edit_path], dest)
    print(f"{dest}  ({len(clips)} inputs + {len(files)} files, sha256-verified; in/ untouched)")


def schedule(edit_path, at, channels, confirm=None):
    """Book the edit's latest render on social channels through Postiz (see publish.py)."""
    edit = models.load(edit_path)
    video = versions.latest(timeline.source(edit["output"]))
    names = channels.split(",")
    unknown = sorted(set(names) - set(publish.SETTINGS))
    if video is None or "post" not in edit or unknown:
        sys.exit(f'needs a render, a "post" caption in the edit and known channels {sorted(publish.SETTINGS)}')
    try:
        when = publish.when(at)
        print(f"{video.name} -> {', '.join(names)} at {when} (UTC)\n{edit['post']['caption']}")
        if confirm != "--yes":
            print("not booked: run again with --yes once the user has confirmed")
            return
        print(publish.book(video, when, edit["post"]["caption"], names))
    except (ValueError, OSError) as error:  # OSError: Postiz not running or refused the request
        sys.exit(f"not booked: {error}")


COMMANDS = {  # name: (function, fewest arguments, most arguments)
    "render": (render, 1, 1),
    "peaks": (peaks, 1, 1),
    "clean": (clean, 1, 2),
    "archive": (archive_edit, 2, 2),
    "schedule": (schedule, 3, 4),
}


def main():
    command, least, most = COMMANDS.get(sys.argv[1] if len(sys.argv) > 1 else "", (None, 0, 0))
    if command is None or not least <= len(sys.argv) - 2 <= most:
        sys.exit(__doc__)
    command(*sys.argv[2:])
