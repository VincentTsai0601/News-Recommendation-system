# Goal: worldwide live news and an understandable AI development process

## Full objective

Let everyone discover live news about the information they want from every country,
while teaching a repeatable process for developing the app with an AI agent.
A six-language feed reader is a starting point, not completion of this goal.

## Evidence at the start

- British-style Streamlit interface; twelve RSS feeds; six original languages.
- Ten-result chronological recommendations with topic and language filters.
- Ten-minute cache and manual refresh; no continuous streaming.
- No country model, country filter, cross-source query service, or coverage audit.
- Production retains a known same-tab article-navigation failure after a requested rollback.
- Automated tests do not establish Android or LINE compatibility.

## Deliverables and proof required

| Work | Acceptance evidence | Status |
| --- | --- | --- |
| Development workflow | Development branch, reviewed PRs, passing CI, separate preview, documented release/rollback | In progress |
| Reader interests | Free-text interests combined with filters; meaningful empty states; no claim to search beyond available sources | Local keyword search added on development |
| Country coverage | Explicit country/territory catalog, coverage by source and language, honest unavailable states | Not implemented |
| Geographic meaning | Separate publisher location from countries discussed; test against labeled articles | Not implemented |
| Broad live discovery | Query-capable providers or indexed ingestion, publisher attribution, rights/limits evaluated, freshness measured | Not implemented |
| All countries | Country-by-country evidence of retrievable relevant news; no unavailable country silently treated as supported | Not verified |
| Reading access | Working original links on desktop, Android Chrome, and actual LINE; accessible fallback | Known production issue; device checks pending |
| Inclusive access | Responsive layout, keyboard and screen-reader checks, legible contrast, language labeling | Partially implemented; audit pending |
| Reliability | Bounded requests, deduplication, outage/stale messaging, reproducible tests and operational visibility | Basic feed handling only |
| Learning | Beginner guide plus change-by-change examples, review and release exercises | Guide added; exercises ongoing |

## Implementation sequence

1. Establish development/production separation, CI, preview and release gates.
   Add search within fetched articles as a small end-to-end learning exercise.
2. Repair article navigation on preview and verify on a real phone before release.
3. Define country metadata and build a coverage catalog. Do not infer country from
   article language. Establish a coverage test dataset.
4. Evaluate query-capable news services and publisher ingestion for global discovery.
   Compare supported countries, languages, freshness, quotas, cost, and permitted use.
   Do not purchase subscriptions or claim universal coverage without evidence.
5. Implement combined country, language, topic, and keyword queries; pagination;
   transparent source coverage; unavailable and stale states.
6. Add multilingual interface/accessibility and broader device checks, then release
   incrementally with measured coverage and failure reporting.

## Current search scope

The first development search checks the title and summary of already-fetched
articles. It matches all whitespace-separated terms, ignores case, and normalizes
Unicode compatibility forms. It neither translates nor fetches additional news.
This is not yet worldwide search. The ten-result cap remains.
