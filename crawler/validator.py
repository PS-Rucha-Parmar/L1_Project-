"""
crawler/validator.py
--------------------
Content quality validation — decide whether extracted text is worth ingesting.

Why this module exists
----------------------
Without validation, the following types of pages silently enter the knowledge
base and degrade retrieval quality:

  - Error pages (404/403 that return HTTP 200 with error text)
  - Login walls / authentication pages
  - CAPTCHA challenge pages
  - Cookie consent walls
  - Navigation-only pages (table of contents with no real content)
  - Near-empty pages (< 150 characters of actual text)

This module provides a single ``ContentValidator.is_valid()`` method that
checks for all of these conditions using fast heuristic pattern matching.

Dependencies    : re (stdlib only)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from config.logging_config import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Rejection patterns
# ---------------------------------------------------------------------------

# Text patterns that indicate an error page (HTTP 200 with error content).
_ERROR_PAGE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)\b(404|page\s+not\s+found)\b"),
    re.compile(r"(?i)\b(403|forbidden|access\s+denied)\b"),
    re.compile(r"(?i)\b(500|internal\s+server\s+error)\b"),
    re.compile(r"(?i)\bthis\s+page\s+(does\s+not\s+exist|could\s+not\s+be\s+found)\b"),
    re.compile(r"(?i)\bsorry,\s+(this\s+page|the\s+page)\b"),
]

# Text patterns indicating CAPTCHA or bot detection.
_CAPTCHA_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)verify\s+you\s+are\s+(human|not\s+a\s+robot)"),
    re.compile(r"(?i)i\s+am\s+not\s+a\s+robot"),
    re.compile(r"(?i)complete\s+the\s+captcha"),
    re.compile(r"(?i)cloudflare\s+ray\s+id"),
    re.compile(r"(?i)please\s+enable\s+javascript\s+and\s+cookies"),
    re.compile(r"(?i)ddos\s+protection\s+by\s+cloudflare"),
]

# Text patterns indicating a cookie consent wall.
_COOKIE_WALL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)accept\s+all\s+cookies"),
    re.compile(r"(?i)we\s+use\s+cookies\s+to"),
    re.compile(r"(?i)this\s+site\s+uses\s+cookies"),
    re.compile(r"(?i)by\s+clicking\s+(accept|agree),\s+you"),
    re.compile(r"(?i)manage\s+cookie\s+(preferences|settings)"),
]

# Text patterns indicating a login / auth wall.
_LOGIN_WALL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)(sign\s+in|log\s+in)\s+to\s+(continue|access|view)"),
    re.compile(r"(?i)you\s+(must|need\s+to)\s+(log\s+in|sign\s+in|be\s+logged\s+in)"),
    re.compile(r"(?i)please\s+(log\s+in|sign\s+in)\s+to"),
    re.compile(r"(?i)create\s+an?\s+account\s+to\s+(continue|access)"),
]


# ---------------------------------------------------------------------------
# Validation result
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """The outcome of a content quality check."""
    valid: bool
    reason: str = ""

    def __bool__(self) -> bool:
        return self.valid


# ===========================================================================
# Content Validator
# ===========================================================================

class ContentValidator:
    """
    Check whether extracted page content is worth ingesting into the knowledge base.

    Checks (in order, short-circuit on first failure):
    1. Minimum content length (character count).
    2. Minimum word count.
    3. Error page detection.
    4. CAPTCHA detection.
    5. Cookie consent wall detection.
    6. Login wall detection.
    7. Navigation page heuristic (link-text ratio too high).

    Args:
        min_chars : Minimum character count for valid content.
        min_words : Minimum word count for valid content.
    """

    def __init__(
        self,
        min_chars: int | None = None,
        min_words: int | None = None,
    ) -> None:
        from config.settings import settings  # Avoid circular at module level
        self._min_chars: int = min_chars if min_chars is not None else settings.crawl_min_content_chars
        self._min_words: int = min_words if min_words is not None else settings.crawl_min_content_words

    def is_valid(self, text: str, url: str = "") -> ValidationResult:
        """
        Return a :class:`ValidationResult` for *text*.

        Args:
            text : Extracted content to validate.
            url  : Source URL (used only for log messages).

        Returns:
            ValidationResult with ``valid=True`` or ``valid=False, reason=...``.
        """
        # 1. Minimum length checks.
        if len(text) < self._min_chars:
            return ValidationResult(
                False,
                f"content too short ({len(text)} chars < {self._min_chars})",
            )

        words = text.split()
        if len(words) < self._min_words:
            return ValidationResult(
                False,
                f"too few words ({len(words)} < {self._min_words})",
            )

        # Use first 2000 chars for pattern checks (faster, avoids huge regex on docs).
        sample = text[:2000]

        # 2. Error page detection.
        # Only flag if error pattern appears near the start AND content is short.
        if len(words) < 100:
            for pattern in _ERROR_PAGE_PATTERNS:
                if pattern.search(sample):
                    return ValidationResult(
                        False,
                        f"error page detected (pattern: {pattern.pattern!r})",
                    )

        # 3. CAPTCHA detection.
        for pattern in _CAPTCHA_PATTERNS:
            if pattern.search(sample):
                return ValidationResult(
                    False,
                    f"CAPTCHA/bot-detection page (pattern: {pattern.pattern!r})",
                )

        # 4. Cookie consent wall.
        for pattern in _COOKIE_WALL_PATTERNS:
            if pattern.search(sample):
                # Cookie banners sometimes appear alongside real content.
                # Only reject if the total word count is very low.
                if len(words) < 150:
                    return ValidationResult(
                        False,
                        f"cookie consent wall (pattern: {pattern.pattern!r})",
                    )

        # 5. Login wall.
        for pattern in _LOGIN_WALL_PATTERNS:
            if pattern.search(sample):
                if len(words) < 200:
                    return ValidationResult(
                        False,
                        f"login/auth wall (pattern: {pattern.pattern!r})",
                    )

        # 6. Navigation-only page heuristic.
        # Markdown link pattern: [text](url) — count how much of the text is links.
        markdown_link_re = re.compile(r"\[([^\]]+)\]\([^)]+\)")
        link_texts = markdown_link_re.findall(text)
        link_char_count = sum(len(t) for t in link_texts)
        total_chars = len(text.replace(" ", "").replace("\n", ""))
        if total_chars > 0:
            link_ratio = link_char_count / total_chars
            if link_ratio > 0.75 and len(words) < 300:
                return ValidationResult(
                    False,
                    f"navigation-only page (link ratio={link_ratio:.0%})",
                )

        return ValidationResult(True)
