"""
crawler/router.py
-----------------
Intelligent backend selection and smart retry logic.

Why this module exists
----------------------
The original spider tried ALL backends for EVERY URL in a fixed order, with 3
retries each.  A single page could trigger up to 12 fetch attempts, including
billed Firecrawl calls for simple static HTML pages that Trafilatura handles
perfectly in one attempt.

This module replaces that with:

  1. Signal-based backend routing — cheap backends first, Firecrawl only when needed.
  2. Smart retry logic — different error types get different retry strategies.
  3. Lazy backend instantiation — backends are created on first use, not at import.

Backend routing strategy
------------------------
The router classifies each URL and selects backends in cost-ascending order:

  Static documentation   → Trafilatura → BeautifulSoup
  GitHub / raw content   → Trafilatura → BeautifulSoup
  Wiki pages             → Trafilatura → BeautifulSoup
  JS-heavy / SPA         → Crawl4AI → Firecrawl
  Unknown / default      → Trafilatura → BeautifulSoup → Crawl4AI

Firecrawl is only added to the fallback chain when an API key is configured AND
the URL shows signs of being JS-rendered (EMPTY error from cheaper backends).

Retry strategy per ErrorType
-----------------------------
  EMPTY        → escalate to next backend immediately
  TIMEOUT      → retry same backend once with longer wait, then escalate
  RATE_LIMIT   → sleep and retry same backend
  AUTH         → skip immediately (do not retry or escalate)
  NETWORK      → retry once, then escalate
  PARSING      → escalate immediately
  API / UNKNOWN → escalate immediately

Dependencies    : crawler.backends.*, config.settings, config.logging_config
"""

from __future__ import annotations

import re
import time
from urllib.parse import urlparse

from crawler.backends.base import _BaseCrawler, CrawlResult, ErrorType
from crawler.backends.beautifulsoup import BeautifulSoupBackend
from crawler.backends.crawl4ai import Crawl4AIBackend
from crawler.backends.firecrawl import FirecrawlBackend
from crawler.backends.trafilatura import TrafilaturaBackend
from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# URL classification signals
# ---------------------------------------------------------------------------

# Patterns in the netloc that strongly suggest static content
_STATIC_NETLOC_RE = re.compile(
    r"(docs\.|readthedocs\.io|github\.com/[^/]+/[^/]+/blob"
    r"|raw\.githubusercontent|wiki\.|wikipedia\.org"
    r"|pypi\.org|npmjs\.com|pkg\.go\.dev)",
    re.IGNORECASE,
)

# Patterns that suggest heavy JavaScript / SPA
_JS_HEAVY_NETLOC_RE = re.compile(
    r"(react\.|nextjs\.|angular\.|vue\.|gatsby\.|vercel\.app"
    r"|netlify\.app|webflow\.io)",
    re.IGNORECASE,
)


def _classify_url(url: str) -> str:
    """
    Return a simple category string for *url* used to pick the backend chain.

    Categories:
        "static"   — plain HTML, no JS needed
        "js_heavy" — SPA or dynamic rendering required
        "unknown"  — no strong signal, use default chain
    """
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path.lower()

    if _STATIC_NETLOC_RE.search(netloc):
        return "static"
    if _JS_HEAVY_NETLOC_RE.search(netloc):
        return "js_heavy"
    # readthedocs pattern via path
    if ".readthedocs." in netloc or "/docs/" in path or netloc.startswith("docs."):
        return "static"
    if "/wiki/" in path:
        return "static"
    return "unknown"


# ===========================================================================
# Backend registry — lazy instantiation
# ===========================================================================

class _BackendRegistry:
    """
    Lazily create and cache backend instances.

    Why lazy
    --------
    Firecrawl's ``is_available()`` makes a network call and creates an SDK
    client.  Crawl4AI may start a browser process.  Instantiating these at
    module import time causes visible startup delay even when the backends
    are never used.
    """

    def __init__(self) -> None:
        self._instances: dict[str, _BaseCrawler] = {}
        self._available: dict[str, bool] = {}

    def get(self, name: str) -> _BaseCrawler:
        """Return the singleton instance for *name*, creating it if needed."""
        if name not in self._instances:
            self._instances[name] = _create_backend(name)
        return self._instances[name]

    def is_available(self, name: str) -> bool:
        """Return True if backend *name* is usable in the current environment."""
        if name not in self._available:
            backend = self.get(name)
            self._available[name] = backend.is_available()
            if not self._available[name]:
                logger.debug("Backend %r is not available.", name)
        return self._available[name]


def _create_backend(name: str) -> _BaseCrawler:
    """Factory that maps a name string to a backend instance."""
    mapping: dict[str, type[_BaseCrawler]] = {
        "firecrawl":     FirecrawlBackend,
        "crawl4ai":      Crawl4AIBackend,
        "trafilatura":   TrafilaturaBackend,
        "beautifulsoup": BeautifulSoupBackend,
    }
    cls = mapping.get(name)
    if cls is None:
        raise ValueError(f"Unknown backend name: {name!r}")
    return cls()


_registry = _BackendRegistry()


# ===========================================================================
# Backend Router
# ===========================================================================

