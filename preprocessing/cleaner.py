"""
preprocessing/cleaner.py
------------------------
Document cleaning pipeline.

Purpose       : Accept raw Markdown text (as produced by the crawler) and
                return a cleaned version ready for chunking.  Cleaning is
                idempotent and deterministic.

Rules
-----
Remove  : navigation artefacts, duplicate headings, duplicate paragraphs,
          HTML fragments, tracking pixels, cookie-banner boilerplate.
Preserve: headings, code blocks, tables, ordered/unordered lists,
          blockquotes (notes / warnings), inline code.

Dependencies  : re (stdlib only)
"""

from __future__ import annotations

import re
from typing import Sequence


# ---------------------------------------------------------------------------
# Compiled regex helpers
# ---------------------------------------------------------------------------

# Matches fenced code blocks (``` ... ```) – we never touch their interior.
_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)

# Common boilerplate patterns found in scraped docs.
_BOILERPLATE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?im)^(skip\s+to\s+(main\s+)?content|back\s+to\s+top|table\s+of\s+contents?)\s*$"),
    re.compile(r"(?im)^(copyright|all\s+rights\s+reserved|privacy\s+policy|terms\s+of\s+(use|service)|cookie\s+(policy|settings?))[^\n]*$"),
    re.compile(r"(?im)^(edit\s+this\s+page|improve\s+this\s+page|suggest\s+edits?|view\s+source)[^\n]*$"),
    re.compile(r"(?im)^(on\s+this\s+page|in\s+this\s+section|navigation|sidebar)[^\n]*$"),
    re.compile(r"(?im)^(search\s+docs?|search\s+documentation)[^\n]*$"),
    re.compile(r"(?i)accept\s+(all\s+)?cookies?[^\n]*"),
    re.compile(r"(?i)we\s+use\s+cookies[^\n]*"),
    re.compile(r"\[!\[.*?\]\(.*?\)\]\(.*?\)"),  # badge images (shields.io etc.)
]

# Matches blank Markdown heading lines: `# `, `## `, … with nothing after.
_EMPTY_HEADING_RE = re.compile(r"^#{1,6}\s*$", re.MULTILINE)

# Collapses 3+ consecutive blank lines into exactly two.
_EXCESS_BLANK_RE = re.compile(r"\n{3,}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def clean_document(text: str) -> str:
    """
    Full cleaning pipeline for a single Markdown document.

    Args:
        text: Raw Markdown string from the crawler.

    Returns:
        Cleaned Markdown string.
    """
    if not text or not text.strip():
        return ""

    # 1. Extract code blocks so we never mangle them.
    text, placeholders = _extract_code_blocks(text)

    # 2. Strip boilerplate lines.
    text = _remove_boilerplate(text)

    # 3. Strip residual HTML tags (but keep Markdown).
    text = _strip_html_tags(text)

    # 4. Remove empty headings.
    text = _EMPTY_HEADING_RE.sub("", text)

    # 5. Deduplicate consecutive identical paragraphs / headings.
    text = _deduplicate_blocks(text)

    # 6. Normalise whitespace.
    text = _normalise_whitespace(text)

    # 7. Re-insert code blocks.
    text = _restore_code_blocks(text, placeholders)

    return text.strip()


def clean_documents(texts: Sequence[str]) -> list[str]:
    """
    Batch-clean a list of Markdown documents.

    Args:
        texts: Iterable of raw Markdown strings.

    Returns:
        List of cleaned Markdown strings (empty strings are filtered out).
    """
    return [c for raw in texts if (c := clean_document(raw))]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_code_blocks(text: str) -> tuple[str, dict[str, str]]:
    """
    Replace fenced code blocks with unique placeholders so later regex
    substitutions cannot accidentally modify code content.

    Returns:
        (text_with_placeholders, {placeholder: original_block})
    """
    placeholders: dict[str, str] = {}

    def _replace(match: re.Match[str]) -> str:  # type: ignore[type-arg]
        key = f"\x00CODE_BLOCK_{len(placeholders)}\x00"
        placeholders[key] = match.group(0)
        return key

    return _CODE_BLOCK_RE.sub(_replace, text), placeholders


def _restore_code_blocks(text: str, placeholders: dict[str, str]) -> str:
    """Re-insert previously extracted code blocks."""
    for key, block in placeholders.items():
        text = text.replace(key, block)
    return text


def _remove_boilerplate(text: str) -> str:
    """Remove known boilerplate patterns line-by-line."""
    for pattern in _BOILERPLATE_PATTERNS:
        text = pattern.sub("", text)
    return text


def _strip_html_tags(text: str) -> str:
    """
    Remove residual HTML tags while preserving their text content.
    Tables expressed as Markdown (|---|) are untouched.
    """
    # Remove HTML comments.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # Remove self-closing tags like <br/>, <hr/>.
    text = re.sub(r"<[a-zA-Z][^>]*/\s*>", " ", text)
    # Remove paired tags but keep inner text: <span>foo</span> → foo.
    text = re.sub(r"</?[a-zA-Z][^>]*>", "", text)
    return text


def _deduplicate_blocks(text: str) -> str:
    """
    Remove consecutive identical non-empty lines/paragraphs.
    Works at the paragraph level (double-newline delimited).
    """
    paragraphs = re.split(r"\n{2,}", text)
    seen: set[str] = set()
    unique: list[str] = []
    for para in paragraphs:
        key = para.strip()
        if not key:
            unique.append(para)
            continue
        if key not in seen:
            seen.add(key)
            unique.append(para)
    return "\n\n".join(unique)


def _normalise_whitespace(text: str) -> str:
    """Collapse excess blank lines; trim trailing spaces on each line."""
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)
    text = _EXCESS_BLANK_RE.sub("\n\n", text)
    return text
