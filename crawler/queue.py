"""
crawler/queue.py
----------------
Pluggable crawl queue with depth tracking, visited deduplication, and retry support.

Why this module exists
----------------------
The original spider used a raw ``collections.deque`` as its BFS queue.  This
worked but had several limitations:

  1. No priority support.
  2. No depth-first option.
  3. No retry queue — failed URLs were permanently lost.
  4. Queue could grow unboundedly for large sites.
  5. No observable stats (how many URLs are waiting?).

This module provides a ``CrawlQueue`` that supports:

  - Breadth-First Search (BFS, default)
  - Depth-First Search (DFS)
  - Priority queue (lower number = higher priority)
  - Max depth enforcement
  - Max pages cap
  - Visited URL deduplication
  - Content-hash deduplication (prevent storing near-identical pages)
  - Retry queue with attempt count tracking

Dependencies    : stdlib (collections, heapq, dataclass)
"""

from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Queue strategy enum
# ---------------------------------------------------------------------------

class QueueStrategy(str, Enum):
    """Traversal strategy for the crawl queue."""
    BFS      = "bfs"       # Breadth-first (default — level-by-level)
    DFS      = "dfs"       # Depth-first (stack)
    PRIORITY = "priority"  # Min-heap by priority score


# ---------------------------------------------------------------------------
# Queue entry
# ---------------------------------------------------------------------------

@dataclass(order=True)
class QueueEntry:
    """
    A single item in the crawl queue.

    Fields
    ------
    priority    : Used by the PRIORITY strategy (lower = crawled first).
    depth       : Distance from the start URL (0 = start URL itself).
    url         : Canonical URL to crawl.
    parent_url  : URL that linked to this one (for debug / logging).
    attempts    : Number of times this URL has been attempted.
    """
    priority:   int    = field(compare=True)
    depth:      int    = field(compare=False)
    url:        str    = field(compare=False)
    parent_url: str    = field(compare=False, default="")
    attempts:   int    = field(compare=False, default=0)


# ===========================================================================
# CrawlQueue
# ===========================================================================

