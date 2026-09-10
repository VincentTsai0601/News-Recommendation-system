# News for you

A British newspaper-inspired Streamlit app with news in six languages, topic filters, and live refresh.

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

## Start with a search

The app opens on **Search news**. Enter a topic, choose an edition, and press
**Search online** to fetch results immediately. Opening the app alone does not
request news. **Browse publisher feeds** filters our fixed publisher collection;
**Sample data** lets you explore offline examples.

## Read live news

- Choose **Browse publisher feeds** for the curated live collection. English feeds come from BBC; Chinese feeds come
  from RTHK and use Traditional Chinese. Articles are not translated.
- Choose **All**, **English**, **Chinese**, **German**, **French**, **Italian**, or **Spanish** under **Language / 語言**.
- Select topics and click **Get recommendations**. No topic selection includes all topics.
- Click **Refresh news** to fetch again immediately.
- Every **Get recommendations** and **Refresh news** click makes a fresh feed request.
  Browsing pages uses the current session results. Idle pages do not continuously poll.
- The page shows the last feed-check time in UTC, plus each article's publication time.
- Up to 10 matches appear, newest first, with ID as a stable tie-breaker.
  All languages are combined by time, without a guaranteed quota per language.

Available live topics are World, Business, Sports, Technology, and Science.
The current Chinese feeds cover World, Business, and Sports. Selecting Chinese
with Technology or Science can produce no matches. If selected topics exclude all
loaded topics for your language, the app explains why. **Show available topics**
clears the topic filter while keeping your language, search words, and date window.

## Feed failures and offline samples

A failing feed displays a warning while other feeds still load. If every feed
fails, previously loaded news from the current session is shown with its earlier
update time. On a first-load failure, use **Refresh news** or switch to **Sample data**.
Click Refresh news or Get recommendations to retry an outage immediately.

Sample mode uses 12 English articles from 2024 in `data/articles.json`.
It is explicitly labeled and works offline after dependencies are installed.
It is never silently presented as live news. Original links need internet access.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests use mocked feed responses, so they require no network. They cover language
and topic filters, timestamps and timezones, result limits, malformed entries,
network failures, duplicate links, fresh submissions, refresh, and the Streamlit reader flow.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Interface, fresh fetches, session fallback |
| `live_news.py` | Publisher feed list, bounded downloads, RSS parsing |
| `recommender.py` | Language/topic filtering and chronological ordering |
| `data_loader.py` | Sample JSON loading and validation |
| `data/articles.json` | Offline sample articles |
| `tests/` | Unit and interface tests |
| `SPEC.md` | Original specification and live-news extension |
| `requirements.txt` | Streamlit dependency |

To add a feed, edit `FEEDS` in `live_news.py`: each entry contains publisher,
language (one of the six names in `LANGUAGES`), topic, and RSS URL. Entries need a title,
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
account, saved reading history, or database. Optional local AI reranking is described below.
Preferences and the last successful live batch are session-only.
No shared response cache is used. Results remain in session memory for paging.

## British edition and additional languages

The design uses cream reading panels, navy and red accents, serif headlines, and
the supplied British wall image. The artwork is bundled locally, with no remote
image or font downloads. Theme settings live in `.streamlit/config.toml`;
the responsive presentation lives in `design.py`.

