"""Fetch a small set of publisher RSS feeds; no API key required."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

FEEDS = [
    ("DW", "German", "World", "https://rss.dw.com/xml/rss-de-all"),
    ("France 24", "French", "World", "https://www.france24.com/fr/rss"),
    ("ANSA", "Italian", "World", "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml"),
    ("BBC Mundo", "Spanish", "World", "https://feeds.bbci.co.uk/mundo/rss.xml"),
    ("BBC", "English", "World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("BBC", "English", "Technology", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("BBC", "English", "Business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("BBC", "English", "Science", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
    ("BBC", "English", "Sports", "https://feeds.bbci.co.uk/sport/rss.xml"),
    ("RTHK 香港電台", "Chinese", "World", "https://rthk.hk/rthk/news/rss/c_expressnews_cinternational.xml"),
    ("RTHK 香港電台", "Chinese", "Business", "https://rthk.hk/rthk/news/rss/c_expressnews_cfinance.xml"),
    ("RTHK 香港電台", "Chinese", "Sports", "https://rthk.hk/rthk/news/rss/c_expressnews_csport.xml"),
]
LANGUAGES = ["English", "Chinese", "German", "French", "Italian", "Spanish"]
MAX_BYTES = 2_000_000


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain_text(value):
    parser = PlainText()
    parser.feed(value)
    return " ".join(" ".join(parser.parts).split())


def parse_feed(content, source, language, category):
    """Skip entries without a usable title, link, or publication time."""
    if len(content) > MAX_BYTES or b"<!DOCTYPE" in content.upper() or b"<!ENTITY" in content.upper():
        raise ValueError("Unsupported feed")
    root = ET.fromstring(content)
    if root.tag != "rss":
        raise ValueError("Expected RSS")
    articles = []
    for item in root.findall("./channel/item")[:100]:
        try:
            title = plain_text(item.findtext("title", ""))
            url = item.findtext("link", "").strip()
            parts = urlsplit(url)
            if not title or parts.scheme not in ("http", "https") or not parts.hostname:
                continue
            if any(c.isspace() for c in url):
                continue
            published = parsedate_to_datetime(item.findtext("pubDate", ""))
            if published.tzinfo is None:
                continue
            published = published.astimezone(timezone.utc)
            # Fragments do not identify a different article.
            url = urlunsplit(parts._replace(fragment=""))
            articles.append({
                "id": sha256(url.encode()).hexdigest(),
                "title": title,
                "summary": plain_text(item.findtext("description", ""))[:500] or "Read the original article for details.",
                "category": category, "source": source, "language": language,
                "published_at": published.isoformat(), "url": url,
            })
        except (ValueError, TypeError, OverflowError):
            continue
    return articles


def fetch_one(feed):
    source, language, category, url = feed
    try:
        request = Request(url, headers={"User-Agent": "NewsForYou/1.0 (RSS reader)"})
        with urlopen(request, timeout=12) as response:
            content = response.read(MAX_BYTES + 1)
        articles = parse_feed(content, source, language, category)
        if not articles:
            raise ValueError("No usable articles")
        return articles, None
    except Exception:
        # A publisher outage must not stop the other feeds or expose a traceback.
        return [], f"{source} / {category} ({language}) is unavailable."


def fetch_live_news():
    """Return articles, feed warnings, and the UTC fetch time."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        batches = list(pool.map(fetch_one, FEEDS))
    articles, warnings, seen = [], [], set()
    for batch, warning in batches:
        if warning:
            warnings.append(warning)
        for article in batch:
            if article["id"] not in seen:
                articles.append(article)
                seen.add(article["id"])
    return articles, warnings, datetime.now(timezone.utc).isoformat()
