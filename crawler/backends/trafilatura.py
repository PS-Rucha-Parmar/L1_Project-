"""
crawler/backends/trafilatura.py
-------------------------------
Trafilatura HTTP-based content extraction backend.

Why this backend
----------------
Trafilatura is a fast, lightweight library purpose-built for extracting readable
content from HTML.  It uses heuristics to identify the main content area and
strips navigation, ads, and boilerplate automatically.  It has zero per-request
cost and requires no browser, making it ideal for static documentation sites.

Availability
-----------
Requires:  pip install trafilatura

Dependencies    : trafilatura (optional), requests, beautifulsoup4,
                  config.settings, crawler.backends.base
"""

from __future__ import annotations

import time
from typing import Optional

import requests
from bs4 import BeautifulSoup  # pyrefly: ignore

from crawler.backends.base import _BaseCrawler, CrawlResult, ErrorType
from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# HTTP headers that mimic a real browser to avoid 403 blocks
# ---------------------------------------------------------------------------

_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


class TrafilaturaBackend(_BaseCrawler):
    """
    Fast HTTP-based content extraction using Trafilatura.

    Strategy
    --------
    1. Pre-fetch with ``requests`` using real browser headers to avoid 403s.
    2. Pass the HTML to trafilatura for main-content extraction.
    3. Preserve the raw HTML for downstream link extraction.
    4. Fall back to trafilatura's own fetch if requests fails.

    Attributes
    ----------
    name        : ``"trafilatura"``
    supports_js : False — purely HTTP-based, no browser.
    cost_tier   : 0 — free, local.
    """

    name         = "trafilatura"
    supports_js  = False
    cost_tier    = 0

    def is_available(self) -> bool:
        """Return True if trafilatura is installed."""
        try:
            import trafilatura  # noqa: F401 PLC0415  # pyrefly: ignore
            return True
        except ImportError:
            logger.debug("trafilatura not installed; TrafilaturaBackend unavailable.")
            return False

    def fetch(self, url: str) -> CrawlResult:
        """
        Fetch *url* and extract main content as Markdown.

        Returns
        -------
        CrawlResult with ``html`` populated for link extraction.
        """
        t0 = time.monotonic()
        timeout = settings.crawl_backend_timeout_seconds

        html_source: Optional[str] = None
        status_code: int = 0

        # Step 1: Pre-fetch with requests (better header control).
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=timeout)
            status_code = resp.status_code
            resp.raise_for_status()
            html_source = resp.text
        except requests.exceptions.Timeout:
            pass  # Fall through to trafilatura's own fetch
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
        except Exception:
            pass  # Fall through to trafilatura's own fetch

        # Step 2: Trafilatura fallback fetch if requests failed.
        if html_source is None:
            try:
                import trafilatura  # noqa: PLC0415  # pyrefly: ignore
                html_source = trafilatura.fetch_url(url)
            except Exception as exc:
                latency_ms = (time.monotonic() - t0) * 1000
                return CrawlResult.failure(
                    url=url,
                    error=f"Both requests and trafilatura.fetch_url failed: {exc}",
                    error_type=ErrorType.NETWORK,
                    backend=self.name,
                    latency_ms=latency_ms,
                )

        if not html_source:
            latency_ms = (time.monotonic() - t0) * 1000
            return CrawlResult.failure(
                url=url,
                error="Fetch returned empty response",
                error_type=ErrorType.EMPTY,
                backend=self.name,
                latency_ms=latency_ms,
                status_code=status_code,
            )

        # Step 3: Extract main content with trafilatura.
        try:
            import trafilatura  # noqa: PLC0415  # pyrefly: ignore
            text = trafilatura.extract(
                html_source,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                output_format="markdown",
            ) or ""
        except Exception as exc:
            latency_ms = (time.monotonic() - t0) * 1000
            return CrawlResult.failure(
                url=url,
                error=f"trafilatura.extract failed: {exc}",
                error_type=ErrorType.PARSING,
                backend=self.name,
                latency_ms=latency_ms,
                status_code=status_code,
            )

        # Step 4: Extract page title from raw HTML.
        title = _extract_title(html_source, url)
        latency_ms = (time.monotonic() - t0) * 1000

        if not text.strip():
            return CrawlResult.failure(
                url=url,
                error="Trafilatura extracted empty content",
                error_type=ErrorType.EMPTY,
                backend=self.name,
                latency_ms=latency_ms,
                status_code=status_code,
            )

        logger.debug(
            "Trafilatura: fetched %s | %d chars | %.0fms",
            url, len(text), latency_ms,
        )
        return CrawlResult(
            url=url,
            title=title,
            raw_text=text,
            html=html_source,           # Preserved for link extraction
            backend=self.name,
            latency_ms=latency_ms,
            status_code=status_code,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_title(html: str, fallback: str) -> str:
    """Parse the <title> element from raw HTML."""
    try:
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find("title")
        return tag.get_text(strip=True) if tag else fallback
    except Exception:
        return fallback
