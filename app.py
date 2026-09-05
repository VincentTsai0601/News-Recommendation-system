"""Run with: python -m streamlit run app.py"""
import streamlit as st

from data_loader import DataError, load_articles
from live_news import fetch_live_news
from recommender import recommend, publication_time


@st.cache_data(ttl=600, show_spinner=False)
def cached_news():
    return fetch_live_news()


def main():
    st.set_page_config(page_title="News for you", page_icon="📰")
    st.title("News for you")
    mode = st.radio("News source", ["Live news", "Sample data"], horizontal=True)
    if mode == "Live news":
        st.caption("English and 中文 news • Publisher RSS feeds • Original languages")
        st.caption("Results are cached for 10 minutes. Refresh to check now; this is not continuous streaming.")
        if st.button("Refresh news"):
            cached_news.clear()
        with st.spinner("Checking news feeds…"):
            articles, warnings, checked_at = cached_news()
        if articles:
            st.session_state["last_live_news"] = (articles, checked_at)
        elif "last_live_news" in st.session_state:
            articles, previous_time = st.session_state["last_live_news"]
            st.warning("Live refresh failed. Showing previously loaded news.")
            st.caption("Last successful update (UTC): " + previous_time)
        st.caption("Last checked (UTC): " + checked_at)
        for warning in warnings:
            st.warning(warning)
        if not articles:
            st.error("Live news is unavailable. Try Refresh news or choose Sample data.")
            return
    else:
        st.caption("Sample data from 2024 — not live news. English only.")
        try:
            articles = load_articles()
        except DataError as exc:
            st.error(str(exc))
            return

    if not articles:
        st.info("No articles available.")
        return
    language = st.selectbox("Language / 語言", ["All", "English", "Chinese"])
    topics = sorted({a["category"] for a in articles})
    with st.form("preferences"):
        selected = st.multiselect("Topics", topics, help="Leave empty to see all topics.")
        submitted = st.form_submit_button("Get recommendations")
    if submitted:
        st.session_state["applied_topics"] = selected
    applied = st.session_state.get("applied_topics", [])
    results = recommend(articles, applied, language)
    st.subheader("Recommended articles" if applied else "Newest articles")
    st.caption("Topics: " + (", ".join(applied) if applied else "All topics"))
    if not results:
        st.info("No matching articles. Try different topics or languages, or clear your selection.")
        return
    st.caption(f"Showing {len(results)} articles (up to 10).")
    for article in results:
        with st.container(border=True):
            st.subheader(article["title"])
            published = publication_time(article["published_at"]).strftime("%Y-%m-%d %H:%M UTC")
            st.text(f"{article['category']} | {article['source']} | {article.get('language', 'English')} | {published}")
            st.text(article["summary"])
            st.link_button("Read original article", article["url"])


if __name__ == "__main__":
    main()
