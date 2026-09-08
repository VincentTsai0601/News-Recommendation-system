import unittest
from unittest.mock import patch
from pathlib import Path
import streamlit as st
from streamlit.testing.v1 import AppTest
from online_search_ui import cached_search

APP = Path(__file__).resolve().parents[1] / "app.py"


class OnlineSearchUITests(unittest.TestCase):
    def test_search_empty_failure_and_no_automatic_queries(self):
        cached_search.clear()
        self.addCleanup(cached_search.clear)
        article = dict(id="one", title="Solar energy", source="Publisher", published_at="2026-09-06T10:00:00+00:00", url="https://example.com/story")
        with patch("live_news.fetch_live_news", return_value=([], [], "now")), patch(
            "online_search_ui.search_feed", return_value=([article], None, "now")
        ) as search:
            st.cache_data.clear()
            app = AppTest.from_file(str(APP), default_timeout=20).run()
            app.radio[0].set_value("Search online (experimental)").run()
            search.assert_not_called()
            app.text_input[0].set_value("solar Taiwan")
            app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.get("link_button")), 1)
            search.return_value = ([], None, "later")
            app.text_input[0].set_value("unmatched")
            app.button[0].click().run()
            self.assertIn("No results returned", app.info[0].value)
            search.return_value = ([], "Online search is unavailable", "later")
            app.text_input[0].set_value("outage")
            app.button[0].click().run()
            self.assertTrue(app.error)
            self.assertEqual(len(app.get("link_button")), 0)
            self.assertFalse(app.exception)
