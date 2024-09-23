import asyncio
import aiohttp
from url_discoverer import URLDiscoverer
from utils import is_product_url

class Crawler:
    def __init__(self, max_concurrent_requests=10):
        self.max_concurrent_requests = max_concurrent_requests
        self.url_discoverer = URLDiscoverer()

    async def crawl_domains(self, domains):
        results = {}
        async with aiohttp.ClientSession() as session:
            tasks = [self.crawl_domain(session, domain) for domain in domains]
            domain_results = await asyncio.gather(*tasks)
            for domain, urls in zip(domains, domain_results):
                results[domain] = urls
        return results

    async def crawl_domain(self, session, domain):
        base_url = f"https://{domain}"
        to_visit = {base_url}
        visited = set()
        product_urls = set()

        while to_visit:
            current_batch = list(to_visit)[:self.max_concurrent_requests]
            to_visit = to_visit - set(current_batch)

            tasks = [self.process_url(session, url, domain) for url in current_batch]
            batch_results = await asyncio.gather(*tasks)

            for url, new_urls, is_product in batch_results:
                visited.add(url)
                if is_product:
                    product_urls.add(url)
                to_visit.update(new_urls - visited)

        return list(product_urls)

    async def process_url(self, session, url, domain):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    new_urls = self.url_discoverer.discover_urls(content, domain)
                    is_product = is_product_url(url)
                    return url, new_urls, is_product
                else:
                    return url, set(), False
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            return url, set(), False