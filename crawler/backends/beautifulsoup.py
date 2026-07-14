"""
crawler/backends/beautifulsoup.py
----------------------------------
Reliable HTML-parsing fallback using requests + BeautifulSoup.

Why this backend
----------------
BeautifulSoup is the most reliable fallback — it works on any HTML page that can
be fetched over HTTP, requires no extra dependencies beyond what is already in the
project, and has zero cost.  Its text extraction is lower quality than Trafilatura
(it lacks content heuristics) but it always produces *something* from valid HTML.

Bug fixed
---------
The original ``_to_markdown()`` used ``soup.descendants`` which visits every node
in the tree, including *parent* nodes that already contain the text of their
children.  This produced badly duplicated content.  The new implementation uses
``find_all()`` per element type with ``recursive=False`` at each level to avoid
double-visiting.

Dependencies    : requests, beautifulsoup4, config.settings
"""

from __future__ import annotations

import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup, Tag  # pyrefly: ignore

from crawler.backends.base import _BaseCrawler, CrawlResult, ErrorType
from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Browser headers
# ---------------------------------------------------------------------------

_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

# ---------------------------------------------------------------------------
# HTML elements that are noise (navigation / chrome)
# ---------------------------------------------------------------------------

_NOISE_SELECTORS: list[str] = [
    "nav", "header", "footer", "aside", "script", "style",
    "noscript", "iframe", "svg", "form", "button",
    '[class*="sidebar"]', '[class*="navbar"]', '[class*="cookie"]',
    '[class*="banner"]', '[class*="advertisement"]', '[class*="promo"]',
    '[class*="social"]', '[class*="share"]', '[class*="newsletter"]',
    '[class*="related"]', '[class*="breadcrumb"]', '[class*="pagination"]',
    '[id*="sidebar"]', '[id*="nav"]', '[id*="menu"]',
]

# Selectors tried in order to find main content — first match wins.
_CONTENT_SELECTORS: list[str] = [
    "main",
    "article",
    '[role="main"]',
    ".content",
    "#content",
    ".documentation",
    "#documentation",
    ".docs-content",
    ".page-content",
    "#main-content",
    ".main-content",
    ".entry-content",
    "body",
]


class BeautifulSoupBackend(_BaseCrawler):
    """
    Reliable HTML-parsing fallback using requests + BeautifulSoup.

    Attributes
    ----------
    name        : ``"beautifulsoup"``
    supports_js : False — pure HTTP, no JavaScript execution.
    cost_tier   : 0 — free, local.
    """

    name         = "beautifulsoup"
    supports_js  = False
    cost_tier    = 0

    def is_available(self) -> bool:
        """Return True — bs4 and requests are core project dependencies."""
        try:
            import bs4  # noqa: F401 PLC0415  # pyrefly: ignore
            return True
        except ImportError:
            return False

    def fetch(self, url: str) -> CrawlResult:
        """
        Fetch *url* and convert main content to Markdown via BeautifulSoup.

        Returns
        -------
        CrawlResult with ``html`` populated for downstream link extraction.
        """
        t0 = time.monotonic()
        timeout = settings.crawl_backend_timeout_seconds
        status_code: int = 0

        try:
            resp = requests.get(url, headers=_HEADERS, timeout=timeout)
            status_code = resp.status_code
            resp.raise_for_status()
            html = resp.text
        except requests.exceptions.Timeout:
            latency_ms = (time.monotonic() - t0) * 1000
            return CrawlResult.failure(
                url=url,
                error=f"Request timed out after {timeout}s",
                error_type=ErrorType.TIMEOUT,
                backend=self.name,
                latency_ms=latency_ms,
            )
        except requests.exceptions.HTTPError as exc:
            latency_ms = (time.monotonic() - t0) * 1000
            return CrawlResult.failure(
                url=url,
                error=str(exc),
                error_type=self._classify_http_error(status_code, str(exc)),
                backend=self.name,
                latency_ms=latency_ms,
                status_code=status_code,
            )
        except Exception as exc:
            latency_ms = (time.monotonic() - t0) * 1000
            return CrawlResult.failure(
                url=url,
                error=str(exc),
                error_type=ErrorType.NETWORK,
                backend=self.name,
                latency_ms=latency_ms,
            )

        # Parse and clean HTML.
        soup = BeautifulSoup(html, "html.parser")

        # Remove noise elements.
        for selector in _NOISE_SELECTORS:
            for el in soup.select(selector):
                el.decompose()

        # Extract title.
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else url

        # Find main content region.
        content_el: Optional[Tag] = None
        for selector in _CONTENT_SELECTORS:
            content_el = soup.select_one(selector)
            if content_el:
                break
        target = content_el or soup.find("body") or soup

        # Convert to Markdown.
        text = _element_to_markdown(target)

        latency_ms = (time.monotonic() - t0) * 1000

        if not text.strip():
            return CrawlResult.failure(
                url=url,
                error="BeautifulSoup extracted empty text",
                error_type=ErrorType.EMPTY,
                backend=self.name,
                latency_ms=latency_ms,
                status_code=status_code,
            )

        logger.debug(
            "BeautifulSoup: fetched %s | %d chars | %.0fms",
            url, len(text), latency_ms,
        )
        return CrawlResult(
            url=url,
            title=title,
            raw_text=text,
            html=html,
            backend=self.name,
            latency_ms=latency_ms,
            status_code=status_code,
        )


