"""Simple topic and language matching."""
from datetime import datetime, timezone


def publication_time(value):
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def recommend(articles, topics, language="All"):
    """Return ten matches, newest first, then ID; old date-only samples also work."""
    selected = set(topics)
    matches = [
        a for a in articles
        if (not selected or a["category"] in selected)
        and (language == "All" or a.get("language", "English") == language)
    ]
    return sorted(matches, key=lambda a: (-publication_time(a["published_at"]).timestamp(), a["id"]))[:10]
