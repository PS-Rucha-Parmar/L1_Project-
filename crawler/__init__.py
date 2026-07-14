"""
crawler/__init__.py
-------------------
Public API for the crawler package.

Importing from this package guarantees backward compatibility regardless of
the internal module restructuring.  All callers (ui/app.py, test files, etc.)
should import from here, not from ``crawler.spider`` directly.

Usage::

    from crawler import crawl, DocumentationSpider
    from crawler import IngestionReport, CrawlEvent

"""

from crawler.spider import DocumentationSpider, crawl
from crawler.report import IngestionReport, CrawlEvent

__all__ = [
    "DocumentationSpider",
    "crawl",
    "IngestionReport",
    "CrawlEvent",
]
