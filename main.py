import asyncio
import logging
from crawler import Crawler

async def main():
    domains = [
        "https://www.veromoda.in",
        "https://www.biba.in/",
        # Add more domains here
    ]
    crawler = Crawler(max_concurrent_requests=20, max_products_per_domain=100, max_depth=3, timeout=30)
    try:
        results = await crawler.crawl_domains(domains)
        for result in results:
            if result:
                logging.info(f"Found {len(result)} product URLs")
    except Exception as e:
        logging.error(f"An error occurred during crawling: {e}")
    
    logging.info("Crawling completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main())