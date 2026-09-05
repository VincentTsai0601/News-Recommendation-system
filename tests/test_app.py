import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from data_loader import DataError

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class AppTests(unittest.TestCase):
    def test_reader_flow(self):
        app = AppTest.from_file(str(APP_PATH)).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("link_button")), 10)
        self.assertIn("Sample data", app.caption[0].value)
        app.multiselect[0].set_value(["Technology"])
        app.button[0].click().run()
        self.assertEqual(len(app.get("link_button")), 3)
        self.assertTrue(all("Technology |" in t.value for t in app.text[::2]))
        app.multiselect[0].set_value(["Technology", "Science"])
        app.button[0].click().run()
        self.assertEqual(len(app.get("link_button")), 6)
        app.multiselect[0].set_value([])
        app.button[0].click().run()
        self.assertEqual(len(app.get("link_button")), 10)
        self.assertFalse(app.exception)

    def test_empty_data_message(self):
        with patch("data_loader.load_articles", return_value=[]):
            app = AppTest.from_file(str(APP_PATH)).run()
        self.assertEqual(app.info[0].value, "No articles available.")
        self.assertFalse(app.exception)

    def test_loading_error_message(self):
        with patch("data_loader.load_articles", side_effect=DataError("Article file is missing.")):
            app = AppTest.from_file(str(APP_PATH)).run()
        self.assertIn("missing", app.error[0].value)
        self.assertFalse(app.exception)

    def test_no_matches_message(self):
        app = AppTest.from_file(str(APP_PATH))
        app.session_state["applied_topics"] = ["Unknown"]
        app.run()
        self.assertIn("Try different topics", app.info[0].value)
        self.assertFalse(app.exception)
