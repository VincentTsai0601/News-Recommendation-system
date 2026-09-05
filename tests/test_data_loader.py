import json
import tempfile
import unittest
from pathlib import Path

from data_loader import DataError, FIELDS, load_articles


class DataLoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "articles.json"
        self.article = dict(id="one", title="A headline", summary="A summary",
                            category="Science", source="Example", published_at="2024-02-29",
                            url="https://example.com/news")

    def load(self, data):
        self.path.write_text(json.dumps(data), encoding="utf-8")
        return load_articles(self.path)

    def test_valid_data_and_empty_list(self):
        self.assertEqual(self.load([self.article]), [self.article])
        self.assertEqual(self.load([]), [])

    def test_bundled_data(self):
        articles = load_articles()
        self.assertGreaterEqual(len(articles), 12)
        self.assertEqual({a["category"] for a in articles},
                         {"Technology", "Business", "Sports", "Science"})

    def test_missing_file(self):
        with self.assertRaisesRegex(DataError, "missing"):
            load_articles(self.path)

    def test_malformed_json_and_encoding(self):
        for content in (b"{broken", b"\xff"):
            with self.subTest(content=content):
                self.path.write_bytes(content)
                with self.assertRaisesRegex(DataError, "UTF-8 JSON"):
                    load_articles(self.path)

    def test_wrong_structure(self):
        for data in ({}, None, "news", [42], [[]]):
            with self.subTest(data=data), self.assertRaises(DataError):
                self.load(data)

    def test_all_fields_required_and_nonempty_strings(self):
        for field in FIELDS:
            for value in (None, "", " ", 123, " padded "):
                article = dict(self.article, **{field: value})
                with self.subTest(field=field, value=value), self.assertRaises(DataError):
                    self.load([article])
            article = self.article.copy()
            del article[field]
            with self.subTest(missing=field), self.assertRaises(DataError):
                self.load([article])

    def test_duplicate_ids(self):
        with self.assertRaisesRegex(DataError, "unique"):
            self.load([self.article, self.article])

    def test_invalid_dates(self):
        for value in ("2023-02-29", "2024-13-01", "2024-2-01", "20240201", "yesterday"):
            with self.subTest(value=value), self.assertRaisesRegex(DataError, "real date"):
                self.load([dict(self.article, published_at=value)])

    def test_invalid_urls(self):
        for value in ("javascript:alert(1)", "ftp://example.com", "https://", "/news",
                      "https://[invalid", "https://example.com:bad", "https://bad host/news"):
            with self.subTest(value=value), self.assertRaisesRegex(DataError, "HTTP"):
                self.load([dict(self.article, url=value)])

    def test_http_url_accepted(self):
        self.assertEqual(len(self.load([dict(self.article, url="http://example.com/news")])), 1)
