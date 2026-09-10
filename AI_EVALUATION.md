# Local BGE validation — 2026-09-10

Model: BAAI/bge-reranker-v2-m3, revision
`953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`.
Downloaded weights SHA256:
`d9e3e081faff1eefb84019509b2f5558fd74c1a05a2c7db22f74174fcedb5286`.
The downloaded file matched the published hash.

Runtime: Windows, Python 3.10.9, torch 2.14.0+cpu, transformers 4.57.6.
CPU batches of four, at most four CPU threads, maximum 512 tokens per pair.
Machine has approximately 16 GB RAM; GPU was not used.

## Six hand-written learning examples

Command: `.\.venv\Scripts\python.exe benchmark_ai.py`.
Each example contrasts a relevant paraphrase with a keyword-heavy crossword
headline. Labels are hand-written expectations, not independent human judgments.

| Language | Keyword top result | BGE top result | Seconds |
| --- | --- | --- | --- |
| English | Distractor | Distractor | 93.96 |
| Chinese | Distractor | Distractor | 0.98 |
| German | Distractor | Distractor | 0.80 |
| French | Distractor | Distractor | 0.92 |
| Italian | Distractor | Distractor | 0.91 |
| Spanish | Distractor | Distractor | 0.92 |

First query includes model startup. Peak Windows process working set was
1,606.4 MiB. These are two-candidate timings, not 100-candidate latency.

Against the expected labels, top-1 accuracy was 0/6 for both methods. These
examples do not demonstrate a quality improvement. Do not change the fixtures
just to manufacture a win. Evaluate a larger, separately judged collection of
real news queries before making quality claims or adopting AI ranking by default.

## Automated checks

70 tests passed, including score ordering, non-finite score rejection, candidate
bounds, pagination reuse, explicit fallback, retry and current CSV behavior.
The AI unit tests mock model scores; real inference is separate evidence.

## Live browser pipeline

At localhost:8502, the query `Taiwan solar energy` in the English edition
retrieved 100 candidates. Selecting AI relevance reranked all 100 in **212.4
seconds**, including first use of the model in that Streamlit process.
The top displayed scores were 4.154, 4.012 and 3.958, in descending order.
The first two titles were `Tainan solar power fuels high-tech industry growth -
Taiwan News` and `J&V Energy to acquire 42 solar sites in Taiwan - Taiwan News`.

Changing to page two displayed articles 11–20 immediately and retained the same
completed ranking and 212.4-second timing. Mocked interface tests additionally
verify no inference or retrieval call occurs on paging. This single live query
was not relevance-labeled, so it verifies operation and latency, not quality.

CPU latency is too high for an assumed interactive default. Keep AI relevance
optional and measure acceleration or a smaller candidate set before deployment.
Streamlit Cloud remains unchanged and has not been tested with this model.

## Documented model sanity check

For the model-card query `what is panda?`, local inference scored `hi` at
-8.183815 and the supplied giant-panda description at 5.265040. The expected
relevant-over-unrelated ordering passed. This verifies basic model behavior;
it does not invalidate the six negative learning-example results above.
