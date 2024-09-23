import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Crawler:
    def __init__(self, domains):
        self.domains = domains
        self.product_urls = {domain: set() for domain in domains}
        self.url_patterns = ['/product/', '/item/', '/p/']

    async def fetch(self, session, url):
        try:
            async with session.get(url) as response:
                return await response.text()
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    async def crawl_domain(self, session, domain):
        homepage = f"http://{domain}"
        html = await self.fetch(session, homepage)
        if html:
            self.parse_html(domain, homepage, html)

    def parse_html(self, domain, base_url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])
            if self.is_product_url(url):
                self.product_urls[domain].add(url)

    def is_product_url(self, url):
        path = urlparse(url).path
        return any(pattern in path for pattern in self.url_patterns)

    async def run(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.crawl_domain(session, domain) for domain in self.domains]
            await asyncio.gather(*tasks)

    def get_results(self):
        return self.product_urls