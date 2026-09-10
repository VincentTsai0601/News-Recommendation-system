import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from ai_reranker import RerankError

APP = Path(__file__).resolve().parents[1] / "app.py"

class AISearchUITests(unittest.TestCase):
    def test_ai_ranking_reused_and_failure_can_be_retried(self):
        articles = [dict(id=str(i), title="Solar " + str(i), summary="Energy", source="Source",
                         published_at="2026-09-10", url="https://example.com/" + str(i)) for i in range(12)]
        ranked = [dict(a, ai_score=float(i)) for i,a in enumerate(articles)][::-1]
        with patch("online_search_ui.search_feed", return_value=(articles,None,"now")) as fetch, patch(
            "online_search_ui.rerank", return_value=ranked) as model:
            app = AppTest.from_file(str(APP), default_timeout=30).run()
            app.text_input[0].set_value("solar")
            app.button[0].click().run()
            model.assert_not_called()
            app.selectbox(key="online_sort").set_value("AI relevance").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.get("link_button")[0].proto.url, articles[-1]["url"])
            self.assertEqual(len(app.get("download_button")),1)
            app.selectbox(key="online_page").set_value(2).run()
            self.assertEqual(model.call_count,1)
            self.assertEqual(fetch.call_count,1)
            model.side_effect = RerankError("AI unavailable; keyword fallback")
            app.button[0].click().run()
            self.assertTrue(app.warning)
            calls = model.call_count
            app.run()
            self.assertEqual(model.call_count,calls)
            model.side_effect = None
            next(b for b in app.button if b.label == "Retry AI reranking").click().run()
            self.assertFalse(app.exception)
            self.assertFalse(app.warning)
            self.assertEqual(model.call_count,calls+1)
            self.assertEqual(fetch.call_count,2)
