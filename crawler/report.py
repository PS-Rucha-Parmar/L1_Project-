"""
crawler/report.py
-----------------
Structured crawl reporting and session logging.

Why this module exists
----------------------
The original IngestionReport had aggregate counters (total, crawled, failed, etc.)
but no per-URL event data.  When page 47 of 200 failed, you had to grep through
rotating log files to find out why, which backend was tried, how long it took,
and how many links it discovered.

This module introduces:

  CrawlEvent      — a structured record for every URL attempt.
  IngestionReport — extended with per-event log and JSON serialisation.

The report can be written to ``crawl_report.json`` beside the knowledge base
for post-mortem analysis, feeding dashboards, or debugging reruns.

Backward compatibility
----------------------
``IngestionReport`` preserves the original field names and ``summary()`` method
so that ``ui/app.py`` and any other callers work without modification.

Dependencies    : stdlib (dataclass, json, datetime)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from crawler.backends.base import ErrorType


# ===========================================================================
# CrawlEvent — one record per URL attempt
# ===========================================================================

@dataclass
class CrawlEvent:
    """
    A structured record of a single URL crawl attempt.

    Every URL processed by the spider produces exactly one CrawlEvent which is
    appended to ``IngestionReport.events``.  This gives a complete audit trail
    of the crawl session.

    Fields
    ------
    url             : Canonical URL attempted.
    status          : Outcome: "success", "skipped", "failed", "filtered".
    reason          : Human-readable explanation (especially for non-success).
    backend         : Backend that produced the final result (empty if filtered).
    depth           : Depth at which this URL was discovered.
    retries         : Number of retry attempts made (across all backends).
    latency_ms      : Total time spent fetching (across all attempts).
    chars_extracted : Character count of extracted text (0 on failure).
    links_discovered: Number of new child links found.
    error_type      : Structured error category (None on success/filtered).
    timestamp       : ISO-8601 UTC timestamp of the attempt.
    """

    url:              str
    status:           Literal["success", "skipped", "failed", "filtered"]
    reason:           str                    = ""
    backend:          str                    = ""
    depth:            int                    = 0
    retries:          int                    = 0
    latency_ms:       float                  = 0.0
    chars_extracted:  int                    = 0
    links_discovered: int                    = 0
    error_type:       Optional[ErrorType]    = None
    timestamp:        str                    = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        """Serialise to a JSON-compatible dictionary."""
        return {
            "url":              self.url,
            "status":           self.status,
            "reason":           self.reason,
            "backend":          self.backend,
            "depth":            self.depth,
            "retries":          self.retries,
            "latency_ms":       round(self.latency_ms, 1),
            "chars_extracted":  self.chars_extracted,
            "links_discovered": self.links_discovered,
            "error_type":       self.error_type.value if self.error_type else None,
            "timestamp":        self.timestamp,
        }


# ===========================================================================
# IngestionReport — aggregate statistics + event log
# ===========================================================================

@dataclass
class IngestionReport:
    """
    Running statistics for a single crawl session.

    Backward-compatible fields (used by ui/app.py)
    -----------------------------------------------
    total_pages_attempted, pages_crawled, pages_skipped,
    duplicates_removed, markdown_files_created, failed_pages, failed_urls.

    New fields
    ----------
    events : list[CrawlEvent] — one record per URL processed.
    """

    # ── Original fields (preserved for backward compatibility) ──────────────
    total_pages_attempted:  int       = 0
    pages_crawled:          int       = 0
    pages_skipped:          int       = 0
    duplicates_removed:     int       = 0
    markdown_files_created: int       = 0
    failed_pages:           int       = 0
    failed_urls:            list[str] = field(default_factory=list)

    # ── New fields ──────────────────────────────────────────────────────────
    events:           list[CrawlEvent] = field(default_factory=list)
    start_time:       str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    end_time:         str = ""
    start_url:        str = ""
    library:          str = ""

    # ------------------------------------------------------------------
    # Event recording
    # ------------------------------------------------------------------

    def record(self, event: CrawlEvent) -> None:
        """Append a :class:`CrawlEvent` and update aggregate counters."""
        self.events.append(event)

        if event.status == "success":
            self.pages_crawled += 1
            self.markdown_files_created += 1
            self.total_pages_attempted += 1

        elif event.status == "failed":
            self.failed_pages += 1
            self.failed_urls.append(event.url)
            self.total_pages_attempted += 1

        elif event.status == "skipped":
            self.pages_skipped += 1
            self.total_pages_attempted += 1

        elif event.status == "filtered":
            # Filtered URLs are not counted as "attempted" — they never
            # even entered the fetch pipeline.
            self.duplicates_removed += 1

    # ------------------------------------------------------------------
    # Presentation
    # ------------------------------------------------------------------

    def summary(self) -> str:
        """Return the original box-style summary string (UI-compatible)."""
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

    def extended_summary(self) -> str:
        """Return a more detailed summary including backend and error breakdown."""
        lines = [self.summary()]

        # Backend success distribution.
        backend_counts: dict[str, int] = {}
        for evt in self.events:
            if evt.status == "success" and evt.backend:
                backend_counts[evt.backend] = backend_counts.get(evt.backend, 0) + 1
        if backend_counts:
            lines.append("Backend distribution:")
            for name, count in sorted(backend_counts.items(), key=lambda x: -x[1]):
                lines.append(f"  {name}: {count} pages")

        # Error type distribution.
        error_counts: dict[str, int] = {}
        for evt in self.events:
            if evt.error_type:
                key = evt.error_type.value
                error_counts[key] = error_counts.get(key, 0) + 1
        if error_counts:
            lines.append("Error breakdown:")
            for err, count in sorted(error_counts.items(), key=lambda x: -x[1]):
                lines.append(f"  {err}: {count}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def finalise(self) -> None:
        """Record the end timestamp (call at the end of the crawl)."""
        self.end_time = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """Serialise the full report to a JSON-compatible dict."""
        return {
            "start_url":              self.start_url,
            "library":                self.library,
            "start_time":             self.start_time,
            "end_time":               self.end_time,
            "total_pages_attempted":  self.total_pages_attempted,
            "pages_crawled":          self.pages_crawled,
            "pages_skipped":          self.pages_skipped,
            "duplicates_removed":     self.duplicates_removed,
            "markdown_files_created": self.markdown_files_created,
            "failed_pages":           self.failed_pages,
            "failed_urls":            self.failed_urls,
            "events":                 [e.to_dict() for e in self.events],
        }

    def write_json(self, path: Path) -> None:
        """
        Write the full report as JSON to *path*.

        Args:
            path: Destination file path (created if not exists).
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fp:
            json.dump(self.to_dict(), fp, indent=2, ensure_ascii=False)
