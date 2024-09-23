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
    def __init__(self, max_concurrent_requests=10, output_file="product_urls.json", max_products_per_domain=100, max_depth=2):
        self.max_concurrent_requests = max_concurrent_requests
        self.max_products_per_domain = max_products_per_domain  # Limit products per domain
        self.max_depth = max_depth  # Limit recursion depth
        self.url_discoverer = URLDiscoverer()
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.output_file = output_file
        self.visited_urls = set()  # Set to track visited URLs
        logging.basicConfig(level=logging.INFO)
        self._initialize_output_file()

    def _initialize_output_file(self):
        """Create or empty the output file at the start."""
        with open(self.output_file, 'w') as f:
            json.dump({}, f)  # Initialize the JSON file with an empty object

    async def fetch(self, session, url):
        """Fetch the content of a given URL."""
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

    async def crawl_domain(self, session, domain, base_domain, depth=0):
        """Crawl the domain and process its content with a depth limit."""
        if depth > self.max_depth:
            return []  # Stop recursion if maximum depth is reached

        async with self.semaphore:
            if domain in self.visited_urls:  # Skip already visited URLs
                logging.info(f"Skipping already visited domain: {domain}")
                return []

            logging.info(f"Crawling domain: {domain} at depth {depth}")
            self.visited_urls.add(domain)  # Mark this domain as visited
            result = await self.fetch(session, domain)
            if result:
                return await self.process_html(session, result, domain, base_domain, depth)
            return []

    async def crawl_domains(self, domains):
        """Crawl multiple domains."""
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            tasks = []
            for domain in domains:
                parsed_url = urlparse(domain)
                base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                tasks.append(self.crawl_domain(session, domain, base_domain))
            results = await asyncio.gather(*tasks)
            return results

    async def process_html(self, session, html_content, current_url, base_domain, depth):
        """Process the HTML content to discover new URLs and check for product pages."""
        new_urls = self.url_discoverer.discover_urls(html_content, base_domain)
        product_urls = set()

        for url in new_urls:
            if url in self.visited_urls:
                continue

            if is_product_url(url):
                logging.info(f"Product URL found: {url}")
                product_urls.add(url)
                await self._save_to_file(url, base_domain)  # Save the product URL immediately
                
                if len(product_urls) >= self.max_products_per_domain:
                    break
            else:
                # Crawl non-product URLs recursively, but limit the depth
                result = await self.crawl_domain(session, url, base_domain, depth + 1)
                product_urls.update(result)

            # Stop after 10 product URLs are found
            if len(product_urls) >= self.max_products_per_domain:
                break

        return product_urls

    async def _save_to_file(self, url, domain):
        """Append the product URL to the JSON file."""
        try:
            with open(self.output_file, 'r+') as f:
                data = json.load(f)
                if domain not in data:
                    data[domain] = []
                if url not in data[domain] and len(data[domain]) < self.max_products_per_domain:
                    data[domain].append(url)
                    f.seek(0)
                    json.dump(data, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving URL to file: {e}")
