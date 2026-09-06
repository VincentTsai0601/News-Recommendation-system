import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from tools.check_news_provider import check


class ProviderCheckTests(unittest.TestCase):
    def test_rate_limit_is_reported_without_retry(self):
        error = HTTPError("https://example.com", 429, "Rate limit", {"Retry-After": "60"}, None)
        with patch("tools.check_news_provider.urlopen", side_effect=error) as request:
            report = check("climate")
        request.assert_called_once()
        self.assertEqual(report["http_status"], 429)
        self.assertEqual(report["retry_after"], "60")
        self.assertNotIn("count", report)

    def test_empty_success_is_distinct_from_failure(self):
        with patch("tools.check_news_provider.urlopen", return_value=io.BytesIO(b'{"articles": []}')):
            report = check("climate")
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["count"], 0)

    def test_malformed_payload_is_not_empty_success(self):
        for payload in (b'no results', b'{"error":"unavailable"}', b'{"articles":[null]}'):
            with self.subTest(payload=payload), patch(
                "tools.check_news_provider.urlopen", return_value=io.BytesIO(payload)
            ):
                self.assertEqual(check("climate")["status"], "failed")
