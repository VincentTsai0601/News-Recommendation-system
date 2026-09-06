"""Simple topic and language matching."""
from datetime import datetime, timezone
import unicodedata


def publication_time(value):
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def recommend(articles, topics, language="All", query="", limit=10):
    """Return newest matches; limit=None includes every loaded match."""
    selected = set(topics)
    terms = unicodedata.normalize("NFKC", query).casefold().split()
    matches = [
        a for a in articles
        if (not selected or a["category"] in selected)
        and (language == "All" or a.get("language", "English") == language)
        and all(term in unicodedata.normalize("NFKC", a.get("title", "") + " " + a.get("summary", "")).casefold() for term in terms)
    ]
    return sorted(matches, key=lambda a: (-publication_time(a["published_at"]).timestamp(), a["id"]))[:limit]
