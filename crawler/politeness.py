"""
crawler/politeness.py
---------------------
Robots.txt compliance and per-domain crawl rate limiting.

Why this module exists
----------------------
The original spider populated a ``RobotsCache`` but never enforced its result:

    if not self.robots.allowed(url):
        logger.warning("robots.txt disallows ... (bypassing)")
        # No return — continues anyway!

This is a correctness bug and a potential ToS / legal issue.  This module
replaces that with:

  1. A ``RobotsChecker`` that actually enforces disallowed URLs (configurable).
  2. A ``CrawlLimiter`` that tracks last-access time per domain and sleeps to
     respect the minimum crawl delay.
  3. Automatic reading of ``Crawl-Delay`` from robots.txt.

Configuration
-------------
  crawl_force_robots      : bool   — If True, disallowed URLs are SKIPPED.
                                     If False, a warning is logged but crawl proceeds.
  crawl_delay_seconds     : float  — Minimum seconds between requests to the same domain.

Dependencies    : stdlib (urllib.robotparser, urllib.parse, time, threading)
"""

from __future__ import annotations

import threading
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


# ===========================================================================
# Robots.txt checker
# ===========================================================================

class RobotsChecker:
    """
    Threadsafe cache of parsed robots.txt files, keyed by origin (scheme+host).

    Why cache
    ---------
    Every domain's robots.txt is fetched once and reused for the entire crawl
    session.  Without caching, a 200-page docs site would make 200 robots.txt
    requests before any real crawl work.

    Args:
        force_robots : If True, disallowed URLs are rejected.
                       If False, violations are logged but not blocked.
    """

    def __init__(self, force_robots: bool | None = None) -> None:
        self._force: bool = (
            force_robots if force_robots is not None else settings.crawl_force_robots
        )
        self._parsers: dict[str, RobotFileParser] = {}
        self._delays: dict[str, float] = {}   # domain → Crawl-Delay value
        self._lock = threading.Lock()

    def allowed(self, url: str) -> tuple[bool, str]:
        """
        Return ``(True, "")`` if crawling *url* is permitted.

        Side effect: Fetches and caches the domain's robots.txt on first call.

        Args:
            url: Canonical URL to check.

        Returns:
            (allowed, reason_if_blocked)
        """
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"

        with self._lock:
            if origin not in self._parsers:
                self._load_robots(origin)

        rp = self._parsers[origin]
        permitted = rp.can_fetch("*", url)

        if not permitted:
            reason = f"robots.txt at {origin} disallows {url!r}"
            if self._force:
                return False, reason
            else:
                logger.warning(
                    "robots.txt disallows %s — proceeding anyway (crawl_force_robots=False).",
                    url,
                )
                return True, ""

        return True, ""

    def crawl_delay(self, url: str) -> float:
        """
        Return the ``Crawl-Delay`` for the domain of *url*, or 0.0 if not set.

        Args:
            url: Any URL on the target domain.

        Returns:
            Crawl-Delay in seconds (float).
        """
        origin = _origin(url)
        return self._delays.get(origin, 0.0)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load_robots(self, origin: str) -> None:
        """Fetch and parse robots.txt for *origin* (must be called under lock)."""
        rp = RobotFileParser()
        robots_url = f"{origin}/robots.txt"
        try:
            rp.set_url(robots_url)
            rp.read()
            # Extract Crawl-Delay if present.
            delay = rp.crawl_delay("*") or 0.0
            self._delays[origin] = float(delay)
            logger.debug(
                "robots.txt loaded: %s (Crawl-Delay=%.1fs)", robots_url, delay
            )
        except Exception as exc:
            # If robots.txt cannot be fetched, assume everything is allowed.
            logger.debug("Could not fetch %s: %s — assuming allowed.", robots_url, exc)
            self._delays[origin] = 0.0
        self._parsers[origin] = rp


# ===========================================================================
# Crawl rate limiter
# ===========================================================================

class CrawlLimiter:
    """
    Enforce a minimum wait time between requests to the same domain.

    Why per-domain
    --------------
    A single crawl session may touch multiple subdomains
    (e.g. ``docs.python.org`` and ``peps.python.org``).  Throttling should be
    applied independently per domain, not globally.

    Args:
        base_delay_seconds : Minimum delay between consecutive requests to the
                             same domain.  Overridden per-domain by
                             ``RobotsChecker.crawl_delay()`` if that value is
                             larger.
    """

    def __init__(self, base_delay_seconds: float | None = None) -> None:
        self._base: float = (
            base_delay_seconds
            if base_delay_seconds is not None
            else settings.crawl_delay_seconds
        )
        self._last_access: dict[str, float] = {}
        self._lock = threading.Lock()

    def wait(self, url: str, robots_delay: float = 0.0) -> None:
        """
        Block until the minimum delay has elapsed for the domain of *url*.

        The effective delay is ``max(base_delay, robots_delay)``.

        Args:
            url          : URL about to be fetched.
            robots_delay : Optional Crawl-Delay value from robots.txt.
        """
        domain = _origin(url)
        effective_delay = max(self._base, robots_delay)

        with self._lock:
            last = self._last_access.get(domain, 0.0)
            elapsed = time.monotonic() - last
            remaining = effective_delay - elapsed

        if remaining > 0:
            logger.debug(
                "Rate-limiting %s: sleeping %.2fs (delay=%.2fs, elapsed=%.2fs)",
                domain, remaining, effective_delay, elapsed,
            )
            time.sleep(remaining)

        with self._lock:
            self._last_access[domain] = time.monotonic()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _origin(url: str) -> str:
    """Return the scheme+netloc (origin) for *url*."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
