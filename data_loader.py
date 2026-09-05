"""Read and validate the small, local article collection."""

import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "articles.json"
FIELDS = ("id", "title", "summary", "category", "source", "published_at", "url")


class DataError(ValueError):
    """An article file cannot be loaded safely for display."""


def load_articles(path=DEFAULT_DATA_PATH):
    """Return validated articles, or raise a reader-friendly DataError."""
    try:
        articles = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DataError("Article file is missing. Restore data/articles.json.") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DataError("Cannot read article data. Check that the file is valid UTF-8 JSON.") from exc

    if not isinstance(articles, list):
        raise DataError("Article data must be a JSON list.")

    seen_ids = set()
    for index, article in enumerate(articles, start=1):
        prefix = f"Article {index}: "
        if not isinstance(article, dict):
            raise DataError(prefix + "each article must be a JSON object.")
        for field in FIELDS:
            value = article.get(field)
            if not isinstance(value, str) or not value.strip():
                raise DataError(prefix + f"'{field}' must be a non-empty string.")
            if value != value.strip():
                raise DataError(prefix + f"remove surrounding whitespace from '{field}'.")
        if article["id"] in seen_ids:
            raise DataError(prefix + "article IDs must be unique.")
        seen_ids.add(article["id"])
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", article["published_at"]):
                raise ValueError
            date.fromisoformat(article["published_at"])
        except ValueError as exc:
            raise DataError(prefix + "'published_at' must be a real date in YYYY-MM-DD format.") from exc
        try:
            url = urlsplit(article["url"])
            if (url.scheme not in ("http", "https") or not url.hostname
                    or any(char.isspace() for char in article["url"])):
                raise ValueError
            url.port  # Reject invalid port numbers too.
        except ValueError as exc:
            raise DataError(prefix + "'url' must be an HTTP or HTTPS address with a host.") from exc
    return articles
