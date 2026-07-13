"""
preprocessing/metadata.py
-------------------------
Metadata enrichment pipeline.

Purpose       : Take a Chunk (produced by chunker.py) and a base metadata
                dict (produced by the crawler) and merge them into a single,
                flat metadata dict ready to be stored alongside the vector
                embedding.

Fields generated
----------------
    id              – stable SHA-256 derived from (url, chunk_index)
    source_url      – canonical URL of the source page
    source_file     – path to the Markdown file in knowledge_base/
    library         – library / documentation domain name
    topic           – inferred from URL path segments
    category        – guide | reference | concept | documentation
    tags            – keyword list
    heading         – nearest Markdown heading above this chunk
    chunk_index     – 0-based position of this chunk in the document
    has_code        – whether the chunk contains a code block
    has_table       – whether the chunk contains a Markdown table
    word_count      – words in this chunk
    char_count      – characters in this chunk
    embedding_model – model that produced the embedding (filled at embed time)
    embedding_status – 'pending' | 'embedded'
    created         – ISO-8601 timestamp
    updated         – ISO-8601 timestamp (same as created initially)

Dependencies  : hashlib, datetime (stdlib), config.logging_config
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from config.logging_config import get_logger
from preprocessing.chunker import Chunk

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_chunk_metadata(
    chunk: Chunk,
    base_metadata: dict[str, Any],
    source_file: str = "",
    embedding_model: str = "",
) -> dict[str, Any]:
    """
    Merge crawler-level metadata with chunk-level metadata.

    Args:
        chunk          : Chunk object from chunker.py.
        base_metadata  : Dict from the crawler's metadata.json file.
        source_file    : Absolute path to the Markdown file.
        embedding_model: Model identifier (filled once embedding runs).

    Returns:
        Flat metadata dict suitable for storage in a vector database.
    """
    url = base_metadata.get("url", chunk.metadata.get("source_url", ""))
    library = base_metadata.get("library", chunk.metadata.get("library", ""))
    now = datetime.now(timezone.utc).isoformat()

    meta: dict[str, Any] = {
        # Identity
        "id": _stable_id(url, chunk.chunk_index),
        "source_url": url,
        "source_file": source_file or base_metadata.get("source_file", ""),
        "library": library,
        # Taxonomy
        "topic": base_metadata.get("topic", ""),
        "category": base_metadata.get("category", "documentation"),
        "tags": base_metadata.get("tags", []),
        # Chunk position & content flags
        "heading": chunk.heading,
        "chunk_index": chunk.chunk_index,
        "char_start": chunk.char_start,
        "char_end": chunk.char_end,
        "has_code": chunk.has_code,
        "has_table": chunk.has_table,
        # Size metrics
        "word_count": len(chunk.text.split()),
        "char_count": len(chunk.text),
        # Embedding
        "embedding_model": embedding_model,
        "embedding_status": "pending" if not embedding_model else "embedded",
        # Timestamps
        "created": base_metadata.get("created", now),
        "updated": now,
    }

    logger.debug(
        "Built metadata | id=%s | chunk=%d | url=%s",
        meta["id"],
        chunk.chunk_index,
        url,
    )
    return meta


def build_batch_metadata(
    chunks: list[Chunk],
    base_metadata: dict[str, Any],
    source_file: str = "",
    embedding_model: str = "",
) -> list[dict[str, Any]]:
    """
    Build metadata for every chunk in *chunks* using the same base metadata.

    Args:
        chunks         : List of Chunk objects for one document.
        base_metadata  : Metadata dict from the crawler's metadata.json.
        source_file    : Absolute path to the Markdown file.
        embedding_model: Embedding model identifier.

    Returns:
        List of metadata dicts, one per chunk.
    """
    return [
        build_chunk_metadata(chunk, base_metadata, source_file, embedding_model)
        for chunk in chunks
    ]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _stable_id(url: str, chunk_index: int) -> str:
    """
    Generate a deterministic 16-character hex ID from URL + chunk_index.

    Using a prefix of the SHA-256 digest gives effectively collision-free IDs
    within any single knowledge base.
    """
    raw = f"{url}::{chunk_index}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]
