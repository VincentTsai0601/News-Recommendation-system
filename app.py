"""Run with: python -m streamlit run app.py"""
import streamlit as st
from html import escape
from datetime import datetime, timedelta, timezone
from design import render_header
from online_search_ui import render_online_search
from result_tools import rank_articles, match_explanation, results_csv

from data_loader import DataError, load_articles
from coverage_summary import source_coverage
from country_catalog import coverage_inventory
from live_news import fetch_live_news, LANGUAGES
from recommender import recommend, publication_time, article_topics


def clear_topic_filter():
    st.session_state["applied_topics"] = []
    st.session_state["preferences_topics"] = []


def main():
    st.set_page_config(page_title="World Brief | International News", page_icon="🌐", layout="wide")
    render_header()
    mode = st.radio("News source", ["Search news", "Browse publisher feeds", "Sample data"], horizontal=True)
    if mode == "Search news":
        render_online_search()
        return
    if mode == "Browse publisher feeds":
        st.caption("English · 中文 · Deutsch · Français · Italiano · Español — original-language news")
        st.caption("Refresh news or Get recommendations fetches the feeds now. Paging and filter changes use the current session results; this is not continuous streaming.")
        st.caption("Browse our publisher collection below. Choose Search news to look beyond these feeds.")
        refresh = st.button("Refresh news")
        requested = st.session_state.pop("fetch_requested", False)
        if refresh or requested or "live_batch" not in st.session_state:
            with st.spinner("Checking news feeds…"):
                st.session_state["live_batch"] = fetch_live_news()
        articles, warnings, checked_at = st.session_state["live_batch"]
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
    period = st.selectbox("Published within", ["Any time", "Last 24 hours", "Last 7 days"], key="publication_period")
    now = datetime.now(timezone.utc)
    duration = {"Last 24 hours": timedelta(hours=24), "Last 7 days": timedelta(days=7)}.get(period)
    since = now - duration if duration else None
    until = now if duration else None
    if duration:
        st.caption("Publication window (UTC): " + since.strftime("%Y-%m-%d %H:%M") + " to " + now.strftime("%Y-%m-%d %H:%M") + ". Based on publisher timestamps; evaluated when the page updates.")
    topics = sorted({topic for a in articles for topic in article_topics(a)})
    with st.form("preferences"):
        query = st.text_input("Search fetched news", help="Matches all words in titles and summaries of loaded articles only. No translation or wider web search.")
        selected = st.multiselect("Topics", topics, key="preferences_topics", help="Leave empty to see all topics.")
        submitted = st.form_submit_button("Get recommendations")
    if submitted:
        st.session_state["applied_topics"] = selected
        st.session_state["applied_query"] = query
        if mode == "Browse publisher feeds":
            st.session_state["fetch_requested"] = True
            st.rerun()
    applied = st.session_state.get("applied_topics", [])
    applied_query = st.session_state.get("applied_query", "")
    available_topics = sorted({topic for article in articles
                              if language == "All" or article.get("language", "English") == language
                              for topic in article_topics(article)})
    if applied and available_topics and not set(applied).intersection(available_topics):
        st.warning(f"{language} articles in this collection provide: {', '.join(available_topics)}. Your topic filter excludes these articles.")
        st.button("Show available topics", on_click=clear_topic_filter)
    results = recommend(articles, applied, language, applied_query, limit=None, since=since, until=until)
    if applied_query.strip():
        st.text("Search in fetched articles: " + applied_query)
    st.subheader("Your briefing" if applied else "Across the world")
    st.caption("Topics: " + (", ".join(applied) if applied else "All topics"))
    if not results:
        st.info("No matching articles. Try a wider publication window, different topics, languages, or search words, or clear your selection.")
        return
    order = st.selectbox("Sort results", ["Newest", "Most relevant"], key="feed_sort")
    results = rank_articles(results, applied_query, order)
    st.caption("Most relevant prioritizes search words in titles, then summaries; ties use newest first. With no search words, results use newest first.")
    st.download_button("Download results CSV", results_csv(results), "news-results.csv",
                       mime="text/csv", on_click="ignore", key="feed_csv")
    st.caption("CSV includes all matching results across pages, in the selected order.")
    # Changing the result set or filters starts a new reading sequence.
    result_context = (mode, language, period, tuple(applied), applied_query, order,
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
            topic_label = ", ".join(article_topics(article))
            st.markdown(f'<div class="story-tag">{escape(topic_label.upper())} &nbsp; / &nbsp; {escape(article.get("language", "English").upper())}</div>', unsafe_allow_html=True)
            st.subheader(article["title"])
            published = publication_time(article["published_at"]).strftime("%Y-%m-%d %H:%M UTC")
            st.text(f"{topic_label} | {article['source']} | {article.get('language', 'English')} | {published}")
            summary = article["summary"]
            st.text(summary if len(summary) <= 240 else summary[:240].rstrip() + "…")
            if applied_query.strip():
                st.caption(match_explanation(article, applied_query))
            st.link_button("Read original article ↗", article["url"])
            st.caption("Opens the publisher in a new tab.")
            with st.expander("Link not opening? Copy article URL"):
                st.caption("Copy this address and paste it into Chrome or another browser. In-app browsers may handle links differently.")
                st.code(article["url"], language=None)
    st.markdown('<div class="world-footer">World / Brief &nbsp; — &nbsp; British-inspired design. Six languages. A global outlook.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
