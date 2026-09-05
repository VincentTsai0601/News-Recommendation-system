# News Recommendation System — Version 1

## Goal and assumptions

Build a small local application that helps a reader find news matching their
interests. Keep the code easy for a beginner to understand and extend.

Earlier product requirements were not available in the conversation or repository.
The scope below is a proposal, not a record of confirmed requirements. This file
specifies future work only; no application is implemented at this stage.

## First-version scope

- Show a list of news articles from a bundled sample JSON file.
- Let the reader select one or more topics, such as Technology, Business, Sports,
  and Science, then request recommendations.
- Show up to 10 matching articles, newest first.
- Show each article's title, short summary, category, source, publication date,
  and a link to the original article.
- When no topics are selected, show the 10 newest articles across all categories.
- When no articles match, show a friendly message suggesting different topics.
- Allow the reader to change topics and refresh the recommendations.

No accounts, database, live news API, scraping, machine learning, reading-history
tracking, or deployment are required for version 1. Preferences last only for the
current session. Clearly label the bundled content as sample data, not live news.

## Proposed approach

Use Python and Streamlit for a single-page interface. Store sample articles in
JSON and keep recommendation logic in a separate Python module. Use Python's
`unittest` for small tests of the recommendation behavior.

The recommendation rule is intentionally simple: include an article if its category
matches any selected topic. Sort results by publication date descending, with
article ID ascending as a stable tie-breaker, then return at most 10. If no topics
are selected, skip the category filter. Derive available topics from the dataset.

### Article data

Each article has these required fields:

| Field | Meaning |
| --- | --- |
| `id` | Unique string identifier |
| `title` | Headline |
| `summary` | Short plain-text description |
| `category` | One topic label |
| `source` | Publisher name |
| `published_at` | Date in `YYYY-MM-DD` format |
| `url` | HTTP or HTTPS link to the original article |

Bundle at least 12 sample articles across the four example categories. Use short,
original summaries and real article links. Validate required fields, unique IDs,
dates, and URL schemes when loading data. If the file is missing or invalid, show
a clear error instead of an unhandled traceback. An empty dataset should show
“No articles available.”

## Proposed file structure

```text
News-Recommendation-system/
├── SPEC.md                  # This specification
├── README.md                # Setup, run instructions, and limitations
├── requirements.txt         # Application dependencies
├── app.py                   # Streamlit page and user interactions
├── recommender.py           # Topic filtering and ordering
├── data_loader.py           # JSON loading and validation
├── data/
│   └── articles.json        # Bundled sample articles
└── tests/
    ├── test_recommender.py  # Recommendation behavior
    └── test_data_loader.py  # Valid and invalid input handling
```

These files are planned; only `SPEC.md` is created now.

## Implementation stages

1. **Prepare the project and data.** Add dependencies, sample articles, the data
   loader, and setup instructions. Verify valid data loads and invalid data
   produces an understandable error.
2. **Build the recommendation logic.** Implement topic matching, date sorting,
   stable tie-breaking, and the 10-result limit. Check these rules with unit tests.
3. **Build the interface.** Add topic selection, a recommendation button, article
   cards, and loading-error and empty-result messages. Check the full reader flow.
4. **Verify and document.** Run tests, manually check the page, and document how to
   install dependencies, start the app, and replace sample data.

## Acceptance criteria

- A beginner can follow the README to install dependencies with
  `python -m pip install -r requirements.txt` and launch with
  `python -m streamlit run app.py`.
- The application works with bundled data without API keys or a network connection
  after dependency installation; opening original article links requires internet.
- Selecting Technology returns only Technology articles; selecting Technology and
  Science returns articles from either category without duplicates.
- No topic selection returns the newest articles across all categories.
- Every result list contains at most 10 articles, ordered newest first; equal dates
  use the documented ID tie-breaker.
- Each result displays all specified reader-facing fields and a working link.
- Changing topic selections and requesting recommendations updates the results.
- No matches, empty data, and missing or malformed data produce the specified
  helpful messages rather than an unhandled traceback.
- Automated tests cover topic filtering, multiple topics, no selection, no matches,
  ordering, ties, the result limit, and data validation. They pass with
  `python -m unittest discover -s tests`.
- The interface identifies the articles as sample data, and the README explains
  the category-based recommendation rule and version 1 limitations.

## Live-news extension (September 2026)

The requested next version adds English and Chinese publisher RSS feeds.
Live mode is the default; offline English samples remain an explicit option.
Keep the first version's simple filtering and ten-result limit.

Acceptance criteria for this extension:
- Language choices are All, English, and Chinese; original language is preserved.
- Fetch BBC English feeds and RTHK Traditional Chinese feeds without API keys.
- Cache for ten minutes and provide a manual Refresh news button that bypasses it.
- Show UTC fetch time and timezone-normalized article publication times.
- Sort by full timestamp, then ID, and remove duplicate article URLs.
- A feed failure does not prevent other feeds from loading.
- If all feeds fail, retain the current session's previous successful batch,
  clearly mark it as previous news, and show its earlier update time.
- If no prior batch exists, offer retry or explicit Sample data mode.
- Test parsing, language/topic combinations, intraday sorting, deduplication,
  partial/total failures, cache reuse, and manual refresh without real network calls.
- Document publisher-dependent delays and the absence of continuous polling.
