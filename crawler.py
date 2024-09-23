import asyncio
import aiohttp
import ssl
import certifi
import logging
from url_discoverer import URLDiscoverer
from utils import is_product_url
from urllib.parse import urljoin, urlparse
import json
import time
import re

class Crawler:
    def __init__(self, max_concurrent_requests=10, output_file="product_urls.json", max_products_per_domain=100, max_depth=2, timeout=30):
        self.max_concurrent_requests = max_concurrent_requests
        self.max_products_per_domain = max_products_per_domain
        self.max_depth = max_depth
        self.url_discoverer = URLDiscoverer()
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.output_file = output_file
        self.visited_urls = set()
        self.timeout = timeout
        self.start_time = time.time()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self._initialize_output_file()

        # Add a list of patterns for URLs to ignore
        self.ignore_patterns = [
            r'privacy',
            r'return',
            r'shipping',
            r'about-us',
            r'contact',
            r'terms',
            r'faq',
            r'career'
        ]

    def _initialize_output_file(self):
        with open(self.output_file, 'w') as f:
            json.dump({}, f)

    def should_ignore_url(self, url):
        """Check if the URL should be ignored based on the ignore patterns."""
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in self.ignore_patterns)

    async def fetch(self, session, url):
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logging.error(f"Error fetching {url}: Status {response.status}")
                    return None
        except asyncio.TimeoutError:
            logging.error(f"Timeout error fetching {url}")
            return None
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    async def crawl_domain(self, session, domain, base_domain, depth=0):
        if depth > self.max_depth or (time.time() - self.start_time) > 300:  # 5 minutes timeout
            return []

        async with self.semaphore:
            if domain in self.visited_urls or self.should_ignore_url(domain):
                logging.info(f"Skipping URL: {domain}")
                return []

            logging.info(f"Crawling domain: {domain} at depth {depth}")
            self.visited_urls.add(domain)
            result = await self.fetch(session, domain)
            if result:
                return await self.process_html(session, result, domain, base_domain, depth)
            return []

    async def crawl_domains(self, domains):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            tasks = []
            for domain in domains:
                parsed_url = urlparse(domain)
                base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                tasks.append(self.crawl_domain(session, domain, base_domain))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in results if not isinstance(r, Exception)]

    async def process_html(self, session, html_content, current_url, base_domain, depth):
        new_urls = self.url_discoverer.discover_urls(html_content, base_domain)
        product_urls = set()
        tasks = []

        for url in new_urls:
            if url in self.visited_urls or self.should_ignore_url(url):
                continue

            if is_product_url(url):
                logging.info(f"Product URL found: {url}")
                product_urls.add(url)
                await self._save_to_file(url, base_domain)
                
                if len(product_urls) >= self.max_products_per_domain:
                    break
            else:
                tasks.append(asyncio.create_task(self.crawl_domain(session, url, base_domain, depth + 1)))

            if len(product_urls) >= self.max_products_per_domain:
                break

        # Process non-product URLs concurrently with a timeout
        done, pending = await asyncio.wait(tasks, timeout=60)  # 60 seconds timeout
        for task in pending:
            task.cancel()
        
        for task in done:
            try:
                result = task.result()
                product_urls.update(result)
                if len(product_urls) >= self.max_products_per_domain:
                    break
            except Exception as e:
                logging.error(f"Error processing task: {e}")

        return product_urls

    async def _save_to_file(self, url, domain):
        try:
            async with asyncio.Lock():
                with open(self.output_file, 'r+') as f:
                    data = json.load(f)
                    if domain not in data:
                        data[domain] = []
                    if url not in data[domain] and len(data[domain]) < self.max_products_per_domain:
                        data[domain].append(url)
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving URL to file: {e}")