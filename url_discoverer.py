import re
from urllib.parse import urljoin, urlparse

class URLDiscoverer:
    def __init__(self):
        self.url_pattern = re.compile(r'href=[\'"]?([^\'" >]+)')

    def discover_urls(self, html_content, base_domain):
        urls = set()
        for match in self.url_pattern.finditer(html_content):
            url = match.group(1)
            full_url = urljoin(base_domain, url)  # Join with base domain to handle relative URLs
            if self.is_valid_url(full_url, base_domain):
                urls.add(full_url)
        return urls

    def is_valid_url(self, url, base_domain):
        parsed_url = urlparse(url)
        return parsed_url.netloc == urlparse(base_domain).netloc and parsed_url.scheme in ('http', 'https')
