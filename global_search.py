"""Experimental GDELT adapter. Not connected to the reader UI yet."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

MAX_BYTES = 2_000_000
LANGUAGES = {"English", "Chinese", "German", "French", "Italian", "Spanish"}


@dataclass
class SearchResult:
    status: str
    articles: list = field(default_factory=list)
    skipped: int = 0
    retry_after: str | None = None
    # A response at the requested cap may be truncated; no completeness claim.
    possibly_truncated: bool = False


def build_url(query, language="All"):
    """Simple English keywords only; provider operators are not reader input."""
    query = query.strip()
    if not query or len(query) > 200 or not re.fullmatch(r"[A-Za-z0-9\s]+", query):
        raise ValueError("Use 1–200 English letters, numbers, and spaces.")
    if language != "All" and language not in LANGUAGES:
        raise ValueError("Unsupported language filter")
    expression = " ".join('"' + word + '"' for word in query.split())
    if language != "All":
        expression += " sourcelang:" + language.lower()
    return "https://api.gdeltproject.org/api/v2/doc/doc?" + urlencode({
        "query": expression, "mode": "artlist", "format": "json",
        "timespan": "24h", "maxrecords": 50, "sort": "datedesc"})


def parse_response(content):
    if len(content) > MAX_BYTES:
        raise ValueError("Oversized response")
    payload = json.loads(content)
    if not isinstance(payload, dict) or not isinstance(payload.get("articles"), list):
        raise ValueError("Unexpected response schema")
    raw = payload["articles"]
    if len(raw) > 50:
        raise ValueError("Response exceeds requested article cap")
    articles, seen, skipped = [], set(), 0
    for item in raw:
        try:
            title, url = item["title"], item["url"]
            if not isinstance(title, str) or not title.strip() or not isinstance(url, str):
                raise ValueError("Missing title or URL")
            parts = urlsplit(url)
            if parts.scheme not in ("https", "http") or not parts.hostname or parts.username or parts.password:
                raise ValueError("Invalid URL")
            if any(c.isspace() or ord(c) < 32 for c in url):
                raise ValueError("Invalid URL")
            observed = datetime.strptime(item["seendate"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            url = urlunsplit(parts._replace(fragment=""))
            if url in seen:
                continue
            # Metadata remains provider-reported, not inferred from language.
            country, language = item.get("sourcecountry"), item.get("language")
            articles.append({"id": sha256(url.encode()).hexdigest(), "title": title.strip(),
                             "url": url, "source": parts.hostname,
                             "language": language if isinstance(language, str) else None,
                             "publisher_country": country if isinstance(country, str) else None,
                             "countries_discussed": None, "published_at": None,
                             "provider_observed_at": observed.isoformat(), "provider": "GDELT"})
            seen.add(url)
        except (KeyError, ValueError, TypeError, OverflowError):
            skipped += 1
    status = "ok" if articles else ("invalid_response" if raw else "empty")
    return SearchResult(status, articles, skipped, possibly_truncated=len(raw) == 50)


def search_news(query, language="All"):
    # Validate before sending any request. There are no automatic retries.
    url = build_url(query, language)
    try:
        request = Request(url, headers={"User-Agent": "WorldBrief/1.0 (news search evaluation)"})
        with urlopen(request, timeout=15) as response:
            return parse_response(response.read(MAX_BYTES + 1))
    except HTTPError as exc:
        return SearchResult("rate_limited" if exc.code == 429 else "unavailable",
                            retry_after=exc.headers.get("Retry-After"))
    except (OSError, TimeoutError):
        return SearchResult("unavailable")
    except (ValueError, TypeError):
        return SearchResult("invalid_response")
