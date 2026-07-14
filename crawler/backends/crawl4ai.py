"""
crawler/backends/crawl4ai.py
-----------------------------
Async Playwright-based headless browser backend via Crawl4AI.

Why this backend
----------------
Crawl4AI uses a real headless Chromium browser (via Playwright) to load pages,
execute JavaScript, and extract content.  It handles SPAs and dynamic pages that
Trafilatura and BeautifulSoup cannot.  It is free but heavier than Trafilatura —
it starts a browser process per crawl session (cost_tier=1).

Availability
-----------
Requires:
    pip install crawl4ai
    playwright install chromium

Dependencies    : crawl4ai (optional), asyncio, config.settings
"""

from __future__ import annotations

import time

from crawler.backends.base import _BaseCrawler, CrawlResult, ErrorType
from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


class Crawl4AIBackend(_BaseCrawler):
    """
    Async Playwright-based content extraction using Crawl4AI.

    Design notes
    ------------
    Crawl4AI is an async library but our crawler is synchronous.  We run the
    async coroutine via ``asyncio.run()`` which creates and tears down an event
    loop per call.  This is intentionally simple — the alternative (maintaining
    a persistent event loop) adds significant complexity with little gain for the
    low-frequency, depth-first crawl pattern used here.

    Attributes
    ----------
    name        : ``"crawl4ai"``
    supports_js : True — full headless Chromium.
    cost_tier   : 1 — free but requires local browser binary.
    """

    name         = "crawl4ai"
    supports_js  = True
    cost_tier    = 1

    def is_available(self) -> bool:
        """Return True if crawl4ai is installed."""
        try:
            import crawl4ai  # noqa: F401 PLC0415  # pyrefly: ignore
            return True
        except ImportError:
            logger.debug("crawl4ai not installed; Crawl4AIBackend unavailable.")
            return False

    def fetch(self, url: str) -> CrawlResult:
        """
        Launch a headless browser, load *url*, and return extracted Markdown.

        Timeout
        -------
        A hard per-page timeout (``crawl_backend_timeout_seconds``) is enforced
        via ``asyncio.wait_for`` so a single slow page never blocks the queue.
        """
        t0 = time.monotonic()
        timeout = float(settings.crawl_backend_timeout_seconds)

        try:
            import asyncio  # noqa: PLC0415
            from crawl4ai import AsyncWebCrawler  # noqa: PLC0415  # pyrefly: ignore

            async def _run() -> CrawlResult:
                async with AsyncWebCrawler() as crawler:
                    result = await asyncio.wait_for(
                        crawler.arun(url=url),
                        timeout=timeout,
                    )
                    text: str = result.markdown or result.cleaned_html or ""
                    meta = result.metadata or {}
                    title: str = meta.get("title", url) if isinstance(meta, dict) else url
                    latency_ms = (time.monotonic() - t0) * 1000

                    if not text.strip():
                        return CrawlResult.failure(
                            url=url,
                            error="Crawl4AI returned empty content",
                            error_type=ErrorType.EMPTY,
                            backend="crawl4ai",
                            latency_ms=latency_ms,
                        )

                    logger.debug(
                        "Crawl4AI: fetched %s | %d chars | %.0fms",
                        url, len(text), latency_ms,
                    )
                    return CrawlResult(
                        url=url,
                        title=title,
                        raw_text=text,
                        # Crawl4AI does not expose raw HTML easily; leave html=""
                        # so the link extractor uses the Markdown path.
                        backend="crawl4ai",
                        latency_ms=latency_ms,
                    )

            return asyncio.run(_run())

        except TimeoutError:
            latency_ms = (time.monotonic() - t0) * 1000
            return CrawlResult.failure(
                url=url,
                error=f"Crawl4AI timed out after {timeout}s",
                error_type=ErrorType.TIMEOUT,
                backend=self.name,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            latency_ms = (time.monotonic() - t0) * 1000
            logger.warning("Crawl4AI error for %s: %s", url, exc)
            return CrawlResult.failure(
                url=url,
                error=str(exc),
                error_type=ErrorType.UNKNOWN,
                backend=self.name,
                latency_ms=latency_ms,
            )
