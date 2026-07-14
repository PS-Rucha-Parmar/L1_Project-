"""
crawler/extractor.py
--------------------
Link extraction and Markdown document builder.

Why this module exists
----------------------
The original ``_extract_links()`` had a critical bug: it only worked when raw
HTML was available.  Firecrawl and Crawl4AI return Markdown, not HTML.  When
those backends were used, ``html_src`` was an empty string and zero child links
were discovered — the crawl became non-recursive for all JS-rendered pages.

The original ``_to_standard_markdown()`` always generated 14 empty section
headings regardless of whether the content matched those sections.  These empty
headings produced ~14 useless chunks per document in the vector database.

This module provides:

  LinkExtractor   — extracts links from both HTML and Markdown content.
  MarkdownBuilder — generates clean YAML-frontmatter Markdown without empty sections.

Dependencies    : re, urllib.parse, beautifulsoup4 (stdlib + project deps)
"""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Optional

from bs4 import BeautifulSoup  # pyrefly: ignore

from crawler.backends.base import CrawlResult
from config.logging_config import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Markdown link regex — matches [text](url) including relative links
# ---------------------------------------------------------------------------

_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


# ===========================================================================
# Link Extractor
# ===========================================================================

class LinkExtractor:
    """
    Extract hyperlinks from a crawled page, handling both HTML and Markdown.

    Why dual-mode extraction
    ------------------------
    Different backends return different formats:
      - BeautifulSoup / Trafilatura → HTML available in ``CrawlResult.html``
      - Firecrawl / Crawl4AI → Markdown only, ``html`` is empty

    This extractor tries HTML first (more reliable, finds all ``<a href>`` tags
    including those not expressed in Markdown), then falls back to Markdown link
    parsing.

    Link post-processing
    --------------------
    All discovered links are:
      1. Resolved to absolute URLs (relative links handled).
      2. Passed to the URL filter via ``should_crawl()`` callback.
      3. Deduplicated.
    """

    def extract(
        self,
        result: CrawlResult,
        should_crawl_fn,
    ) -> list[str]:
        """
        Return a deduplicated list of absolute URLs found in *result*.

        Args:
            result         : The crawl result (may contain html or raw_text).
            should_crawl_fn: Callable(url: str) → bool — from URLFilter.

        Returns:
            List of absolute canonical URLs to enqueue.
        """
        base_url = result.final_url or result.url
        raw_links: list[str] = []

        if result.html:
            raw_links = self._from_html(result.html, base_url)
        elif result.raw_text:
            raw_links = self._from_markdown(result.raw_text, base_url)

        # Filter, canonicalize, deduplicate.
        seen: set[str] = set()
        valid: list[str] = []
        for link in raw_links:
            if link in seen:
                continue
            seen.add(link)
            ok, _ = should_crawl_fn(link)
            if ok:
                valid.append(link)

        logger.debug(
            "LinkExtractor: %d raw links → %d valid from %s (mode=%s)",
            len(raw_links), len(valid), base_url,
            "html" if result.html else "markdown",
        )
        return valid

    # ------------------------------------------------------------------
    # HTML extraction
    # ------------------------------------------------------------------

    def _from_html(self, html: str, base_url: str) -> list[str]:
        """Parse all ``<a href>`` tags from *html*."""
        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception as exc:
            logger.debug("HTML parse error during link extraction: %s", exc)
            return []

        links: list[str] = []
        for a_tag in soup.find_all("a", href=True):
            href: str = str(a_tag["href"]).strip()
            if not href:
                continue
            # Skip in-page anchors, non-HTTP schemes.
            if href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
                continue
            absolute = urljoin(base_url, href)
            # Drop fragment.
            absolute = absolute.split("#")[0]
            if absolute:
                links.append(absolute)

        # Also check for <link rel="next"> for paginated docs.
        for link_tag in soup.find_all("link", rel=True):
            rels = link_tag.get("rel", [])
            if "next" in rels or "canonical" in rels:
                href = link_tag.get("href", "")
                if href:
                    absolute = urljoin(base_url, href).split("#")[0]
                    links.append(absolute)

        return links

    # ------------------------------------------------------------------
    # Markdown extraction
    # ------------------------------------------------------------------

    def _from_markdown(self, markdown: str, base_url: str) -> list[str]:
        """
        Extract links from Markdown content using regex.

        Handles:
        - Standard Markdown links: ``[text](url)``
        - Bare URLs (http/https only): ``https://example.com``
        """
        links: list[str] = []

        # Standard Markdown links.
        for _, href in _MD_LINK_RE.findall(markdown):
            href = href.strip()
            if not href:
                continue
            if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            absolute = urljoin(base_url, href).split("#")[0]
            if absolute:
                links.append(absolute)

        # Bare URLs.
        bare_url_re = re.compile(r"(?<!\()(https?://[^\s\)\]\"\'<>]+)")
        for match in bare_url_re.finditer(markdown):
            url = match.group(1).rstrip(".,;:")
            links.append(url)

        return links


# ===========================================================================
# Markdown Builder
# ===========================================================================

