import asyncio
import json
from crawler import Crawler

async def main():
    # Add your list of domains here
    domains = [
        "https://in.puma.com"
    ]  
    
    crawler = Crawler(max_concurrent_requests=5)
    results = await crawler.crawl_domains(domains)
    
    product_urls = set()
    for result in results:
        if result:
            product_urls.update(result)

    # Save all product URLs to a JSON file
    with open('product_urls.json', 'w') as f:
        json.dump(list(product_urls), f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())