| Language | Live publisher | Initial topic |
| --- | --- | --- |
| German | [DW](https://rss.dw.com/xml/rss-de-all) | World |
| French | [France 24](https://www.france24.com/fr/rss) | World |
| Italian | [ANSA](https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml) | World |
| Spanish | [BBC Mundo](https://feeds.bbci.co.uk/mundo/rss.xml) | World |

These four feeds complement the existing English and Traditional Chinese feeds.
Language support means reading original-language articles, not translating the
interface or news. Other topics may have no matches in the new languages.
Samples remain English-only. Feed failures and session
fallback behavior remain the same.

## Opening articles on phones

On the development branch, **Read original article** opens the publisher in a
new tab. If nothing opens, expand **Link not opening? Copy article URL** and
paste the address into Chrome or another browser. Publisher login, subscription,
and regional restrictions may still apply.

Local desktop browser navigation and the visible URL fallback were checked on
2026-09-06. Actual Android Chrome, LINE, and hosted-preview checks remain pending.

## Development and the worldwide-news goal

See [DEVELOPMENT.md](DEVELOPMENT.md) for the AI-assisted development workflow and
[ROADMAP.md](ROADMAP.md) for requirements, evidence, and unfinished work.
Development happens on codex/dev; master remains the production branch.
Search fetched news matches all entered words across titles and summaries,
ignoring case and normalizing Unicode. It does not search beyond fetched feeds.

Known production limitation: the restored same-tab article link is blocked by
Streamlit Cloud's frame restrictions. The development repair has not been released. Hosted-preview and real-device
verification are required before release. Android and LINE are not yet verified.

### Browsing development results

Use **Results page** to reach all matching loaded articles, ten per page.
Filters and changed refresh results return you to page one. The count describes
loaded articles, not every article on the internet.

Open **Sources in this collection** to see loaded publishers, languages, topics,
article counts, and newest publication times before filtering. This table does
not measure countries discussed or prove worldwide coverage.

### Publication-time filtering

Choose **Published within**: Any time, Last 24 hours, or Last 7 days. Recent
windows use publisher timestamps and exclude future-dated articles. The window
is evaluated when the page updates; it does not continuously advance while idle.
This combines with language, topics, and search. It filters the loaded collection
and cannot retrieve missing news. Sample articles from 2024 will normally have
no matches in a recent window; choose Any time to explore them.

When the same article appears in several feeds, it is shown once and retains
all those feed topics. Selecting any of those topics can find it. These labels
come from the feeds, not from automatic analysis of the article text.

## Online search (development preview)

**Search news** is the starting screen. Enter a topic (optionally including a
country name), select an edition, and press **Search online**. This requests
Google News RSS results beyond our fixed publisher feeds. Every search submission makes a new request; results are displayed in pages of ten, up to the first 100
valid feed entries. The edition influences retrieval; it does not verify article
language, country relevance, or worldwide coverage. Results can include older
stories; read the publication date. Query terms are sent to Google News.

Links use Google News redirects. Use the URL-copy fallback if a browser cannot
open a link. No API key is required by the observed RSS endpoint. This is an
experimental, undocumented integration with no availability guarantee; production
use and provider terms still need review before release.

Verified 2026-09-08: 58 local tests passed, and a real browser search for
Taiwan solar energy returned 100 articles. This is a single-query observation,
not a country coverage audit. Hosted preview, actual Android/LINE checks, and
remote CI remain release gates. master has not been changed.

### British wall background

The development theme uses the user-supplied VLLM.jpg reference, stored locally as
`assets/british-wall.jpg`, with wood, London landmarks, and Union Jack details.
Cream reading panels and navy/red accents keep the text legible. The image is
embedded from the local asset, so deployment does not need access to Downloads
or an external image host. Narrow layouts use a stronger overlay behind text.

## Sorting, match explanations, and CSV export

Both search and publisher-feed results offer **Newest** and **Most relevant**.
Newest remains the default. Most relevant compares the number of distinct search
words found in the title first, then words found only in the summary. Ties use
publication date (newest first), then article ID. Without search words it behaves
like Newest. Matching ignores case and normalizes Unicode; it uses substring
matching, not semantic understanding or translation.

Each result explains title and summary matches for the submitted search. Online
results without literal matches stay visible and are labeled accordingly. This
ranking only reorders the returned collection; feed filters still apply.
Changing sort resets pagination to page one without fetching again.

**Download results CSV** exports all current matching results across pages in
selected order, with Title, Publisher, Published at, and Link columns. Dates retain
the supplied timestamp format. Online links retain Google News redirects. UTF-8
with a BOM preserves Chinese and European characters in Excel. Potential formula
cells receive a leading apostrophe so article text is treated as text.

These features take inspiration from the discovery and export features described
in [Smart News Recommendation System](https://github.com/raiigauravv/Smart-News-Recommendation-System).
The implementation is local to this app and does not require that project's models,
datasets, accounts, or cloud services.

## Local retrieval and AI reranking

Pipeline: query → up to 100 Google News RSS candidates → local BGE cross-encoder
→ ranked results. In **Search news**, submit your query and select **AI relevance**.
The model compares the query with each title and available summary, capped at
512 tokens per pair. It does not fetch or read full publisher articles. Retrieval
still determines which articles can be ranked; a selected edition does not prove
language or country coverage.

Local setup in PowerShell (model files stay under the project on D:):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ai.txt
.\.venv\Scripts\python.exe ai_reranker.py
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502 --server.address 127.0.0.1
```

The setup command downloads the pinned Apache-2.0 BAAI/bge-reranker-v2-m3 model
from Hugging Face into `.models/`, excluded from Git. Normal app requests only
load local model files. CPU inference uses batches of four, at most four CPU
threads, and serializes model access between sessions. The model stays in memory;
ranking results stay in the reader's session for pagination and sorting. Each
new search fetches fresh candidates and invalidates the previous AI ranking.

Higher raw AI scores indicate model relevance; they are not probabilities or
fact-checking confidence. Keyword-match captions are separate lexical information,
not explanations of the neural model. Failure shows an explicit warning and
keyword-ranked results; **Retry AI reranking** retries without fetching again.
CSV exports retain the current ranking across all pages.

`requirements-ai.txt` is optional so the basic app still runs without PyTorch.
Streamlit Community Cloud deployment is a separate step: the machine hosting
Streamlit must have enough RAM and CPU, install these dependencies and provision
the model. Your local D: cache does not transfer automatically. Benchmark first;
a separately hosted reranking service is an alternative for constrained hosting.

To inspect the algorithm with six hand-written language examples, run:

```powershell
.\.venv\Scripts\python.exe benchmark_ai.py
```

This prints keyword versus AI top-ranked IDs, per-query elapsed time (the first
includes model loading), and peak process memory on Windows. The examples are
small learning checks, not proof of improvement on real-world news. For a stronger
evaluation, label a separate set of realistic queries and candidate articles,
compare nDCG@10 or precision@10, and measure end-to-end search latency.

On this Windows machine, Anaconda bundled MSVC 14.27 while the installed system
runtime is 14.50. Loading the older DLLs caused PyTorch WinError 1114. The local
adapter loads the installed system runtime into its own process before importing
PyTorch; it does not replace system or Anaconda files.

See [ALGORITHM.md](ALGORITHM.md) for a code walkthrough and
[AI_EVALUATION.md](AI_EVALUATION.md) for measured results, including limitations.
The first local 100-candidate browser run took 212.4 seconds on CPU. AI relevance
remains optional; do not assume this latency is acceptable for hosted deployment.
