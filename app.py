"""Run with: python -m streamlit run app.py"""
import streamlit as st
from html import escape
from design import render_header

from data_loader import DataError, load_articles
from coverage_summary import source_coverage
from country_catalog import coverage_inventory
from live_news import fetch_live_news, LANGUAGES
from recommender import recommend, publication_time


@st.cache_data(ttl=600, show_spinner=False)
def cached_news():
    return fetch_live_news()


def main():
    st.set_page_config(page_title="World Brief | International News", page_icon="🌐", layout="wide")
    render_header()
    mode = st.radio("News source", ["Live news", "Sample data"], horizontal=True)
    if mode == "Live news":
        st.caption("English · 中文 · Deutsch · Français · Italiano · Español — original-language news")
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
    with st.expander("Sources in this collection"):
        st.caption("This table describes loaded articles before your filters. Publisher and language do not identify the countries discussed. Worldwide coverage is not yet verified.")
        st.table(source_coverage(articles))
    with st.expander("Country coverage audit"):
        st.caption("This is our audit inventory, not a country news filter. Every entry still needs relevant article evidence. ISO country and territory codes plus an explicitly labeled Kosovo extension; names are reference labels, not a position on sovereignty.")
        st.dataframe(coverage_inventory(), hide_index=True)
    language = st.selectbox("Language / 語言", ["All", *LANGUAGES])
    st.caption("German, French, Italian and Spanish currently cover World news. Articles are not translated.")
    topics = sorted({a["category"] for a in articles})
    with st.form("preferences"):
        query = st.text_input("Search fetched news", help="Matches all words in titles and summaries of loaded articles only. No translation or wider web search.")
        selected = st.multiselect("Topics", topics, help="Leave empty to see all topics.")
        submitted = st.form_submit_button("Get recommendations")
    if submitted:
        st.session_state["applied_topics"] = selected
        st.session_state["applied_query"] = query
    applied = st.session_state.get("applied_topics", [])
    applied_query = st.session_state.get("applied_query", "")
    results = recommend(articles, applied, language, applied_query, limit=None)
    if applied_query.strip():
        st.text("Search in fetched articles: " + applied_query)
    st.subheader("Your briefing" if applied else "Across the world")
    st.caption("Topics: " + (", ".join(applied) if applied else "All topics"))
    if not results:
        st.info("No matching articles. Try different topics, languages, or search words, or clear your selection.")
        return
    # Changing the result set or filters starts a new reading sequence.
    result_context = (mode, language, tuple(applied), applied_query,
                      tuple((a["id"], a["published_at"]) for a in results))
    if st.session_state.get("result_context") != result_context:
        st.session_state["result_page"] = 1
        st.session_state["result_context"] = result_context
    total = len(results)
    pages = (total + 9) // 10
    page = st.selectbox("Results page", range(1, pages + 1), key="result_page")
    start = (page - 1) * 10
    results = results[start:start + 10]
    st.caption(f"Showing {start + 1}–{start + len(results)} of {total} matching loaded articles. Page {page} of {pages}.")
    for index, article in enumerate(results):
        if index % 2 == 0:
            columns = st.columns(2, gap="large")
        with columns[index % 2].container(border=True):
            st.markdown(f'<div class="story-tag">{escape(article["category"].upper())} &nbsp; / &nbsp; {escape(article.get("language", "English").upper())}</div>', unsafe_allow_html=True)
            st.subheader(article["title"])
            published = publication_time(article["published_at"]).strftime("%Y-%m-%d %H:%M UTC")
            st.text(f"{article['category']} | {article['source']} | {article.get('language', 'English')} | {published}")
            summary = article["summary"]
            st.text(summary if len(summary) <= 240 else summary[:240].rstrip() + "…")
            st.link_button("Read original article ↗", article["url"])
            st.caption("Opens the publisher in a new tab.")
            with st.expander("Link not opening? Copy article URL"):
                st.caption("Copy this address and paste it into Chrome or another browser. In-app browsers may handle links differently.")
                st.code(article["url"], language=None)
    st.markdown('<div class="world-footer">World / Brief &nbsp; — &nbsp; British-inspired design. Six languages. A global outlook.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
