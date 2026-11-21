"""Turn raw capoeira clips into a finished vertical short: cut, join, grade, then animate
brand-styled, movement-timed text cards on top.

Usage:
    uv run shorts.py peaks <clip>        # print motion peaks, to pick cuts and card timings
    uv run shorts.py render <edit.json>  # render the edit described in the JSON
    uv run shorts.py archive <edit.json> <folder>  # cold-archive its inputs, render and edit
                                                   # into <folder>/<edit name>/ (e.g. Google Drive)

An edit file (models.py) declares its video "type" (see models.MODELS), its "clips" (timeline.py), an "output"
path, an optional "brightness", and its text cards. Educational edits may omit "cards": each
clip then gets a numbered step card automatically (its optional "text", or "Step <n>").
The type and the sources are written into the output's metadata.

Text cards (cards.py): the last word of each card is its key word: it is set huge
and marked in yellow; the words before it form the small kicker line above. Each card is timed
to the movement:
    {"text": "It is not about talent", "in": s, "hit": s, "out": s, "kick": "left"}
  in   - the kicker starts entering (once the body has cleared the text band)
  hit  - the key word has landed and the yellow marker is complete
  out  - the card starts leaving; past the clip end = hold to the end
  kick - optional, "left" or "right": at `out` a kick sweeping in that direction knocks the
         letters off screen instead of the normal slide-out
  shrink - optional time: from here the card shrinks toward its aligned top corner, staying
         readable but out of the movement's way until `out` (bridges a long gap to the next card)
Cards alternate left / right alignment. Design rules behind every constant: STYLE.md.

Clip and output paths may use environment variables (e.g. "$SC_CONTENT/...") or be relative to
the repo (e.g. "in/IMG_7011.MOV"), so edit files never contain a machine-specific (or private)
path. "brightness" (ffmpeg eq, -0.2..0.2, default 0) grades the footage only, so the type keeps its
exact brand colors.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

import archive
import cards
import models
import timeline

ROOT = models.ROOT
W, H = cards.W, cards.H


def render(edit_path):
    edit = models.load(edit_path)
    dst = timeline.source(ROOT, edit["output"])
    dst.parent.mkdir(parents=True, exist_ok=True)
    cut = dst.with_suffix(".timeline.mp4")
    timeline.assemble(models.play_clips(edit), edit.get("brightness", 0), ROOT, cut)
    placed = [(cards.compose(c, i), c) for i, c in enumerate(models.edit_cards(edit))]
    fps = timeline.FPS
    metadata = json.dumps({"type": edit["type"], "edit": Path(edit_path).name,
                           "clips": [Path(c["src"]).name for c in edit["clips"]],
                           "text": [c["text"] for _, c in placed]})

    decode = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(cut), "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
                              stdout=subprocess.PIPE)
    encode = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
         "-r", str(fps), "-i", "-", "-i", str(cut), "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
         "-map_metadata", "-1", "-metadata", f"genre={edit['type']}", "-metadata", f"comment={metadata}",
         str(dst)],
        stdin=subprocess.PIPE)

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
    print(f"{dst}  ({index} frames, {edit['type']})")


def peaks(clip, top=6):
    """Print the strongest motion moments: mean frame difference, smoothed over 0.3 s."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(clip), "-vf", "scale=90:160,fps=30,format=gray",
         "-f", "rawvideo", "-"], capture_output=True).stdout
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


def archive_edit(edit_path, folder):
    """Archive a rendered edit to <folder>/<edit name>/: raw source clips in inputs/, plus the
    render and the edit file. The folder must already exist (e.g. a synced Google Drive folder),
    so a mistyped path fails instead of silently creating a local copy."""
    root = timeline.source(ROOT, folder)
    if not root.is_dir():
        sys.exit(f"archive folder not found: {root} (is Google Drive for desktop running?)")
    edit = models.load(edit_path)
    render_path = timeline.source(ROOT, edit["output"])
    if not render_path.is_file():
        sys.exit(f"render {render_path} first: the archive keeps inputs and output together")
    dest = root / Path(edit_path).stem
    clips = archive.archive([timeline.source(ROOT, c["src"]) for c in edit["clips"]], dest / "inputs")
    files = archive.archive([render_path, edit_path], dest)
    print(f"{dest}  ({len(clips)} inputs + {len(files)} files, sha256-verified; in/ untouched)")


if __name__ == "__main__":
    commands = {"render": (render, 1), "peaks": (peaks, 1), "archive": (archive_edit, 2)}
    command, arity = commands.get(sys.argv[1] if len(sys.argv) > 1 else "", (None, 0))
    if command is None or len(sys.argv) != 2 + arity:
        sys.exit(__doc__)
    command(*sys.argv[2:])
