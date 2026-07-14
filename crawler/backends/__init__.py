"""
crawler/backends/__init__.py
----------------------------
Re-exports the public backend interface so callers can do:

    from crawler.backends import CrawlResult, ErrorType, _BaseCrawler
"""

from crawler.backends.base import (
    CrawlResult,
    ErrorType,
    _BaseCrawler,
)

__all__ = ["CrawlResult", "ErrorType", "_BaseCrawler"]