class MarkdownBuilder:
    """
    Convert a :class:`CrawlResult` into a clean Markdown document.

    Why not the original 15-section template
    -----------------------------------------
    The original ``_to_standard_markdown()`` always added 14 empty section
    headings (``# Concepts``, ``# Architecture``, etc.) even when the page had
    no matching content.  The semantic chunker then created one chunk per
    section, most of them containing only an empty heading.  This polluted the
    vector database and wasted embedding tokens.

    New approach
    ------------
    - Only emit sections that have actual content.
    - Frontmatter (YAML) contains all metadata: title, url, library, backend,
      word_count, crawled_at.
    - The raw extracted text is placed under a ``## Content`` section.
    - A ``## References`` section is always added with the source URL.
    """

    def build(self, result: CrawlResult, library: str) -> str:
        """
        Build a clean Markdown document from *result*.

        Args:
            result  : The successful crawl result.
            library : Library name (from URL heuristic).

        Returns:
            Markdown string with YAML frontmatter.
        """
        now = datetime.now(timezone.utc).isoformat()
        body = result.raw_text.strip()
        word_count = len(body.split())

        # Escape double-quotes in title for YAML.
        safe_title = result.title.replace('"', '\\"') if result.title else result.url

        doc = f"""---
title: "{safe_title}"
url: "{result.url}"
library: "{library}"
backend: "{result.backend}"
word_count: {word_count}
crawled_at: "{now}"
---

## Content

{body}

## References

- Source: [{result.url}]({result.url})
"""
        return doc

    # ------------------------------------------------------------------
    # Helpers (also used by spider.py for metadata)
    # ------------------------------------------------------------------

    @staticmethod
    def infer_topic(url: str) -> str:
        """Best-guess topic from URL path segments."""
        path = urlparse(url).path.lower()
        topics = [
            "retrieval", "embedding", "chain", "agent", "tool",
            "prompt", "memory", "model", "output", "vector",
            "index", "loader", "splitter", "callback", "integration",
            "guide", "tutorial", "quickstart", "reference", "api",
        ]
        for topic in topics:
            if topic in path:
                return topic
        segments = [s for s in path.split("/") if s]
        return segments[-1] if segments else "general"

    @staticmethod
    def infer_category(url: str) -> str:
        """Best-guess category from URL path."""
        path = urlparse(url).path.lower()
        if any(k in path for k in ("guide", "tutorial", "how-to", "how_to")):
            return "guide"
        if any(k in path for k in ("reference", "api", "module")):
            return "reference"
        if any(k in path for k in ("concept", "explanation", "overview")):
            return "concept"
        return "documentation"

    @staticmethod
    def infer_tags(url: str, title: str) -> list[str]:
        """Generate tags from URL and title."""
        combined = (urlparse(url).path + " " + title).lower()
        keywords = [
            "langchain", "langgraph", "rag", "retrieval", "embedding",
            "vector", "chromadb", "faiss", "openai", "groq", "anthropic",
            "streamlit", "python", "agent", "tool", "chain", "prompt",
            "memory", "splitter", "loader", "callback", "model",
        ]
        return [kw for kw in keywords if kw in combined] or ["documentation"]


# ---------------------------------------------------------------------------
# Content hash for deduplication
# ---------------------------------------------------------------------------

def content_hash(text: str) -> str:
    """SHA-256 of normalised whitespace — used for exact-duplicate detection."""
    normalised = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(normalised.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------

def library_name(start_url: str) -> str:
    """
    Derive a safe folder name from the documentation URL.

    Examples:
        https://python.langchain.com/docs/  → langchain
        https://docs.streamlit.io/          → streamlit
    """
    netloc = urlparse(start_url).netloc.lower()
    for prefix in ("docs.", "python.", "js.", "www.", "api."):
        if netloc.startswith(prefix):
            netloc = netloc[len(prefix):]
            break
    label = netloc.split(".")[0]
    label = re.sub(r"[^a-z0-9_\-]", "_", label)
    return label or "unknown"


def safe_filename(url: str) -> str:
    """Convert a URL to a filesystem-safe stem (no extension, max 120 chars)."""
    path = urlparse(url).path.strip("/").replace("/", "_") or "index"
    path = re.sub(r"[^a-zA-Z0-9_\-]", "_", path)
    return path[:120]


def write_document(
    result: CrawlResult,
    library: str,
    kb_dir: Path,
    builder: Optional[MarkdownBuilder] = None,
) -> Path:
    """
    Write Markdown + metadata.json sidecar to ``kb_dir/<library>/``.

    Args:
        result  : Successful crawl result.
        library : Library folder name.
        kb_dir  : Root knowledge base directory.
        builder : MarkdownBuilder instance (created if None).

    Returns:
        Path to the written Markdown file.
    """
    import json

    if builder is None:
        builder = MarkdownBuilder()

    lib_dir = kb_dir / library
    lib_dir.mkdir(parents=True, exist_ok=True)

    stem = safe_filename(result.url)
    md_path = lib_dir / f"{stem}.md"
    meta_path = lib_dir / f"{stem}_metadata.json"

    markdown = builder.build(result, library)
    md_path.write_text(markdown, encoding="utf-8")

    word_count = len(result.raw_text.split())
    reading_time = max(1, round(word_count / 200))

    metadata: dict = {
        "id": str(uuid.uuid4()),
        "title": result.title,
        "library": library,
        "topic": builder.infer_topic(result.url),
        "url": result.url,
        "category": builder.infer_category(result.url),
        "tags": builder.infer_tags(result.url, result.title),
        "word_count": word_count,
        "reading_time": f"{reading_time} min",
        "backend": result.backend,
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "embedding_status": "pending",
        "source_file": str(md_path),
    }
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.debug("Written: %s", md_path)
    return md_path
