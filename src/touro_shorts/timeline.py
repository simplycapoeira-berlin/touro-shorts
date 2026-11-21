"""Cut, re-time, grade and join raw clips into one 1080x1920 / 30 fps timeline with audio.

A clip is {"src": path, "start": s, "end": s, "speed": x}; only "src" is required. Paths may use
environment variables and ~, and relative paths are taken from the repository root, so users can
point edits at their own input folders. Output metadata from the sources (iPhone GPS, device
info) is always dropped.
"""

import os
import subprocess
import sys
from pathlib import Path

W, H, FPS = 1080, 1920, 30


def source(src):
    """A clip or output path: env vars and ~ expanded; relative paths are relative to the working
    directory (run commands from the repository root)."""
    return Path(os.path.expanduser(os.path.expandvars(src)))


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True,
        text=True,
    ).stdout
    return float(out)


def segments(clips):
    """[(start, end)] of every clip on the output timeline, in seconds."""
    t, spans = 0.0, []
    for clip in clips:
        end = clip.get("end") or duration(source(clip["src"]))
        length = (end - clip.get("start", 0)) / clip.get("speed", 1)
        spans.append((t, t + length))
        t += length
    return spans


def assemble(clips, brightness, dst):
    """Write the joined timeline to dst. Portrait/rotation is handled by ffmpeg's autorotate."""
    args, graph = ["ffmpeg", "-v", "error", "-y"], []
    for i, clip in enumerate(clips):
        src = source(clip["src"])
        if not src.is_file():
            sys.exit(f"clip not found: {src} (relative to the repo, or is $SC_CONTENT set?)")
        args += ["-i", str(src)]
        cut = f"start={clip.get('start', 0)}" + (f":end={clip['end']}" if "end" in clip else "")
        speed = clip.get("speed", 1)  # atempo keeps pitch; it accepts 0.5..2 per instance
        graph.append(
            f"[{i}:v:0]trim={cut},setpts=(PTS-STARTPTS)/{speed},fps={FPS},"
            f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,"
            f"eq=brightness={brightness}[v{i}];"
            f"[{i}:a:0]atrim={cut},asetpts=PTS-STARTPTS,atempo={speed},"
            f"aformat=sample_rates=48000:channel_layouts=stereo[a{i}];"
        )
    pairs = "".join(f"[v{i}][a{i}]" for i in range(len(clips)))
    args += [
        "-filter_complex",
        "".join(graph) + f"{pairs}concat=n={len(clips)}:v=1:a=1[v][a]",
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-map_metadata",
        "-1",
        "-c:v",
        "libx264",
        "-crf",
        "12",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        str(dst),
    ]
    if subprocess.run(args).returncode != 0:
        sys.exit("ffmpeg timeline assembly failed")
