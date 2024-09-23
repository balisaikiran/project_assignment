import re

def is_product_url(url):
    """Return True if the URL is likely to be a product URL."""
    # Add more patterns to match product URLs
    product_patterns = [
        r"/product/.*",       # Matches /product/12345
        r"/p/.*",             # Matches /p/12345
        r"/item/.*",          # Matches /item/12345
        r"-p.*",              # Matches URLs with -p (e.g., /shoes-p12345)
        r"/\d+\.html",        # Matches product pages ending with numbers.html
        r"/shop/.*",          # Matches /shop/product-name
        r"/detail/.*",        # Matches /detail/product-name
    ]

    for pattern in product_patterns:
        if re.search(pattern, url):
            return True
    return False
