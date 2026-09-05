"""Simple topic matching; input articles are validated by data_loader."""

from datetime import date


def recommend(articles, topics):
    """Return at most ten matches, newest first, then by ID ascending."""
    selected = set(topics)
    matches = [a for a in articles if not selected or a["category"] in selected]
    return sorted(
        matches,
        key=lambda a: (-date.fromisoformat(a["published_at"]).toordinal(), a["id"]),
    )[:10]