class BackendRouter:
    """
    Select and execute the appropriate backend chain for a given URL.

    The router uses two strategies:

    1. **Signal-based routing** — classify the URL and pick the cheapest
       backend that can handle it.
    2. **Smart retry** — when a backend fails, the retry action depends on the
       *type* of error, not just whether success was False.

    Args:
        preferred_backend : Override from settings (``CRAWLER_TYPE``).
                            If set, this backend is always tried first regardless
                            of URL classification.
    """

    def __init__(self, preferred_backend: str | None = None) -> None:
        self._preferred = preferred_backend or settings.crawler_type
        logger.info(
            "BackendRouter initialised | preferred=%r", self._preferred
        )

    def fetch(self, url: str) -> CrawlResult:
        """
        Fetch *url* using the most appropriate backend chain.

        The router:
        1. Builds a backend chain for the URL (cheap → expensive).
        2. Executes backends in order with smart per-error retry logic.
        3. Returns the first successful result, or the last failure.

        Args:
            url: Canonical URL to fetch.

        Returns:
            :class:`CrawlResult` — always returned, never raises.
        """
        chain = self._build_chain(url)
        available_chain = [b for b in chain if _registry.is_available(b)]

        if not available_chain:
            logger.error("No backends available for %s", url)
            return CrawlResult.failure(
                url=url,
                error="No crawler backends are available",
                error_type=ErrorType.UNKNOWN,
            )

        last_result: CrawlResult = CrawlResult.failure(
            url=url, error="No attempt made", error_type=ErrorType.UNKNOWN
        )

        for backend_name in available_chain:
            backend = _registry.get(backend_name)
            result = self._try_backend(url, backend)

            if result.success and len(result.raw_text.strip()) >= settings.crawl_min_content_chars:
                logger.info(
                    "Fetched %s via %s (%.0fms | %d chars)",
                    url, backend_name, result.latency_ms, len(result.raw_text),
                )
                return result

            last_result = result

            # Auth errors: never escalate, just stop.
            if result.error_type == ErrorType.AUTH:
                logger.warning(
                    "Auth error fetching %s — skipping all backends.", url
                )
                break

            logger.debug(
                "Backend %r failed for %s (type=%s) — trying next.",
                backend_name, url, result.error_type,
            )

        return last_result

    # ------------------------------------------------------------------
    # Chain builder
    # ------------------------------------------------------------------

    def _build_chain(self, url: str) -> list[str]:
        """
        Return an ordered list of backend names to try for *url*.

        The preferred backend (from settings) is always inserted first.
        The remaining order is cost-ascending with JS capability considered.
        """
        category = _classify_url(url)

        if category == "static":
            base_chain = ["trafilatura", "beautifulsoup"]
        elif category == "js_heavy":
            base_chain = ["crawl4ai", "firecrawl", "trafilatura", "beautifulsoup"]
        else:
            # Unknown — start cheap, escalate to JS capable if needed.
            base_chain = ["trafilatura", "beautifulsoup", "crawl4ai"]
            # Only add Firecrawl if the user has an API key.
            if settings.firecrawl_api_key:
                base_chain.append("firecrawl")

        # Ensure preferred backend is at the front (without duplicating).
        chain = [self._preferred] + [b for b in base_chain if b != self._preferred]
        return chain

    # ------------------------------------------------------------------
    # Smart per-backend retry
    # ------------------------------------------------------------------

    def _try_backend(
        self,
        url: str,
        backend: _BaseCrawler,
        max_retries: int | None = None,
    ) -> CrawlResult:
        """
        Attempt *url* with *backend*, applying smart retry logic per error type.

        Retry strategy
        --------------
        - RATE_LIMIT : sleep exponentially, retry up to max_retries.
        - TIMEOUT    : retry once with no extra wait, then give up.
        - NETWORK    : retry once, then give up.
        - EMPTY      : return immediately (escalate to next backend).
        - AUTH       : return immediately (no retry).
        - Others     : return immediately.
        """
        max_retries = max_retries if max_retries is not None else settings.crawl_max_retries_per_backend
        result = CrawlResult.failure(url=url, error="", error_type=ErrorType.UNKNOWN, backend=backend.name)

        for attempt in range(1, max_retries + 1):
            result = backend.fetch(url)

            if result.success:
                return result

            error_type = result.error_type

            if error_type == ErrorType.AUTH:
                # Never retry auth failures.
                return result

            if error_type in (ErrorType.EMPTY, ErrorType.PARSING, ErrorType.API):
                # Escalate to next backend immediately.
                return result

            if error_type == ErrorType.RATE_LIMIT:
                wait = 2 ** attempt  # 2, 4, 8, ...
                logger.warning(
                    "Rate-limited by %s for %s — sleeping %ds (attempt %d/%d)",
                    backend.name, url, wait, attempt, max_retries,
                )
                time.sleep(wait)
                continue

            if error_type in (ErrorType.TIMEOUT, ErrorType.NETWORK):
                if attempt < max_retries:
                    logger.warning(
                        "Backend %r %s for %s — retrying (attempt %d/%d)",
                        backend.name, error_type.value, url, attempt, max_retries,
                    )
                    time.sleep(1.0)
                    continue
                return result

            # Unknown — one retry then give up.
            if attempt < max_retries:
                time.sleep(1.0)
                continue
            return result

        return result
