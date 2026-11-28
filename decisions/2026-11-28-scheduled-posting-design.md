# scheduled posting through Postiz, run inside this project

- **Date:** 2026-11-28
- **Requested by:** project owner
- **Area:** process

## Feedback

Share finished shorts on a schedule to TikTok, Instagram and other social media, in a way that
can be extended, with users scheduling by talking to the app. Then: use a free, open-source tool
instead of a paid posting service. Use Postiz, started from this project (it's our monolith
product), as a local app for now, with a separate server possibly later.

## Decision

**Postiz publishes; touro-shorts books.** [Postiz](https://github.com/gitroomhq/postiz-app) is
an open-source scheduler (AGPL-3.0) for Instagram, TikTok, YouTube and 20+ more networks.
It has a public API.
- **The stack:** `deploy/postiz/compose.yaml` runs Postiz with its Postgres, Redis and Temporal
  (Temporal runs the scheduled jobs).
  - It is trimmed from Postiz's official compose file: the debug and admin UIs are removed.
  - The image version is pinned (v2.26.0), and all ports listen on localhost only.
  - Secrets live in `deploy/postiz/.env`, which is git-ignored; `.env.example` lists them.
- **The command:** `touro-shorts schedule <edit> <time> <channels> [--yes]` (`publish.py`).
  1. It uploads the edit's latest render to Postiz.
  2. It creates one scheduled post with the same video and caption on every named channel.
- **Extendable:** a new platform is one entry in `publish.SETTINGS`, the fields Postiz needs for
  it. Postiz handles each platform's login and upload flow.
- **Safe by construction:**
  - Without `--yes`, the command only prints the plan. Claude shows that plan to the user and
    adds `--yes` only after they confirm: a post is public.
  - The time must name its time zone and lie in the future.
  - Each channel must be connected in Postiz exactly once.
- **Captions live in the edit,** in a new `"post": {"caption": "..."}` block (1..2200
  characters, Instagram's limit), reviewed in pull requests like the on-screen text.
- **Keys:** `POSTIZ_API_KEY` (and `POSTIZ_URL` for a server later) come from each user's
  environment, never from the repo.

**Known limits of running it locally:**
- **The machine must be on.** Posts go out only while this machine is on and Docker is
  running. The same compose file moves to a server unchanged.
- **Instagram downloads each video from a public link,** and localhost isn't one. Set up
  Cloudflare R2 (free tier) as Postiz's storage (`STORAGE_PROVIDER=cloudflare`) before the first
  Instagram post. Instagram also needs a professional account and a Meta developer app.
- **TikTok needs a public HTTPS domain** for its login and for the media, and keeps posts
  private until our TikTok developer app passes TikTok's review. TikTok therefore starts with
  the server.

**Considered and rejected:**
- **A paid posting service** (Buffer, Ayrshare): it works, but the owner wants free and open
  source.
- **A Claude Code routine as the clock, with our own code posting to each platform:** we would
  rebuild what Postiz already does (each platform's login, upload, retry and review rules).
  Routines are also a research preview.

**Sources:**
- [Postiz Docker Compose](https://docs.postiz.com/installation/docker-compose)
- [Postiz public API](https://docs.postiz.com/public-api)
- [Postiz Instagram setup](https://docs.postiz.com/providers/instagram)
- [Postiz TikTok setup](https://docs.postiz.com/providers/tiktok)
- [TikTok content sharing guidelines](https://developers.tiktok.com/doc/content-sharing-guidelines)
- [Claude Code routines](https://code.claude.com/docs/en/routines.md)
