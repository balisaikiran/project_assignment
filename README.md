# project_assignment

Problem Statement: Crawler for Discovering Product URLs on E-commerce Websites

Objective:
Design and implement a web crawler whose primary task is to discover and list all product URLs across multiple e-commerce websites. You will be provided with a list of domains belonging to various e-commerce platforms. The output should be a comprehensive list of product URLs found on each of the given websites.

Requirements:

Input:

A list of domains that belong to different e-commerce websites.
Example: [“example1.com”, “example2.com”, example3.com”…]
The crawler should be able to handle a minimum of 10 domains and scale to handle potentially hundreds.

Output:

A structured list or file that contains all the discovered product URLs for each domain. The output should map each domain to its corresponding list of product URLs.
The URLs should be unique and must point directly to product pages (e.g., www.example.com/product/12345).

-Key Features:

•⁠  ⁠URL Discovery: The crawler should intelligently discover product pages, considering different URL patterns that might be used by different websites (e.g., /product/, /item/, /p/).
•⁠  ⁠Scalability: The solution should be able to handle large websites with deep hierarchies and a large number of products efficiently.
•⁠  ⁠Performance: The crawler should be able to execute in parallel or asynchronously to minimize runtime, especially for large sites.
•⁠  ⁠Robustness: Handle edge cases such as:
	- Websites with infinite scrolling or dynamically loaded content.
	- Variations in URL structures across different e-commerce platforms.