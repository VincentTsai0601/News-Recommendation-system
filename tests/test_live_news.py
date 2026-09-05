import unittest
from unittest.mock import patch
from live_news import parse_feed, fetch_live_news, fetch_one, MAX_BYTES
from recommender import recommend

XML = b"""<rss><channel><item><title>News</title><link>https://example.com/a</link>
<description>&lt;p&gt;Hello &amp;amp; world&lt;/p&gt;</description>
<pubDate>Sat, 05 Sep 2026 10:00:00 +0800</pubDate></item></channel></rss>"""


class LiveNewsTests(unittest.TestCase):
    def test_parse_normalizes_timezone_and_removes_html(self):
        article = parse_feed(XML, "Publisher", "Chinese", "World")[0]
        self.assertEqual(article["published_at"], "2026-09-05T02:00:00+00:00")
        self.assertEqual(article["summary"], "Hello & world")
        self.assertEqual(article["language"], "Chinese")

    def test_bad_entries_are_skipped(self):
        for invalid in (
            XML.replace(b"Sat, 05 Sep 2026 10:00:00 +0800", b"invalid"),
            XML.replace(b"https://example.com/a", b"javascript:alert(1)"),
            XML.replace(b"<title>News</title>", b"<title></title>"),
        ):
            with self.subTest(invalid=invalid):
                self.assertEqual(parse_feed(invalid, "BBC", "English", "World"), [])

    def test_rejects_html_entities_and_oversized_feeds(self):
        for content in (b"<html/>", b"<!DOCTYPE rss><rss/>", b"x" * (MAX_BYTES + 1)):
            with self.subTest(content=content[:30]), self.assertRaises(ValueError):
                parse_feed(content, "BBC", "English", "World")

    def test_network_failure_is_reported(self):
        with patch("live_news.urlopen", side_effect=TimeoutError):
            articles, warning = fetch_one(("BBC", "English", "World", "https://example.com"))
        self.assertEqual(articles, [])
        self.assertIn("unavailable", warning)

    def test_partial_failure_and_deduplication(self):
        article = parse_feed(XML, "BBC", "English", "World")[0]
        with patch("live_news.FEEDS", [1, 2, 3]), patch(
            "live_news.fetch_one", side_effect=[([article], None), ([], "unavailable"), ([article], None)]
        ):
            articles, warnings, checked = fetch_live_news()
        self.assertEqual(len(articles), 1)
        self.assertEqual(warnings, ["unavailable"])
        self.assertIn("+00:00", checked)

    def test_intraday_order_and_language(self):
        base = parse_feed(XML, "BBC", "English", "World")[0]
        later = dict(base, id="later", language="Chinese", published_at="2026-09-05T03:00:00+00:00")
        self.assertEqual(recommend([base, later], [])[0]["id"], "later")
        self.assertEqual(recommend([base, later], [], "Chinese"), [later])
        self.assertEqual(recommend([base, later], [], "English"), [base])

    def test_new_language_text_survives_parsing(self):
        for language, title in [("German", "Grüße"), ("French", "Français"),
                                ("Italian", "Novità"), ("Spanish", "España")]:
            with self.subTest(language=language):
                content = XML.replace(b"News", title.encode("utf-8"))
                article = parse_feed(content, "Publisher", language, "World")[0]
                self.assertEqual(article["title"], title)
                self.assertEqual(recommend([article], [], language), [article])
                self.assertEqual(recommend([article], [], "Chinese"), [])
