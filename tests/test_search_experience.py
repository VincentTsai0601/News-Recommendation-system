import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


class SearchExperienceTests(unittest.TestCase):
    def test_start_screen_is_online_search_without_prefetching(self):
        with patch("live_news.fetch_live_news", return_value=([], [], "now")) as feeds, patch("online_search_ui.search_feed") as search:
            app = AppTest.from_file(str(APP), default_timeout=20).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.radio[0].value, "Search news")
        self.assertIn("What news are you looking for?", [w.label for w in app.text_input])
        feeds.assert_not_called()
        search.assert_not_called()

    def test_incompatible_topics_explained_and_recoverable(self):
        articles = [dict(id="es", title="Noticias", summary="Resumen", language="Spanish",
                         category="World", source="Publisher", published_at="2026-09-10", url="https://example.com/es"),
                    dict(id="en", title="Sport", summary="Summary", language="English",
                         category="Sports", source="Publisher", published_at="2026-09-10", url="https://example.com/en")]
        with patch("live_news.fetch_live_news", return_value=(articles, [], "now")):
            app = AppTest.from_file(str(APP), default_timeout=20).run()
            self.assertIn("Browse publisher feeds", app.radio[0].options)
            app.radio[0].set_value("Browse publisher feeds").run()
            app.selectbox[0].set_value("Spanish").run()
            app.multiselect[0].set_value(["Sports"])
            app.button[1].click().run()
            self.assertTrue(any("Spanish" in w.value and "World" in w.value for w in app.warning))
            buttons = [b for b in app.button if b.label == "Show available topics"]
            self.assertEqual(len(buttons), 1)
            buttons[0].click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.multiselect[0].value, [])
            self.assertEqual(len(app.get("link_button")), 1)
            self.assertEqual(app.selectbox[0].value, "Spanish")
