import unittest
from coverage_summary import source_coverage


class CoverageSummaryTests(unittest.TestCase):
    def test_counts_unique_articles_and_compares_timezones(self):
        first = dict(id="1", source="Publisher", language="French", category="World",
                     published_at="2026-09-06T10:00:00+08:00")
        second = dict(first, id="2", category="Science", published_at="2026-09-06T03:00:00+00:00")
        rows = source_coverage([first, first, second])
        self.assertEqual(rows, [{"Publisher": "Publisher", "Language": "French",
                                "Loaded articles": 2, "Topics": "Science, World",
                                "Newest publication (UTC)": "2026-09-06 03:00"}])
        self.assertEqual(source_coverage([]), [])

    def test_same_publisher_languages_are_separate(self):
        article = dict(id="1", source="Publisher", category="World", published_at="2024-01-01")
        rows = source_coverage([article, dict(article, id="2", language="Chinese")])
        self.assertEqual({r["Language"] for r in rows}, {"English", "Chinese"})
