"""Run with: python -m streamlit run app.py"""

import streamlit as st

from data_loader import DataError, load_articles
from recommender import recommend


def main():
    st.set_page_config(page_title="News for you", page_icon="📰")
    st.title("News for you")
    st.caption("Sample data from 2024 — not live news.")
    st.write("Choose topics to find related articles, ordered newest first.")

    try:
        articles = load_articles()
    except DataError as exc:
        st.error(str(exc))
        return
    if not articles:
        st.info("No articles available.")
        return

    topics = sorted({article["category"] for article in articles})
    with st.form("preferences"):
        selected = st.multiselect("Topics", topics, help="Leave empty to see all topics.")
        submitted = st.form_submit_button("Get recommendations")
    if submitted:
        st.session_state["applied_topics"] = selected

    applied = st.session_state.get("applied_topics", [])
    results = recommend(articles, applied)
    st.subheader("Recommended articles" if applied else "Newest articles")
    st.caption("Topics: " + (", ".join(applied) if applied else "All topics"))
    if not results:
        st.info("No matching articles. Try different topics or clear your selection.")
        return
    st.caption(f"Showing {len(results)} articles (up to 10).")
    for article in results:
        with st.container(border=True):
            st.subheader(article["title"])
            st.text(f"{article['category']} | {article['source']} | {article['published_at']}")
            st.text(article["summary"])
            st.link_button("Read original article", article["url"])


if __name__ == "__main__":
    main()
