"""
retrieval/hybrid_retriever.py
------------------------------
Hybrid retrieval pipeline combining BM25 keyword search with semantic
(vector) search, fused via Reciprocal Rank Fusion (RRF), and reranked
by a cross-encoder model.

Pipeline
--------
  1.  Semantic MMR search  → top candidate_k results
  2.  BM25 keyword search  → top candidate_k results
  3.  RRF fusion           → merged, deduplicated ranked list
  4.  Cross-encoder rerank → top rerank_top_n results
  5.  Context expansion    → adjacent chunks (chunk_index ± 1)

Dependencies : rank-bm25, sentence-transformers, vectordb.vector_store,
               retrieval.searcher, config.settings, config.logging_config
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Optional

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Lazy imports of heavy dependencies (kept at function level)
# ---------------------------------------------------------------------------

def _get_search_result_class():
    from retrieval.searcher import SearchResult  # noqa: PLC0415
    return SearchResult


def _get_store():
    from vectordb.vector_store import get_vector_store  # noqa: PLC0415
    return get_vector_store()


def _get_searcher():
    from retrieval.searcher import get_searcher  # noqa: PLC0415
    return get_searcher()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Lowercase + punctuation-stripped whitespace tokenizer for BM25."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return [t for t in text.split() if len(t) > 1]


def _parse_tags(raw: Any) -> list[str]:
    """Parse tags from a JSON string or list."""
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, list) else [raw]
        except Exception:
            return [raw] if raw else []
    return []


def _result_key(result) -> str:
    """Stable deduplication key for a SearchResult."""
    return result.chunk_id or result.text[:120]


# ---------------------------------------------------------------------------
# BM25 Index
# ---------------------------------------------------------------------------

class BM25Index:
    """
    In-memory BM25 index built over all documents in the vector store.
    Built lazily on first use and can be force-rebuilt after ingestion.
    """

    def __init__(self) -> None:
        self._index = None
        self._docs: list[str] = []
        self._metadatas: list[dict] = []
        self._built = False

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self, force: bool = False) -> None:
        """Build the index from Chroma. No-op if already built (unless force=True)."""
        if self._built and not force:
            return

        try:
            from rank_bm25 import BM25Okapi  # noqa: PLC0415
        except ImportError:
            logger.warning("rank-bm25 not installed – BM25 search disabled.")
            return

        store = _get_store()
        store._ensure_loaded()

        try:
            col = store._store._collection  # type: ignore[attr-defined]
            result = col.get(include=["documents", "metadatas"])
            docs: list[str] = result.get("documents", []) or []
            metas: list[dict] = result.get("metadatas", []) or []
        except Exception as exc:
            logger.warning("BM25 index build failed (store not ready?): %s", exc)
            return

        if not docs:
            logger.warning("BM25 index: no documents found in the store.")
            return

        self._docs = docs
        self._metadatas = metas
        self._index = BM25Okapi([_tokenize(d) for d in docs])
        self._built = True
        logger.info("BM25 index built | %d documents", len(docs))

    def rebuild(self) -> None:
        """Force a full rebuild (call after new documents are added)."""
        self.build(force=True)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query: str, k: int = 20) -> list[tuple[str, dict, float]]:
        """
        Search the index.

        Returns:
            List of (text, metadata, bm25_score) tuples, descending score.
        """
        if not self._built:
            self.build()
        if self._index is None or not self._docs:
            return []

        tokens = _tokenize(query)
        raw_scores = self._index.get_scores(tokens)

        scored = [
            (self._docs[i], self._metadatas[i], float(raw_scores[i]))
            for i in range(len(self._docs))
        ]
        scored.sort(key=lambda x: x[2], reverse=True)
        return scored[:k]


# ---------------------------------------------------------------------------
# Cross-Encoder Reranker
# ---------------------------------------------------------------------------

class CrossEncoderReranker:
    """
    Reranks a list of SearchResult objects using a cross-encoder model.
    The model is lazy-loaded on the first call to ``rerank()``.
    """

    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model = None

    def _load(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import CrossEncoder  # noqa: PLC0415
            logger.info("Loading cross-encoder: %s (first-time download may take ~30s)", self._model_name)
            self._model = CrossEncoder(self._model_name, max_length=512)
            logger.info("Cross-encoder loaded.")
        except Exception as exc:
            logger.warning("Cross-encoder unavailable (%s) – skipping rerank.", exc)

    def rerank(self, query: str, results: list, top_n: int) -> list:
        """
        Rerank *results* by cross-encoder score.

        Args:
            query   : The user query.
            results : Candidate SearchResult list.
            top_n   : Maximum number of results to return.

        Returns:
            Reranked list with updated ``score`` values.
        """
        if not results:
            return results

        self._load()
        if self._model is None:
            return results[:top_n]

        pairs = [(query, r.text[:512]) for r in results]
        try:
            scores = self._model.predict(pairs)
            ranked = sorted(zip(results, scores), key=lambda x: float(x[1]), reverse=True)

            # Cross-encoder scores are raw logits (typically -10 to +10).
            # Convert to [0, 1] via sigmoid so they are compatible with
            # the retrieval_min_score threshold in rag_chain.py.
            import math
            def sigmoid(x: float) -> float:
                return 1.0 / (1.0 + math.exp(-x))

            out = []
            for r, s in ranked[:top_n]:
                r.score = round(sigmoid(float(s)), 4)
                out.append(r)
            logger.info("Reranked %d → %d results (scores normalized via sigmoid).", len(results), len(out))
            return out
        except Exception as exc:
            logger.warning("Reranking failed: %s – using original order.", exc)
            return results[:top_n]


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------------------------

def _reciprocal_rank_fusion(
    result_lists: list[list],
    rrf_k: int = 60,
) -> list:
    """
    Merge multiple ranked result lists using Reciprocal Rank Fusion (RRF).

    RRF score = Σ 1 / (rank + 1 + rrf_k)  for every list containing the doc.

    Args:
        result_lists : List of SearchResult lists (each pre-ranked).
        rrf_k        : RRF constant (standard default = 60).

    Returns:
        Merged, deduplicated list sorted by descending RRF score.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, Any] = {}

    for result_list in result_lists:
        for rank, result in enumerate(result_list):
            key = _result_key(result)
            scores[key] = scores.get(key, 0.0) + 1.0 / (rank + 1 + rrf_k)
            if key not in doc_map:
                doc_map[key] = result

    sorted_keys = sorted(scores, key=lambda k: scores[k], reverse=True)

    # Normalize RRF scores to [0, 1] range.
    # Raw RRF scores are tiny (e.g. 0.016 for rank-1 with rrf_k=60).
    # Without normalization, ALL scores fall below the retrieval_min_score
    # threshold in rag_chain.py and the answer is always "not available".
    raw_vals = [scores[k] for k in sorted_keys]
    min_s = min(raw_vals) if raw_vals else 0.0
    max_s = max(raw_vals) if raw_vals else 1.0
    score_range = max_s - min_s if max_s != min_s else 1.0

    fused: list = []
    for key in sorted_keys:
        r = doc_map[key]
        # Scale to [0.5, 1.0] so top results are clearly above any threshold.
        normalised = 0.5 + 0.5 * (scores[key] - min_s) / score_range
        r.score = round(normalised, 4)
        fused.append(r)
    return fused


