import re

def is_product_url(url):
    # Refine the patterns for product URLs
    product_patterns = [r"/product/.*", r"/p/.*", r"/item/.*", r"/shop/.*", r"/products/.*"]

    for pattern in product_patterns:
        if re.search(pattern, url):
            return True
    return False
