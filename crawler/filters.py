"""
crawler/filters.py
------------------
URL filtering, canonicalization, and domain restriction.

Why this module exists
----------------------
The original spider had a single 15-line ``_is_documentation_url()`` function
that only filtered file extensions and 3 hardcoded path segments.  It missed:

  - UTM/tracking parameters → same page crawled multiple times
  - Social / auth / account pages → noise in knowledge base
  - Alternate domains → crawl escaping to unrelated sites
  - Fragment-only links → ``/page#section`` treated as new URL

This module replaces that with a composable, fully configurable filtering layer.

Classes
-------
URLCanonicalizer    Strip tracking params, fragments, trailing slashes.
URLFilter           Decide whether a URL should be crawled.
DomainRestriction   Configurable allow/block domain logic.

Dependencies        : stdlib only (urllib, re)
"""

from __future__ import annotations

import re
from urllib.parse import (
    ParseResult,
    parse_qs,
    urlencode,
    urlparse,
    urlunparse,
)

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Tracking parameters to strip from all URLs
# ---------------------------------------------------------------------------

_TRACKING_PARAMS: frozenset[str] = frozenset({
    # Google Analytics / Ads
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "utm_source_platform",
    "_ga", "_gl", "gclid", "gclsrc", "dclid",
    # Facebook
    "fbclid", "fb_action_ids", "fb_action_types",
    # Microsoft
    "msclkid",
    # Other common trackers
    "ref", "source", "referral", "mc_cid", "mc_eid",
    "igshid", "twclid", "li_fat_id",
    "WT.mc_id", "WT.srch",
})

# ---------------------------------------------------------------------------
# URL path patterns that indicate non-content pages
# ---------------------------------------------------------------------------

_IGNORE_PATH_RE: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"/login/?$", r"/signin/?$", r"/sign-in/?$",
        r"/signup/?$", r"/sign-up/?$", r"/register/?$",
        r"/logout/?$", r"/signout/?$",
        r"/privacy", r"/terms", r"/legal", r"/cookies",
        r"/cookie-policy", r"/gdpr",
        r"/share/", r"/follow", r"/clap", r"/vote", r"/like",
        r"/profile/", r"/account/", r"/settings/",
        r"/help/", r"/support/contact",
        r"/rss", r"/feed", r"/sitemap",
        r"/cdn-cgi/",
        r"/static/fonts/",
        r"/assets/img/",
        r"/wp-admin/",
        r"/wp-login",
        r"/__pycache__/",
    ]
]

# ---------------------------------------------------------------------------
# File extensions that are never worth crawling (unless PDF allowed)
# ---------------------------------------------------------------------------

_SKIP_EXTENSIONS: tuple[str, ...] = (
    ".pdf", ".zip", ".tar", ".gz", ".bz2", ".xz",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".mp4", ".webm", ".mp3", ".wav", ".ogg",
    ".exe", ".dmg", ".deb", ".rpm", ".whl", ".msi",
    ".ttf", ".woff", ".woff2", ".eot",
    ".css",   # CSS files — we want HTML pages, not stylesheets
    ".js",    # Raw JS files — not documentation
    ".json",  # JSON data files (unless it's a special docs API)
    ".xml",
    ".csv",
)

# ---------------------------------------------------------------------------
# Schemes that are not HTTP(S) and should always be skipped
# ---------------------------------------------------------------------------

_SKIP_SCHEMES: frozenset[str] = frozenset({
    "mailto", "tel", "javascript", "data", "ftp", "file",
    "about", "blob", "#",
})


# ===========================================================================
# URL Canonicalizer
# ===========================================================================

class URLCanonicalizer:
    """
    Produce a canonical form of a URL suitable for deduplication.

    Operations performed (in order):
    1. Lowercase scheme and host.
    2. Strip all known tracking query parameters.
    3. Remove URL fragment (``#section``).
    4. Strip trailing slash from path (unless path is ``/``).
    5. Sort remaining query parameters for deterministic comparison.

    Usage::

        c = URLCanonicalizer()
        url = c.normalize("https://docs.example.com/page?utm_source=email#intro")
        # → "https://docs.example.com/page"
    """

    def normalize(self, url: str) -> str:
        """
        Return the canonical form of *url*.

        Args:
            url: Raw URL string (may include tracking params, fragments).

        Returns:
            Canonical URL string.
        """
        try:
            parsed: ParseResult = urlparse(url)
        except Exception:
            return url

        # 1. Lowercase scheme and host.
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        # 2. Strip tracking params; sort the rest for determinism.
        if parsed.query:
            qs = parse_qs(parsed.query, keep_blank_values=False)
            qs_clean = {
                k: v for k, v in qs.items()
                if k.lower() not in _TRACKING_PARAMS
            }
            clean_query = urlencode(sorted(qs_clean.items()), doseq=True)
        else:
            clean_query = ""

        # 3. Strip fragment.
        # 4. Strip trailing slash (but keep root "/" intact).
        path = parsed.path.rstrip("/") or "/"

        canonical = urlunparse((scheme, netloc, path, "", clean_query, ""))
        return canonical