# ---------------------------------------------------------------------------
# HTML → Markdown converter (fixed: no more duplicate text)
# ---------------------------------------------------------------------------

def _element_to_markdown(element: Tag) -> str:
    """
    Convert a BeautifulSoup element to rough but correct Markdown.

    Why not ``soup.descendants``
    ----------------------------
    ``descendants`` visits every node in depth-first order, meaning a ``<li>``
    inside a ``<ul>`` is visited both when processing the ``<ul>`` *and* when
    the iterator reaches the ``<li>`` directly.  This produces duplicate text.

    Instead, this function recurses explicitly through the tree, processing each
    node type at most once and not double-visiting children.

    Args:
        element: A BeautifulSoup Tag to convert.

    Returns:
        Markdown string.
    """
    parts: list[str] = []
    _recurse(element, parts)
    text = "\n".join(parts)
    # Collapse 3+ consecutive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _recurse(node: Tag, parts: list[str]) -> None:
    """Recursively walk *node* and append Markdown lines to *parts*."""
    for child in node.children:
        if not hasattr(child, "name"):
            # NavigableString — plain text (only if parent is a leaf we handle below)
            continue

        tag: Tag = child

        if tag.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag.name[1])
            heading_text = tag.get_text(separator=" ", strip=True)
            if heading_text:
                parts.append(f"\n{'#' * level} {heading_text}\n")

        elif tag.name == "p":
            text = tag.get_text(separator=" ", strip=True)
            if text:
                parts.append(f"\n{text}\n")

        elif tag.name == "pre":
            # Preserve code blocks verbatim.
            code_tag = tag.find("code")
            lang = ""
            if code_tag:
                classes = code_tag.get("class") or []
                for cls in classes:
                    if cls.startswith("language-"):
                        lang = cls.replace("language-", "")
                        break
            code_text = (code_tag or tag).get_text()
            parts.append(f"\n```{lang}\n{code_text}\n```\n")

        elif tag.name in ("ul", "ol"):
            _process_list(tag, parts, ordered=(tag.name == "ol"))

        elif tag.name == "table":
            _process_table(tag, parts)

        elif tag.name == "blockquote":
            inner = tag.get_text(separator=" ", strip=True)
            if inner:
                parts.append(f"\n> {inner}\n")

        elif tag.name == "a":
            href = tag.get("href", "")
            text = tag.get_text(strip=True)
            if href and text:
                parts.append(f"[{text}]({href})")
            elif text:
                parts.append(text)

        elif tag.name in (
            "div", "section", "article", "main",
            "aside", "span", "strong", "em", "b", "i",
        ):
            # Generic containers — recurse into them.
            _recurse(tag, parts)

        elif tag.name == "br":
            parts.append("\n")

        elif tag.name == "hr":
            parts.append("\n---\n")


def _process_list(list_tag: Tag, parts: list[str], ordered: bool) -> None:
    """Convert <ul>/<ol> to Markdown list items."""
    for idx, li in enumerate(list_tag.find_all("li", recursive=False), start=1):
        prefix = f"{idx}." if ordered else "-"
        text = li.get_text(separator=" ", strip=True)
        if text:
            parts.append(f"{prefix} {text}")


def _process_table(table_tag: Tag, parts: list[str]) -> None:
    """Convert <table> to Markdown pipe-table format."""
    rows: list[list[str]] = []
    for tr in table_tag.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
        if cells:
            rows.append(cells)

    if not rows:
        return

    # Pad all rows to the same column count.
    max_cols = max(len(r) for r in rows)
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    header = "| " + " | ".join(rows[0]) + " |"
    separator = "| " + " | ".join(["---"] * max_cols) + " |"
    body = "\n".join("| " + " | ".join(row) + " |" for row in rows[1:])

    parts.append(f"\n{header}\n{separator}\n{body}\n")
