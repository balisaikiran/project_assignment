import asyncio
import json
from crawler import Crawler

async def main():
    # List of e-commerce domains to crawl
    domains = [
        "example1.com",
        "example2.com",
        "example3.com",
        # Add more domains here
    ]

    crawler = Crawler()
    results = await crawler.crawl_domains(domains)

    # Save results to a JSON file
    with open("product_urls.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Crawling completed. Results saved to product_urls.json")

if __name__ == "__main__":
    asyncio.run(main())