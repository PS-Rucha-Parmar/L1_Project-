"""
vectordb/vector_store.py
------------------------
Persistent vector database manager (Chroma + optional FAISS).

Purpose       : Provide a unified interface for:
                  - Building a vector store from chunks + embeddings.
                  - Persisting and loading the store from disk.
                  - Performing similarity/MMR search with metadata filters.

Supported backends
------------------
    chroma  (default) – persistent SQLite-based store via langchain-chroma
    faiss             – flat FAISS index + docstore via langchain-community

Both backends are wrapped in a thin ``VectorStore`` class so the retrieval
and pipeline layers never need to know which backend is active.

Dependencies  : langchain-chroma, langchain-community (faiss),
                embeddings.embedder, config.settings, config.logging_config
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from langchain_core.documents import Document

from config.logging_config import get_logger
from config.settings import settings
from embeddings.embedder import DocEmbedder, get_embedder

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CHROMA_COLLECTION = "docai_knowledge_base"


# ---------------------------------------------------------------------------
# VectorStore facade
# ---------------------------------------------------------------------------

class VectorStore:
    """
    Unified interface over Chroma or FAISS vector stores.

    Usage::

        store = VectorStore()
        store.add_chunks(chunks, metadatas)
        results = store.similarity_search("how does RAG work?", k=5)
    """

    def __init__(
        self,
        backend: Optional[str] = None,
        persist_dir: Optional[Path] = None,
        embedder: Optional[DocEmbedder] = None,
    ) -> None:
        self.backend = backend or settings.vector_db_type
        self.persist_dir = persist_dir or settings.vector_db_path()
        self.embedder = embedder or get_embedder()
        self._store: Any = None  # lazy-init

        # Ensure storage directory exists.
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            "VectorStore init | backend=%s | persist_dir=%s",
            self.backend,
            self.persist_dir,
        )

    # ------------------------------------------------------------------
    # Build / load
    # ------------------------------------------------------------------

    def load_or_create(self) -> "VectorStore":
        """
        Load an existing store from disk; create an empty one if absent.

        Returns:
            Self, for chaining.
        """
        if self.backend == "chroma":
            self._store = self._load_chroma()
        elif self.backend == "faiss":
            self._store = self._load_faiss()
        else:
            raise ValueError(f"Unsupported backend: {self.backend!r}")
        return self

    def add_chunks(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]],
        ids: Optional[list[str]] = None,
    ) -> None:
        """
        Embed *texts* and add them to the store.

        Args:
            texts     : List of chunk text strings.
            metadatas : Parallel list of metadata dicts.
            ids       : Optional explicit IDs (must match length of texts).
        """
        if not texts:
            logger.warning("add_chunks called with empty texts list - skipping.")
            return

        if self._store is None:
            self.load_or_create()

        logger.info("Adding %d chunks to %s vector store…", len(texts), self.backend)

        # Sanitise metadata: Chroma requires str/int/float/bool values.
        clean_metas = [_sanitise_metadata(m) for m in metadatas]
        doc_ids = ids or [m.get("id", "") for m in clean_metas]

        if self.backend == "chroma":
            self._add_to_chroma(texts, clean_metas, doc_ids)
        elif self.backend == "faiss":
            self._add_to_faiss(texts, clean_metas)

        logger.info("Chunks added and persisted.")

    def add_documents(self, documents: list[Document]) -> None:
        """
        Convenience wrapper: add LangChain Document objects.

        Args:
            documents: List of :class:`langchain_core.documents.Document`.
        """
        texts = [d.page_content for d in documents]
        metadatas = [d.metadata for d in documents]
        self.add_chunks(texts, metadatas)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict[str, Any]] = None,
        score_threshold: float = 0.0,
    ) -> list[tuple[Document, float]]:
        """
        Cosine similarity search.

        Args:
            query           : Query string.
            k               : Number of results.
            filter          : Metadata filter dict (Chroma WHERE clause syntax).
            score_threshold : Minimum score to include (0.0 = all).

        Returns:
            List of (Document, score) tuples sorted by descending score.
        """
        self._ensure_loaded()
        logger.debug("Similarity search | query=%r | k=%d", query[:80], k)

        if self.backend == "chroma":
            raw = self._store.similarity_search_with_relevance_scores(
                query, k=k, filter=filter
            )
        else:  # faiss
            raw = self._store.similarity_search_with_score(query, k=k)

        results = [(doc, float(score)) for doc, score in raw if float(score) >= score_threshold]
        return sorted(results, key=lambda x: x[1], reverse=True)

    def mmr_search(
        self,
        query: str,
        k: int = 5,
        fetch_k: Optional[int] = None,
        lambda_mult: Optional[float] = None,
        filter: Optional[dict[str, Any]] = None,
    ) -> list[Document]:
        """
        Maximal Marginal Relevance search for diverse results.

        Args:
            query      : Query string.
            k          : Number of results to return.
            fetch_k    : Candidate pool size (default from settings).
            lambda_mult: Relevance vs. diversity tradeoff (default from settings).
            filter     : Metadata filter.

        Returns:
            List of Documents.
        """
        self._ensure_loaded()
        _fetch_k = fetch_k or settings.mmr_fetch_k
        _lambda = lambda_mult if lambda_mult is not None else settings.mmr_lambda_mult

        logger.debug("MMR search | query=%r | k=%d | fetch_k=%d", query[:80], k, _fetch_k)

        if self.backend == "chroma":
            return self._store.max_marginal_relevance_search(
                query, k=k, fetch_k=_fetch_k, lambda_mult=_lambda, filter=filter
            )
        else:  # faiss
            return self._store.max_marginal_relevance_search(
                query, k=k, fetch_k=_fetch_k, lambda_mult=_lambda
            )

    def as_retriever(self, **kwargs: Any):
        """
        Return a LangChain retriever (for use inside chains/graphs).

        Args:
            **kwargs: Forwarded to ``VectorStore.as_retriever()``.

        Returns:
            LangChain ``VectorStoreRetriever``.
        """
        self._ensure_loaded()
        method = settings.retrieval_method
        search_kwargs: dict = {"k": settings.retrieval_top_k}

        if method == "mmr":
            search_kwargs.update(
                fetch_k=settings.mmr_fetch_k,
                lambda_mult=settings.mmr_lambda_mult,
            )

        search_kwargs.update(kwargs.pop("search_kwargs", {}))
        return self._store.as_retriever(
            search_type=method,
            search_kwargs=search_kwargs,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return number of vectors in the store."""
        self._ensure_loaded()
        if self.backend == "chroma":
            return self._store._collection.count()
        else:
            return self._store.index.ntotal if hasattr(self._store, "index") else 0

    # ------------------------------------------------------------------
    # Chroma helpers
    # ------------------------------------------------------------------

    def _load_chroma(self):
        from langchain_chroma import Chroma
        return Chroma(
            collection_name=_CHROMA_COLLECTION,
            embedding_function=self.embedder,
            persist_directory=str(self.persist_dir),
        )

    def _add_to_chroma(
        self,
        texts: list[str],
        metadatas: list[dict],
        ids: list[str],
    ) -> None:
        # Filter out empty IDs.
        safe_ids = [i if i else None for i in ids]
        self._store.add_texts(texts=texts, metadatas=metadatas, ids=safe_ids)

    # ------------------------------------------------------------------
    # FAISS helpers
    # ------------------------------------------------------------------

    def _load_faiss(self):
        from langchain_community.vectorstores import FAISS
        faiss_index = self.persist_dir / "faiss_index"
        if faiss_index.exists():
            logger.info("Loading existing FAISS index from %s", faiss_index)
            return FAISS.load_local(
                str(faiss_index),
                embeddings=self.embedder,
                allow_dangerous_deserialization=True,
            )
        logger.info("Creating new FAISS index (no existing index found).")
        # Return None; will be created on first add.
        return None

    def _add_to_faiss(self, texts: list[str], metadatas: list[dict]) -> None:
        from langchain_community.vectorstores import FAISS
        if self._store is None:
            self._store = FAISS.from_texts(
                texts=texts,
                embedding=self.embedder,
                metadatas=metadatas,
            )
        else:
            self._store.add_texts(texts=texts, metadatas=metadatas)

        faiss_index = self.persist_dir / "faiss_index"
        self._store.save_local(str(faiss_index))
        logger.info("FAISS index saved to %s", faiss_index)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _ensure_loaded(self) -> None:
        if self._store is None:
            self.load_or_create()


# ---------------------------------------------------------------------------
# Metadata sanitiser
# ---------------------------------------------------------------------------

def _sanitise_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    """
    Chroma only accepts str / int / float / bool values.
    Convert lists and nested dicts to JSON strings; drop None values.
    """
    clean: dict[str, Any] = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            clean[k] = v
        elif isinstance(v, (list, dict)):
            clean[k] = json.dumps(v)
        else:
            clean[k] = str(v)
    return clean


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_store_instance: Optional[VectorStore] = None


def get_vector_store(
    backend: Optional[str] = None,
    persist_dir: Optional[Path] = None,
) -> VectorStore:
    """
    Return the module-level singleton :class:`VectorStore`.

    Args:
        backend    : Override backend ('chroma' | 'faiss').
        persist_dir: Override persistence directory.

    Returns:
        Shared :class:`VectorStore` instance.
    """
    global _store_instance
    if _store_instance is None:
        _store_instance = VectorStore(backend=backend, persist_dir=persist_dir)
        _store_instance.load_or_create()
    return _store_instance
