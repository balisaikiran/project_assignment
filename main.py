import asyncio
from crawler import Crawler

async def main():
    domains = [
        "https://www.veromoda.in",
        "https://www.biba.in/",
        # Add more domains here
    ]
    crawler = Crawler(max_concurrent_requests=20, max_products_per_domain=100, max_depth=3)
    results = await crawler.crawl_domains(domains)
    for result in results:
        if result:
            print(f"Found {len(result)} product URLs")

if __name__ == "__main__":
    asyncio.run(main())