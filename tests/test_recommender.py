import unittest

from recommender import recommend


class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.articles = [
            {"id": "b", "category": "Technology", "published_at": "2024-05-02"},
            {"id": "c", "category": "Sports", "published_at": "2024-06-01"},
            {"id": "a", "category": "Science", "published_at": "2024-05-02"},
            {"id": "d", "category": "Technology", "published_at": "2023-12-31"},
        ]

    def ids(self, topics):
        return [a["id"] for a in recommend(self.articles, topics)]

    def test_single_topic(self):
        self.assertEqual(self.ids(["Technology"]), ["b", "d"])

    def test_multiple_topics_and_repeated_selection(self):
        self.assertEqual(self.ids(["Technology", "Science", "Technology"]), ["a", "b", "d"])

    def test_no_selection_orders_dates_then_ids(self):
        self.assertEqual(self.ids([]), ["c", "a", "b", "d"])

    def test_no_matches(self):
        self.assertEqual(self.ids(["Unknown"]), [])

    def test_empty_collection(self):
        self.assertEqual(recommend([], []), [])

    def test_limit_applies_after_sorting(self):
        articles = [dict(id=str(i), category="Science", published_at=f"2024-01-{i:02}")
                    for i in range(1, 13)]
        self.assertEqual([a["id"] for a in recommend(articles, [])],
                         [str(i) for i in range(12, 2, -1)])

    def test_input_is_not_reordered(self):
        original = list(self.articles)
        recommend(self.articles, [])
        self.assertEqual(self.articles, original)

    def test_keyword_search_combines_fields_and_filters(self):
        articles = [
            dict(id="a", category="Science", language="English", published_at="2026-09-06",
                 title="Solar power", summary="Research in Chile"),
            dict(id="b", category="Science", language="Spanish", published_at="2026-09-06",
                 title="Solar Chile", summary="Energía"),
        ]
        self.assertEqual([a["id"] for a in recommend(articles, ["Science"], "English", "CHILE solar")], ["a"])
        self.assertEqual(recommend(articles, ["Sports"], "All", "solar"), [])
        self.assertEqual(recommend(articles, [], "All", "notpresent"), [])
        self.assertEqual(len(recommend(articles, [], "All", "  ")), 2)

    def test_keyword_search_handles_unicode(self):
        article = dict(id="a", category="World", published_at="2026-09-06",
                       title="Straße 太陽能源 ＡＩ", summary="")
        self.assertEqual(recommend([article], [], query="STRASSE 太陽 ai"), [article])

    def test_all_matches_remain_available_for_pagination(self):
        articles = [dict(id=str(i), category="Science", published_at=f"2024-01-{i:02}")
                    for i in range(1, 24)]
        matches = recommend(articles, [], limit=None)
        self.assertEqual([a["id"] for a in matches], [str(i) for i in range(23, 0, -1)])
        self.assertEqual(len(recommend(articles, [])), 10)
