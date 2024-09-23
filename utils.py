import re

def is_product_url(url):
    product_patterns = [
        r'/product/',
        r'/item/',
        r'/p/',
        r'/[A-Za-z0-9-]+/dp/',  # Amazon-like pattern
        r'/[A-Za-z0-9-]+-p\d+',  # Common pattern with product ID
    ]
    
    for pattern in product_patterns:
        if re.search(pattern, url):
            return True
    return False