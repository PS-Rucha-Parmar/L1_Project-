"""
crawler/backends/base.py
------------------------
Foundation data models and abstract base class shared by every crawler backend.

Why this file exists
--------------------
The original spider.py combined data models, backend logic, routing, queuing, and
orchestration in one 844-line file.  This module extracts only the contracts so
each backend can be written, tested, and swapped independently.

Classes
-------
ErrorType       Structured error categories (replaces raw exception strings).
CrawlResult     The single value a backend returns for one URL fetch.
_BaseCrawler    Abstract interface every backend must implement.

Dependencies    : stdlib only (enum, dataclass)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Error taxonomy
# ---------------------------------------------------------------------------

class ErrorType(str, Enum):
    """
    Structured classification of crawl failures.

    Using a string-enum means values are JSON-serialisable without extra steps,
    and are human-readable when printed to logs.
    """

    NETWORK     = "network"       # TCP/DNS failure, connection refused
    TIMEOUT     = "timeout"       # Request exceeded the configured timeout
    RATE_LIMIT  = "rate_limit"    # HTTP 429 or explicit backoff signal
    AUTH        = "auth"          # HTTP 401/403 – credentials required
    EXTRACTION  = "extraction"    # Backend could not extract meaningful text
    PARSING     = "parsing"       # HTML/Markdown parsing error
    API         = "api"           # Cloud API (Firecrawl) error
    EMPTY       = "empty"         # Page returned but content was empty / too short
    UNKNOWN     = "unknown"       # Catch-all


# ---------------------------------------------------------------------------
# Crawl result
# ---------------------------------------------------------------------------

@dataclass
class CrawlResult:
    """
    Encapsulates the complete output of a single URL fetch attempt.

    Fields
    ------
    url             : Canonical URL that was fetched.
    title           : Page title extracted from <title> or metadata.
    raw_text        : Extracted text content (Markdown or plain text).
    html            : Raw HTML response (empty for API-only backends like Firecrawl).
    success         : True if text was successfully extracted.
    error           : Human-readable error message (empty on success).
    error_type      : Structured error category (None on success).
    backend         : Name of the backend that produced this result.
    latency_ms      : Wall-clock time for the fetch in milliseconds.
    status_code     : HTTP status code (0 if not applicable / unknown).
    final_url       : URL after redirects (may differ from ``url``).
    """

    url: str
    title: str
    raw_text: str
    html: str                       = ""
    success: bool                   = True
    error: str                      = ""
    error_type: Optional[ErrorType] = None
    backend: str                    = ""
    latency_ms: float               = 0.0
    status_code: int                = 0
    final_url: str                  = ""

    def __post_init__(self) -> None:
        # Populate final_url from url if not explicitly provided.
        if not self.final_url:
            self.final_url = self.url

    @classmethod
    def failure(
        cls,
        url: str,
        error: str,
        error_type: ErrorType = ErrorType.UNKNOWN,
        backend: str = "",
        latency_ms: float = 0.0,
        status_code: int = 0,
    ) -> "CrawlResult":
        """
        Convenience constructor for failed results.

        Example::

            return CrawlResult.failure(
                url=url,
                error="Connection refused",
                error_type=ErrorType.NETWORK,
                backend="trafilatura",
            )
        """
        return cls(
            url=url,
            title="",
            raw_text="",
            success=False,
            error=error,
            error_type=error_type,
            backend=backend,
            latency_ms=latency_ms,
            status_code=status_code,
        )


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class _BaseCrawler:
    """
    Abstract interface every crawler backend must implement.

    Attributes
    ----------
    name        : Unique lowercase identifier (e.g. ``"trafilatura"``).
    supports_js : True if the backend can execute JavaScript.
    cost_tier   : Relative cost indicator:
                    0 = free / local
                    1 = lightweight cloud / local browser
                    2 = heavy cloud with compute cost
                    3 = billed per-request cloud API
    """

    name: str        = "base"
    supports_js: bool = False
    cost_tier: int   = 0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """
        Return True if this backend is usable in the current environment.

        Implementations should check:
        - Required Python packages are importable.
        - Required API keys / credentials are present.
        - Required system dependencies (e.g. Playwright browsers) exist.
        """
        raise NotImplementedError

    def fetch(self, url: str) -> CrawlResult:
        """
        Fetch and extract content from *url*.

        Implementations MUST:
        - Return a :class:`CrawlResult` in all cases (never raise).
        - Populate ``backend``, ``latency_ms``, and ``status_code``.
        - Set ``html`` when the raw HTML is available (for link extraction).
        - Classify failures using :class:`ErrorType`.

        Args:
            url: The canonical URL to fetch.

        Returns:
            :class:`CrawlResult` — success or failure, always populated.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Helpers available to all implementations
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_http_error(status_code: int, message: str = "") -> ErrorType:
        """
        Map an HTTP status code to a structured :class:`ErrorType`.

        Args:
            status_code : HTTP response status code.
            message     : Optional exception message for additional context.

        Returns:
            The most appropriate :class:`ErrorType` for the failure.
        """
        if status_code in (401, 403):
            return ErrorType.AUTH
        if status_code == 429:
            return ErrorType.RATE_LIMIT
        if status_code in (408, 504):
            return ErrorType.TIMEOUT
        if 400 <= status_code < 500:
            return ErrorType.NETWORK
        if 500 <= status_code < 600:
            return ErrorType.NETWORK
        # Fallback: inspect message string
        msg_lower = message.lower()
        if "timeout" in msg_lower:
            return ErrorType.TIMEOUT
        if "connection" in msg_lower or "dns" in msg_lower:
            return ErrorType.NETWORK
        return ErrorType.UNKNOWN

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name={self.name!r} js={self.supports_js} tier={self.cost_tier}>"
        )
