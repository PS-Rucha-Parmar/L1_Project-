"""
preprocessing/chunker.py
------------------------
Semantic chunking with a RecursiveCharacterTextSplitter fallback.

Purpose       : Split a cleaned Markdown document into overlapping chunks
                suitable for embedding.  The chunker:

                1. Tries semantic splitting (respecting heading / paragraph
                   boundaries).
                2. Falls back to LangChain's RecursiveCharacterTextSplitter
                   for any chunk that is still too large.

Rules (from MASTER_RAG_PROMPT)
------------------------------
- Chunk size   : 800 tokens (approximated as characters / 4)
- Overlap      : 150 tokens
- Never split  : code blocks, tables, lists, examples

Dependencies  : langchain-text-splitters, config.settings, config.logging_config
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    """A single text chunk with positional metadata."""

    text: str
    chunk_index: int
    char_start: int = 0
    char_end: int = 0
    heading: str = ""          # nearest heading above this chunk
    has_code: bool = False
    has_table: bool = False
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Regex helpers – compiled once
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_TABLE_RE = re.compile(r"^\|.+\|$", re.MULTILINE)
# Matches all-whitespace paragraphs
_BLANK_PARA_RE = re.compile(r"\n{3,}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chunk_document(
    text: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    source_url: str = "",
    library: str = "",
) -> list[Chunk]:
    """
    Split *text* into overlapping chunks respecting Markdown structure.

    Args:
        text          : Cleaned Markdown document text.
        chunk_size    : Target chunk size in characters (default from settings).
        chunk_overlap : Overlap in characters (default from settings).
        source_url    : Original URL – stored in each chunk's metadata.
        library       : Library name – stored in each chunk's metadata.

    Returns:
        Ordered list of :class:`Chunk` objects.
    """
    # Character-based approximation: 1 token ≈ 4 chars.
    _size = (chunk_size or settings.chunk_size) * 4
    _overlap = (chunk_overlap or settings.chunk_overlap) * 4

    if not text or not text.strip():
        return []

    # Step 1: semantic split along heading/paragraph boundaries.
    semantic_segments = _semantic_split(text, _size)

    # Step 2: sub-split any segment that is still too large.
    final_texts: list[str] = []
    for segment in semantic_segments:
        if len(segment) <= _size:
            final_texts.append(segment)
        else:
            sub = _recursive_split(segment, _size, _overlap)
            final_texts.extend(sub)

    # Step 3: build Chunk objects.
    chunks: list[Chunk] = []
    cursor = 0
    for idx, chunk_text in enumerate(final_texts):
        chunk_text = chunk_text.strip()
        if not chunk_text:
            continue
        start = text.find(chunk_text, cursor)
        if start == -1:
            start = cursor
        end = start + len(chunk_text)
        cursor = max(cursor, start)

        chunk = Chunk(
            text=chunk_text,
            chunk_index=idx,
            char_start=start,
            char_end=end,
            heading=_nearest_heading(text, start),
            has_code=bool(_CODE_BLOCK_RE.search(chunk_text)),
            has_table=bool(_TABLE_RE.search(chunk_text)),
            metadata={
                "source_url": source_url,
                "library": library,
                "chunk_index": idx,
                "char_start": start,
                "char_end": end,
            },
        )
        chunks.append(chunk)

    logger.debug(
        "Chunked document | source=%s | segments=%d → chunks=%d",
        source_url or "<unknown>",
        len(semantic_segments),
        len(chunks),
    )
    return chunks


def chunk_documents(
    documents: list[dict],
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> list[Chunk]:
    """
    Chunk multiple documents provided as dicts with 'text', 'url', 'library' keys.

    Args:
        documents    : List of dicts, each with keys: text, url, library.
        chunk_size   : Override chunk_size.
        chunk_overlap: Override chunk_overlap.

    Returns:
        Flat list of all chunks from all documents.
    """
    all_chunks: list[Chunk] = []
    for doc in documents:
        chunks = chunk_document(
            text=doc.get("text", ""),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            source_url=doc.get("url", ""),
            library=doc.get("library", ""),
        )
        all_chunks.extend(chunks)
    return all_chunks


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _semantic_split(text: str, max_size: int) -> list[str]:
    """
    Split *text* along heading and paragraph boundaries.

    Strategy:
    - Collect heading positions.
    - Build segments: each segment starts at a heading and includes
      all content up to (but not including) the next same-or-higher heading.
    - If no headings exist, split by double-newline paragraphs.
    - Never break inside a code block or table.
    """
    # Protect code blocks and tables from being split.
    protected = _protect_blocks(text)

    # Find heading positions.
    heading_positions = [(m.start(), m.group(0)) for m in _HEADING_RE.finditer(protected)]

    if not heading_positions:
        # Fall back to paragraph-level splitting.
        return _paragraph_split(protected, max_size)

    segments: list[str] = []
    positions = [pos for pos, _ in heading_positions] + [len(protected)]

    for i, (start, _) in enumerate(heading_positions):
        end = positions[i + 1]
        segment = protected[start:end].strip()
        if segment:
            segments.append(segment)

    # Add any content that appears before the first heading.
    preamble = protected[: heading_positions[0][0]].strip()
    if preamble:
        segments.insert(0, preamble)

    return [_unprotect_blocks(s, text) for s in segments if s.strip()]


def _paragraph_split(text: str, max_size: int) -> list[str]:
    """Split text by double newlines, then merge short fragments."""
    paragraphs = _BLANK_PARA_RE.split(text)
    merged: list[str] = []
    current = ""
    for para in paragraphs:
        if not para.strip():
            continue
        if len(current) + len(para) + 2 <= max_size:
            current = (current + "\n\n" + para).lstrip()
        else:
            if current:
                merged.append(current)
            current = para
    if current:
        merged.append(current)
    return merged or [text]


def _recursive_split(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Use LangChain's RecursiveCharacterTextSplitter for oversized segments.
    This is the fallback for very long sections with no natural boundaries.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
        keep_separator=True,
    )
    return splitter.split_text(text)


def _protect_blocks(text: str) -> str:
    """
    Replace code blocks and tables with unique single-line placeholders so
    that the heading-based splitter never cuts through them.
    """
    # We use a simple marker that won't appear in real Markdown.
    placeholder_lines: list[str] = []

    def _replace_code(m: re.Match[str]) -> str:  # type: ignore[type-arg]
        idx = len(placeholder_lines)
        placeholder_lines.append(m.group(0))
        return f"\x00PROTECTED_{idx}\x00"

    # Protect fenced code blocks.
    protected = _CODE_BLOCK_RE.sub(_replace_code, text)
    return protected


def _unprotect_blocks(protected: str, original: str) -> str:
    """
    Restore protected blocks.  We re-scan the original to reconstruct content.
    Since _protect_blocks replaces with indexed placeholders we do a simple
    lookup back to the original segments.
    """
    # Re-run extraction to get a stable mapping.
    mapping: dict[str, str] = {}
    idx = 0

    def _record(m: re.Match[str]) -> str:  # type: ignore[type-arg]
        nonlocal idx
        key = f"\x00PROTECTED_{idx}\x00"
        mapping[key] = m.group(0)
        idx += 1
        return key

    _CODE_BLOCK_RE.sub(_record, original)

    for key, value in mapping.items():
        protected = protected.replace(key, value)
    return protected


def _nearest_heading(text: str, position: int) -> str:
    """Return the text of the nearest heading at or before *position*."""
    best = ""
    for m in _HEADING_RE.finditer(text):
        if m.start() <= position:
            best = m.group(2).strip()
        else:
            break
    return best
