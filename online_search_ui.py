"""Reader-facing experiment kept separate from fixed-feed recommendations."""
import streamlit as st
from search_feed import search_feed, EDITIONS
from recommender import publication_time


@st.cache_data(ttl=600, max_entries=128, show_spinner=False)
def cached_search(query, edition):
    return search_feed(query, edition)


def render_online_search():
    st.subheader("Search news online")
    st.caption("Experimental Google News RSS search. Enter a topic and, if useful, a country name. Results may be incomplete or unrelated; country coverage is not verified.")
    with st.form("online_search"):
        query = st.text_input("What news are you looking for?", max_chars=200,
                              help="Your submitted search words are sent to Google News. Try: Taiwan solar energy.")
        edition = st.selectbox("Search edition", list(EDITIONS))
        submitted = st.form_submit_button("Search online")
    st.caption("Edition influences search results; it does not verify each article’s language or country. Cached searches may be up to 10 minutes old.")
    if submitted:
        if not query.strip():
            st.info("Enter a topic to search.")
            return
        with st.spinner("Searching news…"):
            try:
                articles, error, checked = cached_search(query.strip(), edition)
            except ValueError as exc:
                st.error(str(exc))
                return
        st.session_state["online_result"] = (query.strip(), edition, articles, error, checked)
        st.session_state["online_page"] = 1
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
    articles = sorted(articles, key=lambda a: (-publication_time(a["published_at"]).timestamp(), a["id"]))
    pages = (len(articles) + 9) // 10
    page = st.selectbox("Search results page", range(1, pages + 1), key="online_page")
    start = (page - 1) * 10
    st.caption(f"Showing {start + 1}–{min(start + 10, len(articles))} of {len(articles)} returned articles. These are not all matching articles on the web.")
    for article in articles[start:start + 10]:
        with st.container(border=True):
            st.subheader(article["title"])
            st.text(article["source"] + " | " + publication_time(article["published_at"]).strftime("%Y-%m-%d %H:%M UTC"))
            st.link_button("Open article via Google News ↗", article["url"])
            with st.expander("Link not opening? Copy article URL"):
                st.code(article["url"], language=None)
    st.caption("Links go through Google News to the publisher. Publisher access restrictions may apply.")
