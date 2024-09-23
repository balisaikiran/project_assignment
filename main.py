import asyncio
from crawler import Crawler

async def main():
    domains = ["https://www.biba.in/", "https://www.biba.in/"]
    crawler = Crawler()
    results = await crawler.crawl_domains(domains)
    for result in results:
        if result:
            print(result)

if __name__ == "__main__":
    asyncio.run(main())
