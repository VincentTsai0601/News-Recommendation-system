import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from result_tools import results_csv

APP = Path(__file__).resolve().parents[1] / "app.py"


class ResultControlsTests(unittest.TestCase):
    def test_sort_export_and_pagination_in_both_modes(self):
        articles = [dict(id=str(i), title="Other news " + str(i), summary="solar",
                         source="Publisher", category="World", language="English",
                         published_at="2026-09-10", url="https://example.com/" + str(i))
                    for i in range(11)]
        articles.append(dict(articles[0], id="best", title="Solar title match", published_at="2026-09-01"))
        for mode, sort_key, page_key in [("Search news", "online_sort", "online_page"),
                                          ("Browse publisher feeds", "feed_sort", "result_page")]:
            with self.subTest(mode=mode), patch("live_news.fetch_live_news", return_value=(articles, [], "now")) as feeds, patch(
                "online_search_ui.search_feed", return_value=(articles, None, "now")
            ) as search, patch("result_tools.results_csv", wraps=results_csv) as export:
                online_export = patch("online_search_ui.results_csv", export)
                online_export.start()
                self.addCleanup(online_export.stop)
                app = AppTest.from_file(str(APP), default_timeout=30).run()
                app.radio[0].set_value(mode).run()
                app.text_input[0].set_value("solar")
                label = "Search online" if mode == "Search news" else "Get recommendations"
                next(b for b in app.button if b.label == label).click().run()
                self.assertFalse(app.exception)
                self.assertEqual(export.call_args.args[0][-1]["id"], "best")
                app.selectbox(key=page_key).set_value(2).run()
                calls = (feeds.call_count, search.call_count)
                app.selectbox(key=sort_key).set_value("Most relevant").run()
                self.assertFalse(app.exception)
                self.assertEqual(app.selectbox(key=page_key).value, 1)
                self.assertEqual((feeds.call_count, search.call_count), calls)
                self.assertEqual(export.call_args.args[0][0]["id"], "best")
                self.assertEqual(len(export.call_args.args[0]), 12)
                self.assertEqual(len(app.get("download_button")), 1)
                self.assertTrue(any("Title matches: solar" in c.value for c in app.caption))
                app.selectbox(key=sort_key).set_value("Newest").run()
                self.assertNotEqual(export.call_args.args[0][0]["id"], "best")
