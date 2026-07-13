from crawler.spider import crawl, DocumentationSpider
import logging

logging.basicConfig(level=logging.DEBUG)

spider = DocumentationSpider(
    start_url="https://console.groq.com/docs/quickstart",
    max_depth=1,
    max_pages=1
)
# Hack to bypass robots check
spider.robots.allowed = lambda x: True

print("Starting test crawl 2...")
report = spider.run()
print(report.summary())
