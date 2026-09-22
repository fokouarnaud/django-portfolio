import re

_YOUTUBE_ID_PATTERNS = [
    re.compile(r"youtu\.be/(?P<id>[\w-]{11})"),
    re.compile(r"youtube\.com/watch\?.*?v=(?P<id>[\w-]{11})"),
    re.compile(r"youtube\.com/embed/(?P<id>[\w-]{11})"),
]


def youtube_video_id(url):
    if not url:
        return ""
    for pattern in _YOUTUBE_ID_PATTERNS:
        match = pattern.search(url)
        if match:
            return match.group("id")
    return ""


def youtube_embed_url(url):
    video_id = youtube_video_id(url)
    return f"https://www.youtube.com/embed/{video_id}" if video_id else ""
