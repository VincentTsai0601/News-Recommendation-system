"""Deterministic keyword ranking and portable result exports."""
import csv
import io
import unicodedata
from recommender import publication_time


def normalize(text):
    return unicodedata.normalize("NFKC", text).casefold()


def matches(article, query):
    terms = list(dict.fromkeys(normalize(query).split()))
    title = normalize(article.get("title", ""))
    summary = normalize(article.get("summary", ""))
    return ([term for term in terms if term in title],
            [term for term in terms if term in summary and term not in title])


def rank_articles(articles, query, order):
    """Title-match count takes priority, then summary count, date and ID."""
    def key(article):
        title, summary = matches(article, query) if order == "Most relevant" else ([], [])
        return (-len(title), -len(summary),
                -publication_time(article["published_at"]).timestamp(), article["id"])
    return sorted(articles, key=key)


def match_explanation(article, query):
    if not query.strip():
        return ""
    title, summary = matches(article, query)
    parts = []
    if title:
        parts.append("Title matches: " + ", ".join(title))
    if summary:
        parts.append("Summary matches: " + ", ".join(summary))
    return " | ".join(parts) or "No search words matched the title or summary."


def results_csv(articles):
    """Export all supplied results in order, with Excel-friendly UTF-8 BOM."""
    def safe(value):
        text = str(value)
        if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")):
            return "'" + text
        return text
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Title", "Publisher", "Published at", "Link"])
    for article in articles:
        writer.writerow([safe(article[field]) for field in ("title", "source", "published_at", "url")])
    return output.getvalue().encode("utf-8-sig")
