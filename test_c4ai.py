import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://console.groq.com/docs/quickstart")
        print("Success:", result.success)
        if result.markdown:
            print("Length:", len(result.markdown))
        else:
            print("No markdown")

asyncio.run(main())
