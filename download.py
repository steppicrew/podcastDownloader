#!/usr/bin/env python3
"""Download all episodes of an ARD Audiothek podcast as MP3 files.

Usage:
    ./download.py <show-url-or-urn> [output-dir]

Examples:
    ./download.py https://www.ardsounds.de/sendung/professor-van-dusen/urn:ard:show:8103e24c954e0404/
    ./download.py urn:ard:show:8103e24c954e0404

Files are saved as "<NN> <title>.mp3" inside a folder named after the
podcast's title (e.g. "Professor van Dusen/").
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request

GRAPHQL_URL = "https://api.ardaudiothek.de/graphql"

# GraphQL query used by the ardsounds.de frontend to page through a show's episodes.
QUERY = (
    "query ProgramSetEpisodesQuery($id:ID!,$offset:Int!,$count:Int!){"
    "result:programSet(id:$id){items(offset:$offset first:$count "
    "filter:{isPublished:{equalTo:true},itemType:{notEqualTo:EVENT_LIVESTREAM}}){"
    "pageInfo{hasNextPage endCursor}"
    "nodes{id title programSet{title}"
    "audios{url mimeType downloadUrl allowDownload}}}}}"
)

PAGE_SIZE = 24
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.ardsounds.de/",
}


def extract_show_urn(arg):
    """Accept a full ardsounds URL or a bare urn:ard:show:... string."""
    m = re.search(r"urn:ard:show:[0-9a-f]+", arg)
    if not m:
        sys.exit(f"No show URN found in: {arg!r}")
    return m.group(0)


def fetch_page(show_urn, offset):
    variables = {"id": show_urn, "offset": offset, "count": PAGE_SIZE}
    qs = urllib.parse.urlencode({"query": QUERY, "variables": json.dumps(variables)})
    req = urllib.request.Request(f"{GRAPHQL_URL}?{qs}", headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["data"]["result"]["items"]


def iter_episodes(show_urn):
    offset = 0
    while True:
        items = fetch_page(show_urn, offset)
        nodes = items["nodes"]
        for node in nodes:
            yield node
        if not items["pageInfo"]["hasNextPage"] or not nodes:
            break
        offset += len(nodes)


def parse_folge_number(title):
    """Return the 'Folge NN' number from a title, or None."""
    m = re.search(r"Folge\s+(\d+)", title)
    return int(m.group(1)) if m else None


def clean_title(title):
    """Strip surrounding quotes and the '- Folge NN' suffix; sanitize for filename."""
    t = re.sub(r"\s*[–-]\s*Folge\s+\d+\s*$", "", title)
    t = t.strip().strip("„“\"”").strip()
    t = re.sub(r'[\\/:*?"<>|]', "", t)        # chars illegal in filenames
    t = re.sub(r"\s+", " ", t).strip()
    return t


def pick_audio_url(audios):
    for a in audios:
        if a.get("allowDownload") and a.get("downloadUrl"):
            return a["downloadUrl"]
    for a in audios:
        if a.get("downloadUrl"):
            return a["downloadUrl"]
        if a.get("url"):
            return a["url"]
    return None


def download(url, path):
    tmp = path + ".part"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp, open(tmp, "wb") as f:
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)
    os.replace(tmp, path)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    show_urn = extract_show_urn(sys.argv[1])

    episodes = list(iter_episodes(show_urn))
    if not episodes:
        sys.exit("No episodes found.")

    show_title = episodes[0]["programSet"]["title"] or "podcast"
    out_root = sys.argv[2] if len(sys.argv) > 2 else "."
    out_dir = os.path.join(out_root, show_title)
    os.makedirs(out_dir, exist_ok=True)
    print(f"Show: {show_title}  ({len(episodes)} episodes) -> {out_dir}")

    for ep in episodes:
        title = ep["title"]
        num = parse_folge_number(title)
        if num is None:
            print(f"  SKIP (no Folge number, e.g. trailer): {title}")
            continue
        url = pick_audio_url(ep["audios"])
        if url is None:
            print(f"  SKIP (no audio): {title}")
            continue
        name = f"{num:02d} {clean_title(title)}.mp3"
        path = os.path.join(out_dir, name)
        if os.path.exists(path):
            print(f"  exists: {name}")
            continue
        print(f"  downloading: {name}")
        try:
            download(url, path)
        except Exception as e:
            print(f"  FAILED: {name}: {e}")


if __name__ == "__main__":
    main()
