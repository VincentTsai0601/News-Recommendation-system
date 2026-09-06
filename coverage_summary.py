"""Describe the loaded collection without claiming geographic coverage."""
from recommender import publication_time


def source_coverage(articles):
    groups = {}
    for article in articles:
        key = (article["source"], article.get("language", "English"))
        group = groups.setdefault(key, {"ids": set(), "topics": set(), "latest": None})
        group["ids"].add(article["id"])
        group["topics"].add(article["category"])
        published = publication_time(article["published_at"])
        if group["latest"] is None or published > group["latest"]:
            group["latest"] = published
    return [{"Publisher": source, "Language": language,
             "Loaded articles": len(group["ids"]),
             "Topics": ", ".join(sorted(group["topics"])),
             "Newest publication (UTC)": group["latest"].strftime("%Y-%m-%d %H:%M")}
            for (source, language), group in sorted(groups.items())]
