from crawler.spider import crawl
import logging

logging.basicConfig(level=logging.DEBUG)

print("Starting test crawl...")
report = crawl("https://console.groq.com/docs/quickstart", max_depth=1, max_pages=3)
print(report.summary())
