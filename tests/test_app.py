import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from data_loader import load_articles

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class AppTests(unittest.TestCase):
    def setUp(self):
        import streamlit as st
        st.cache_data.clear()
        self.articles = load_articles()
        self.articles[0] = dict(self.articles[0], language="Chinese", title="中文新聞")
        self.mock = patch("live_news.fetch_live_news", return_value=(self.articles, [], "2026-09-05T00:00:00+00:00"))
        self.fetch = self.mock.start()
        self.addCleanup(self.mock.stop)
        self.addCleanup(st.cache_data.clear)

    def test_reader_flow_and_language(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("link_button")), 10)
        app.selectbox[0].set_value("Chinese").run()
        self.assertEqual(len(app.get("link_button")), 1)
        self.assertIn("中文新聞", [s.value for s in app.subheader])
        app.selectbox[0].set_value("English").run()
        self.assertNotIn("中文新聞", [s.value for s in app.subheader])
        app.multiselect[0].set_value(["Science"])
        app.button[1].click().run()
        self.assertEqual(len(app.get("link_button")), 3)
        self.assertFalse(app.exception)

    def test_refresh_bypasses_cache(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run()
        calls = self.fetch.call_count
        app.selectbox[0].set_value("Chinese").run()
        self.assertEqual(self.fetch.call_count, calls)
        app.button[0].click().run()
        self.assertEqual(self.fetch.call_count, calls + 1)

    def test_total_failure_then_sample_mode(self):
        self.fetch.return_value = ([], ["Feed unavailable"], "now")
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run()
        self.assertIn("unavailable", app.error[0].value)
        app.radio[0].set_value("Sample data").run()
        self.assertEqual(len(app.get("link_button")), 10)
        self.assertFalse(app.exception)

    def test_last_good_results_retained(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run()
        self.fetch.return_value = ([], ["Feed unavailable"], "later")
        app.button[0].click().run()
        self.assertEqual(len(app.get("link_button")), 10)
        self.assertIn("previously loaded", app.warning[0].value)

    def test_empty_sample_data(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run()
        with patch("data_loader.load_articles", return_value=[]):
            app.radio[0].set_value("Sample data").run()
        self.assertEqual(app.info[0].value, "No articles available.")

    def test_no_matches(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run()
        app.selectbox[0].set_value("Chinese").run()
        app.multiselect[0].set_value(["Science"])
        app.button[1].click().run()
        self.assertIn("No matching articles", app.info[0].value)

    def test_each_added_language_filters_articles(self):
        languages = {"German": "Grüße aus Berlin", "French": "Actualités françaises",
                     "Italian": "Novità dall’Italia", "Spanish": "Noticias de España"}
        for language, title in languages.items():
            self.articles.append(dict(self.articles[0], id=language, language=language,
                                      title=title, category="World",
                                      url="https://example.com/" + language))
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run()
        for language, title in languages.items():
            with self.subTest(language=language):
                app.selectbox[0].set_value(language).run()
                self.assertFalse(app.exception)
                self.assertEqual(len(app.get("link_button")), 1)
                self.assertIn(title, [s.value for s in app.subheader])
        app.radio[0].set_value("Sample data").run()
        self.assertIn("No matching articles", app.info[0].value)

    def test_article_links_use_current_tab_and_escape_url(self):
        from html.parser import HTMLParser

        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.links = []

            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    attributes = dict(attrs)
                    if attributes.get("class") == "article-open":
                        self.links.append(attributes)

        url = 'https://example.com/article?a=1&title="news"'
        self.articles[0] = dict(self.articles[0], url=url)
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run()
        app.selectbox[0].set_value("Chinese").run()
        parser = Links()
        for block in app.markdown:
            parser.feed(block.value)
        self.assertEqual(len(parser.links), 1)
        self.assertEqual(parser.links[0]["target"], "_top")
        self.assertEqual(parser.links[0]["href"], url)
        self.assertNotIn("onclick", parser.links[0])
        self.assertFalse(app.exception)
