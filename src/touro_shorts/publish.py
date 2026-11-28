"""Sharing: book a finished short on social channels through Postiz, the open-source scheduler we
run ourselves (deploy/postiz/). Postiz holds the timer and publishes; this module only uploads the
video and creates the scheduled post through its public API.

Configured by environment, never by committed files: POSTIZ_API_KEY (Postiz > Settings >
Developers > Public API) and optionally POSTIZ_URL (default: the local stack).
A new platform is one entry in SETTINGS, with the fields Postiz requires for it
(docs.postiz.com/public-api/posts/create).
"""

import json
import os
import urllib.request
import uuid
from datetime import UTC, datetime
from pathlib import Path

# What Postiz needs to publish a vertical video on each channel type ("identifier" in Postiz).
SETTINGS = {
    "instagram": {"__type": "instagram", "post_type": "post"},
    "instagram-standalone": {"__type": "instagram-standalone", "post_type": "post"},
    "youtube": {"__type": "youtube", "type": "public", "selfDeclaredMadeForKids": "no"},
    "tiktok": {  # public once our TikTok app passes TikTok's review; Postiz forces private until then
        "__type": "tiktok",
        "privacy_level": "PUBLIC_TO_EVERYONE",
        "duet": False,
        "stitch": False,
        "comment": True,
        "autoAddMusic": "no",
        "brand_content_toggle": False,
        "brand_organic_toggle": False,
        "content_posting_method": "DIRECT_POST",
    },
}


def when(text, now=None):
    """The publish time as Postiz wants it (UTC ISO 8601). It must name its time zone, so a
    post never goes out an hour off, and it must be in the future."""
    at = datetime.fromisoformat(text)
    if at.tzinfo is None:
        raise ValueError(f"give the time zone too, e.g. {text}+01:00 (Berlin winter time)")
    if at <= (now or datetime.now(UTC)):
        raise ValueError(f"{text} is in the past")
    return at.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def post_body(at, caption, video, channels):
    """The scheduled post for Postiz: one entry per channel, same video and caption everywhere."""
    posts = []
    for channel in channels:
        settings = dict(SETTINGS[channel["identifier"]])
        if settings["__type"] == "youtube":
            settings["title"] = caption.splitlines()[0][:100]
        value = [{"content": caption, "image": [{"id": video["id"], "path": video["path"]}]}]
        posts.append({"integration": {"id": channel["id"]}, "value": value, "settings": settings})
    return {"type": "schedule", "date": at, "shortLink": False, "tags": [], "posts": posts}


def pick(integrations, names):
    """The connected Postiz channel for each requested name; exactly one each, or a clear error."""
    picked = []
    for name in names:
        found = [i for i in integrations if i["identifier"] == name and not i.get("disabled")]
        if len(found) != 1:
            have = sorted({i["identifier"] for i in integrations})
            raise ValueError(f"{len(found)} connected {name!r} channels in Postiz (connected: {have})")
        picked.append(found[0])
    return picked


def book(video_path, at, caption, names):
    """Upload the video, then schedule it on every named channel. Returns Postiz's answer."""
    channels = pick(_request("GET", "/integrations"), names)
    video = _upload(Path(video_path))
    return _request("POST", "/posts", post_body(at, caption, video, channels))


def _upload(path):
    boundary = uuid.uuid4().hex
    head = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        "Content-Type: video/mp4\r\n\r\n"
    ).encode()
    data = head + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    return _request("POST", "/upload", data=data, content_type=f"multipart/form-data; boundary={boundary}")


def _request(method, path, body=None, data=None, content_type="application/json"):
    key = os.environ.get("POSTIZ_API_KEY")
    if not key:
        raise ValueError("set POSTIZ_API_KEY (Postiz > Settings > Developers > Public API)")
    url = os.environ.get("POSTIZ_URL", "http://localhost:4007/api").rstrip("/") + "/public/v1" + path
    payload = json.dumps(body).encode() if body is not None else data
    request = urllib.request.Request(url, payload, {"Authorization": key, "Content-Type": content_type}, method=method)
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.load(response)
