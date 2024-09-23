import asyncio
from crawler import Crawler

def main():
    domains = ["example1.com", "example2.com", "example3.com"]
    crawler = Crawler(domains)
    asyncio.run(crawler.run())
    results = crawler.get_results()
    for domain, urls in results.items():
        print(f"Domain: {domain}")
        for url in urls:
            print(f"  {url}")

if __name__ == "__main__":
    main()