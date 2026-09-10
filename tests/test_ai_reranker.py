import unittest
from unittest.mock import patch
from ai_reranker import rerank, RerankError

class AIRerankerTests(unittest.TestCase):
    def test_scores_determine_order_without_mutating_articles(self):
        items = [dict(id="a", title="A", summary="", published_at="2026-09-10"),
                 dict(id="b", title="B", summary="", published_at="2026-09-01")]
        with patch("ai_reranker.score_pairs", return_value=[-2, 3]) as scorer:
            result = rerank("query", items)
        self.assertEqual([a["id"] for a in result], ["b", "a"])
        self.assertNotIn("ai_score", items[0])
        self.assertEqual(result[0]["ai_score"], 3)
        self.assertEqual(scorer.call_args.args[0], "query")

    def test_rejects_invalid_model_outputs(self):
        item = dict(id="a", title="A", published_at="2026-09-10")
        for scores in [[], [float("nan")], [float("inf")]]:
            with patch("ai_reranker.score_pairs", return_value=scores):
                with self.assertRaises(RerankError):
                    rerank("query", [item])

    def test_empty_does_not_load_model_and_bounds_candidates(self):
        with patch("ai_reranker.score_pairs") as scorer:
            self.assertEqual(rerank("query", []), [])
            scorer.assert_not_called()
            with self.assertRaises(RerankError):
                rerank("", [{"id":"a"}])
            with self.assertRaises(RerankError):
                rerank("query", [{}] * 101)
