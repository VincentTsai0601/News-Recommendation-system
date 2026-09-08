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

## Alternative providers reviewed 2026-09-06

| Provider | Observed contract | Consequence for this app |
| --- | --- | --- |
| GNews | Advertises 41 languages and 71 publisher countries. Free plan: 100 requests/day, 10 results/request, 12-hour delay; presented for development/testing. Essential: EUR 49.99/month, 1,000 requests/day, 25 results/request, real-time availability. | Needs an account/key and a production plan decision. Does not establish every-country coverage. |
| NewsAPI | Developer terms exclude staging and production, including internal deployments. | The free developer plan cannot power our hosted app. Paid plan evaluation is still needed. |

Sources: [GNews pricing and coverage](https://gnews.io/),
[GNews search contract](https://docs.gnews.io/endpoints/search-endpoint),
[NewsAPI terms](https://newsapi.org/terms).

GNews `country` filters where articles were published; it does not identify the
country discussed. Its `q` parameter accepts up to 200 characters, and its
publication date filters use ISO 8601. These documented capabilities have not
been tested with an authenticated request here. No account, trial, or subscription
has been created. No key has been requested in chat.

Next decision: user preference for free-only research versus evaluating paid
providers is pending. No purchase is authorized. Meanwhile, source transparency,
country modeling, offline adapter contracts, and accessibility can proceed.

Second GDELT probe at 2026-09-06T10:05:59Z: HTTP 429 after 11.51 seconds,
no Retry-After header. No coverage data returned; integration remains pending.

## Experimental adapter

`global_search.py` now contains a bounded GDELT adapter with offline synthetic
fixtures. It is not called by app.py. It requests up to 50 results over 24 hours
with simple English keywords and an optional original-language filter. Quotes,
punctuation, and provider operators in reader input are rejected in this initial
contract. Broader query syntax and multilingual input remain future work.

Results distinguish ok, empty, rate_limited, unavailable, and invalid_response.
There are no retries. A full-size response is flagged as potentially truncated.
Unsafe/malformed article URLs are skipped, duplicate URL fragments are collapsed,
and provider-observed timestamps remain separate from unknown publication dates.
Publisher country is provider-reported; countries discussed remain unknown.

The existing recommender expects publication dates, so these records must not be
passed directly into it. Integration requires explicit observation-time display
and sorting, successful provider evidence, request caching/rate-limit handling,
and UI states that preserve the distinction between failed and empty searches.
52 offline tests passed across the project after this change; this establishes
local behavior only. No live-response or worldwide-coverage claim follows.

## Google News RSS development experiment

The public RSS search endpoint returned HTTP 200 with four entries for
`climate Taiwan when:1d` on 2026-09-06T10:22:24Z. A browser search through our
adapter for `Taiwan solar energy` on 2026-09-08T10:21:57Z returned 100 entries.
These observations support a local experiment, not a stable API contract.
`search_feed.py` and `online_search_ui.py` implement this separate path. They
retain publisher attribution, distinguish outages from empty results, bound
requests and response size, cache searches, and show Google redirect links.

The locale settings are search editions, not reliable article-language or
country labels. No country classification is inferred. No full article bodies
are fetched or republished. Endpoint support, applicable production terms,
coverage, real-device redirect behavior, and performance under load remain open.
Do not automatically promote this experiment to production based on local tests.