# ===========================================================================
# Domain Restriction
# ===========================================================================

class DomainRestriction:
    """
    Enforce which domains the crawler is allowed to visit.

    Modes (checked in order of specificity):
    - ``allowed_prefixes`` — URL must start with one of these strings.
    - ``allowed_domains``  — URL's netloc must be in this set.
    - ``same_domain_only`` — URL's netloc must match the start URL's netloc.

    If none of the lists are populated, ``same_domain_only=True`` is the
    implicit default.

    Args:
        start_url        : The root URL of the crawl (for same-domain check).
        allowed_domains  : Explicit set of allowed domain names.
        allowed_prefixes : Explicit set of allowed URL prefixes.
    """

    def __init__(
        self,
        start_url: str,
        allowed_domains: list[str] | None = None,
        allowed_prefixes: list[str] | None = None,
    ) -> None:
        self._start_netloc: str = urlparse(start_url).netloc.lower()
        self._allowed_domains: frozenset[str] = frozenset(
            d.lower() for d in (allowed_domains or settings.crawl_allowed_domains)
        )
        self._allowed_prefixes: tuple[str, ...] = tuple(
            allowed_prefixes or settings.crawl_allowed_prefixes
        )

    def is_allowed(self, url: str) -> bool:
        """
        Return True if *url* is within the allowed domain/prefix scope.

        Args:
            url: Canonical URL to check.

        Returns:
            True if the URL may be crawled.
        """
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()

        # Prefix restriction takes precedence (most specific).
        if self._allowed_prefixes:
            return any(url.startswith(p) for p in self._allowed_prefixes)

        # Explicit domain allowlist.
        if self._allowed_domains:
            return netloc in self._allowed_domains

        # Default: same domain as start URL (including www. variant matching).
        return netloc == self._start_netloc


# ===========================================================================
# URL Filter
# ===========================================================================

class URLFilter:
    """
    Determine whether a URL should be added to the crawl queue.

    Checks performed (all must pass):
    1. Scheme is HTTP or HTTPS.
    2. File extension is not a binary/media file.
    3. URL path does not match any ignore pattern.
    4. URL is within the allowed domain scope.

    Args:
        domain_restriction : A configured :class:`DomainRestriction` instance.
        allow_pdf          : If True, ``*.pdf`` URLs are allowed (default: settings).
    """

    def __init__(
        self,
        domain_restriction: DomainRestriction,
        allow_pdf: bool | None = None,
    ) -> None:
        self._domain = domain_restriction
        self._allow_pdf: bool = (
            allow_pdf if allow_pdf is not None else settings.crawl_allow_pdf
        )

    def should_crawl(self, url: str) -> tuple[bool, str]:
        """
        Return ``(True, "")`` if the URL should be crawled, else ``(False, reason)``.

        Args:
            url: Canonical URL to evaluate.

        Returns:
            (should_crawl, reason_if_rejected)
        """
        parsed = urlparse(url)

        # 1. Scheme check.
        if parsed.scheme in _SKIP_SCHEMES or parsed.scheme not in ("http", "https"):
            return False, f"scheme={parsed.scheme!r}"

        # 2. Extension check.
        path_lower = parsed.path.lower()
        skip_exts = _SKIP_EXTENSIONS
        if self._allow_pdf:
            skip_exts = tuple(e for e in skip_exts if e != ".pdf")
        if any(path_lower.endswith(ext) for ext in skip_exts):
            ext = next((e for e in skip_exts if path_lower.endswith(e)), "")
            return False, f"extension={ext!r}"

        # 3. Path pattern check.
        for pattern in _IGNORE_PATH_RE:
            if pattern.search(parsed.path):
                return False, f"path matches ignore pattern {pattern.pattern!r}"

        # 4. Domain restriction.
        if not self._domain.is_allowed(url):
            return False, f"domain={parsed.netloc!r} not in allowed scope"

        return True, ""
