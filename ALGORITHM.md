# Retrieval and reranking in World Brief

## Follow one query

For `Taiwan solar energy`:

1. `search_feed.py` sends the query and chosen edition to Google News RSS.
   It parses at most 100 feed entries and removes duplicate article IDs.
   This produces the candidate collection C. Its size may be less than 100.
2. `online_search_ui.py` keeps that collection in your current session.
   Choosing **AI relevance** passes the submitted query and candidates to
   `ai_reranker.rerank`.
3. `score_pairs` builds one pair per article: `(query, title + summary)`.
   BGE-reranker-v2-m3 jointly reads each pair (a cross-encoder) and emits a
   raw relevance score. Text is capped at 512 model tokens, with four pairs
   per CPU batch. This is inference using pretrained weights; no training
   happens in the app.
4. `rerank` sorts descending by model score. Equal scores use publication
   time, newest first, and then article ID for deterministic order.
5. The interface displays ten per page. CSV includes the entire current
   ranking. Page changes reuse scores; a new search retrieves fresh news.

In symbols: `score_i = BGE(query, title_i + summary_i)` and
`ranked = sort(C, by=score_i descending)`.

## Compare the three sort options

| Option | Ranking signal | What it cannot do |
| --- | --- | --- |
| Newest | Publication time | Measure relevance |
| Most relevant | Distinct title keyword matches, then summary-only matches | Understand paraphrases beyond literal substrings |
| AI relevance | Learned query/article relationship | Find articles absent from the retrieved candidates or verify facts |

AI relevance is currently available in **Search news**. Publisher-feed browsing
retains its existing language/topic/time/keyword filters and simpler sorting.
The chosen search edition influences retrieval; the app does not assert every
candidate is in that language or about that country. Multilingual model support
also does not guarantee equal quality across languages.

## What scores mean

A larger raw score means the model prefers that query/article pair. It is not a
percentage probability, a quality rating, or factual confidence. The visible
keyword-match caption is a separate literal-match check; it does not explain
why the neural model assigned its score.

## Evaluate before replacing your baseline

Run `benchmark_ai.py` after downloading the model. Six hand-written examples
compare a relevant paraphrase with a keyword-heavy distractor. The output records
which ranks first and elapsed time; the first example includes model loading.
These deliberately simple examples show behavior, not production quality.

Next, collect 20 real queries across your languages. For each, save the exact
candidate collection and independently mark relevant articles before examining
rankings. Compare the same candidates under keyword and AI ranking using
precision@10 (relevant articles among the first ten) or graded nDCG@10. Include
queries where keyword ranking already works, not only difficult paraphrases.
Measure retrieval time separately from reranking time and report cold and warm
runs, memory, and sample size. Candidate recall requires a broader judged pool;
reordering a weak candidate set cannot repair missing coverage.

## Files to read

- `search_feed.py`: live retrieval and parsing.
- `ai_reranker.py`: pinned model loading, batching, scores, validation and sorting.
- `online_search_ui.py`: pipeline, session reuse and explicit fallback.
- `result_tools.py`: keyword baseline and CSV serialization.
- `benchmark_ai.py`: small multilingual learning experiment.
- `tests/test_ai_reranker.py`: deterministic unit tests using mocked scores.
- `tests/test_ai_search_ui.py`: inference reuse, errors and retry behavior.

Unit tests prove control flow, not semantic quality. Real model runs and judged
examples provide separate evidence. Later cloud deployment needs its own model
provisioning and resource checks; local files on D: are not part of Git.
