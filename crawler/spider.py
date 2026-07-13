"""
crawler/spider.py
-----------------
Multi-strategy documentation crawler.

Purpose       : Recursively crawl a documentation website, stay within the
                originating domain, deduplicate URLs, clean and extract text,
                convert each page to the standard Markdown template, write the
                Markdown + metadata.json to knowledge_base/<library>/, and
                produce a detailed ingestion report.

Crawling priority (highest available wins):
    1. Firecrawl  – cloud API, handles JS-heavy SPAs
    2. Crawl4AI   – async Playwright-based headless browser
    3. Trafilatura – fast, content-focused HTTP extraction
    4. BeautifulSoup – reliable HTML-parsing fallback

Dependencies  : requests, beautifulsoup4, trafilatura, crawl4ai, firecrawl-py,
                python-dotenv, config.settings, config.logging_config
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import requests
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# HTML elements that are considered noise (navigation/chrome)
_NOISE_TAGS: list[str] = [
    "nav", "header", "footer", "aside", "script", "style",
    "noscript", "iframe", "svg", "form", "button",
    '[class*="sidebar"]', '[class*="navbar"]', '[class*="cookie"]',
    '[class*="banner"]', '[class*="advertisement"]', '[class*="promo"]',
]

_CONTENT_TAGS: list[str] = [
    "main", "article", '[role="main"]', ".content", "#content",
    ".documentation", "#documentation", ".docs-content",
]


@dataclass
class CrawlResult:
    """Encapsulates the raw extraction result for a single URL."""

    url: str
    title: str
    raw_text: str
    html: str = ""
    success: bool = True
    error: str = ""


@dataclass
class IngestionReport:
    """Running statistics for the crawl session."""

    total_pages_attempted: int = 0
    pages_crawled: int = 0
    pages_skipped: int = 0
    duplicates_removed: int = 0
    markdown_files_created: int = 0
    failed_pages: int = 0
    failed_urls: list[str] = field(default_factory=list)

    def summary(self) -> str:
        """Return a human-readable report."""
        return (
            "\n"
            "╔══════════════════════════════════════════╗\n"
            "║          INGESTION REPORT                ║\n"
            "╠══════════════════════════════════════════╣\n"
            f"║  Total pages attempted : {self.total_pages_attempted:<16}║\n"
            f"║  Pages crawled         : {self.pages_crawled:<16}║\n"
            f"║  Pages skipped         : {self.pages_skipped:<16}║\n"
            f"║  Duplicates removed    : {self.duplicates_removed:<16}║\n"
            f"║  Markdown files created: {self.markdown_files_created:<16}║\n"
            f"║  Failed pages          : {self.failed_pages:<16}║\n"
            "╚══════════════════════════════════════════╝\n"
        )


# ---------------------------------------------------------------------------
# URL utilities
# ---------------------------------------------------------------------------

def _normalise_url(url: str) -> str:
    """Lowercase scheme/host, strip fragments and trailing slashes."""
    parsed = urlparse(url)
    clean = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip("/") or "/",
        "",          # params
        parsed.query,
        "",          # fragment – always drop
    ))
    return clean


def _is_same_domain(base: str, target: str) -> bool:
    """Return True if *target* shares the same netloc as *base*."""
    return urlparse(target).netloc == urlparse(base).netloc


def _is_documentation_url(url: str) -> bool:
    """Heuristic filter – skip binary / media / tracking resources."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    skip_extensions = (
        ".pdf", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg",
        ".gif", ".svg", ".mp4", ".webm", ".mp3", ".wav",
        ".exe", ".dmg", ".deb", ".rpm",
    )
    skip_paths = ("/cdn-cgi/", "/static/fonts/", "/assets/img/")
    if any(path.endswith(ext) for ext in skip_extensions):
        return False
    if any(seg in path for seg in skip_paths):
        return False
    return True


