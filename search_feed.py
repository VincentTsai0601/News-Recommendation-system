"""Experimental Google News RSS search; no claim of exhaustive coverage."""
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from live_news import MAX_BYTES, parse_feed, plain_text

EDITIONS = {"English": ("en-US", "US", "US:en"), "Chinese": ("zh-TW", "TW", "TW:zh-Hant"),
            "German": ("de", "DE", "DE:de"), "French": ("fr", "FR", "FR:fr"),
            "Italian": ("it", "IT", "IT:it"), "Spanish": ("es", "ES", "ES:es")}


def search_feed(query, edition="English"):
    query = query.strip()
    if not query or len(query) > 200 or any(ord(c) < 32 for c in query):
        raise ValueError("Enter 1–200 characters without control characters.")
    if edition not in EDITIONS:
        raise ValueError("Unknown edition")
    hl, gl, ceid = EDITIONS[edition]
    url = "https://news.google.com/rss/search?" + urlencode({"q": query, "hl": hl, "gl": gl, "ceid": ceid})
    checked = datetime.now(timezone.utc).isoformat()
    try:
        with urlopen(Request(url, headers={"User-Agent": "WorldBrief/1.0 RSS reader"}), timeout=15) as response:
            content = response.read(MAX_BYTES + 1)
        # The shared parser bounds size and rejects DTD/entity declarations.
        articles = parse_feed(content, "Google News", "Unverified", "Search")
        root = ET.fromstring(content)
        sources = {item.findtext("link", "").strip().split("#")[0]: plain_text(item.findtext("source", ""))
                   for item in root.findall("./channel/item")[:100]}
        unique = {}
        for article in articles:
            article["source"] = sources.get(article["url"]) or "Publisher not supplied"
            article["edition"] = edition
            article["link_provider"] = "Google News"
            unique.setdefault(article["id"], article)
        if root.findall("./channel/item") and not articles:
            return [], "Search returned entries we could not read. Try again later.", checked
        return list(unique.values()), None, checked
    except (OSError, ValueError, ET.ParseError, TimeoutError):
        return [], "Online search is unavailable. Try again later.", checked
