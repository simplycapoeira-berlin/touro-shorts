# scheduled posting to Instagram, TikTok and more (design, not built)

- **Date:** 2026-11-28
- **Requested by:** project owner
- **Area:** process

## Feedback

Extend the product so finished shorts are shared on a schedule to TikTok, Instagram and other
social media, in a way that can be extended. Different users should schedule by talking to the
app, and the post should go out while their computer is closed, possibly with Claude's cloud
scheduling.

## Decision

**Status: designed, not built.** This file is the spec. The open questions at the end need the
owner's answers before any code is written.

**A posting service holds the timer, not our app.** A scheduling service (Buffer, Ayrshare or
similar) books the post and publishes it at the set time, so laptops can be closed. These
services already handle each platform's upload flow, its review rules and its limits, and
they cover Instagram, TikTok, YouTube and more through one API.
- *Rejected as the clock:* a Claude Code routine (cloud scheduled agent) that posts whatever is
  due. Routines do run with the laptop closed, but they are a research preview, and our app
  would then have to own API keys, retries and "already posted?" state for every platform.
  Routines stay useful for light jobs on top, e.g. a weekly "what's scheduled / what went out"
  report.
- *Rejected:* posting directly through each platform's API. Unreviewed TikTok apps can only post
  privately, for up to 5 users a day, and public posting needs TikTok's review (days to weeks).
  Instagram needs a professional (Business) account. A posting service already went through this.

**How a user schedules (the whole interface):**

```bash
uv run touro-shorts schedule edits/<file>.json --at "2026-12-02 18:00" --to instagram,tiktok
```

1. The user tells Claude, for example "post Martelo de chão Tuesday at 6 pm on Instagram and
   TikTok". Claude shows the video version, the time with its time zone, the platforms and the
   caption, and books it **only after the user confirms**. A post is public and can't be taken
   back from everyone who saw it.
2. The command uploads the latest render version (the kept one, after `clean`) to a link that
   only the posting service uses, then creates the scheduled post through the service's API.
3. It prints what was booked, with the service's post ID. Listing and cancelling scheduled
   posts are two more commands of the same shape (`schedule --list`, `schedule --cancel <id>`).

**Where it lives (extendable):**
- `src/touro_shorts/publish.py`: one small adapter per posting service, all with the same three
  functions: upload, book, cancel. Supporting another service or platform is one adapter plus
  a test. `cli.py` only wires the `schedule` command to it.
- **The caption is part of the edit**, so it's reviewed in a pull request like the text cards: a
  new optional `post` block in the edit file, `{"caption": "...", "hashtags": [...]}`, validated
  by `models.problems` (length limits per platform, no personal data).
- **Accounts and API keys** live in each user's environment (e.g. `TOURO_POST_API_KEY`) or the
  service's own settings, never in the repo. Each user connects their own social accounts once,
  in the posting service.

**Privacy principle, changed on purpose:** until now a render never left the laptop. Now a
render may leave it **only when a user schedules it**, to a link used by the posting service.
Footage (`in/`) still never leaves except through `archive`, and nothing goes to GitHub.

**Open questions for the owner:**
1. Which posting service? Buffer (simple, a free key, TikTok business accounts only) or
   Ayrshare (built for apps, more platforms, paid tiers).
2. Which Instagram and TikTok accounts post (personal Creator or Business), and who connects them?
3. Where does the upload go: the posting service's own media storage, or a shared Google Drive
   folder with a link?
4. Captions: written by the user, or drafted by Claude from the edit's text and confirmed?

**Sources:**
- [Claude Code routines](https://code.claude.com/docs/en/routines.md)
- [Instagram content publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/)
- [TikTok content sharing guidelines](https://developers.tiktok.com/doc/content-sharing-guidelines)
- [Buffer API](https://buffer.com/resources/best-social-media-apis/)
- [Ayrshare publishing API](https://www.ayrshare.com/social-media-publishing-api/)