def _content_hash(text: str) -> str:
    """SHA-256 of normalised whitespace — used for deduplication."""
    normalised = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(normalised.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Robots.txt
# ---------------------------------------------------------------------------

class RobotsCache:
    """Lightweight cache for robots.txt parsers, keyed by domain."""

    def __init__(self) -> None:
        self._parsers: dict[str, RobotFileParser] = {}

    def allowed(self, url: str) -> bool:
        """Return True if crawling *url* is permitted by robots.txt."""
        parsed = urlparse(url)
        domain_key = f"{parsed.scheme}://{parsed.netloc}"
        if domain_key not in self._parsers:
            rp = RobotFileParser()
            robots_url = f"{domain_key}/robots.txt"
            try:
                rp.set_url(robots_url)
                rp.read()
            except Exception:
                # If we cannot fetch robots.txt, assume allowed
                pass
            self._parsers[domain_key] = rp
        return self._parsers[domain_key].can_fetch("*", url)


# ---------------------------------------------------------------------------
# Backend implementations
# ---------------------------------------------------------------------------

class _BaseCrawler:
    """Abstract interface every backend must implement."""

    name: str = "base"

    def is_available(self) -> bool:  # noqa: D102
        raise NotImplementedError

    def fetch(self, url: str) -> CrawlResult:  # noqa: D102
        raise NotImplementedError


class FirecrawlBackend(_BaseCrawler):
    """Use the Firecrawl cloud API to render and extract content."""

    name = "firecrawl"

    def __init__(self) -> None:
        self._api_key = settings.firecrawl_api_key
        self._client: object | None = None

    def is_available(self) -> bool:
        """Check that the SDK is installed and an API key is present."""
        if not self._api_key:
            return False
        try:
            # pyrefly: ignore [missing-import]
            from firecrawl import FirecrawlApp  # noqa: PLC0415
            self._client = FirecrawlApp(api_key=self._api_key)
            return True
        except ImportError:
            return False

    def fetch(self, url: str) -> CrawlResult:
        """Fetch a single URL via Firecrawl."""
        try:
            from firecrawl import FirecrawlApp  # noqa: PLC0415

            if self._client is None:
                self._client = FirecrawlApp(api_key=self._api_key)
            # SDK v1+ uses keyword args directly, not params=
            try:
                result = self._client.scrape_url(url, formats=["markdown"])
            except TypeError:
                # Fallback for older SDK versions
                result = self._client.scrape_url(url, params={"formats": ["markdown"]})
            if hasattr(result, "markdown"):
                markdown = result.markdown or ""
                title = getattr(result, "metadata", {}) or {}
                title = title.get("title", url) if isinstance(title, dict) else url
            else:
                markdown = result.get("markdown", "") or ""
                title = result.get("metadata", {}).get("title", url)
            return CrawlResult(url=url, title=title, raw_text=markdown)
        except Exception as exc:
            return CrawlResult(url=url, title="", raw_text="", success=False, error=str(exc))


class Crawl4AIBackend(_BaseCrawler):
    """Async Playwright-based headless browser via Crawl4AI."""

    name = "crawl4ai"

    def is_available(self) -> bool:
        try:
            import crawl4ai  # noqa: F401 PLC0415
            return True
        except ImportError:
            return False

    def fetch(self, url: str) -> CrawlResult:
        try:
            import asyncio  # noqa: PLC0415
            from crawl4ai import AsyncWebCrawler  # noqa: PLC0415

            async def _run() -> CrawlResult:
                # Hard 30-second timeout per page so it never hangs
                async with AsyncWebCrawler() as crawler:
                    result = await asyncio.wait_for(
                        crawler.arun(url=url),
                        timeout=30.0,
                    )
                    text = result.markdown or result.cleaned_html or ""
                    title = result.metadata.get("title", url) if result.metadata else url
                    return CrawlResult(url=url, title=title, raw_text=text)

            return asyncio.run(_run())
        except Exception as exc:
            return CrawlResult(url=url, title="", raw_text="", success=False, error=str(exc))


class TrafilaturaBackend(_BaseCrawler):
    """Fast HTTP-based content extraction using Trafilatura."""

    name = "trafilatura"

    def is_available(self) -> bool:
        try:
            import trafilatura  # noqa: F401 PLC0415
            return True
        except ImportError:
            return False

    def fetch(self, url: str) -> CrawlResult:
        try:
            import trafilatura  # noqa: PLC0415

            # Use real browser headers to avoid 403 blocks
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
            # Pre-fetch with requests using real headers, then hand HTML to trafilatura
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                resp.raise_for_status()
                downloaded = resp.text
            except Exception:
                downloaded = trafilatura.fetch_url(url)

            if not downloaded:
                return CrawlResult(url=url, title="", raw_text="", success=False, error="fetch returned None")

            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                output_format="markdown",
            ) or ""
            soup = BeautifulSoup(downloaded, "html.parser")
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else url
            return CrawlResult(url=url, title=title, raw_text=text, html=downloaded)
        except Exception as exc:
            return CrawlResult(url=url, title="", raw_text="", success=False, error=str(exc))


