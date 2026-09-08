import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from search_feed import search_feed
from test_live_news import XML


class SearchFeedTests(unittest.TestCase):
    def test_publisher_and_edition_do_not_infer_geography_or_language(self):
        content = XML.replace(b"</item>", b"<source>Publisher</source></item>")
        with patch("search_feed.urlopen", return_value=io.BytesIO(content)):
            articles, error, checked = search_feed("climate Taiwan", "Chinese")
        self.assertIsNone(error)
        self.assertEqual(articles[0]["source"], "Publisher")
        self.assertEqual(articles[0]["edition"], "Chinese")
        self.assertEqual(articles[0]["language"], "Unverified")
        self.assertNotIn("country", articles[0])

    def test_empty_and_failed_responses_are_distinct(self):
        with patch("search_feed.urlopen", return_value=io.BytesIO(b"<rss><channel/></rss>")):
            self.assertEqual(search_feed("climate")[:2], ([], None))
        for content in (b"<html/>", b"<!DOCTYPE rss><rss/>", XML.replace(b"https://example.com/a", b"javascript:1")):
            with patch("search_feed.urlopen", return_value=io.BytesIO(content)):
                self.assertIsNotNone(search_feed("climate")[1])
        with patch("search_feed.urlopen", side_effect=TimeoutError) as request:
            self.assertIsNotNone(search_feed("climate")[1])
            request.assert_called_once()

    def test_query_validation_before_network(self):
        with patch("search_feed.urlopen") as request:
            for query in (" ", "x" * 201, "a\nb"):
                with self.assertRaises(ValueError):
                    search_feed(query)
            request.assert_not_called()
