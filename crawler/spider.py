"""
crawler/spider.py
-----------------
Production-grade documentation ingestion spider — refactored orchestrator.

Purpose
-------
Recursively crawl a documentation website, clean and extract text, convert
each page to structured Markdown, write Markdown + metadata.json to the
knowledge base directory, and produce a detailed ingestion report.

Architecture
------------
This file is now a thin orchestrator that delegates to focused sub-modules:

    filters.py     — URL canonicalization, filtering, domain restriction
    politeness.py  — robots.txt compliance + per-domain rate limiting
    router.py      — intelligent backend selection + smart retry
    validator.py   — content quality validation
    extractor.py   — link extraction (HTML + Markdown) + Markdown builder
    queue.py       — BFS/DFS/priority queue with deduplication
    report.py      — structured per-URL event logging + JSON output

Public API (unchanged — UI compatibility preserved)
---------------------------------------------------
    class DocumentationSpider:
        __init__(start_url, max_depth, max_pages, knowledge_base)
        run() -> IngestionReport

    def crawl(url, max_depth, max_pages) -> IngestionReport

Dependencies : crawler.*, config.settings, config.logging_config
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from config.logging_config import get_logger
from config.settings import settings
from crawler.extractor import (
    LinkExtractor,
    MarkdownBuilder,
    content_hash,
    library_name,
    write_document,
)
from crawler.filters import DomainRestriction, URLCanonicalizer, URLFilter
from crawler.politeness import CrawlLimiter, RobotsChecker
from crawler.queue import CrawlQueue, QueueStrategy
from crawler.report import CrawlEvent, IngestionReport
from crawler.router import BackendRouter
from crawler.validator import ContentValidator

logger = get_logger(__name__)


# ===========================================================================
# DocumentationSpider
# ===========================================================================

class DocumentationSpider:
    """
    Recursively crawl a documentation website and ingest all pages.

    Args:
        start_url      : Root URL of the documentation to crawl.
        max_depth      : Maximum link-following depth (default from settings).
        max_pages      : Hard cap on pages crawled (0 = unlimited).
        knowledge_base : Path to the knowledge_base root directory.
    """

    def __init__(
        self,
        start_url: str,
        max_depth: Optional[int] = None,
        max_pages: int = 0,
        knowledge_base: Optional[Path] = None,
    ) -> None:
        # --- Canonicalize the start URL ---
        self._canonicalizer = URLCanonicalizer()
        self.start_url      = self._canonicalizer.normalize(start_url)
        self.max_depth      = max_depth if max_depth is not None else settings.max_depth
        self.max_pages      = max_pages
        self.kb_dir         = knowledge_base or settings.knowledge_base_dir
        self.library        = library_name(start_url)

        # --- Sub-module wiring ---
        domain_restriction = DomainRestriction(self.start_url)
        self._filter    = URLFilter(domain_restriction)
        self._robots    = RobotsChecker()
        self._limiter   = CrawlLimiter()
        self._router    = BackendRouter()
        self._validator = ContentValidator()
        self._extractor = LinkExtractor()
        self._builder   = MarkdownBuilder()

        # --- Queue & Report ---
        self._queue  = CrawlQueue(
            strategy=QueueStrategy.BFS,
            max_depth=self.max_depth,
            max_pages=max_pages,
        )
        self.report = IngestionReport(
            start_url=self.start_url,
            library=self.library,
        )

        logger.info(
            "Spider initialised | url=%s | library=%s | max_depth=%s | max_pages=%s",
            self.start_url, self.library, self.max_depth, max_pages or "unlimited",
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> IngestionReport:
        """
        Start the BFS crawl from ``start_url`` and return an ingestion report.

        Returns:
            :class:`IngestionReport` — statistics and per-URL event log.
        """
        logger.info("Starting crawl: %s", self.start_url)

        # Seed the queue with the start URL.
        self._queue.push(self.start_url, depth=0)
        self._queue.mark_visited(self.start_url)

        while not self._queue.is_empty():
            entry = self._queue.pop()
            if entry is None:
                break

            # Page cap check.
            if self._queue.at_page_limit():
                logger.info("Max pages (%d) reached — stopping.", self.max_pages)
                break

            url = entry.url

            # ── 1. URL filtering ──────────────────────────────────────
            ok, filter_reason = self._filter.should_crawl(url)
            if not ok:
                self.report.record(CrawlEvent(
                    url=url, status="filtered", reason=filter_reason, depth=entry.depth,
                ))
                logger.debug("Filtered: %s (%s)", url, filter_reason)
                continue

            # ── 2. Robots.txt check ───────────────────────────────────
            robots_ok, robots_reason = self._robots.allowed(url)
            if not robots_ok:
                self.report.record(CrawlEvent(
                    url=url, status="skipped", reason=robots_reason, depth=entry.depth,
                ))
                logger.info("Skipped (robots.txt): %s", url)
                continue

            # ── 3. Politeness delay ───────────────────────────────────
            robots_delay = self._robots.crawl_delay(url)
            self._limiter.wait(url, robots_delay=robots_delay)

            # ── 4. Fetch with intelligent router ──────────────────────
            t0 = time.monotonic()
            result = self._router.fetch(url)
            fetch_latency = (time.monotonic() - t0) * 1000

            if not result.success:
                self.report.record(CrawlEvent(
                    url=url,
                    status="failed",
                    reason=result.error,
                    backend=result.backend,
                    depth=entry.depth,
                    latency_ms=fetch_latency,
                    error_type=result.error_type,
                ))
                logger.warning(
                    "Fetch failed: %s | backend=%s | error=%s | type=%s",
                    url, result.backend, result.error, result.error_type,
                )
                continue

            # ── 5. Content validation ─────────────────────────────────
            validation = self._validator.is_valid(result.raw_text, url)
            if not validation.valid:
                self.report.record(CrawlEvent(
                    url=url,
                    status="skipped",
                    reason=f"content validation failed: {validation.reason}",
                    backend=result.backend,
                    depth=entry.depth,
                    latency_ms=fetch_latency,
                ))
                logger.debug("Rejected content at %s: %s", url, validation.reason)
                continue

            # ── 6. Content-hash deduplication ─────────────────────────
            chash = content_hash(result.raw_text)
            if not self._queue.add_content_hash(chash):
                self.report.record(CrawlEvent(
                    url=url, status="filtered", reason="duplicate content hash", depth=entry.depth,
                ))
                logger.debug("Duplicate content, skipping: %s", url)
                continue

            # ── 7. Link extraction (before writing) ───────────────────
            new_links = self._extractor.extract(
                result,
                should_crawl_fn=self._filter.should_crawl,
            )
            # Canonicalize and enqueue discovered links.
            canonical_links = [self._canonicalizer.normalize(lnk) for lnk in new_links]
            enqueued = self._queue.push_batch(
                canonical_links,
                depth=entry.depth + 1,
                parent_url=url,
            )
            # Mark all as visited to prevent re-enqueuing.
            for lnk in canonical_links:
                self._queue.mark_visited(lnk)

            # ── 8. Persist to knowledge base ──────────────────────────
            try:
                write_document(result, self.library, self.kb_dir, self._builder)
                self._queue.mark_success()

                self.report.record(CrawlEvent(
                    url=url,
                    status="success",
                    backend=result.backend,
                    depth=entry.depth,
                    latency_ms=fetch_latency,
                    chars_extracted=len(result.raw_text),
                    links_discovered=len(new_links),
                ))

                logger.info(
                    "[%d] Ingested: %s | backend=%s | %d chars | %d links | %.0fms",
                    self.report.pages_crawled,
                    url,
                    result.backend,
                    len(result.raw_text),
                    len(new_links),
                    fetch_latency,
                )

            except Exception as exc:
                self.report.record(CrawlEvent(
                    url=url,
                    status="failed",
                    reason=f"write_document failed: {exc}",
                    backend=result.backend,
                    depth=entry.depth,
                    latency_ms=fetch_latency,
                ))
                logger.error("Failed to write document for %s: %s", url, exc, exc_info=True)
                continue

        # ── Finalise & write JSON report ──────────────────────────────
        self.report.finalise()
        logger.info("Crawl complete.\n%s", self.report.extended_summary())

        # Write structured JSON report beside the knowledge base.
        try:
            report_path = self.kb_dir / self.library / "crawl_report.json"
            self.report.write_json(report_path)
            logger.info("Crawl report written: %s", report_path)
        except Exception as exc:
            logger.warning("Could not write crawl_report.json: %s", exc)

        return self.report


# ===========================================================================
# Public convenience function (unchanged API)
# ===========================================================================

def crawl(
    url: str,
    max_depth: Optional[int] = None,
    max_pages: int = 0,
) -> IngestionReport:
    """
    Public convenience function — crawl *url* and return the ingestion report.

    Args:
        url       : Documentation root URL to crawl.
        max_depth : Override the default crawl depth from settings.
        max_pages : Hard cap on crawled pages (0 = unlimited).

    Returns:
        :class:`IngestionReport` — crawl statistics and per-URL event log.
    """
    spider = DocumentationSpider(
        start_url=url,
        max_depth=max_depth,
        max_pages=max_pages,
    )
    return spider.run()


# ===========================================================================
# CLI entry point
# ===========================================================================

if __name__ == "__main__":
    import sys
    from config.logging_config import setup_logging

    setup_logging(log_level=settings.log_level)

    if len(sys.argv) < 2:
        print("Usage: python -m crawler.spider <documentation_url> [max_depth] [max_pages]")
        sys.exit(1)

    _url       = sys.argv[1]
    _depth     = int(sys.argv[2]) if len(sys.argv) > 2 else None
    _max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    _report    = crawl(_url, max_depth=_depth, max_pages=_max_pages)
    print(_report.summary())
