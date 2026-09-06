import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from global_search import build_url, parse_response, search_news, MAX_BYTES

# Synthetic contract fixture, not evidence of live coverage.
ITEM = {"title": "Research in Chile", "url": "https://example.com/story?a=1&b=2",
        "seendate": "20260906T100000Z", "sourcecountry": "France", "language": "French"}


class GlobalSearchTests(unittest.TestCase):
    def test_query_operators_cannot_be_injected(self):
        query = parse_qs(urlsplit(build_url("climate OR energy", "French")).query)["query"][0]
        self.assertEqual(query, '\"climate\" \"OR\" \"energy\" sourcelang:french')
        for value in ("", " ", "climate sourcecountry:US", 'a" OR b', "x" * 201):
            with self.subTest(value=value), patch("global_search.urlopen") as request:
                with self.assertRaises(ValueError):
                    search_news(value)
                request.assert_not_called()

    def test_geography_and_time_are_not_mislabeled(self):
        result = parse_response(json.dumps({"articles": [ITEM]}).encode())
        article = result.articles[0]
        self.assertEqual(article["publisher_country"], "France")
        self.assertIsNone(article["countries_discussed"])
        self.assertIsNone(article["published_at"])
        self.assertEqual(article["provider_observed_at"], "2026-09-06T10:00:00+00:00")

    def test_invalid_links_skipped_and_fragments_deduplicated(self):
        items = [ITEM, dict(ITEM, url=ITEM["url"] + "#part"),
                 dict(ITEM, url="javascript:alert(1)"), dict(ITEM, url="https://user:secret@example.com"),
                 dict(ITEM, seendate="yesterday"), None]
        result = parse_response(json.dumps({"articles": items}).encode())
        self.assertEqual(len(result.articles), 1)
        self.assertEqual(result.skipped, 4)

    def test_empty_invalid_and_network_failure_are_distinct(self):
        for payload, expected in [(b'{"articles":[]}', "empty"), (b'{}', "invalid_response"),
                                  (b'{"articles":[null]}', "invalid_response"),
                                  (b'x' * (MAX_BYTES + 1), "invalid_response")]:
            with self.subTest(expected=expected), patch("global_search.urlopen", return_value=io.BytesIO(payload)):
                self.assertEqual(search_news("climate").status, expected)
        with patch("global_search.urlopen", side_effect=TimeoutError):
            self.assertEqual(search_news("climate").status, "unavailable")

    def test_rate_limit_does_not_retry(self):
        error = HTTPError("https://example.com", 429, "limited", {"Retry-After": "120"}, None)
        with patch("global_search.urlopen", side_effect=error) as request:
            result = search_news("climate")
        request.assert_called_once()
        self.assertEqual(result.status, "rate_limited")
        self.assertEqual(result.retry_after, "120")