# ---------------------------------------------------------------------------
# HybridRetriever
# ---------------------------------------------------------------------------

class HybridRetriever:
    """
    Full hybrid retrieval pipeline:
      BM25 ──┐
             ├─► RRF Fusion ─► Cross-Encoder Rerank ─► Context Expand
    Semantic ┘

    All components are class-level singletons to share the BM25 index and
    reranker model across requests without reloading them.

    Usage::

        retriever = get_hybrid_retriever()
        results = retriever.retrieve("How do I create an API key?", k=10)
    """

    # Class-level singletons shared across all instances
    _bm25: BM25Index = BM25Index()
    _reranker: CrossEncoderReranker = CrossEncoderReranker(
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
    )

    def __init__(self) -> None:
        self._searcher = _get_searcher()
        self._store = _get_store()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        k: int = 10,
        library_filter: Optional[str] = None,
        candidate_k: int = 30,
        rerank: bool = True,
        expand_context: bool = True,
    ) -> list:
        """
        Run the full hybrid retrieval pipeline.

        Args:
            query          : Natural language query.
            k              : Final number of results.
            library_filter : Restrict to a specific documentation library.
            candidate_k    : Number of candidates from each individual retriever.
            rerank         : Whether to apply cross-encoder reranking.
            expand_context : Whether to include adjacent chunks.

        Returns:
            List of enriched SearchResult objects.
        """
        t0 = time.monotonic()

        # 1. Semantic search (MMR for diversity in the candidate pool)
        semantic = self._semantic_search(query, k=candidate_k, library_filter=library_filter)

        # 2. BM25 keyword search
        bm25 = self._bm25_search(query, k=candidate_k, library_filter=library_filter)

        # 3. RRF fusion
        fused = _reciprocal_rank_fusion([semantic, bm25])[:candidate_k]

        # 4. Cross-encoder reranking
        rerank_top_n = getattr(settings, "rerank_top_n", k * 2)
        if rerank and fused:
            fused = self._reranker.rerank(query, fused, top_n=rerank_top_n)

        # 5. Take final top-k
        top = fused[:k]

        # 6. Context expansion
        if expand_context and top:
            top = self._expand_context(top, neighbors=1)

        elapsed = time.monotonic() - t0
        logger.info(
            "Hybrid retrieval | semantic=%d | bm25=%d → fused=%d | final=%d | %.3fs",
            len(semantic), len(bm25), len(fused), len(top), elapsed,
        )
        return top

    def rebuild_bm25(self) -> None:
        """Force-rebuild BM25 index (call after new documents are indexed)."""
        self._bm25.rebuild()

    # ------------------------------------------------------------------
    # Internal retrieval steps
    # ------------------------------------------------------------------

    def _semantic_search(self, query: str, k: int, library_filter: Optional[str]) -> list:
        try:
            if library_filter:
                return self._searcher.search_by_library(
                    query, library_filter, k=k, method="similarity"
                )
            return self._searcher.search(query, k=k, method="similarity")
        except Exception as exc:
            logger.warning("Semantic search error: %s", exc)
            return []

    def _bm25_search(self, query: str, k: int, library_filter: Optional[str]) -> list:
        SearchResult = _get_search_result_class()
        if not self._bm25._built:
            self._bm25.build()

        # Fetch more if we need to filter
        fetch_k = k * 3 if library_filter else k
        raw = self._bm25.search(query, k=fetch_k)

        results: list = []
        for text, meta, bm25_score in raw:
            if library_filter and meta.get("library") != library_filter:
                continue
            if bm25_score <= 0:
                continue
            # Normalise to approximate 0-1 range (BM25 is unbounded)
            normalised = min(bm25_score / 20.0, 1.0)
            r = SearchResult(
                text=text,
                score=normalised,
                source_url=meta.get("source_url", ""),
                source_file=meta.get("source_file", ""),
                chunk_id=meta.get("id", ""),
                chunk_index=int(meta.get("chunk_index", 0)),
                library=meta.get("library", ""),
                topic=meta.get("topic", ""),
                category=meta.get("category", ""),
                heading=meta.get("heading", ""),
                has_code=bool(meta.get("has_code", False)),
                has_table=bool(meta.get("has_table", False)),
                tags=_parse_tags(meta.get("tags", "[]")),
                metadata=meta,
            )
            results.append(r)
            if len(results) >= k:
                break
        return results

    def _expand_context(self, results: list, neighbors: int = 1) -> list:
        """
        For each top result, fetch adjacent chunks (chunk_index ± neighbors)
        from the same source URL and insert them after the parent result.
        Adjacent chunks are marked with ``_expanded=True`` in their metadata
        and assigned a slightly lower score.
        """
        expanded: list = []
        seen_keys: set[str] = {_result_key(r) for r in results}
        seen_url_idx: set[tuple[str, int]] = {
            (r.source_url, r.chunk_index) for r in results
        }

        for result in results:
            expanded.append(result)
            if not result.source_url:
                continue

            for delta in range(-neighbors, neighbors + 1):
                if delta == 0:
                    continue
                neighbor_idx = result.chunk_index + delta
                if neighbor_idx < 0:
                    continue
                coord = (result.source_url, neighbor_idx)
                if coord in seen_url_idx:
                    continue
                seen_url_idx.add(coord)

                nbr = self._fetch_chunk_by_coords(result.source_url, neighbor_idx)
                if nbr is None:
                    continue
                key = _result_key(nbr)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                nbr.score = result.score * 0.80   # slightly penalise expanded chunks
                nbr.metadata["_expanded"] = True
                expanded.append(nbr)

        return expanded

    def _fetch_chunk_by_coords(self, source_url: str, chunk_index: int):
        """Fetch a single chunk from Chroma by (source_url, chunk_index)."""
        SearchResult = _get_search_result_class()
        try:
            self._store._ensure_loaded()
            col = self._store._store._collection  # type: ignore[attr-defined]
            result = col.get(
                where={
                    "$and": [
                        {"source_url": {"$eq": source_url}},
                        {"chunk_index": {"$eq": chunk_index}},
                    ]
                },
                include=["documents", "metadatas"],
            )
            docs = result.get("documents") or []
            metas = result.get("metadatas") or []
            if not docs:
                return None
            meta = metas[0] if metas else {}
            return SearchResult(
                text=docs[0],
                score=0.0,
                source_url=meta.get("source_url", ""),
                source_file=meta.get("source_file", ""),
                chunk_id=meta.get("id", ""),
                chunk_index=int(meta.get("chunk_index", 0)),
                library=meta.get("library", ""),
                topic=meta.get("topic", ""),
                category=meta.get("category", ""),
                heading=meta.get("heading", ""),
                has_code=bool(meta.get("has_code", False)),
                has_table=bool(meta.get("has_table", False)),
                tags=_parse_tags(meta.get("tags", "[]")),
                metadata=meta,
            )
        except Exception as exc:
            logger.debug("Could not fetch chunk (%s, %d): %s", source_url, chunk_index, exc)
            return None


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_hybrid_retriever: Optional[HybridRetriever] = None


def get_hybrid_retriever() -> HybridRetriever:
    """Return the module-level singleton HybridRetriever."""
    global _hybrid_retriever
    if _hybrid_retriever is None:
        _hybrid_retriever = HybridRetriever()
    return _hybrid_retriever
