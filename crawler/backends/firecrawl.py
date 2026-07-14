"""
crawler/backends/firecrawl.py
-----------------------------
Firecrawl cloud API backend.

Why this backend
----------------
Firecrawl renders JavaScript-heavy Single Page Applications (React, Next.js, Vue)
and returns clean Markdown directly.  It is the highest-quality option for modern
documentation sites but is a billed API (cost_tier=3) — it should only be used
when simpler backends fail or when JS rendering is explicitly required.

Availability
-----------
Requires:
    pip install firecrawl-py
    FIRECRAWL_API_KEY=<key> in .env

Dependencies    : firecrawl-py (optional), config.settings
"""

from __future__ import annotations

import time

from crawler.backends.base import _BaseCrawler, CrawlResult, ErrorType
from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


class FirecrawlBackend(_BaseCrawler):
    """
    Use the Firecrawl cloud API to render and extract page content as Markdown.

    Attributes
    ----------
    name        : ``"firecrawl"``
    supports_js : True — Firecrawl uses headless Chromium via the cloud.
    cost_tier   : 3 — billed per page.
    """

    name         = "firecrawl"
    supports_js  = True
    cost_tier    = 3

    def __init__(self) -> None:
        # Lazy: credentials validated on first use, not at import time.
        self._api_key: str = settings.firecrawl_api_key
        self._client: object | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """
        Return True if firecrawl-py is installed and an API key is configured.

        Why lazy import
        ---------------
        Importing at module level would raise ImportError at startup for users
        who have not installed firecrawl-py.  Lazy import means the module
        loads fine and ``is_available()`` simply returns False.
        """
        if not self._api_key:
            return False
        try:
            from firecrawl import FirecrawlApp  # noqa: PLC0415  # pyrefly: ignore
            self._client = FirecrawlApp(api_key=self._api_key)
            return True
        except ImportError:
            logger.debug("firecrawl-py not installed; FirecrawlBackend unavailable.")
            return False

    # ------------------------------------------------------------------
    # Fetch
    # ------------------------------------------------------------------

    def fetch(self, url: str) -> CrawlResult:
        """
        Scrape *url* using the Firecrawl API and return Markdown content.

        Notes on SDK version compat
        ---------------------------
        Firecrawl's Python SDK changed its calling convention between v0 and v1.
        We try the modern keyword-arg form first and fall back to params={...}.
        """
        t0 = time.monotonic()
        try:
            from firecrawl import FirecrawlApp  # noqa: PLC0415  # pyrefly: ignore

            if self._client is None:
                self._client = FirecrawlApp(api_key=self._api_key)

            # SDK v1+ uses keyword args; older versions use params=dict.
            try:
                result = self._client.scrape_url(url, formats=["markdown"])
            except TypeError:
                result = self._client.scrape_url(url, params={"formats": ["markdown"]})

            latency_ms = (time.monotonic() - t0) * 1000

            # Handle both object-style (v1) and dict-style (v0) responses.
            if hasattr(result, "markdown"):
                markdown = result.markdown or ""
                meta = getattr(result, "metadata", {}) or {}
                title = meta.get("title", url) if isinstance(meta, dict) else url
            else:
                markdown = result.get("markdown", "") or ""
                title = result.get("metadata", {}).get("title", url)

            if not markdown.strip():
                return CrawlResult.failure(
                    url=url,
                    error="Firecrawl returned empty markdown",
                    error_type=ErrorType.EMPTY,
                    backend=self.name,
                    latency_ms=latency_ms,
                )

            logger.debug(
                "Firecrawl: fetched %s | %d chars | %.0fms",
                url, len(markdown), latency_ms,
            )
            return CrawlResult(
                url=url,
                title=title,
                raw_text=markdown,
                backend=self.name,
                latency_ms=latency_ms,
            )

        except Exception as exc:
            latency_ms = (time.monotonic() - t0) * 1000
            error_str = str(exc)
            error_type = self._classify_from_message(error_str)
            logger.warning("Firecrawl error for %s: %s", url, error_str)
            return CrawlResult.failure(
                url=url,
                error=error_str,
                error_type=error_type,
                backend=self.name,
                latency_ms=latency_ms,
            )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_from_message(message: str) -> ErrorType:
        """Map exception message to an ErrorType without an HTTP status code."""
        msg = message.lower()
        if "429" in msg or "rate limit" in msg or "too many" in msg:
            return ErrorType.RATE_LIMIT
        if "401" in msg or "403" in msg or "unauthorized" in msg or "forbidden" in msg:
            return ErrorType.AUTH
        if "timeout" in msg:
            return ErrorType.TIMEOUT
        if "api" in msg:
            return ErrorType.API
        return ErrorType.UNKNOWN
