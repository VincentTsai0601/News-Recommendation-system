# Code Review

Review date: 2026-09-13

Target: current system on `codex/dev`, commit `f8e62e3e5780899c3a21b7ef9a0a7dba2cdaa5ab`.

Verdict: **REQUEST_CHANGES**. Two major reliability issues and one minor parser protection issue were reproduced. Fixes remain outstanding.

## Scope

Read-only review of recommendation logic, online search, RSS parsing, optional AI reranking, CSV exports, UI state, documentation, and tests. Separate manual passes covered specification alignment, regressions, and security. No application code was changed during the review.

## Findings

### 1. Major: Filter controls disagree with active filters

Location: [app.py](app.py), lines 77-88.

The applied query and topics survive switching modes, but their widgets reset when the feed view is no longer rendered.

Reproduction:

1. Open Browse publisher feeds.
2. Submit query `zzzznomatch` and topic `Science`.
3. Switch to Search news, then back to Browse publisher feeds.

Observed: the query widget is empty and the topic widget shows no selection, but `applied_query` remains `zzzznomatch` and `applied_topics` remains `["Science"]`. The results still show no matches. Applied-filter captions remain visible, but the controls disagree with them.

Suggested fix: restore widgets from persistent preferences when entering the view, or reset both widget and applied state consistently. Add a mode-switch regression test.

### 2. Major: Malformed feed encoding crashes online search

Location: [search_feed.py](search_feed.py), line 39.

An XML response declaring an unknown encoding raises `LookupError`, which is not handled by the online search exception boundary. This propagates instead of returning the reader-facing unavailable message.

Reproduction: mock the HTTP response with the following content and call `search_feed("solar")`:

```xml
<?xml version="1.0" encoding="not-a-real-encoding"?><rss><channel/></rss>
```

Observed: uncaught `LookupError: unknown encoding: not-a-real-encoding`.

Suggested fix: handle unsupported encoding errors at the parser or search boundary and add a regression test that asserts a friendly failure result.

### 3. Minor: XML protection misses UTF-16 declarations

Location: [live_news.py](live_news.py), the initial checks in `parse_feed`.

The raw-byte checks for ASCII `<!DOCTYPE` and `<!ENTITY` markers do not detect UTF-16 declarations. An otherwise valid UTF-16 RSS fixture containing an internal entity passed the checks and expanded the entity into the article title.

Suggested fix: reject DTDs and entities at the parser level, independently of input encoding, and test both UTF-8 and UTF-16 fixtures.

The reproduction establishes a bypass of the intended rejection policy. It does not establish external-file access or denial of service.

## Verification

Executed from the project directory:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
git diff --check
git status --short
```

- Existing test suite: **70 tests passed**, reported runtime 26.263 seconds.
- Additional in-memory checks reproduced all three findings without changing source files or contacting live providers.
- `git diff --check` reported no whitespace errors.
- The working tree was clean at the end of the review, before this report was added.
- Streamlit emitted bare-mode context/cache warnings during tests; the suite completed successfully.

## Positive Observations

- Recommendation and ranking order is deterministic.
- CSV exports include protection against common spreadsheet formula prefixes.
- AI reranking has an explicit keyword-ranking fallback.
- Tests cover filtering, pagination, refresh behavior, outage recovery, and several AI UI flows.

## Documentation and Verification Gaps

- `SPEC.md` still describes a ten-minute cache and live-feed default, while current code and README describe session-held results and search-first startup. Reconcile the intended contract before claiming specification alignment.
- No `Plans.md` was found. Plan alignment and TDD history were not verified.
- Live provider availability, hosted CI status, actual model relevance, browser/device accessibility, Android Chrome, and LINE behavior were not verified in this review.
- No release-preflight command was run. This review is not release approval.
- No candidate findings were formally rejected. The accepted findings are the three documented above.

## Follow-up

Fix the two major issues, address the parser protection issue, add focused regression cases, and rerun the existing suite. Re-review the changed behavior and reconcile the specification before approval.
