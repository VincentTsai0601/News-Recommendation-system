# News for you

A beginner-friendly local news recommendation app built with Python and Streamlit.
Choose topics and get up to 10 articles, newest first. The app includes 12 sample
articles from 2024 across Technology, Business, Sports, and Science. This is not
a live news feed.

## Setup and run

You need Python 3.10 or newer. Tested with Python 3.10 and Streamlit 1.63.0.
Open a terminal in this project folder.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Using the environment's Python directly avoids PowerShell activation restrictions.
If `python` is not found but the Python launcher is installed, use `py -3` for the
first command.

On macOS or Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed in the terminal (usually http://localhost:8501).
Stop the server with Ctrl+C. Installing dependencies needs internet; browsing the
bundled dataset does not. Original article links need internet access.

## Use the app

1. On first load, see the 10 newest articles across all topics.
2. Select one or more topics and click **Get recommendations**.
3. Read each article's summary, category, source, and publication date. Use
   **Read original article** to visit its source.
4. Change your topics and click the button again. Clear all topics to see all news.

Selections are held only in the current Streamlit session; nothing is saved to
disk. A fresh session starts with all topics.

## How recommendations work

An article matches if its category equals any selected topic. With no selection,
all articles match. Matches are sorted by publication date descending, then ID
ascending for equal dates, and limited to 10. Topic choices come from the dataset.
There are no relevance scores or machine learning models.

## Run tests

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

With an activated virtual environment on any platform:

```sh
python -m unittest discover -s tests
```

Tests cover filtering, ordering, ties, limits, data validation, and the Streamlit
reader flow using AppTest. No live article requests are made during tests.

## Project files

```text
app.py                    Streamlit page and session preferences
recommender.py            Topic filtering and result ordering
data_loader.py            JSON loading and validation
data/articles.json        Sample articles with source links
tests/test_recommender.py  Recommendation tests
tests/test_data_loader.py  Data validation tests
tests/test_app.py          Interface behavior tests
requirements.txt          Streamlit dependency
SPEC.md                   Original version 1 specification
```

## Replace the sample data

Edit `data/articles.json` as a UTF-8 JSON list. Each entry must have the following
non-empty string fields, without surrounding whitespace:

```json
{
  "id": "science-04",
  "title": "Your article headline",
  "summary": "Your own short summary of the article.",
  "category": "Science",
  "source": "Publisher name",
  "published_at": "2024-09-01",
  "url": "https://example.com/replace-with-a-real-article"
}
```

Use a unique ID, a real date in `YYYY-MM-DD` format, and an HTTP or HTTPS article
URL with a host. The example URL above is a placeholder: replace it with your
source. Match category spelling consistently. New categories appear automatically.
Save the file and click **Get recommendations** to reload the data. Update the
sample-data caption in `app.py` if you change the date range or content type.

Missing or malformed data displays a helpful error. Fix the indicated entry and
rerun the page. An empty list (`[]`) displays “No articles available.” An unmatched
selection displays a suggestion to change topics.

## Sample sources and limitations

The bundled titles and summaries are short paraphrases of linked reporting and
announcements from Apple Newsroom, NASA, and Associated Press. Every entry includes
its original source URL. The small collection is for demonstrating behavior and
does not represent balanced coverage; several entries concern the same company or
sport. External publishers may change links or restrict access.

Version 1 has no accounts, database, live ingestion, scraping, saved reading
history, or deployment setup. Recommendations depend only on selected categories
and dates. The loader checks URL format, not whether a remote page is reachable.
