"""
embeddings/embedder.py
----------------------
HuggingFace / SentenceTransformers embedding pipeline.

Purpose       : Convert text chunks into dense vector embeddings using the
                configured SentenceTransformer model and expose a LangChain-
                compatible Embeddings interface for plug-and-play integration
                with Chroma / FAISS.

Pipeline
--------
    Chunk texts
        → Batch encode via SentenceTransformer
        → Return as list[list[float]]

The class also satisfies the LangChain ``Embeddings`` ABC so it can be
passed directly to ``Chroma(..., embedding_function=embedder)`` etc.

Default model : BAAI/bge-small-en-v1.5   (384-dim, fast, high quality)

Dependencies  : sentence-transformers, langchain-core,
                config.settings, config.logging_config
"""

from __future__ import annotations

import time
from typing import Optional

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Embedder
# ---------------------------------------------------------------------------

class DocEmbedder(Embeddings):
    """
    LangChain-compatible embedder backed by a SentenceTransformer model.

    Usage::

        embedder = DocEmbedder()
        vectors = embedder.embed_documents(["hello world", "foo bar"])
        query_vec = embedder.embed_query("what is langchain?")

    Args:
        model_name  : HuggingFace model identifier. Defaults to settings.
        batch_size  : Number of texts per encoding batch. Defaults to settings.
        device      : 'cpu', 'cuda', or 'mps'.  ``None`` = auto-detect.
        normalize   : Normalize embeddings to unit length (recommended for
                      cosine similarity).
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        batch_size: Optional[int] = None,
        device: Optional[str] = None,
        normalize: bool = True,
    ) -> None:
        self.model_name = model_name or settings.embedding_model
        self.batch_size = batch_size or settings.embedding_batch_size
        self.normalize = normalize

        logger.info("Loading embedding model: %s", self.model_name)
        t0 = time.monotonic()
        self._model = SentenceTransformer(self.model_name, device=device)
        logger.info(
            "Embedding model loaded in %.2fs | dim=%d",
            time.monotonic() - t0,
            self._model.get_sentence_embedding_dimension(),
        )

    # ------------------------------------------------------------------
    # LangChain Embeddings interface
    # ------------------------------------------------------------------

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of document texts.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors (list of floats).
        """
        if not texts:
            return []

        logger.info("Embedding %d document(s) in batches of %d", len(texts), self.batch_size)
        t0 = time.monotonic()

        vectors = self._model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=len(texts) > 100,
            convert_to_numpy=True,
        ).tolist()

        elapsed = time.monotonic() - t0
        logger.info(
            "Embedded %d texts in %.2fs (%.1f texts/s)",
            len(texts),
            elapsed,
            len(texts) / elapsed if elapsed > 0 else float("inf"),
        )
        return vectors

    def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query string.

        For BGE models the recommended prefix is added automatically.

        Args:
            text: Query string.

        Returns:
            Embedding vector as list of floats.
        """
        # BGE models benefit from a query prefix.
        query_text = f"Represent this sentence for searching relevant passages: {text}" \
            if "bge" in self.model_name.lower() else text

        vector = self._model.encode(
            query_text,
            normalize_embeddings=self.normalize,
            convert_to_numpy=True,
        ).tolist()
        return vector

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def dimension(self) -> int:
        """Return the embedding dimension of the loaded model."""
        return self._model.get_sentence_embedding_dimension()

    def embed_chunks(self, chunks: list) -> list[list[float]]:
        """
        Convenience wrapper: embed a list of :class:`Chunk` objects.

        Args:
            chunks: List of Chunk objects (must have a ``text`` attribute).

        Returns:
            List of embedding vectors.
        """
        texts = [c.text for c in chunks]
        return self.embed_documents(texts)


# ---------------------------------------------------------------------------
# Module-level singleton (lazy-loaded to avoid import-time GPU init)
# ---------------------------------------------------------------------------

_embedder_instance: Optional[DocEmbedder] = None


def get_embedder(
    model_name: Optional[str] = None,
    batch_size: Optional[int] = None,
) -> DocEmbedder:
    """
    Return the module-level singleton :class:`DocEmbedder`.

    The model is only loaded on first call.

    Args:
        model_name : Override the default model.
        batch_size : Override the default batch size.

    Returns:
        Shared :class:`DocEmbedder` instance.
    """
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = DocEmbedder(model_name=model_name, batch_size=batch_size)
    return _embedder_instance
