# Country coverage audit

The inventory uses pycountry 26.2.16 (249 ISO 3166-1 country/territory entries)
plus Kosovo under the explicitly labeled application extension XK. Reference:
[pycountry project and data policy](https://github.com/pycountry/pycountry).
The package wraps Debian ISO data and is distributed under LGPL-2.1.
Names/codes are reference identifiers, not sovereignty judgments. Additional
reader-requested regions can be modeled separately; this list is not a claim
that every geographic identity is represented.

All 250 entries currently show **Not verified**. The app's country coverage
expander is an audit inventory, not an article filter. No news is classified by
country yet. Do not infer country from a language, a publisher, or a dropdown.

## Evidence required for each entry

Record provider, public query, retrieval time in UTC, original article URL,
publication time when supplied, article language, and reviewer notes confirming
relevance to that country. Distinguish publisher country from country discussed.
Include ambiguous names (Georgia, Congo), cross-border stories, and languages
other than English. A title mention alone is insufficient when meaning is unclear.
Record outages, empty responses, relevance failures, and untested entries
separately. Old observations must not become permanent live-coverage claims.

A passing adapter test proves parsing/filter logic, not provider coverage. A
successful article retrieval establishes an observation, not exhaustive coverage
of all topics. Repeat representative topic queries and track missing results
before claiming the full reader goal is met.

## Beginner development exercise

1. Inventory the scope before implementing a country filter.
2. Pin the reference dependency so local and CI catalogs agree.
3. Test unique identifiers and keep non-ISO extensions explicit.
4. Display unverified status until real evidence exists.
5. Next, add provider observations and review country relevance before connecting
   the inventory to search filters.
