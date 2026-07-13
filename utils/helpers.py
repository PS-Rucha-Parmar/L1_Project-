"""
utils/helpers.py
----------------
General utility helpers used across the DocAI project.

Purpose       : Provide small, reusable functions that do not belong to any
                single module but are needed in multiple places.

Utilities
---------
    slugify             – URL/file-safe string conversion
    truncate_text       – Truncate long text with an ellipsis
    format_elapsed      – Human-readable duration string
    load_markdown_file  – Read a Markdown file from the knowledge base
    list_knowledge_base – Walk the knowledge base and list all documents
    read_metadata_json  – Load a document's metadata.json sidecar
    count_tokens        – Approximate token count for a string

Dependencies  : pathlib, re, json (stdlib)
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Iterator, Optional

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# String utilities
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """
    Convert *text* to a lowercase, hyphen-separated, URL-safe slug.

    Args:
        text: Input string.

    Returns:
        Slug string (e.g. "Hello World!" → "hello-world").
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def truncate_text(text: str, max_chars: int = 300, suffix: str = "…") -> str:
    """
    Truncate *text* to *max_chars* characters, appending *suffix* if cut.

    Args:
        text     : Input string.
        max_chars: Maximum length of the output.
        suffix   : Appended when the text is truncated.

    Returns:
        Truncated string.
    """
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(suffix)].rstrip() + suffix


def format_elapsed(seconds: float) -> str:
    """
    Format a duration in seconds as a human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        E.g. "42ms", "1.23s", "2m 05s".
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs:02d}s"


def count_tokens(text: str) -> int:
    """
    Approximate token count using the heuristic: 1 token ≈ 4 characters.

    Args:
        text: Input string.

    Returns:
        Estimated token count.
    """
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Knowledge base utilities
# ---------------------------------------------------------------------------

def list_knowledge_base(
    kb_dir: Optional[Path] = None,
) -> Iterator[tuple[Path, Path]]:
    """
    Walk the knowledge base directory and yield (markdown_path, metadata_path)
    pairs for every document that has both files.

    Args:
        kb_dir: Root knowledge base directory (default from settings).

    Yields:
        (Path to .md file, Path to _metadata.json file)
    """
    kb_dir = kb_dir or settings.knowledge_base_dir
    if not kb_dir.exists():
        logger.warning("Knowledge base directory does not exist: %s", kb_dir)
        return

    for md_path in sorted(kb_dir.rglob("*.md")):
        if md_path.name.startswith("."):
            continue
        # Sidecar: same stem with _metadata.json suffix.
        meta_path = md_path.with_name(md_path.stem + "_metadata.json")
        yield md_path, meta_path


def load_markdown_file(path: Path) -> str:
    """
    Read and return the text content of a Markdown file.

    Args:
        path: Absolute path to the .md file.

    Returns:
        File contents as a string (empty string on error).
    """
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.error("Failed to read %s: %s", path, exc)
        return ""


def read_metadata_json(path: Path) -> dict[str, Any]:
    """
    Load a metadata.json sidecar file.

    Args:
        path: Absolute path to the *_metadata.json file.

    Returns:
        Parsed dict (empty dict on error or absence).
    """
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Failed to read metadata %s: %s", path, exc)
        return {}


def count_documents(kb_dir: Optional[Path] = None) -> dict[str, int]:
    """
    Count documents per library in the knowledge base.

    Args:
        kb_dir: Root knowledge base directory.

    Returns:
        Dict mapping library name → document count.
    """
    counts: dict[str, int] = {}
    for md_path, _ in list_knowledge_base(kb_dir):
        library = md_path.parent.name
        counts[library] = counts.get(library, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Timing context manager
# ---------------------------------------------------------------------------

class Timer:
    """Simple context manager for measuring elapsed time."""

    def __init__(self) -> None:
        self.elapsed: float = 0.0
        self._start: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.monotonic()
        return self

    def __exit__(self, *_: Any) -> None:
        self.elapsed = time.monotonic() - self._start

    def __str__(self) -> str:
        return format_elapsed(self.elapsed)
