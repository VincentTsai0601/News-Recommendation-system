# News for you

A small Streamlit app for English and Chinese news, with topic and language filters.

## Run locally

Open a terminal in the project folder. Python 3.10 or newer is required.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

On macOS/Linux, create and activate an environment with `python3 -m venv .venv`
and `source .venv/bin/activate`, then run:

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed in the terminal. Stop with Ctrl+C.
Live feeds require internet access; no API key is required.

## Read live news

- **Live news** is the default. English feeds come from BBC; Chinese feeds come
  from RTHK and use Traditional Chinese. Articles are not translated.
- Choose **All**, **English**, or **Chinese** under **Language / 語言**.
- Select topics and click **Get recommendations**. No topic selection includes all topics.
- Click **Refresh news** to fetch again immediately.
- Results are cached for 10 minutes. An interaction after cache expiry fetches again;
  leaving the page idle does not continuously poll. Publication timing depends on publishers.
- The page shows the last feed-check time in UTC, plus each article's publication time.
- Up to 10 matches appear, newest first, with ID as a stable tie-breaker.
  All languages are combined by time, without a guaranteed quota per language.

Available live topics are World, Business, Sports, Technology, and Science.
The current Chinese feeds cover World, Business, and Sports. Selecting Chinese
with Technology or Science can produce no matches; the app explains how to change filters.

## Feed failures and offline samples

A failing feed displays a warning while other feeds still load. If every feed
fails, previously loaded news from the current session is shown with its earlier
update time. On a first-load failure, use **Refresh news** or switch to **Sample data**.
An outage response is also cached for up to 10 minutes unless manually refreshed.

Sample mode uses 12 English articles from 2024 in `data/articles.json`.
It is explicitly labeled and works offline after dependencies are installed.
It is never silently presented as live news. Original links need internet access.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests use mocked feed responses, so they require no network. They cover language
and topic filters, timestamps and timezones, result limits, malformed entries,
network failures, duplicate links, caching, refresh, and the Streamlit reader flow.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Interface, cached fetches, session fallback |
| `live_news.py` | Publisher feed list, bounded downloads, RSS parsing |
| `recommender.py` | Language/topic filtering and chronological ordering |
| `data_loader.py` | Sample JSON loading and validation |
| `data/articles.json` | Offline sample articles |
| `tests/` | Unit and interface tests |
| `SPEC.md` | Original specification and live-news extension |
| `requirements.txt` | Streamlit dependency |

To add a feed, edit `FEEDS` in `live_news.py`: each entry contains publisher,
language (`English` or `Chinese`), topic, and RSS URL. Entries need a title,
HTTP(S) article link, and valid publication date with timezone.
Feeds are fetched concurrently, with a 12-second socket timeout and 2 MB limit
per response. Invalid entries are skipped; duplicate article URLs are removed.
HTML descriptions become plain text excerpts limited to 500 characters.
The app reads feed summaries, not full article pages.

To edit samples, keep a UTF-8 JSON list with unique string `id`, `title`,
`summary`, `category`, `source`, `published_at` (YYYY-MM-DD), and `url`.
All fields must be non-empty strings. The sample loader validates the format.

## Sources and limitations

Chinese feed URLs are listed on [RTHK's RSS page](https://news.rthk.hk/rthk/ch/rss.htm).
English feeds include [BBC World](https://feeds.bbci.co.uk/news/world/rss.xml)
and [BBC Technology](https://feeds.bbci.co.uk/news/technology/rss.xml).
Publisher availability and coverage can change. Some feeds redirect to HTTP.
News is near real-time, not an instant streaming service. There is no translation,
account, saved reading history, database, or machine learning model.
Preferences and the last successful live batch are session-only.
The cache is shared by app users; refreshing clears the live-news cache.
