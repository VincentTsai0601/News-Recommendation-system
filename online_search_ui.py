"""Reader-facing experiment kept separate from fixed-feed recommendations."""
import streamlit as st
from time import perf_counter
from ai_reranker import rerank, RerankError
from search_feed import search_feed, EDITIONS
from recommender import publication_time
from result_tools import rank_articles, match_explanation, results_csv


def render_online_search():
    st.subheader("Search news online")
    st.caption("Experimental Google News RSS search. Enter a topic and, if useful, a country name. Results may be incomplete or unrelated; country coverage is not verified.")
    with st.form("online_search"):
        query = st.text_input("What news are you looking for?", max_chars=200,
                              help="Your submitted search words are sent to Google News. Try: Taiwan solar energy.")
        edition = st.selectbox("Search edition", list(EDITIONS))
        submitted = st.form_submit_button("Search online")
    st.caption("Edition influences search results; it does not verify each article’s language or country. Each Search online click makes a fresh request. Results stay in this session while you browse.")
    if submitted:
        if not query.strip():
            st.info("Enter a topic to search.")
            return
        with st.spinner("Searching news…"):
            try:
                articles, error, checked = search_feed(query.strip(), edition)
            except ValueError as exc:
                st.error(str(exc))
                return
        st.session_state["online_result"] = (query.strip(), edition, articles, error, checked)
        st.session_state["online_page"] = 1
        st.session_state.pop("ai_result", None)
    if "online_result" not in st.session_state:
        return
    applied_query, applied_edition, articles, error, checked = st.session_state["online_result"]
    st.text(f"Results for: {applied_query} | Edition: {applied_edition}")
    st.caption("Fetched (UTC): " + checked)
    if error:
        st.error(error)
        return
    if not articles:
        st.info("No results returned. Try different words or another edition. This does not mean no news exists.")
        return
    order = st.selectbox("Sort results", ["Newest", "Most relevant", "AI relevance"], key="online_sort")
    if order == "AI relevance":
        ai_key = (applied_query, applied_edition, checked,
                  tuple((a["id"], a["title"], a.get("summary", ""), a["published_at"]) for a in articles))
        saved = st.session_state.get("ai_result")
        retry = bool(saved and saved[0] == ai_key and saved[2]) and st.button("Retry AI reranking")
        if not saved or saved[0] != ai_key or retry:
            started = perf_counter()
            with st.spinner("AI is comparing your query with each article. The first run may take longer…"):
                try:
                    ranked, failure = rerank(applied_query, articles), None
                except RerankError as exc:
                    ranked, failure = [], str(exc)
            saved = (ai_key, ranked, failure, perf_counter() - started)
            st.session_state["ai_result"] = saved
        if saved[2]:
            st.warning(saved[2])
            articles = rank_articles(articles, applied_query, "Most relevant")
        else:
            articles = saved[1]
            st.caption(f"AI reranked {len(articles)} candidates in {saved[3]:.1f} seconds using BGE-reranker-v2-m3. Higher scores indicate stronger model relevance, not confidence or factual accuracy.")
    else:
        articles = rank_articles(articles, applied_query, order)
    st.caption("Most relevant prioritizes search words in titles, then summaries; ties use newest first. This ranks the returned results only.")
    context = (applied_query, applied_edition, checked, order,
               tuple(a["id"] for a in articles))
    if st.session_state.get("online_order_context") != context:
        st.session_state["online_page"] = 1
        st.session_state["online_order_context"] = context
    st.download_button("Download results CSV", results_csv(articles), "news-search-results.csv",
                       mime="text/csv", on_click="ignore", key="online_csv")
    st.caption("CSV includes all returned results across pages, in the selected order.")
    pages = (len(articles) + 9) // 10
    page = st.selectbox("Search results page", range(1, pages + 1), key="online_page")
    start = (page - 1) * 10
    st.caption(f"Showing {start + 1}–{min(start + 10, len(articles))} of {len(articles)} returned articles. These are not all matching articles on the web.")
    for article in articles[start:start + 10]:
        with st.container(border=True):
            st.subheader(article["title"])
            st.text(article["source"] + " | " + publication_time(article["published_at"]).strftime("%Y-%m-%d %H:%M UTC"))
            if "ai_score" in article:
                st.caption(f"AI relevance score: {article['ai_score']:.3f}")
            st.caption("Keyword matches (separate from AI scoring): " + match_explanation(article, applied_query))
            st.link_button("Open article via Google News ↗", article["url"])
            with st.expander("Link not opening? Copy article URL"):
                st.code(article["url"], language=None)
    st.caption("Links go through Google News to the publisher. Publisher access restrictions may apply.")
