# Worldwide search: provider evaluation

Decision: GDELT DOC 2 is a candidate, not an enabled or verified provider.
The current application still searches its configured RSS feeds only.

## Documentation evidence

Reviewed 2026-09-06: [official DOC 2 documentation](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/).
It describes English keyword searches across machine-translated coverage in 65
languages, JSON article lists, and a maximum of 250 returned articles.
`sourcecountry` identifies the publisher country, not the country discussed.
Country names or FIPS codes belong inside `query`; ISO codes are not interchangeable.
The documentation is old; deployed behavior needs verification.

## Observed evidence

On 2026-09-06 a public `climate` query with `timespan=24h`, `maxrecords=5`,
`mode=artlist`, `format=json`, and `sort=datedesc` returned HTTP 429 after
approximately 9.4 seconds. The request used a 25-second timeout. No retry was
attempted. No article payload, freshness, or country coverage was verified.
The preceding sandbox network denial was an environment restriction and is not
counted as evidence of a provider outage. A 429 on one machine does not establish
that the service is unavailable everywhere.

## Reproduce manually

From the repository, using the project's Python environment:

```powershell
.\.venv\Scripts\python.exe tools/check_news_provider.py climate
```

The diagnostic makes one bounded public request, prints a JSON report, and does
not change app data. It reports any Retry-After header; respect it before trying
again. Do not run probes in a loop or as part of unit tests. Search terms are
sent to the provider, so use public example topics. A successful empty response
means no returned matches, not worldwide coverage or an outage.

## Acceptance gates before reader-facing integration

- Verify a real JSON response from the intended hosting environment and retain
  its observation time, response status, latency, and sample URLs.
- Confirm current use terms, attribution requirements, quotas, and any costs.
  API access does not grant republication rights to publisher article bodies.
- Keep provider observation time separate from publisher publication time;
  do not map `seendate` into `published_at` without verified semantics.
- Support timeouts, rate limits and malformed responses with clear unavailable
  states; never silently switch a failed global query to unrelated RSS results.
- Validate and encode reader input; make English query limitations visible until
  a verified multilingual query mechanism is available.
- Label publisher geography separately from countries discussed. Evaluate
  country relevance on a labeled multilingual set, including ambiguous names.
- Audit every country/territory in an explicit coverage catalog. Record missing
  coverage and sample relevance. A provider's global claim is not this audit.
- Treat the result cap as truncation. Pagination over one response cannot prove
  that every matching article has been retrieved.

## Learning exercise: evidence before integration

1. State the reader need: search topics outside the current feed collection.
2. Read the provider contract and identify fields that differ from our data model.
3. Run one small real request with a timeout and inspect the result.
4. Record both failures and uncertainties, then choose the next experiment.
5. Only after the contract is verified, implement an adapter with offline fixture
   tests and an explicit UI state for failure, empty results, and limited coverage.

This evaluation remains open. Compare another provider if reliable access cannot
be established; do not reduce the goal to the existing RSS collection.