class CrawlQueue:
    """
    Pluggable crawl queue supporting BFS, DFS, and priority-based traversal.

    Args:
        strategy        : Traversal order.
        max_depth       : Skip URLs deeper than this level.
        max_pages       : Stop after this many pages have been successfully crawled.
                          0 = unlimited.
        max_retries     : Maximum number of times to retry a failed URL.
    """

    def __init__(
        self,
        strategy: QueueStrategy = QueueStrategy.BFS,
        max_depth: Optional[int] = None,
        max_pages: int = 0,
        max_retries: int = 1,
    ) -> None:
        self._strategy   = strategy
        self._max_depth  = max_depth if max_depth is not None else settings.max_depth
        self._max_pages  = max_pages
        self._max_retries = max_retries

        # The active queue — data structure depends on strategy.
        self._queue: deque[QueueEntry] | list[QueueEntry]
        if strategy == QueueStrategy.PRIORITY:
            self._queue = []  # min-heap
        else:
            self._queue = deque()

        # State tracking
        self._visited: set[str]        = set()   # canonical URLs already processed
        self._content_hashes: set[str] = set()   # SHA-256 of extracted content
        self._retry_queue: deque[QueueEntry] = deque()

        # Stats
        self._pages_crawled: int  = 0
        self._pages_skipped: int  = 0
        self._duplicates:    int  = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def push(self, url: str, depth: int = 0, priority: int = 0, parent_url: str = "") -> bool:
        """
        Add *url* to the queue if it has not been visited and depth is within limit.

        Args:
            url       : Canonical URL to enqueue.
            depth     : Crawl depth (0 = start URL).
            priority  : Used by PRIORITY strategy (lower = higher priority).
            parent_url: URL that discovered this link (for tracing).

        Returns:
            True if the URL was enqueued, False if it was rejected.
        """
        if url in self._visited:
            self._duplicates += 1
            return False

        if depth > self._max_depth:
            self._pages_skipped += 1
            logger.debug("Max depth %d reached, skipping: %s", self._max_depth, url)
            return False

        entry = QueueEntry(priority=priority, depth=depth, url=url, parent_url=parent_url)
        self._enqueue(entry)
        return True

    def push_batch(self, urls: list[str], depth: int, parent_url: str = "") -> int:
        """
        Enqueue multiple URLs at the same depth.

        Args:
            urls      : List of canonical URLs to enqueue.
            depth     : Depth at which these URLs were discovered.
            parent_url: URL that discovered these links.

        Returns:
            Number of URLs actually enqueued.
        """
        count = 0
        for url in urls:
            if self.push(url, depth=depth, parent_url=parent_url):
                count += 1
        return count

    def pop(self) -> Optional[QueueEntry]:
        """
        Remove and return the next item from the queue.

        Returns:
            :class:`QueueEntry`, or None if the queue is empty.
        """
        if self._strategy == QueueStrategy.PRIORITY:
            try:
                entry = heapq.heappop(self._queue)  # type: ignore[arg-type]
                return entry
            except IndexError:
                return self._pop_retry()
        else:
            try:
                if self._strategy == QueueStrategy.DFS:
                    entry = self._queue.pop()  # type: ignore[union-attr]
                else:
                    entry = self._queue.popleft()  # type: ignore[union-attr]
                return entry
            except IndexError:
                return self._pop_retry()

    def mark_visited(self, url: str) -> None:
        """Record *url* as visited so it is never enqueued again."""
        self._visited.add(url)

    def mark_success(self) -> None:
        """Increment the pages-crawled counter (called after successful ingestion)."""
        self._pages_crawled += 1

    def add_content_hash(self, content_hash: str) -> bool:
        """
        Register a content hash.

        Returns:
            True if this is a new hash (content not seen before).
            False if the hash already exists (duplicate content).
        """
        if content_hash in self._content_hashes:
            self._duplicates += 1
            return False
        self._content_hashes.add(content_hash)
        return True

    def enqueue_retry(self, entry: QueueEntry) -> bool:
        """
        Re-queue a failed URL for a later retry attempt.

        Args:
            entry: The failed QueueEntry.

        Returns:
            True if queued for retry, False if max retries exceeded.
        """
        if entry.attempts >= self._max_retries:
            return False
        retried = QueueEntry(
            priority=entry.priority + 10,  # Lower priority than fresh URLs
            depth=entry.depth,
            url=entry.url,
            parent_url=entry.parent_url,
            attempts=entry.attempts + 1,
        )
        self._retry_queue.append(retried)
        return True

    def at_page_limit(self) -> bool:
        """Return True if the configured max_pages limit has been reached."""
        return bool(self._max_pages and self._pages_crawled >= self._max_pages)

    def is_empty(self) -> bool:
        """Return True if both the main queue and retry queue are empty."""
        return len(self._queue) == 0 and len(self._retry_queue) == 0  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    @property
    def stats(self) -> dict:
        """Return a snapshot of queue statistics."""
        return {
            "pages_crawled":  self._pages_crawled,
            "pages_skipped":  self._pages_skipped,
            "duplicates":     self._duplicates,
            "queue_size":     len(self._queue),  # type: ignore[arg-type]
            "retry_size":     len(self._retry_queue),
            "visited_count":  len(self._visited),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _enqueue(self, entry: QueueEntry) -> None:
        """Add *entry* to the backing data structure."""
        if self._strategy == QueueStrategy.PRIORITY:
            heapq.heappush(self._queue, entry)  # type: ignore[arg-type]
        elif self._strategy == QueueStrategy.DFS:
            self._queue.append(entry)  # type: ignore[union-attr]
        else:
            self._queue.append(entry)  # type: ignore[union-attr]

    def _pop_retry(self) -> Optional[QueueEntry]:
        """Drain the retry queue when the main queue is empty."""
        try:
            return self._retry_queue.popleft()
        except IndexError:
            return None
