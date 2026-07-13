"""
retrieval/searcher.py
---------------------
High-level retrieval interface.

Purpose       : Wrap the VectorStore in a clean retrieval API that returns
                structured SearchResult objects containing:
                  - The matched text chunk
                  - Similarity score
                  - Source file path
                  - Source URL
                  - Chunk ID
                  - Full metadata

Features
--------
    - Similarity search (cosine)
    - MMR search (diverse results)
    - Metadata filtering (library, category, topic, has_code, …)
    - Top-K limiting
    - Reranking hook (optional – currently identity)

Dependencies  : vectordb.vector_store, config.settings, config.logging_config
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional

from langchain_core.documents import Document

from config.logging_config import get_logger
from config.settings import settings
from vectordb.vector_store import VectorStore, get_vector_store

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SearchResult:
    """A single retrieved chunk with all associated metadata."""

    text: str
    score: float
    source_url: str = ""
    source_file: str = ""
    chunk_id: str = ""
    chunk_index: int = 0
    library: str = ""
    topic: str = ""
    category: str = ""
    heading: str = ""
    page_title: str = ""                                  # title of the source page
    section_hierarchy: list[str] = field(default_factory=list)  # breadcrumb path
    has_code: bool = False
    has_table: bool = False
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Searcher
# ---------------------------------------------------------------------------

class Searcher:
    """
    High-level retrieval facade over :class:`~vectordb.vector_store.VectorStore`.

    Args:
        store: Vector store instance. Defaults to the module singleton.
    """

    def __init__(self, store: Optional[VectorStore] = None) -> None:
        self._store = store or get_vector_store()

    # ------------------------------------------------------------------
    # Public search methods
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        k: Optional[int] = None,
        method: Optional[str] = None,
        filter: Optional[dict[str, Any]] = None,
        score_threshold: float = 0.0,
    ) -> list[SearchResult]:
        """
        Execute a retrieval query and return structured results.

        Args:
            query           : Natural language query.
            k               : Number of results (default from settings).
            method          : 'similarity' or 'mmr' (default from settings).
            filter          : Metadata filter dict.
            score_threshold : Minimum relevance score (0.0 = all).

        Returns:
            List of :class:`SearchResult`, ordered by descending score.
        """
        _k = k or settings.retrieval_top_k
        _method = method or settings.retrieval_method

        logger.info(
            "Searching | method=%s | k=%d | query=%r",
            _method,
            _k,
            query[:100],
        )
        t0 = time.monotonic()

        if _method == "mmr":
            docs = self._store.mmr_search(query, k=_k, filter=filter)
            results = [_doc_to_result(doc, score=1.0) for doc in docs]
        else:
            pairs = self._store.similarity_search(
                query, k=_k, filter=filter, score_threshold=score_threshold
            )
            results = [_doc_to_result(doc, score) for doc, score in pairs]

        elapsed = time.monotonic() - t0
        logger.info(
            "Retrieved %d result(s) in %.3fs",
            len(results),
            elapsed,
        )
        return results

    def search_by_library(
        self,
        query: str,
        library: str,
        k: Optional[int] = None,
        method: Optional[str] = None,
    ) -> list[SearchResult]:
        """
        Filter results to a specific library (e.g. 'langchain').

        Args:
            query   : Natural language query.
            library : Library name to filter by.
            k       : Number of results.
            method  : Search method.

        Returns:
            List of :class:`SearchResult`.
        """
        return self.search(
            query=query,
            k=k,
            method=method,
            filter={"library": library},
        )

    def search_code_examples(
        self,
        query: str,
        k: Optional[int] = None,
    ) -> list[SearchResult]:
        """
        Retrieve chunks that contain code examples.

        Args:
            query: Natural language query.
            k    : Number of results.

        Returns:
            List of :class:`SearchResult` where has_code is True.
        """
        results = self.search(query=query, k=(k or settings.retrieval_top_k) * 2)
        code_results = [r for r in results if r.has_code]
        return code_results[: k or settings.retrieval_top_k]

    def as_langchain_retriever(self, **kwargs: Any):
        """
        Return a LangChain-compatible retriever for use in chains / graphs.

        Args:
            **kwargs: Forwarded to ``VectorStore.as_retriever()``.

        Returns:
            LangChain ``VectorStoreRetriever``.
        """
        return self._store.as_retriever(**kwargs)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def list_libraries(self) -> list[str]:
        """
        Return unique library names currently in the vector store.

        This is a best-effort scan using Chroma's get() API.

        Returns:
            Sorted list of library names.
        """
        try:
            collection = self._store._store._collection  # type: ignore[attr-defined]
            result = collection.get(include=["metadatas"])
            libraries: set[str] = set()
            for meta in result.get("metadatas", []):
                lib = (meta or {}).get("library", "")
                if lib:
                    libraries.add(lib)
            return sorted(libraries)
        except Exception as exc:
            logger.warning("Could not list libraries: %s", exc)
            return []

    def count(self) -> int:
        """Return total number of chunks in the vector store."""
        return self._store.count()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _doc_to_result(doc: Document, score: float) -> SearchResult:
    """Convert a LangChain Document + score into a :class:`SearchResult`."""
    meta = doc.metadata or {}
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        import json as _json
        try:
            tags = _json.loads(tags)
        except Exception:
            tags = [tags]

    # Build a breadcrumb section hierarchy from available metadata
    heading = meta.get("heading", "")
    topic = meta.get("topic", "")
    category = meta.get("category", "")
    library = meta.get("library", "")
    hierarchy: list[str] = [x for x in [library, category, topic, heading] if x]

    # Best-effort page title: use heading or derive from URL
    from urllib.parse import urlparse as _urlparse  # noqa: PLC0415
    url = meta.get("source_url", "")
    page_title = heading
    if not page_title and url:
        path = _urlparse(url).path.strip("/")
        page_title = path.split("/")[-1].replace("-", " ").replace("_", " ").title() if path else url

    return SearchResult(
        text=doc.page_content,
        score=score,
        source_url=url,
        source_file=meta.get("source_file", ""),
        chunk_id=meta.get("id", ""),
        chunk_index=int(meta.get("chunk_index", 0)),
        library=library,
        topic=topic,
        category=category,
        heading=heading,
        page_title=page_title,
        section_hierarchy=hierarchy,
        has_code=bool(meta.get("has_code", False)),
        has_table=bool(meta.get("has_table", False)),
        tags=tags,
        metadata=meta,
    )


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_searcher_instance: Optional[Searcher] = None


def get_searcher(store: Optional[VectorStore] = None) -> Searcher:
    """
    Return the module-level singleton :class:`Searcher`.

    Args:
        store: Optional custom store. If provided, resets the singleton.

    Returns:
        Shared :class:`Searcher` instance.
    """
    global _searcher_instance
    if _searcher_instance is None or store is not None:
        _searcher_instance = Searcher(store=store)
    return _searcher_instance
