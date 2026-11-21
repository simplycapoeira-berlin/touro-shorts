# hook research and dash versions

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** style

## Feedback

Name versions with a dash (`-v2`), not a dot. The educational video's first move is too quick
to follow: maybe add about 1 s before and after, but keep the opening catchy, because people
swipe Reels and TikTok fast. Research what works best for attention in the first seconds, and
apply the research even where it contradicts this suggestion.

## Decision

Research consulted (platform guidance plus marketing and creator reports; no peer-reviewed
studies were found):
- TikTok's official creative best practices put the hook within the first 6 seconds;
- guides and creator reports agree that the scroll decision happens in roughly the first
  1–3 seconds, so the visual hook should land in ~1–1.5 s;
- start mid-action, with no slow lead-in;
- put text on screen from the first frame (many viewers start muted), and concrete numbers help;
- show a real person early.

Applied:
- **Hook timing:** we did *not* add a full second before the move, which would be the slow
  lead-in the research warns against. The hook now starts ~0.7 s earlier, while Touro is
  already moving, so the aú peaks at ~1.0 s. Roughly 1 s of landing and recovery follows for
  comprehension. 261120-steps hook: IMG_7017 3.9–6.0 s (2.1 s).
- **First-frame text:** the educational hook gets an automatic card from frame 0, "In <n>
  steps" (or the hook clip's `text`). It lands by 0.5 s and leaves as the hook ends.
- **Length:** move cuts end 1.3 s after the peak (was 1.4) to keep the video at 19.8 s.
- **Versions:** renders are named `<name>-v<n>.mp4`.
