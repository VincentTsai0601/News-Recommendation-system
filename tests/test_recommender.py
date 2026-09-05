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