class BeautifulSoupBackend(_BaseCrawler):
    """Reliable HTML parsing fallback using requests + BeautifulSoup."""

    name = "beautifulsoup"

    # Real Chrome User-Agent avoids 403 blocks from docs sites
    _HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

    def is_available(self) -> bool:
        try:
            import bs4  # noqa: F401 PLC0415
            return True
        except ImportError:
            return False

    def fetch(self, url: str) -> CrawlResult:
        try:
            resp = requests.get(url, headers=self._HEADERS, timeout=20)
            resp.raise_for_status()
            html = resp.text

            soup = BeautifulSoup(html, "html.parser")

            # Remove noise elements
            for selector in _NOISE_TAGS:
                for el in soup.select(selector):
                    el.decompose()

            # Extract title
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else url

            # Try to extract main content
            main_content = None
            for selector in _CONTENT_TAGS:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            target = main_content or soup.find("body") or soup

            # Convert to plain text preserving structure
            text = self._to_markdown(target)
            return CrawlResult(url=url, title=title, raw_text=text, html=html)
        except Exception as exc:
            return CrawlResult(url=url, title="", raw_text="", success=False, error=str(exc))

    @staticmethod
    def _to_markdown(soup_element: BeautifulSoup) -> str:
        """Convert a BeautifulSoup element tree to rough Markdown."""
        lines: list[str] = []
        for el in soup_element.descendants:
            if not hasattr(el, "name"):
                continue
            if el.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                level = int(el.name[1])
                lines.append(f"\n{'#' * level} {el.get_text(strip=True)}\n")
            elif el.name == "p":
                text = el.get_text(strip=True)
                if text:
                    lines.append(f"\n{text}\n")
            elif el.name == "code" and el.parent and el.parent.name != "pre":
                lines.append(f"`{el.get_text(strip=True)}`")
            elif el.name == "pre":
                code = el.get_text()
                lines.append(f"\n```\n{code}\n```\n")
            elif el.name == "li":
                lines.append(f"- {el.get_text(strip=True)}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Backend selector
# ---------------------------------------------------------------------------

_BACKEND_ORDER: list[str] = ["firecrawl", "crawl4ai", "trafilatura", "beautifulsoup"]
_BACKEND_MAP: dict[str, _BaseCrawler] = {
    "firecrawl": FirecrawlBackend(),
    "crawl4ai": Crawl4AIBackend(),
    "trafilatura": TrafilaturaBackend(),
    "beautifulsoup": BeautifulSoupBackend(),
}


def _get_available_backends() -> list[_BaseCrawler]:
    """
    Return all available crawler backends, prioritised by user settings.
    """
    preferred = settings.crawler_type
    order = [preferred] + [b for b in _BACKEND_ORDER if b != preferred]

    available: list[_BaseCrawler] = []
    for name in order:
        if name not in _BACKEND_MAP:
            continue
        backend = _BACKEND_MAP[name]
        if backend.is_available():
            available.append(backend)

    if not available:
        logger.warning("No advanced backends available, falling back to BeautifulSoup.")
        available.append(_BACKEND_MAP["beautifulsoup"])
        
    logger.info("Available backends: %s", [b.name for b in available])
    return available


# ---------------------------------------------------------------------------
# Link extraction
# ---------------------------------------------------------------------------

def _extract_links(html: str, base_url: str) -> list[str]:
    """
    Parse *html* and return absolute URLs found in <a href=...>.

    Only same-domain, documentation-worthy links are returned.
    """
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    for a_tag in soup.find_all("a", href=True):
        href: str = a_tag["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        absolute = urljoin(base_url, href)
        absolute = _normalise_url(absolute)
        if _is_same_domain(base_url, absolute) and _is_documentation_url(absolute):
            links.append(absolute)
    return links


# ---------------------------------------------------------------------------
# Markdown template
# ---------------------------------------------------------------------------

def _to_standard_markdown(result: CrawlResult, library: str) -> str:
    """
    Wrap extracted text in the standardised documentation Markdown template.

    Sections that have no content are kept as empty headings so that the
    structure is always consistent across all documents.
    """
    now = datetime.now(timezone.utc).isoformat()
    body = result.raw_text.strip()

    return f"""---
title: "{result.title}"
url: "{result.url}"
library: "{library}"
created: "{now}"
---

# Overview

{body}

# Concepts

# Architecture

# Workflow

# API

# Parameters

# Return Values

# Code Example

# Output

# Notes

# Best Practices

# Common Mistakes

# Performance Notes

# Related Topics

# References

- Source: [{result.url}]({result.url})
"""


# ---------------------------------------------------------------------------
# Knowledge base writer
# ---------------------------------------------------------------------------

def _library_name(start_url: str) -> str:
    """
    Derive a safe folder name from the documentation URL.

    Examples:
        https://python.langchain.com/docs/  → langchain
        https://docs.streamlit.io/          → streamlit
        https://huggingface.co/docs/        → huggingface
    """
    netloc = urlparse(start_url).netloc.lower()
    # Strip common prefixes
    for prefix in ("docs.", "python.", "js.", "www.", "api."):
        if netloc.startswith(prefix):
            netloc = netloc[len(prefix):]
            break
    # Take the first label of the domain
    label = netloc.split(".")[0]
    # Sanitise
    label = re.sub(r"[^a-z0-9_\-]", "_", label)
    return label or "unknown"


def _safe_filename(url: str) -> str:
    """Convert a URL to a filesystem-safe stem (no extension)."""
    path = urlparse(url).path.strip("/").replace("/", "_") or "index"
    path = re.sub(r"[^a-zA-Z0-9_\-]", "_", path)
    return path[:120]  # keep filenames short


def _write_document(
    result: CrawlResult,
    library: str,
    kb_dir: Path,
) -> Path:
    """
    Write Markdown + metadata.json to ``kb_dir/<library>/``.

    Returns:
        Path to the written Markdown file.
    """
    lib_dir = kb_dir / library
    lib_dir.mkdir(parents=True, exist_ok=True)

    stem = _safe_filename(result.url)
    md_path = lib_dir / f"{stem}.md"
    meta_path = lib_dir / f"{stem}_metadata.json"

    # Write Markdown
    markdown = _to_standard_markdown(result, library)
    md_path.write_text(markdown, encoding="utf-8")

    # Word / reading-time estimates
    word_count = len(result.raw_text.split())
    reading_time = max(1, round(word_count / 200))  # ~200 wpm

    # Build metadata
    metadata: dict = {
        "id": str(uuid.uuid4()),
        "title": result.title,
        "library": library,
        "topic": _infer_topic(result.url),
        "url": result.url,
        "category": _infer_category(result.url),
        "tags": _infer_tags(result.url, result.title),
        "word_count": word_count,
        "reading_time": f"{reading_time} min",
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "embedding_status": "pending",
        "source_file": str(md_path),
    }
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.debug("Written: %s", md_path)
    return md_path


# ---------------------------------------------------------------------------
# Metadata inference helpers
# ---------------------------------------------------------------------------

def _infer_topic(url: str) -> str:
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


def _infer_category(url: str) -> str:
    """Best-guess category from URL path."""
    path = urlparse(url).path.lower()
    if any(k in path for k in ("guide", "tutorial", "how-to", "how_to")):
        return "guide"
    if any(k in path for k in ("reference", "api", "module")):
        return "reference"
    if any(k in path for k in ("concept", "explanation", "overview")):
        return "concept"
    return "documentation"


def _infer_tags(url: str, title: str) -> list[str]:
    """Generate a list of tags from the URL path and title."""
    combined = (urlparse(url).path + " " + title).lower()
    all_keywords = [
        "langchain", "langgraph", "rag", "retrieval", "embedding",
        "vector", "chromadb", "faiss", "openai", "groq", "anthropic",
        "streamlit", "python", "agent", "tool", "chain", "prompt",
        "memory", "splitter", "loader", "callback", "model",
    ]
    return [kw for kw in all_keywords if kw in combined] or ["documentation"]



# ---------------------------------------------------------------------------
# Main Spider class
# ---------------------------------------------------------------------------

class DocumentationSpider:
    """
    Recursively crawl a documentation website and ingest all pages into the
    knowledge base.

    Args:
        start_url      : The root URL of the documentation to crawl.
        max_depth      : Maximum link-following depth (default from settings).
        max_pages      : Hard cap on pages crawled (0 = unlimited).
        knowledge_base : Path to the knowledge_base root directory.
    """

    def __init__(
        self,
        start_url: str,
        max_depth: Optional[int] = None,
        max_pages: int = 0,
        knowledge_base: Optional[Path] = None,
    ) -> None:
        self.start_url = _normalise_url(start_url)
        self.max_depth = max_depth if max_depth is not None else settings.max_depth
        self.max_pages = max_pages
        self.kb_dir = knowledge_base or settings.knowledge_base_dir
        self.library = _library_name(start_url)
        self.backends = _get_available_backends()
        self.robots = RobotsCache()
        self.report = IngestionReport()

        # Crawl state
        self._visited: set[str] = set()
        self._content_hashes: set[str] = set()

        logger.info(
            "Spider initialised | url=%s | library=%s | backends=%s | max_depth=%s",
            self.start_url, self.library, [b.name for b in self.backends], self.max_depth,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> IngestionReport:
        """
        Start the BFS crawl from ``start_url`` and return an ingestion report.

        Returns:
            IngestionReport: Statistics about the completed crawl.
        """
        logger.info("Starting crawl: %s", self.start_url)
        queue: deque[tuple[str, int]] = deque([(self.start_url, 0)])

        while queue:
            url, depth = queue.popleft()

            # Depth / page-count limits
            if depth > self.max_depth:
                logger.debug("Max depth reached, skipping: %s", url)
                self.report.pages_skipped += 1
                continue
            if self.max_pages and self.report.pages_crawled >= self.max_pages:
                logger.info("Max pages (%d) reached, stopping.", self.max_pages)
                break

            url = _normalise_url(url)

            # Skip already-visited
            if url in self._visited:
                self.report.duplicates_removed += 1
                continue
            self._visited.add(url)

            # Robots.txt check (bypassed with warning, since many docs block blanket crawlers)
            if not self.robots.allowed(url):
                logger.warning("robots.txt disallows: %s (bypassing for documentation ingestion)", url)

            self.report.total_pages_attempted += 1
            result = self._fetch_with_retry(url)

            if not result.success or not result.raw_text.strip():
                self.report.failed_pages += 1
                self.report.failed_urls.append(url)
                logger.warning("Failed/empty page: %s | error: %s", url, result.error)
                continue

            # Content deduplication
            chash = _content_hash(result.raw_text)
            if chash in self._content_hashes:
                self.report.duplicates_removed += 1
                logger.debug("Duplicate content, skipping: %s", url)
                continue
            self._content_hashes.add(chash)

            # Persist to knowledge base
            try:
                _write_document(result, self.library, self.kb_dir)
                self.report.pages_crawled += 1
                self.report.markdown_files_created += 1
                logger.info(
                    "[%d] Ingested: %s (%d words)",
                    self.report.pages_crawled,
                    url,
                    len(result.raw_text.split()),
                )
            except Exception as exc:
                logger.error("Failed to write document for %s: %s", url, exc)
                self.report.failed_pages += 1
                self.report.failed_urls.append(url)
                continue

            # Discover new links from HTML (if available)
            html_src = result.html or ""
            if not html_src and result.raw_text:
                # Some backends return Markdown, not HTML — skip link extraction
                html_src = ""
            for link in _extract_links(html_src, url):
                if link not in self._visited:
                    queue.append((link, depth + 1))

            # Polite crawl delay
            time.sleep(0.25)

        logger.info("Crawl complete.\n%s", self.report.summary())
        return self.report

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_with_retry(self, url: str, retries: int = 3) -> CrawlResult:
        """
        Fetch *url* trying multiple backends if the page is empty/JS-rendered.
        """
        last_error = ""
        # We try each backend in priority order
        for backend in self.backends:
            for attempt in range(1, retries + 1):
                result = backend.fetch(url)
                if result.success and len(result.raw_text.strip()) > 50:
                    return result
                
                last_error = result.error or "Empty content (possibly JS rendered)"
                wait = 2 ** attempt
                logger.warning(
                    "Backend '%s' attempt %d/%d failed for %s – retrying in %ds | error: %s",
                    backend.name, attempt, retries, url, wait, last_error,
                )
                time.sleep(wait)
            logger.warning("Backend '%s' completely failed for %s. Falling back to next backend.", backend.name, url)
        
        return CrawlResult(url=url, title="", raw_text="", success=False, error=last_error)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def crawl(
    url: str,
    max_depth: Optional[int] = None,
    max_pages: int = 0,
) -> IngestionReport:
    """
    Public convenience function — crawl *url* and return the ingestion report.

    Args:
        url       : Documentation root URL to crawl.
        max_depth : Override the default crawl depth from settings.
        max_pages : Hard cap on crawled pages (0 = unlimited).

    Returns:
        IngestionReport: Crawl statistics.
    """
    spider = DocumentationSpider(
        start_url=url,
        max_depth=max_depth,
        max_pages=max_pages,
    )
    return spider.run()


if __name__ == "__main__":
    import sys
    from config.logging_config import setup_logging

    setup_logging(log_level=settings.log_level)

    if len(sys.argv) < 2:
        print("Usage: python -m crawler.spider <documentation_url> [max_depth]")
        sys.exit(1)

    _url = sys.argv[1]
    _depth = int(sys.argv[2]) if len(sys.argv) > 2 else None
    _report = crawl(_url, max_depth=_depth)
    print(_report.summary())
