"""One read-only GDELT probe. Run manually; never during unit tests."""
import argparse
from datetime import datetime, timezone
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def check(query):
    params = dict(query=query, mode="artlist", format="json", timespan="24h",
                  maxrecords=5, sort="datedesc")
    url = "https://api.gdeltproject.org/api/v2/doc/doc?" + urlencode(params)
    report = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "provider": "GDELT DOC 2", "query": query, "window": "24h"}
    started = time.monotonic()
    try:
        request = Request(url, headers={"User-Agent": "WorldBrief-provider-evaluation/1.0"})
        with urlopen(request, timeout=25) as response:
            content = response.read(2_000_001)
            if len(content) > 2_000_000:
                raise ValueError("Response exceeds size limit")
            payload = json.loads(content)
        if not isinstance(payload, dict) or not isinstance(payload.get("articles"), list):
            raise ValueError("Unexpected response schema")
        articles = payload["articles"]
        report.update(status="ok", count=len(articles),
                      source_countries=sorted({str(a.get("sourcecountry", "Unknown")) for a in articles}),
                      languages=sorted({str(a.get("language", "Unknown")) for a in articles}),
                      samples=[{k: a.get(k) for k in ("url", "title", "seendate", "sourcecountry", "language")}
                               for a in articles[:3]])
    except HTTPError as exc:
        report.update(status="http_error", http_status=exc.code,
                      retry_after=exc.headers.get("Retry-After"))
    except (URLError, TimeoutError, ValueError, TypeError, AttributeError) as exc:
        report.update(status="failed", error_type=type(exc).__name__)
    report["elapsed_seconds"] = round(time.monotonic() - started, 2)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Public test query; do not include private information")
    args = parser.parse_args()
    print(json.dumps(check(args.query), ensure_ascii=True, indent=2))
