import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

CHANNEL_ID = "UCQpAC3qn9g2jPInA3J-xAbQ"
HANDLE_URL = "https://www.youtube.com/@SparkLightIgniteStudios/videos"
LIMIT = 20
ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "site" if (ROOT / "site").exists() else ROOT
OUTPUT = SITE_ROOT / "youtube-videos.json"
FEED_URLS = [
    f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}",
    f"https://www.youtube.com/feeds/videos.xml?playlist_id=UU{CHANNEL_ID[2:]}"
]
ATOM = "{http://www.w3.org/2005/Atom}"
YT = "{http://www.youtube.com/xml/schemas/2015}"
MEDIA = "{http://search.yahoo.com/mrss/}"


def text(parent, name):
    match = parent.find(name)
    return match.text.strip() if match is not None and match.text else ""


def label(value):
    if not value:
        return "Recent release"
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return value
    return parsed.strftime("%b %-d, %Y") if sys.platform != "win32" else parsed.strftime("%b %#d, %Y")


def load_url(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def build_from_feed(xml_bytes):
    root = ET.fromstring(xml_bytes)
    videos = []
    for entry in root.findall(f"{ATOM}entry")[:LIMIT]:
        video_id = text(entry, f"{YT}videoId")
        title = text(entry, f"{ATOM}title")
        published = text(entry, f"{ATOM}published")
        thumbnail = ""
        group = entry.find(f"{MEDIA}group")
        if group is not None:
            thumb = group.find(f"{MEDIA}thumbnail")
            if thumb is not None:
                thumbnail = thumb.attrib.get("url", "")
        if video_id and title:
            videos.append(video(video_id, title, published, label(published), thumbnail))
    return videos


def video(video_id, title, published, published_label, thumbnail=""):
    return {
        "id": video_id,
        "title": html.unescape(title),
        "published": published,
        "publishedLabel": published_label or "Recent release",
        "thumbnail": (thumbnail or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg").replace("\\u0026", "&"),
        "url": f"https://www.youtube.com/watch?v={video_id}"
    }


def extract_balanced_object(source, start):
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        else:
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return source[start:index + 1]
    return ""


def build_from_channel_page(html_text):
    videos = []
    seen = set()
    marker = '"lockupViewModel"'
    position = 0
    while len(videos) < LIMIT:
        marker_index = html_text.find(marker, position)
        if marker_index == -1:
            break
        object_start = html_text.rfind("{", 0, marker_index)
        chunk = extract_balanced_object(html_text, object_start) if object_start != -1 else ""
        position = marker_index + len(marker)
        if not chunk:
            continue
        ids = re.findall(r'https://i\.ytimg\.com/vi/([A-Za-z0-9_-]{11})/', chunk)
        if not ids:
            ids = re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', chunk)
        if not ids:
            continue
        video_id = ids[0]
        if video_id in seen:
            continue
        title_match = re.search(r'"title":\{"content":"((?:\\.|[^"\\])*)"\}', chunk)
        title = json.loads(f'"{title_match.group(1)}"') if title_match else "Spark Light Ignite video"
        date_match = re.search(r'"accessibilityLabel":"([^"\\]*(?:ago|premiered|streamed)[^"\\]*)"', chunk, re.I)
        if not date_match:
            date_match = re.search(r'"text":\{"content":"([^"\\]*(?:ago|premiered|streamed)[^"\\]*)"\}', chunk, re.I)
        published_label = json.loads(f'"{date_match.group(1)}"') if date_match else "Recent release"
        thumb_match = re.search(r'"url":"(https://i\.ytimg\.com/vi/[^"]+)"', chunk)
        thumbnail = json.loads(f'"{thumb_match.group(1)}"') if thumb_match else ""
        videos.append(video(video_id, title, "", published_label, thumbnail))
        seen.add(video_id)
    return videos


def load_videos():
    for url in FEED_URLS:
        try:
            videos = build_from_feed(load_url(url))
            if videos:
                return videos, url
        except Exception:
            pass
    page = load_url(HANDLE_URL).decode("utf-8", errors="ignore")
    videos = build_from_channel_page(page)
    if videos:
        return videos, HANDLE_URL
    raise RuntimeError("No YouTube videos found")


def main():
    videos, source = load_videos()
    data = {
        "channelId": CHANNEL_ID,
        "source": source,
        "updatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "videos": videos[:LIMIT]
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT} with {len(data['videos'])} videos")


if __name__ == "__main__":
    main()
