import asyncio
import aiohttp
import ssl
import certifi
import logging
from url_discoverer import URLDiscoverer
from utils import is_product_url
from urllib.parse import urljoin, urlparse
import json

class Crawler:
    def __init__(self, max_concurrent_requests=10, output_file="product_urls.json"):
        self.max_concurrent_requests = max_concurrent_requests
        self.url_discoverer = URLDiscoverer()
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.output_file = output_file
        logging.basicConfig(level=logging.INFO)
        self._initialize_output_file()

    def _initialize_output_file(self):
        """Create or empty the output file at the start."""
        with open(self.output_file, 'w') as f:
            json.dump([], f)  # Create an empty list in the JSON file

    async def fetch(self, session, url):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logging.error(f"Error fetching {url}: Status {response.status}")
                    return None
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    async def crawl_domain(self, session, domain, base_domain):
        async with self.semaphore:
            logging.info(f"Crawling domain: {domain}")
            result = await self.fetch(session, domain)
            if result:
                return await self.process_html(session, result, domain, base_domain)
            return []

    async def crawl_domains(self, domains):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            tasks = []
            for domain in domains:
                parsed_url = urlparse(domain)
                base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                tasks.append(self.crawl_domain(session, domain, base_domain))
            results = await asyncio.gather(*tasks)
        return results

    async def process_html(self, session, html_content, current_url, base_domain):
        # Discover URLs from the content
        new_urls = self.url_discoverer.discover_urls(html_content, base_domain)
        product_urls = set()

        # Filter URLs to determine if they are product pages
        for url in new_urls:
            if is_product_url(url):
                product_urls.add(url)
                await self._save_to_file(url)  # Write product URL to file immediately
            else:
                # Recursively crawl non-product URLs (depth-first search)
                result = await self.crawl_domain(session, url, base_domain)
                product_urls.update(result)

        return product_urls

    async def _save_to_file(self, url):
        """Append the product URL to the JSON file."""
        try:
            with open(self.output_file, 'r+') as f:
                data = json.load(f)
                data.append(url)
                f.seek(0)
                json.dump(data, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving URL to file: {e}")
