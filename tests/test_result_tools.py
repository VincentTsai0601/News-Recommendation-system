import csv
import io
import unittest
from result_tools import rank_articles, match_explanation, results_csv


def story(id, title, summary, date="2026-09-10"):
    return dict(id=id, title=title, summary=summary, published_at=date,
                source="Publisher", url="https://example.com/" + id)


class ResultToolsTests(unittest.TestCase):
    def test_title_matches_rank_above_summary_and_newest_is_optional(self):
        old = story("a", "Solar power", "", "2026-09-01")
        new = story("b", "Energy", "solar power")
        articles = [new, old]
        self.assertEqual(rank_articles(articles, "solar power", "Most relevant"), [old, new])
        self.assertEqual(rank_articles(articles, "solar power", "Newest"), [new, old])
        self.assertEqual(articles, [new, old])

    def test_normalization_duplicates_and_explanations_agree(self):
        article = story("a", "SOLAR 中文", "power")
        self.assertEqual(match_explanation(article, "solar SOLAR 中文 power absent"),
                         "Title matches: solar, 中文 | Summary matches: power")
        self.assertEqual(match_explanation(article, "absent"), "No search words matched the title or summary.")
        self.assertEqual(match_explanation(article, "  "), "")

    def test_ties_and_blank_query_use_date_then_id(self):
        articles = [story("b", "same", ""), story("a", "same", "")]
        self.assertEqual([a["id"] for a in rank_articles(articles, "same", "Most relevant")], ["a", "b"])
        self.assertEqual(rank_articles(articles, "", "Most relevant"), rank_articles(articles, "", "Newest"))

    def test_csv_roundtrip_unicode_quotes_and_formula_safety(self):
        articles = [story("a", '中文, "news"', ""), story("b", "=1+1", "")]
        data = results_csv(articles)
        rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
        self.assertEqual(list(rows[0]), ["Title", "Publisher", "Published at", "Link"])
        self.assertEqual(rows[0]["Title"], articles[0]["title"])
        self.assertEqual(rows[0]["Link"], articles[0]["url"])
        self.assertEqual(rows[1]["Title"], "'=1+1")
        self.assertEqual(len(rows), 2)
