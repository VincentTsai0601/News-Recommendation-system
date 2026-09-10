"""Optional local BGE cross-encoder; no model download during app requests."""
from functools import lru_cache
from pathlib import Path
from threading import Lock
import math
from recommender import publication_time

MODEL_ID = "BAAI/bge-reranker-v2-m3"
REVISION = "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e"
MODEL_CACHE = Path(__file__).resolve().parent / ".models"
MODEL_LOCK = Lock()


class RerankError(Exception):
    pass


@lru_cache(maxsize=1)
def torch_runtime():
    # Anaconda can shadow modern MSVC libraries with older bundled copies.
    # Select installed system libraries for this process; never replace DLLs.
    import sys
    if sys.platform == "win32":
        import ctypes
        directory = ctypes.create_unicode_buffer(32768)
        if not ctypes.windll.kernel32.GetSystemDirectoryW(directory, len(directory)):
            raise OSError("Cannot locate the Windows runtime directory")
        for name in ("vcruntime140_1.dll", "msvcp140.dll"):
            ctypes.WinDLL(str(Path(directory.value) / name))
    import torch
    return torch


@lru_cache(maxsize=1)
def load_model(download=False):
    torch = torch_runtime()
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    torch.set_num_threads(min(4, torch.get_num_threads()))
    options = dict(revision=REVISION, cache_dir=str(MODEL_CACHE),
                   local_files_only=not download, trust_remote_code=False)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, **options)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_ID, use_safetensors=True, **options)
    model.eval()
    return tokenizer, model


def score_pairs(query, articles):
    torch = torch_runtime()
    # Serialize CPU inference across Streamlit sessions to limit peak memory.
    with MODEL_LOCK:
        tokenizer, model = load_model()
        scores = []
        with torch.inference_mode():
            for start in range(0, len(articles), 4):
                pairs = [[query, a.get("title", "") + "\n" + a.get("summary", "")]
                         for a in articles[start:start + 4]]
                inputs = tokenizer(pairs, padding=True, truncation=True,
                                   max_length=512, return_tensors="pt")
                scores.extend(model(**inputs).logits.reshape(-1).float().tolist())
        return scores


def rerank(query, articles):
    if not query.strip() or len(query) > 200 or len(articles) > 100:
        raise RerankError("AI reranking needs a query of 1–200 characters and at most 100 articles.")
    if not articles:
        return []
    try:
        scores = score_pairs(query, articles)
        if len(scores) != len(articles) or not all(math.isfinite(s) for s in scores):
            raise ValueError("Invalid model scores")
        ranked = [dict(article, ai_score=float(score)) for article, score in zip(articles, scores)]
        return sorted(ranked, key=lambda a: (-a["ai_score"],
                      -publication_time(a["published_at"]).timestamp(), a["id"]))
    except Exception as exc:
        raise RerankError("Local AI reranking is unavailable. Showing keyword ranking instead. Check the local model setup in README.") from exc


if __name__ == "__main__":
    load_model(download=True)
    print("BGE model ready in " + str(MODEL_CACHE))
