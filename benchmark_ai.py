"""Run explicitly after local model setup; uses six small labeled examples."""
import json
import time
import ctypes
from ctypes import wintypes
from ai_reranker import rerank, MODEL_ID, REVISION
from result_tools import rank_articles

# Hand-written learning examples, not a representative quality benchmark.
EXAMPLES = [
    ("English", "electric car batteries", "New advances in EV energy storage", "Electric car batteries: weekly crossword clues"),
    ("Chinese", "電動車電池", "新型鋰離子技術提升汽車續航力", "電動車電池：本週填字遊戲答案"),
    ("German", "Elektroauto Batterie", "Neue Akkutechnik verbessert die Reichweite von Fahrzeugen", "Elektroauto Batterie: Kreuzworträtsel der Woche"),
    ("French", "batterie voiture électrique", "Une nouvelle technologie de stockage améliore l’autonomie des véhicules", "Batterie voiture électrique : mots croisés de la semaine"),
    ("Italian", "batteria auto elettrica", "Nuovi accumulatori aumentano l’autonomia dei veicoli", "Batteria auto elettrica: cruciverba della settimana"),
    ("Spanish", "batería coche eléctrico", "Una nueva tecnología de almacenamiento mejora la autonomía de los vehículos", "Batería coche eléctrico: crucigrama semanal"),
]


def peak_memory_mib():
    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
            "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    process = ctypes.windll.kernel32.GetCurrentProcess
    process.restype = wintypes.HANDLE
    getter = ctypes.windll.psapi.GetProcessMemoryInfo
    getter.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    if getter(process(), ctypes.byref(counters), counters.cb):
        return round(counters.PeakWorkingSetSize / 1024**2, 1)
    return None


if __name__ == "__main__":
    results = []
    for language, query, relevant, distractor in EXAMPLES:
        articles = [dict(id="relevant", title=relevant, summary="", published_at="2026-09-09"),
                    dict(id="distractor", title=distractor, summary="", published_at="2026-09-10")]
        start = time.perf_counter()
        ranked = rerank(query, articles)
        row = dict(language=language, keyword_top1=rank_articles(articles, query, "Most relevant")[0]["id"],
                   ai_top1=ranked[0]["id"], seconds=round(time.perf_counter()-start, 2))
        results.append(row)
        print(json.dumps(row, ensure_ascii=True), flush=True)
    print(json.dumps(dict(model=MODEL_ID, revision=REVISION, peak_process_mib=peak_memory_mib(),
                         examples=results)), flush=True)
