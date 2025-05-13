# # """
# # Real Walmart Scraper Implementation for DealFinder AI.

# # This module implements the RealWalmartScraperAgent class that uses BeautifulSoup
# # and requests to extract actual product data from Walmart.
# # """

# # import random
# # import time
# # import logging
# # import json
# # import re
# # from typing import Dict, Any, List, Optional, Tuple

# # import requests
# # from bs4 import BeautifulSoup

# # from dealfinder.agents.base import Agent, MCPMessage
# # from dealfinder import config
# # from dealfinder.utils.logging import get_logger
# # from dealfinder.agents.gemini_agent import GeminiAgent

# # logger = get_logger("Scrapers.Walmart")

# # class RealWalmartScraperAgent(Agent):
# #     """Agent for scraping Walmart product listings with actual web scraping"""
    
# #     def __init__(self):
# #         """Initialize the Walmart scraper agent."""
# #         super().__init__("WalmartScraperAgent")
# #         self.base_url = config.WALMART_BASE_URL
        
# #         # Configure headers with default values
# #         self.headers = {
# #             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
# #             "Accept-Language": "en-US,en;q=0.5",
# #             "Accept-Encoding": "gzip, deflate, br",
# #             "Connection": "keep-alive",
# #             "Upgrade-Insecure-Requests": "1",
# #             "Cache-Control": "max-age=0",
# #         }
    
# #     def process_message(self, message: MCPMessage) -> MCPMessage:
# #         """
# #         Process search request for Walmart.
        
# #         Args:
# #             message: The incoming MCPMessage to process
            
# #         Returns:
# #             A new MCPMessage containing the search results
# #         """
# #         if message.message_type != "SEARCH_REQUEST":
# #             return MCPMessage(
# #                 sender=self.name,
# #                 receiver=message.sender,
# #                 content={"error": "Only SEARCH_REQUEST message type is supported"},
# #                 message_type="ERROR",
# #                 conversation_id=message.conversation_id
# #             )
        
# #         search_params = message.content
# #         self.logger.info(f"Searching Walmart for: {search_params}")
        
# #         try:
# #             # Convert search parameters to Walmart search query
# #             query = self._build_search_query(search_params)
            
# #             # Perform the search
# #             products = self._scrape_search_results(query, search_params)
            
# #             return MCPMessage(
# #                 sender=self.name,
# #                 receiver=message.sender,
# #                 content={
# #                     "source": "Walmart",
# #                     "query": query,
# #                     "products": products
# #                 },
# #                 message_type="SEARCH_RESPONSE",
# #                 conversation_id=message.conversation_id
# #             )
        
# #         except Exception as e:
# #             self.logger.error(f"Error scraping Walmart: {str(e)}")
# #             return MCPMessage(
# #                 sender=self.name,
# #                 receiver=message.sender,
# #                 content={"error": f"Walmart scraping error: {str(e)}"},
# #                 message_type="ERROR",
# #                 conversation_id=message.conversation_id
# #             )
    
# #     def _build_search_query(self, search_params: Dict[str, Any]) -> str:
# #         """
# #         Build search query string from parameters.
        
# #         Args:
# #             search_params: Search parameters to use for the query
            
# #         Returns:
# #             A search query string
# #         """
# #         components = []
        
# #         if "product_type" in search_params:
# #             components.append(search_params["product_type"])
        
# #         if "keywords" in search_params:
# #             if isinstance(search_params["keywords"], list):
# #                 components.extend(search_params["keywords"])
# #             else:
# #                 components.append(search_params["keywords"])
        
# #         if "brands" in search_params and search_params["brands"]:
# #             brands = search_params["brands"]
# #             if isinstance(brands, list):
# #                 components.append(" ".join(brands))
# #             else:
# #                 components.append(brands)
        
# #         if "features" in search_params and search_params["features"]:
# #             features = search_params["features"]
# #             if isinstance(features, list):
# #                 components.extend(features)
# #             else:
# #                 components.append(features)
        
# #         return " ".join(components)
    
# #     def _is_relevant_product(self, product, keywords):
# #         title = product.get("title", "").lower()
# #         return all(kw.lower() in title for kw in keywords if kw)

# #     def _scrape_search_results(self, query: str, search_params: Dict[str, Any], max_results: int = None) -> List[Dict[str, Any]]:
# #         """
# #         Scrape Walmart search results for the given query.
        
# #         Args:
# #             query: The search query string
# #             search_params: Additional search parameters
# #             max_results: Maximum number of results to return (default: from config)
            
# #         Returns:
# #             A list of product dictionaries
# #         """
# #         # Use configured max_results if not specified
# #         if max_results is None:
# #             max_results = config.MAX_PRODUCTS_PER_SOURCE
        
# #         # Construct the search URL
# #         params = {
# #             "q": query,
# #         }
        
# #         # Add price range if specified
# #         if "price_range" in search_params and search_params["price_range"]:
# #             price_range = search_params["price_range"]
# #             if isinstance(price_range, list) and len(price_range) == 2:
# #                 min_price, max_price = price_range
# #                 if min_price and max_price:
# #                     params["min_price"] = min_price
# #                     params["max_price"] = max_price
# #                 elif min_price:
# #                     params["min_price"] = min_price
# #                 elif max_price:
# #                     params["max_price"] = max_price
        
# #         # Add sorting parameter if specified
# #         if "sorting_preference" in search_params:
# #             sort_pref = search_params["sorting_preference"]
# #             if sort_pref == "price_low_to_high":
# #                 params["sort"] = "price_low"
# #             elif sort_pref == "price_high_to_low":
# #                 params["sort"] = "price_high"
# #             elif sort_pref == "rating":
# #                 params["sort"] = "best_match"
# #             elif sort_pref == "newest":
# #                 params["sort"] = "new"
        
# #         # Use a random user agent for each request
# #         current_headers = self.headers.copy()
# #         current_headers["User-Agent"] = random.choice(config.USER_AGENTS)

# #         for attempt in range(3):
# #             try:
# #                 response = requests.get(
# #                     self.base_url,
# #                     params=params,
# #                     headers=current_headers,
# #                     timeout=config.SCRAPING_TIMEOUT
# #                 )
# #                 if response.status_code == 200:
# #                     break
# #                 else:
# #                     time.sleep(2 ** attempt)
# #             except Exception as e:
# #                 self.logger.warning(f"Retrying due to error: {str(e)}")
# #                 time.sleep(2 ** attempt)
# #         else:
# #             self.logger.error("Max retries exceeded")
# #             return []

# #         soup = BeautifulSoup(response.text, 'html.parser')
# #         # always_use_gemini support
# #         if search_params.get("always_use_gemini"):
# #             self.logger.info("Gemini used for product extraction")
# #             from dealfinder.agents.gemini_agent import GeminiAgent
# #             gemini = GeminiAgent()
# #             # try product divs from HTML
# #             product_divs = soup.select('div[data-item-id]')
# #             if not product_divs:
# #                 product_divs = soup.select('.product-card')
# #             if not product_divs:
# #                 product_divs = soup.select('.search-result-gridview-item')
# #             return [gemini.extract_product_details_from_html(str(div)) for div in product_divs[:max_results]]

# #         products = self._extract_from_json_data(soup)
# #         if not products:
# #             products = self._extract_from_html(soup, max_results)
# #         # Deduplicate by product_id
# #         seen_ids = set()
# #         filtered_products = []
# #         for product in products:
# #             if not self._is_relevant_product(product, search_params.get("keywords", [])):
# #                 continue
# #             pid = product.get("product_id")
# #             if pid in seen_ids:
# #                 continue
# #             seen_ids.add(pid)
# #             product["source"] = "Walmart"
# #             self.logger.info(f"Extracted product: {product.get('title', '')} at {product.get('price', 0)} USD")
# #             filtered_products.append(product)
# #             if len(filtered_products) >= (max_results if max_results is not None else config.MAX_PRODUCTS_PER_SOURCE):
# #                 break

# #         time.sleep(random.uniform(
# #             config.SCRAPING_DELAY_MIN,
# #             config.SCRAPING_DELAY_MAX
# #         ))
# #         return filtered_products[:max_results] if max_results else filtered_products
    
# #     def _extract_from_json_data(self, soup) -> List[Dict[str, Any]]:
# #         """
# #         Extract product data from JSON embedded in the page.
        
# #         Args:
# #             soup: BeautifulSoup object of the page
            
# #         Returns:
# #             A list of product dictionaries
# #         """
# #         products = []
        
# #         try:
# #             # Look for script tags that might contain product data
# #             script_tags = soup.find_all('script', type='application/json')
            
# #             for script in script_tags:
# #                 try:
# #                     json_data = json.loads(script.string)
                    
# #                     # Scan through the JSON to find product data
# #                     if 'items' in json_data:
# #                         for item in json_data['items']:
# #                             product = self._parse_json_product(item)
# #                             if product:
# #                                 products.append(product)
                    
# #                     # Also check for 'searchContent' structure
# #                     if 'searchContent' in json_data and 'searchResultsMap' in json_data['searchContent']:
# #                         results = json_data['searchContent']['searchResultsMap']
# #                         if 'REGULAR_SEARCH' in results and 'products' in results['REGULAR_SEARCH']:
# #                             for item in results['REGULAR_SEARCH']['products']:
# #                                 product = self._parse_json_product(item)
# #                                 if product:
# #                                     products.append(product)
                
# #                 except (json.JSONDecodeError, KeyError, TypeError) as e:
# #                     # Not the JSON we're looking for, try the next script tag
# #                     continue
            
# #             return products
            
# #         except Exception as e:
# #             self.logger.error(f"Error extracting from JSON data: {str(e)}")
# #             return []
    
# #     def _parse_json_product(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
# #         """
# #         Parse product data from a JSON item.
        
# #         Args:
# #             item: JSON object containing product data
            
# #         Returns:
# #             A dictionary of product data, or None if parsing fails
# #         """
# #         try:
# #             # Extract basic product info
# #             product_id = item.get('id', item.get('productId', ''))
# #             title = item.get('title', item.get('name', ''))
            
# #             # Extract price information
# #             price = 0.0
# #             price_info = item.get('price', item.get('priceInfo', {}))
# #             if isinstance(price_info, dict):
# #                 current_price = price_info.get('currentPrice', price_info.get('displayPrice', 0))
# #                 if isinstance(current_price, (int, float)):
# #                     price = float(current_price)
# #                 elif isinstance(current_price, dict) and 'price' in current_price:
# #                     price = float(current_price['price'])
# #             elif isinstance(price_info, (int, float)):
# #                 price = float(price_info)
            
# #             # Extract URL
# #             product_url = ""
# #             if 'canonicalUrl' in item:
# #                 product_url = f"https://www.walmart.com{item['canonicalUrl']}"
# #             elif 'productPageUrl' in item:
# #                 product_url = f"https://www.walmart.com{item['productPageUrl']}"
# #             elif 'productUrl' in item:
# #                 product_url = f"https://www.walmart.com{item['productUrl']}"
            
# #             # Extract image URL
# #             image_url = ""
# #             if 'imageInfo' in item and 'thumbnailUrl' in item['imageInfo']:
# #                 image_url = item['imageInfo']['thumbnailUrl']
# #             elif 'images' in item and len(item['images']) > 0:
# #                 image_url = item['images'][0].get('url', '')
# #             elif 'image' in item:
# #                 image_url = item['image']
            
# #             # Extract rating
# #             rating = 0.0
# #             if 'averageRating' in item:
# #                 rating = float(item['averageRating'])
# #             elif 'rating' in item and 'averageRating' in item['rating']:
# #                 rating = float(item['rating']['averageRating'])
            
# #             # Extract number of reviews
# #             reviews = 0
# #             if 'numberOfReviews' in item:
# #                 reviews = int(item['numberOfReviews'])
# #             elif 'rating' in item and 'numberOfReviews' in item['rating']:
# #                 reviews = int(item['rating']['numberOfReviews'])
# #             elif 'reviewCount' in item:
# #                 reviews = int(item['reviewCount'])
            
# #             # Check if product is sponsored
# #             is_sponsored = False
# #             if 'sponsored' in item:
# #                 is_sponsored = bool(item['sponsored'])
            
# #             # Check if product is available for pickup
# #             is_pickup_today = False
# #             if 'fulfillmentBadge' in item and 'fulfillmentType' in item:
# #                 is_pickup_today = 'PICKUP' in item['fulfillmentType']
# #             elif 'fulfillment' in item and 'pickup' in item['fulfillment']:
# #                 is_pickup_today = True
# #             # Use Gemini fallback if essential fields are missing
# #             if (not title or title == "Unknown Product") or not product_url or price == 0.0:
# #                 gemini = GeminiAgent()
# #                 html_context = json.dumps(item)  # Pass the JSON item as context string
# #                 gemini_response = gemini.extract_product_details_from_html(html_context)
# #                 if isinstance(gemini_response, dict):
# #                     title = gemini_response.get("title", title)
# #                     price = gemini_response.get("price", price)
# #                     product_url = gemini_response.get("url", product_url)
# #                     image_url = gemini_response.get("image_url", image_url)

# #             # Create product dictionary
# #             product = {
# #                 "title": title,
# #                 "price": price,
# #                 "currency": "USD",
# #                 "url": product_url,
# #                 "image_url": image_url,
# #                 "rating": rating,
# #                 "reviews": reviews,
# #                 "is_sponsored": is_sponsored,
# #                 "is_pickup_today": is_pickup_today,
# #                 "product_id": product_id,
# #             }

# #             return product

# #         except Exception as e:
# #             self.logger.error(f"Error parsing JSON product: {str(e)}")
# #             return None
    
# #     def _extract_from_html(self, soup, max_results: int) -> List[Dict[str, Any]]:
# #         """
# #         Extract product data from HTML when JSON extraction fails.
        
# #         Args:
# #             soup: BeautifulSoup object of the page
# #             max_results: Maximum number of results to return
            
# #         Returns:
# #             A list of product dictionaries
# #         """
# #         products = []
        
# #         try:
# #             # Find all product divs in the search results
# #             product_divs = soup.select('div[data-item-id]')
            
# #             if not product_divs:
# #                 # Try alternate selector
# #                 product_divs = soup.select('.product-card')
            
# #             if not product_divs:
# #                 # Try another alternate selector
# #                 product_divs = soup.select('.search-result-gridview-item')
            
# #             for div in product_divs[:max_results]:
# #                 product = self._extract_product_data(div)
# #                 if product:
# #                     products.append(product)
                    
# #                     # If we've collected enough products, stop
# #                     if len(products) >= max_results:
# #                         break
            
# #             return products
            
# #         except Exception as e:
# #             self.logger.error(f"Error extracting from HTML: {str(e)}")
# #             return []
    
# #     def _extract_product_data(self, product_div) -> Optional[Dict[str, Any]]:
# #         """
# #         Extract product data from a product div element.
        
# #         Args:
# #             product_div: BeautifulSoup element containing product data
            
# #         Returns:
# #             A dictionary of product data, or None if extraction fails
# #         """
# #         try:
# #             # Extract product ID
# #             product_id = product_div.get('data-item-id', '')
# #             if not product_id:
# #                 product_id = product_div.get('data-product-id', '')

# #             # Check if the product is sponsored
# #             is_sponsored = bool(product_div.select_one('.sponsored-flag'))

# #             # Extract product title
# #             title_element = product_div.select_one('.product-title-link span')
# #             if not title_element:
# #                 title_element = product_div.select_one('.ProductPlaceholder-title')

# #             # If we still don't have a title, try other common selectors
# #             if not title_element:
# #                 title_element = product_div.select_one('span[data-automation="product-title"]')

# #             # If still no title, search for any heading element
# #             if not title_element:
# #                 for heading in product_div.select('h2, h3'):
# #                     if heading.text.strip():
# #                         title_element = heading
# #                         break

# #             title = title_element.text.strip() if title_element else "Unknown Product"

# #             # Extract product URL
# #             url_element = product_div.select_one('a.product-title-link')
# #             if not url_element:
# #                 url_element = product_div.select_one('a[href^="/ip/"]')

# #             url = "https://www.walmart.com" + url_element['href'] if url_element and 'href' in url_element.attrs else "#"

# #             # Extract product image URL
# #             img_element = product_div.select_one('img.product-image-photo')
# #             if not img_element:
# #                 img_element = product_div.select_one('img.ProductPlaceholder-image')

# #             image_url = img_element['src'] if img_element and 'src' in img_element.attrs else ""
# #             if not image_url and img_element and 'data-src' in img_element.attrs:
# #                 image_url = img_element['data-src']

# #             # Extract product price
# #             price_element = product_div.select_one('.price-main')
# #             if not price_element:
# #                 price_element = product_div.select_one('.product-price')
# #             if not price_element:
# #                 price_element = product_div.select_one('span[data-automation="product-price"]')
# #             if not price_element:
# #                 price_element = product_div.select_one('[data-price]')
# #                 if price_element and 'data-price' in price_element.attrs:
# #                     price = float(price_element['data-price'])
# #                     # Skip the text extraction below
# #                     price_extracted = True
# #                 else:
# #                     price_extracted = False
# #             else:
# #                 price_extracted = False

# #             price = 0.0
# #             if price_element and not price_extracted:
# #                 price_text = price_element.text.strip()
# #                 price = self._parse_price(price_text)

# #             # Extract product rating
# #             rating_element = product_div.select_one('.stars-reviews-count')
# #             if not rating_element:
# #                 rating_element = product_div.select_one('.ratings')

# #             rating = 0.0
# #             if rating_element:
# #                 rating_text = rating_element.text.strip()
# #                 rating_match = re.search(r'(\d+\.\d+)', rating_text)
# #                 if rating_match:
# #                     rating = float(rating_match.group(1))

# #             # Extract number of reviews
# #             reviews_element = product_div.select_one('.stars-reviews-count span')
# #             if not reviews_element:
# #                 reviews_element = product_div.select_one('.review-count')

# #             reviews = 0
# #             if reviews_element:
# #                 reviews_text = reviews_element.text.strip()
# #                 reviews_text = reviews_text.replace(',', '')
# #                 reviews_match = re.search(r'(\d+)', reviews_text)
# #                 if reviews_match:
# #                     reviews = int(reviews_match.group(1))

# #             # Check if the product has pickup today
# #             is_pickup_today = bool(product_div.select_one('.fulfillment-shipping-text'))
# #             if not is_pickup_today:
# #                 is_pickup_today = bool(product_div.select_one('.pickup-today'))

# #             # Use Gemini fallback if title is 'Unknown Product' or URL is missing or price is 0
# #             if (not title or title == "Unknown Product") or not url or price == 0.0:
# #                 try:
# #                     gemini = GeminiAgent()
# #                     html_context = str(product_div)
# #                     gemini_response = gemini.extract_product_details_from_html(html_context)
# #                     if isinstance(gemini_response, dict):
# #                         self.logger.info("Gemini used for product extraction")
# #                         self.logger.info(f"Extracted product: {gemini_response.get('title', '')} at {gemini_response.get('price', 0)} USD")
# #                         title = gemini_response.get("title", title)
# #                         price = gemini_response.get("price", price)
# #                         url = gemini_response.get("url", url)
# #                         image_url = gemini_response.get("image_url", image_url)
# #                 except Exception as e:
# #                     self.logger.error(f"Gemini fallback failed: {str(e)}")

# #             self.logger.info(f"Extracted product: {title} at {price} USD")

# #             # Create product dictionary
# #             product = {
# #                 "title": title,
# #                 "price": price,
# #                 "currency": "USD",
# #                 "url": url,
# #                 "image_url": image_url,
# #                 "rating": rating,
# #                 "reviews": reviews,
# #                 "is_sponsored": is_sponsored,
# #                 "is_pickup_today": is_pickup_today,
# #                 "product_id": product_id,
# #             }

# #             return product

# #         except Exception as e:
# #             self.logger.error(f"Error extracting product data: {str(e)}")
# #             return None
    
# #     def _parse_price(self, price_text: str) -> float:
# #         """
# #         Parse price string to float.
        
# #         Args:
# #             price_text: Price text to parse
            
# #         Returns:
# #             Parsed price as float
# #         """
# #         try:
# #             # Remove currency symbol and commas, then convert to float
# #             price_text = price_text.replace('$', '').replace(',', '')
# #             # Extract numbers using regex
# #             price_match = re.search(r'(\d+\.\d+)', price_text)
# #             if price_match:
# #                 return float(price_match.group(1))
# #             return 0.0
# #         except (ValueError, AttributeError):
# #             return 0.0
# """
# Real Walmart Scraper Implementation for DealFinder AI.

# This module implements the RealWalmartScraperAgent class that uses BeautifulSoup
# and requests to extract actual product data from Walmart.
# """

# import random
# import time
# import logging
# import json
# import re
# from typing import Dict, Any, List, Optional, Tuple

# import requests
# from bs4 import BeautifulSoup

# from dealfinder.agents.base import Agent, MCPMessage
# from dealfinder import config
# from dealfinder.utils.logging import get_logger
# from dealfinder.agents.gemini_agent import GeminiAgent

# logger = get_logger("Scrapers.Walmart")

# class RealWalmartScraperAgent(Agent):
#     """Agent for scraping Walmart product listings with actual web scraping"""
    
#     def __init__(self):
#         """Initialize the Walmart scraper agent."""
#         super().__init__("WalmartScraperAgent")
#         self.base_url = config.WALMART_BASE_URL
        
#         # Configure headers with default values
#         self.headers = {
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#             "Accept-Language": "en-US,en;q=0.5",
#             "Accept-Encoding": "gzip, deflate, br",
#             "Connection": "keep-alive",
#             "Upgrade-Insecure-Requests": "1",
#             "Cache-Control": "max-age=0",
#         }
    
#     def process_message(self, message: MCPMessage) -> MCPMessage:
#         """
#         Process search request for Walmart.
        
#         Args:
#             message: The incoming MCPMessage to process
            
#         Returns:
#             A new MCPMessage containing the search results
#         """
#         if message.message_type != "SEARCH_REQUEST":
#             return MCPMessage(
#                 sender=self.name,
#                 receiver=message.sender,
#                 content={"error": "Only SEARCH_REQUEST message type is supported"},
#                 message_type="ERROR",
#                 conversation_id=message.conversation_id
#             )
        
#         search_params = message.content
#         self.logger.info(f"Searching Walmart for: {search_params}")
        
#         try:
#             # Convert search parameters to Walmart search query
#             query = self._build_search_query(search_params)
            
#             # Perform the search
#             products = self._scrape_search_results(query, search_params)
            
#             return MCPMessage(
#                 sender=self.name,
#                 receiver=message.sender,
#                 content={
#                     "source": "Walmart",
#                     "query": query,
#                     "products": products
#                 },
#                 message_type="SEARCH_RESPONSE",
#                 conversation_id=message.conversation_id
#             )
        
#         except Exception as e:
#             self.logger.error(f"Error scraping Walmart: {str(e)}")
#             return MCPMessage(
#                 sender=self.name,
#                 receiver=message.sender,
#                 content={"error": f"Walmart scraping error: {str(e)}"},
#                 message_type="ERROR",
#                 conversation_id=message.conversation_id
#             )
    
#     def _build_search_query(self, search_params: Dict[str, Any]) -> str:
#         """
#         Build search query string from parameters.
        
#         Args:
#             search_params: Search parameters to use for the query
            
#         Returns:
#             A search query string
#         """
#         components = []
        
#         if "product_type" in search_params:
#             components.append(search_params["product_type"])
        
#         if "keywords" in search_params:
#             if isinstance(search_params["keywords"], list):
#                 components.extend(search_params["keywords"])
#             else:
#                 components.append(search_params["keywords"])
        
#         if "brands" in search_params and search_params["brands"]:
#             brands = search_params["brands"]
#             if isinstance(brands, list):
#                 components.append(" ".join(brands))
#             else:
#                 components.append(brands)
        
#         if "features" in search_params and search_params["features"]:
#             features = search_params["features"]
#             if isinstance(features, list):
#                 components.extend(features)
#             else:
#                 components.append(features)
        
#         return " ".join(components)

#     def _scrape_search_results(self, query: str, search_params: Dict[str, Any], max_results: int = None) -> List[Dict[str, Any]]:
#         """
#         Scrape Walmart search results for the given query.
        
#         Args:
#             query: The search query string
#             search_params: Additional search parameters
#             max_results: Maximum number of results to return (default: from config)
            
#         Returns:
#             A list of product dictionaries
#         """
#         # Use configured max_results if not specified
#         if max_results is None:
#             max_results = config.MAX_PRODUCTS_PER_SOURCE
        
#         # Construct the search URL
#         params = {
#             "q": query,
#         }
        
#         # Add price range if specified
#         if "price_range" in search_params and search_params["price_range"]:
#             price_range = search_params["price_range"]
#             if isinstance(price_range, list) and len(price_range) == 2:
#                 min_price, max_price = price_range
#                 if min_price and max_price:
#                     params["min_price"] = min_price
#                     params["max_price"] = max_price
#                 elif min_price:
#                     params["min_price"] = min_price
#                 elif max_price:
#                     params["max_price"] = max_price
        
#         # Add sorting parameter if specified
#         if "sorting_preference" in search_params:
#             sort_pref = search_params["sorting_preference"]
#             if sort_pref == "price_low_to_high":
#                 params["sort"] = "price_low"
#             elif sort_pref == "price_high_to_low":
#                 params["sort"] = "price_high"
#             elif sort_pref == "rating":
#                 params["sort"] = "best_match"
#             elif sort_pref == "newest":
#                 params["sort"] = "new"
        
#         # Use a random user agent for each request
#         current_headers = self.headers.copy()
#         current_headers["User-Agent"] = random.choice(config.USER_AGENTS)

#         for attempt in range(3):
#             try:
#                 response = requests.get(
#                     self.base_url,
#                     params=params,
#                     headers=current_headers,
#                     timeout=config.SCRAPING_TIMEOUT
#                 )
#                 if response.status_code == 200:
#                     break
#                 else:
#                     time.sleep(2 ** attempt)
#             except Exception as e:
#                 self.logger.warning(f"Retrying due to error: {str(e)}")
#                 time.sleep(2 ** attempt)
#         else:
#             self.logger.error("Max retries exceeded")
#             return []

#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Always use Gemini support
#         if search_params.get("always_use_gemini"):
#             self.logger.info("Gemini used for product extraction")
#             from dealfinder.agents.gemini_agent import GeminiAgent
#             gemini = GeminiAgent()
#             # Try product divs from HTML
#             product_divs = soup.select('div[data-item-id]')
#             if not product_divs:
#                 product_divs = soup.select('.product-card')
#             if not product_divs:
#                 product_divs = soup.select('.search-result-gridview-item')
#             return [gemini.extract_product_details_from_html(str(div)) for div in product_divs[:max_results]]

#         # Extract products from the page
#         products = self._extract_from_json_data(soup)
#         if not products:
#             products = self._extract_from_html(soup, max_results)
            
#         # Deduplicate by product_id
#         seen_ids = set()
#         filtered_products = []
        
#         for product in products:
#             # REMOVED the relevance check:
#             # if not self._is_relevant_product(product, search_params.get("keywords", [])):
#             #    continue
            
#             # Keep deduplication logic
#             pid = product.get("product_id")
#             if pid in seen_ids:
#                 continue
                
#             seen_ids.add(pid)
#             product["source"] = "Walmart"
#             self.logger.info(f"Extracted product: {product.get('title', '')} at {product.get('price', 0)} USD")
#             filtered_products.append(product)
            
#             if len(filtered_products) >= (max_results if max_results is not None else config.MAX_PRODUCTS_PER_SOURCE):
#                 break

#         time.sleep(random.uniform(
#             config.SCRAPING_DELAY_MIN,
#             config.SCRAPING_DELAY_MAX
#         ))
        
#         self.logger.info(f"Returning {len(filtered_products)} products from Walmart")
#         return filtered_products[:max_results] if max_results else filtered_products
    
#     def _extract_from_json_data(self, soup) -> List[Dict[str, Any]]:
#         """
#         Extract product data from JSON embedded in the page.
        
#         Args:
#             soup: BeautifulSoup object of the page
            
#         Returns:
#             A list of product dictionaries
#         """
#         products = []
        
#         try:
#             # Look for script tags that might contain product data
#             script_tags = soup.find_all('script', type='application/json')
            
#             for script in script_tags:
#                 try:
#                     json_data = json.loads(script.string)
                    
#                     # Scan through the JSON to find product data
#                     if 'items' in json_data:
#                         for item in json_data['items']:
#                             product = self._parse_json_product(item)
#                             if product:
#                                 products.append(product)
                    
#                     # Also check for 'searchContent' structure
#                     if 'searchContent' in json_data and 'searchResultsMap' in json_data['searchContent']:
#                         results = json_data['searchContent']['searchResultsMap']
#                         if 'REGULAR_SEARCH' in results and 'products' in results['REGULAR_SEARCH']:
#                             for item in results['REGULAR_SEARCH']['products']:
#                                 product = self._parse_json_product(item)
#                                 if product:
#                                     products.append(product)
                
#                 except (json.JSONDecodeError, KeyError, TypeError) as e:
#                     # Not the JSON we're looking for, try the next script tag
#                     continue
            
#             self.logger.info(f"Extracted {len(products)} products from JSON data")
#             return products
            
#         except Exception as e:
#             self.logger.error(f"Error extracting from JSON data: {str(e)}")
#             return []
    
#     def _parse_json_product(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
#         """
#         Parse product data from a JSON item.
        
#         Args:
#             item: JSON object containing product data
            
#         Returns:
#             A dictionary of product data, or None if parsing fails
#         """
#         try:
#             # Extract basic product info
#             product_id = item.get('id', item.get('productId', ''))
#             title = item.get('title', item.get('name', ''))
            
#             # Extract price information
#             price = 0.0
#             price_info = item.get('price', item.get('priceInfo', {}))
#             if isinstance(price_info, dict):
#                 current_price = price_info.get('currentPrice', price_info.get('displayPrice', 0))
#                 if isinstance(current_price, (int, float)):
#                     price = float(current_price)
#                 elif isinstance(current_price, dict) and 'price' in current_price:
#                     price = float(current_price['price'])
#             elif isinstance(price_info, (int, float)):
#                 price = float(price_info)
            
#             # Extract URL
#             product_url = ""
#             if 'canonicalUrl' in item:
#                 product_url = f"https://www.walmart.com{item['canonicalUrl']}"
#             elif 'productPageUrl' in item:
#                 product_url = f"https://www.walmart.com{item['productPageUrl']}"
#             elif 'productUrl' in item:
#                 product_url = f"https://www.walmart.com{item['productUrl']}"
            
#             # Extract image URL
#             image_url = ""
#             if 'imageInfo' in item and 'thumbnailUrl' in item['imageInfo']:
#                 image_url = item['imageInfo']['thumbnailUrl']
#             elif 'images' in item and len(item['images']) > 0:
#                 image_url = item['images'][0].get('url', '')
#             elif 'image' in item:
#                 image_url = item['image']
            
#             # Extract rating
#             rating = 0.0
#             if 'averageRating' in item:
#                 rating = float(item['averageRating'])
#             elif 'rating' in item and 'averageRating' in item['rating']:
#                 rating = float(item['rating']['averageRating'])
            
#             # Extract number of reviews
#             reviews = 0
#             if 'numberOfReviews' in item:
#                 reviews = int(item['numberOfReviews'])
#             elif 'rating' in item and 'numberOfReviews' in item['rating']:
#                 reviews = int(item['rating']['numberOfReviews'])
#             elif 'reviewCount' in item:
#                 reviews = int(item['reviewCount'])
            
#             # Check if product is sponsored
#             is_sponsored = False
#             if 'sponsored' in item:
#                 is_sponsored = bool(item['sponsored'])
            
#             # Check if product is available for pickup
#             is_pickup_today = False
#             if 'fulfillmentBadge' in item and 'fulfillmentType' in item:
#                 is_pickup_today = 'PICKUP' in item['fulfillmentType']
#             elif 'fulfillment' in item and 'pickup' in item['fulfillment']:
#                 is_pickup_today = True
                
#             # Extract description if available
#             description = ""
#             if 'description' in item:
#                 description = item['description']
#             elif 'shortDescription' in item:
#                 description = item['shortDescription']
            
#             # Use Gemini fallback if essential fields are missing
#             if (not title or title == "Unknown Product") or not product_url or price == 0.0:
#                 gemini = GeminiAgent()
#                 html_context = json.dumps(item)  # Pass the JSON item as context string
#                 gemini_response = gemini.extract_product_details_from_html(html_context)
#                 if isinstance(gemini_response, dict):
#                     title = gemini_response.get("title", title)
#                     price = gemini_response.get("price", price)
#                     product_url = gemini_response.get("url", product_url)
#                     image_url = gemini_response.get("image_url", image_url)

#             # Create product dictionary
#             product = {
#                 "title": title,
#                 "price": price,
#                 "currency": "USD",
#                 "url": product_url,
#                 "image_url": image_url,
#                 "rating": rating,
#                 "reviews": reviews,
#                 "is_sponsored": is_sponsored,
#                 "is_pickup_today": is_pickup_today,
#                 "product_id": product_id,
#                 "description": description
#             }

#             return product

#         except Exception as e:
#             self.logger.error(f"Error parsing JSON product: {str(e)}")
#             return None
    
#     def _extract_from_html(self, soup, max_results: int) -> List[Dict[str, Any]]:
#         """
#         Extract product data from HTML when JSON extraction fails.
        
#         Args:
#             soup: BeautifulSoup object of the page
#             max_results: Maximum number of results to return
            
#         Returns:
#             A list of product dictionaries
#         """
#         products = []
        
#         try:
#             # Find all product divs in the search results
#             product_divs = soup.select('div[data-item-id]')
            
#             if not product_divs:
#                 # Try alternate selector
#                 product_divs = soup.select('.product-card')
            
#             if not product_divs:
#                 # Try another alternate selector
#                 product_divs = soup.select('.search-result-gridview-item')
            
#             self.logger.info(f"Found {len(product_divs)} product divs in HTML")
            
#             for div in product_divs[:max_results * 2]:  # Get extra products in case some fail extraction
#                 product = self._extract_product_data(div)
#                 if product:
#                     products.append(product)
                    
#                     # If we've collected enough products, stop
#                     if len(products) >= max_results:
#                         break
            
#             self.logger.info(f"Extracted {len(products)} products from HTML")
#             return products
            
#         except Exception as e:
#             self.logger.error(f"Error extracting from HTML: {str(e)}")
#             return []
    
#     def _extract_product_data(self, product_div) -> Optional[Dict[str, Any]]:
#         """
#         Extract product data from a product div element.
        
#         Args:
#             product_div: BeautifulSoup element containing product data
            
#         Returns:
#             A dictionary of product data, or None if extraction fails
#         """
#         try:
#             # Extract product ID
#             product_id = product_div.get('data-item-id', '')
#             if not product_id:
#                 product_id = product_div.get('data-product-id', '')

#             # Check if the product is sponsored
#             is_sponsored = bool(product_div.select_one('.sponsored-flag'))

#             # Extract product title
#             title_element = product_div.select_one('.product-title-link span')
#             if not title_element:
#                 title_element = product_div.select_one('.ProductPlaceholder-title')

#             # If we still don't have a title, try other common selectors
#             if not title_element:
#                 title_element = product_div.select_one('span[data-automation="product-title"]')

#             # If still no title, search for any heading element
#             if not title_element:
#                 for heading in product_div.select('h2, h3'):
#                     if heading.text.strip():
#                         title_element = heading
#                         break

#             title = title_element.text.strip() if title_element else "Unknown Product"

#             # Extract product URL
#             url_element = product_div.select_one('a.product-title-link')
#             if not url_element:
#                 url_element = product_div.select_one('a[href^="/ip/"]')

#             url = "https://www.walmart.com" + url_element['href'] if url_element and 'href' in url_element.attrs else "#"

#             # Extract product image URL
#             img_element = product_div.select_one('img.product-image-photo')
#             if not img_element:
#                 img_element = product_div.select_one('img.ProductPlaceholder-image')

#             image_url = img_element['src'] if img_element and 'src' in img_element.attrs else ""
#             if not image_url and img_element and 'data-src' in img_element.attrs:
#                 image_url = img_element['data-src']

#             # Extract product price
#             price_element = product_div.select_one('.price-main')
#             if not price_element:
#                 price_element = product_div.select_one('.product-price')
#             if not price_element:
#                 price_element = product_div.select_one('span[data-automation="product-price"]')
#             if not price_element:
#                 price_element = product_div.select_one('[data-price]')
#                 if price_element and 'data-price' in price_element.attrs:
#                     price = float(price_element['data-price'])
#                     # Skip the text extraction below
#                     price_extracted = True
#                 else:
#                     price_extracted = False
#             else:
#                 price_extracted = False

#             price = 0.0
#             if price_element and not price_extracted:
#                 price_text = price_element.text.strip()
#                 price = self._parse_price(price_text)

#             # Extract product rating
#             rating_element = product_div.select_one('.stars-reviews-count')
#             if not rating_element:
#                 rating_element = product_div.select_one('.ratings')

#             rating = 0.0
#             if rating_element:
#                 rating_text = rating_element.text.strip()
#                 rating_match = re.search(r'(\d+\.\d+)', rating_text)
#                 if rating_match:
#                     rating = float(rating_match.group(1))

#             # Extract number of reviews
#             reviews_element = product_div.select_one('.stars-reviews-count span')
#             if not reviews_element:
#                 reviews_element = product_div.select_one('.review-count')

#             reviews = 0
#             if reviews_element:
#                 reviews_text = reviews_element.text.strip()
#                 reviews_text = reviews_text.replace(',', '')
#                 reviews_match = re.search(r'(\d+)', reviews_text)
#                 if reviews_match:
#                     reviews = int(reviews_match.group(1))

#             # Check if the product has pickup today
#             is_pickup_today = bool(product_div.select_one('.fulfillment-shipping-text'))
#             if not is_pickup_today:
#                 is_pickup_today = bool(product_div.select_one('.pickup-today'))
                
#             # Extract description if available
#             description_element = product_div.select_one('.product-description-text')
#             description = description_element.text.strip() if description_element else ""

#             # Use Gemini fallback if title is 'Unknown Product' or URL is missing or price is 0
#             if (not title or title == "Unknown Product") or not url or price == 0.0:
#                 try:
#                     gemini = GeminiAgent()
#                     html_context = str(product_div)
#                     gemini_response = gemini.extract_product_details_from_html(html_context)
#                     if isinstance(gemini_response, dict):
#                         self.logger.info("Gemini used for product extraction")
#                         self.logger.info(f"Extracted product: {gemini_response.get('title', '')} at {gemini_response.get('price', 0)} USD")
#                         title = gemini_response.get("title", title)
#                         price = gemini_response.get("price", price)
#                         url = gemini_response.get("url", url)
#                         image_url = gemini_response.get("image_url", image_url)
#                 except Exception as e:
#                     self.logger.error(f"Gemini fallback failed: {str(e)}")

#             self.logger.info(f"Extracted product: {title} at {price} USD")

#             # Create product dictionary
#             product = {
#                 "title": title,
#                 "price": price,
#                 "currency": "USD",
#                 "url": url,
#                 "image_url": image_url,
#                 "rating": rating,
#                 "reviews": reviews,
#                 "is_sponsored": is_sponsored,
#                 "is_pickup_today": is_pickup_today,
#                 "product_id": product_id,
#                 "description": description
#             }

#             return product

#         except Exception as e:
#             self.logger.error(f"Error extracting product data: {str(e)}")
#             return None
    
#     def _parse_price(self, price_text: str) -> float:
#         """
#         Parse price string to float.
        
#         Args:
#             price_text: Price text to parse
            
#         Returns:
#             Parsed price as float
#         """
#         try:
#             # Remove currency symbol and commas, then convert to float
#             price_text = price_text.replace('$', '').replace(',', '')
#             # Extract numbers using regex
#             price_match = re.search(r'(\d+\.\d+)', price_text)
#             if price_match:
#                 return float(price_match.group(1))
#             return 0.0
#         except (ValueError, AttributeError):
#             return 0.0
"""
Real Walmart Scraper Implementation for DealFinder AI with Gemini query optimization.

This module implements the RealWalmartScraperAgent class that uses BeautifulSoup,
requests, and Gemini AI to extract and optimize product data from Walmart.
"""

import random
import time
import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from dealfinder.agents.base import Agent, MCPMessage
from dealfinder import config
from dealfinder.utils.logging import get_logger
from dealfinder.agents.gemini_agent import GeminiAgent

logger = get_logger("Scrapers.Walmart")

class RealWalmartScraperAgent(Agent):
    """Agent for scraping Walmart product listings with Gemini-enhanced search optimization"""
    
    def __init__(self):
        """Initialize the Walmart scraper agent."""
        super().__init__("WalmartScraperAgent")
        self.base_url = config.WALMART_BASE_URL
        self.gemini_agent = GeminiAgent()
        
        # Configure headers with default values
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
    
    def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Process search request for Walmart.
        
        Args:
            message: The incoming MCPMessage to process
            
        Returns:
            A new MCPMessage containing the search results
        """
        if message.message_type != "SEARCH_REQUEST":
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": "Only SEARCH_REQUEST message type is supported"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
        
        search_params = message.content
        self.logger.info(f"Searching Walmart for: {search_params}")
        
        try:
            # Use Gemini to optimize the search query for Walmart's search engine
            optimized_params = self._optimize_search_params(search_params)
            self.logger.info(f"Optimized search parameters: {optimized_params}")
            
            # Convert optimized parameters to Walmart search query
            query = self._build_search_query(optimized_params)
            self.logger.info(f"Built Walmart query: {query}")
            
            # Perform the search
            products = self._scrape_search_results(query, optimized_params)
            
            # Apply Gemini-based relevance filtering
            if not search_params.get("skip_relevance_filter", False):
                products = self._apply_relevance_filter(products, search_params)
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={
                    "source": "Walmart",
                    "query": query,
                    "products": products
                },
                message_type="SEARCH_RESPONSE",
                conversation_id=message.conversation_id
            )
        
        except Exception as e:
            self.logger.error(f"Error scraping Walmart: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Walmart scraping error: {str(e)}"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
    
    def _optimize_search_params(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Gemini to optimize search parameters for Walmart's search engine.
        
        Args:
            search_params: Original search parameters
            
        Returns:
            Optimized search parameters
        """
        try:
            # Extract query components for optimization
            query_components = []
            if "product_type" in search_params and search_params["product_type"]:
                query_components.append(search_params["product_type"])
                
            if "keywords" in search_params:
                if isinstance(search_params["keywords"], list):
                    query_components.extend(search_params["keywords"])
                else:
                    query_components.append(search_params["keywords"])
                    
            if "brands" in search_params and search_params["brands"]:
                brands = search_params["brands"]
                if isinstance(brands, list):
                    query_components.extend(brands)
                else:
                    query_components.append(brands)
                    
            if "features" in search_params and search_params["features"]:
                features = search_params["features"]
                if isinstance(features, list):
                    query_components.extend(features)
                else:
                    query_components.append(features)
            
            # If no components to optimize, return original parameters
            if not query_components:
                return search_params
            
            # Create prompt for Gemini
            original_query = " ".join(query_components)
            prompt = f"""
            Optimize this search query for Walmart's search engine:
            
            "{original_query}"
            
            For Walmart searches, please:
            1. Focus on model numbers and specific identifiers if present
            2. Include key brand names (Walmart's search works well with brand names)
            3. Remove generic words that may dilute results
            4. Add Walmart-specific terms that might improve results (like "Rollback" if looking for deals)
            5. Prioritize precise product names and specifications
            
            Return a JSON object with:
            - optimized_keywords: List of 3-5 optimized search terms (most important first)
            - department_hint: Any Walmart department suggestion (Electronics, Home, etc.)
            - must_include_terms: Terms that MUST be in results
            - exclude_terms: Terms that should NOT be in results
            - walmart_specific_filters: Any Walmart-specific filters to apply
            
            Format as JSON only with no explanation.
            """
            
            # Call Gemini
            message = MCPMessage(
                sender="WalmartScraperAgent",
                receiver="GeminiAgent",
                content=prompt,
                message_type="REQUEST"
            )
            
            response = self.gemini_agent.process_message(message)
            
            # Parse response
            optimization_data = {}
            if isinstance(response.content, str):
                # Try to extract JSON from the response
                try:
                    # Check if response is wrapped in code blocks
                    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response.content)
                    if json_match:
                        optimization_data = json.loads(json_match.group(1))
                    else:
                        # Try direct parsing
                        optimization_data = json.loads(response.content)
                except json.JSONDecodeError:
                    self.logger.warning("Could not parse Gemini optimization response as JSON")
            else:
                # Response is already parsed
                optimization_data = response.content
            
            # Create optimized parameters
            optimized_params = search_params.copy()
            
            # Update keywords if optimized keywords were provided
            if "optimized_keywords" in optimization_data and optimization_data["optimized_keywords"]:
                optimized_params["keywords"] = optimization_data["optimized_keywords"]
            
            # Add department hints if provided
            if "department_hint" in optimization_data and optimization_data["department_hint"]:
                optimized_params["department"] = optimization_data["department_hint"]
            
            # Add must-include terms
            if "must_include_terms" in optimization_data and optimization_data["must_include_terms"]:
                optimized_params["must_include_terms"] = optimization_data["must_include_terms"]
            
            # Add exclude terms
            if "exclude_terms" in optimization_data and optimization_data["exclude_terms"]:
                optimized_params["exclude_terms"] = optimization_data["exclude_terms"]
            
            # Add Walmart-specific filters
            if "walmart_specific_filters" in optimization_data and optimization_data["walmart_specific_filters"]:
                optimized_params["walmart_filters"] = optimization_data["walmart_specific_filters"]
            
            return optimized_params
            
        except Exception as e:
            self.logger.error(f"Error optimizing search parameters: {str(e)}")
            # Fall back to original parameters
            return search_params
    
    def _build_search_query(self, search_params: Dict[str, Any]) -> str:
        """
        Build optimized search query string from parameters for Walmart's search engine.
        
        Args:
            search_params: Optimized search parameters
            
        Returns:
            A search query string
        """
        components = []
        
        # Brand is very important for Walmart searches
        if "brands" in search_params and search_params["brands"]:
            brands = search_params["brands"]
            if isinstance(brands, list):
                # Add each brand as a high-priority component
                components.extend(brands)
            else:
                components.append(brands)
        
        # Product type is also important
        if "product_type" in search_params and search_params["product_type"]:
            components.append(search_params["product_type"])
        
        # Add keywords with priority
        if "keywords" in search_params:
            if isinstance(search_params["keywords"], list):
                # For Walmart, use all optimized keywords
                components.extend(search_params["keywords"])
            else:
                components.append(search_params["keywords"])
        
        # Add department hint if specified - Walmart's search works better with department context
        if "department" in search_params and search_params["department"]:
            department = search_params["department"]
            if isinstance(department, list) and department:
                components.append(department[0])
            else:
                components.append(department)
        
        # Add must_include_terms if specified (critical terms)
        if "must_include_terms" in search_params and search_params["must_include_terms"]:
            terms = search_params["must_include_terms"]
            if isinstance(terms, list):
                components.extend(terms)
            else:
                components.append(terms)
        
        # For Walmart, we're more selective with features
        if "features" in search_params and search_params["features"]:
            features = search_params["features"]
            if isinstance(features, list):
                # Only include the first 2 most important features
                if len(features) > 2:
                    components.extend(features[:2])
                else:
                    components.extend(features)
            else:
                components.append(features)
        
        # Join with spaces for the query
        query = " ".join(components)
        
        # If query is too long, prioritize the most important components
        if len(query.split()) > 8:
            # For Walmart, prioritize brands and specific identifiers
            short_components = []
            
            # Brands are very important for Walmart
            if "brands" in search_params and search_params["brands"]:
                if isinstance(search_params["brands"], list) and search_params["brands"]:
                    short_components.append(search_params["brands"][0])  # Use first brand
                else:
                    short_components.append(search_params["brands"])
            
            # Product type is important
            if "product_type" in search_params and search_params["product_type"]:
                short_components.append(search_params["product_type"])
            
            # Add a few critical keywords
            if "keywords" in search_params and search_params["keywords"]:
                if isinstance(search_params["keywords"], list) and search_params["keywords"]:
                    # Take top 3 keywords only
                    short_components.extend(search_params["keywords"][:3])
                else:
                    short_components.append(search_params["keywords"])
            
            query = " ".join(short_components)
        
        self.logger.info(f"Built optimized Walmart search query: {query}")
        return query

    def _scrape_search_results(self, query: str, search_params: Dict[str, Any], max_results: int = None) -> List[Dict[str, Any]]:
        """
        Scrape Walmart search results for the given query with enhanced parameters.
        
        Args:
            query: The search query string
            search_params: Optimized search parameters
            max_results: Maximum number of results to return (default: from config)
            
        Returns:
            A list of product dictionaries
        """
        # Use configured max_results if not specified
        if max_results is None:
            max_results = config.MAX_PRODUCTS_PER_SOURCE
        
        # Get extra results for better filtering
        scrape_count = max_results * 2
        
        # Construct the search URL params with enhanced parameters
        params = {
            "q": query,
            "page": 1,
            "affinityOverride": "default",
        }
        
        # Add Walmart department filter if available
        if "department" in search_params and search_params["department"]:
            department = search_params["department"]
            if isinstance(department, list) and department:
                department = department[0]
            # Walmart uses departments in the search query rather than separate parameters
            params["q"] = f"{params['q']} {department}"
        
        # Add price range if specified
        if "price_range" in search_params and search_params["price_range"]:
            price_range = search_params["price_range"]
            if isinstance(price_range, list) and len(price_range) == 2:
                min_price, max_price = price_range
                if min_price and max_price:
                    params["min_price"] = min_price
                    params["max_price"] = max_price
                elif min_price:
                    params["min_price"] = min_price
                elif max_price:
                    params["max_price"] = max_price
        
        # Add sorting parameter if specified
        if "sorting_preference" in search_params:
            sort_pref = search_params["sorting_preference"]
            if sort_pref == "price_low_to_high":
                params["sort"] = "price_low"
            elif sort_pref == "price_high_to_low":
                params["sort"] = "price_high"
            elif sort_pref == "rating":
                params["sort"] = "best_match"
            elif sort_pref == "newest":
                params["sort"] = "new"
                
        # Add Walmart-specific filters
        if "walmart_filters" in search_params:
            walmart_filters = search_params["walmart_filters"]
            if isinstance(walmart_filters, dict):
                # Walmart filters can include various parameters
                for key, value in walmart_filters.items():
                    params[key] = value
        
        # Use a random user agent for each request to avoid blocking
        current_headers = self.headers.copy()
        current_headers["User-Agent"] = random.choice(config.USER_AGENTS)

        # Make the request with retry logic
        for attempt in range(3):
            try:
                self.logger.info(f"Making Walmart search request with params: {params}")
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=current_headers,
                    timeout=config.SCRAPING_TIMEOUT
                )
                
                if response.status_code == 200:
                    break
                else:
                    self.logger.warning(f"Walmart search request failed with status {response.status_code}, retrying")
                    time.sleep(2 ** attempt)
            except Exception as e:
                self.logger.warning(f"Request error: {str(e)}, retrying")
                time.sleep(2 ** attempt)
        else:
            self.logger.error("Max retries exceeded")
            return []

        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get product listings - always_use_gemini support
        if search_params.get("always_use_gemini"):
            self.logger.info("Using Gemini for all product extraction")
            # Try product divs from HTML
            product_divs = soup.select('div[data-item-id]')
            if not product_divs:
                product_divs = soup.select('.product-card')
            if not product_divs:
                product_divs = soup.select('.search-result-gridview-item')
                
            extracted_products = []
            
            for div in product_divs[:scrape_count]:
                product = self.gemini_agent.extract_product_details_from_html(str(div))
                if product and isinstance(product, dict):
                    product["source"] = "Walmart"
                    extracted_products.append(product)
                    
            # Return the requested number of products
            return extracted_products[:max_results]

        # Try JSON extraction first (more reliable)
        products = self._extract_from_json_data(soup)
        
        # Fall back to HTML extraction if JSON extraction fails
        if not products:
            self.logger.info("JSON extraction failed, falling back to HTML extraction")
            products = self._extract_from_html(soup, scrape_count)
            
        # Deduplicate by product_id
        seen_ids = set()
        filtered_products = []
        
        for product in products:
            pid = product.get("product_id")
            if pid in seen_ids:
                continue
                
            seen_ids.add(pid)
            product["source"] = "Walmart"
            self.logger.info(f"Extracted product: {product.get('title', '')} at {product.get('price', 0)} USD")
            filtered_products.append(product)
            
            if len(filtered_products) >= scrape_count:
                break

        # Add a short delay to avoid rate limiting
        time.sleep(random.uniform(
            config.SCRAPING_DELAY_MIN,
            config.SCRAPING_DELAY_MAX
        ))
        
        self.logger.info(f"Extracted {len(filtered_products)} products from Walmart")
        
        # Return the requested number of products (will be filtered for relevance later)
        return filtered_products
    
    def _apply_relevance_filter(self, products: List[Dict[str, Any]], search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply advanced relevance filtering using Gemini-enhanced criteria.
        
        Args:
            products: List of products to filter
            search_params: Search parameters with relevance criteria
            
        Returns:
            Filtered list of products
        """
        if not products:
            return []
            
        # If we have too few products, skip filtering
        if len(products) <= 3:
            return products
            
        try:
            self.logger.info(f"Applying relevance filtering to {len(products)} products")
            
            # Extract filtering criteria
            must_include_terms = search_params.get("must_include_terms", [])
            exclude_terms = search_params.get("exclude_terms", [])
            
            # Prepare keywords for matching
            keywords = []
            if "keywords" in search_params:
                if isinstance(search_params["keywords"], list):
                    keywords.extend([k.lower() for k in search_params["keywords"] if k])
                elif search_params["keywords"]:
                    keywords.append(search_params["keywords"].lower())
            
            # Prepare brands for matching
            brands = []
            if "brands" in search_params and search_params["brands"]:
                if isinstance(search_params["brands"], list):
                    brands.extend([b.lower() for b in search_params["brands"] if b])
                else:
                    brands.append(search_params["brands"].lower())
            
            # Convert must_include and exclude_terms to lists if they're not already
            if must_include_terms and not isinstance(must_include_terms, list):
                must_include_terms = [must_include_terms]
            
            if exclude_terms and not isinstance(exclude_terms, list):
                exclude_terms = [exclude_terms]
            
            # Apply basic filtering
            filtered_products = []
            for product in products:
                # Get product text for matching (combine title and description)
                title = product.get("title", "").lower()
                description = product.get("description", "").lower()
                combined_text = f"{title} {description}"
                
                # Skip products with exclude terms
                if exclude_terms and any(term.lower() in combined_text for term in exclude_terms if term):
                    continue
                
                # Keep products with must_include terms
                if must_include_terms:
                    if not all(term.lower() in combined_text for term in must_include_terms if term):
                        continue
                
                # Ensure brand match if brands were specified
                if brands and not any(brand in combined_text for brand in brands):
                    continue
                
                # Calculate a relevance score for Walmart-specific ranking
                relevance_score = 0
                
                # Keywords in title are very important
                keyword_matches = sum(1 for kw in keywords if kw in title)
                relevance_score += keyword_matches * 10
                
                # Keywords in description are less important
                description_matches = sum(1 for kw in keywords if kw in description)
                relevance_score += description_matches * 2
                
                # Walmart-specific bonuses:
                
                # Prefer items with better ratings
                rating = product.get("rating", 0)
                if rating > 4.5:
                    relevance_score += 8
                elif rating > 4.0:
                    relevance_score += 5
                elif rating > 3.0:
                    relevance_score += 2
                
                # Prefer items with more reviews
                reviews = product.get("reviews", 0)
                if reviews > 1000:
                    relevance_score += 6
                elif reviews > 500:
                    relevance_score += 4
                elif reviews > 100:
                    relevance_score += 2
                
                # Prefer pickup today items
                if product.get("is_pickup_today", False):
                    relevance_score += 3
                
                # Penalize sponsored products slightly
                if product.get("is_sponsored", False):
                    relevance_score -= 2
                
                # Store the relevance score in the product
                product["relevance_score"] = relevance_score
                
                # Add to filtered products
                filtered_products.append(product)
            
            # Sort by relevance score
            sorted_products = sorted(filtered_products, key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            # Get top products by relevance
            max_results = min(len(sorted_products), config.MAX_PRODUCTS_PER_SOURCE)
            top_products = sorted_products[:max_results]
            
            self.logger.info(f"Filtered to {len(top_products)} most relevant products")
            return top_products
            
        except Exception as e:
            self.logger.error(f"Error in relevance filtering: {str(e)}")
            # On error, return original products
            return products[:config.MAX_PRODUCTS_PER_SOURCE]
    
    def _extract_from_json_data(self, soup) -> List[Dict[str, Any]]:
        """
        Extract product data from JSON embedded in the page.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            A list of product dictionaries
        """
        products = []
        
        try:
            # Look for script tags that might contain product data
            script_tags = soup.find_all('script', type='application/json')
            
            for script in script_tags:
                try:
                    json_data = json.loads(script.string)
                    
                    # Scan through the JSON to find product data
                    if 'items' in json_data:
                        for item in json_data['items']:
                            product = self._parse_json_product(item)
                            if product:
                                products.append(product)
                    
                    # Also check for 'searchContent' structure
                    if 'searchContent' in json_data and 'searchResultsMap' in json_data['searchContent']:
                        results = json_data['searchContent']['searchResultsMap']
                        if 'REGULAR_SEARCH' in results and 'products' in results['REGULAR_SEARCH']:
                            for item in results['REGULAR_SEARCH']['products']:
                                product = self._parse_json_product(item)
                                if product:
                                    products.append(product)
                
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    # Not the JSON we're looking for, try the next script tag
                    continue
            
            self.logger.info(f"Extracted {len(products)} products from JSON data")
            return products
            
        except Exception as e:
            self.logger.error(f"Error extracting from JSON data: {str(e)}")
            return []
    
    def _parse_json_product(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse product data from a JSON item with enhanced extraction.
        
        Args:
            item: JSON object containing product data
            
        Returns:
            A dictionary of product data, or None if parsing fails
        """
        try:
            # Extract basic product info
            product_id = item.get('id', item.get('productId', ''))
            title = item.get('title', item.get('name', ''))
            
            # Extract price information with better fallbacks
            price = 0.0
            price_info = item.get('price', item.get('priceInfo', {}))
            
            if isinstance(price_info, dict):
                # Try multiple paths for price
                if 'currentPrice' in price_info:
                    current_price = price_info['currentPrice']
                    if isinstance(current_price, (int, float)):
                        price = float(current_price)
                    elif isinstance(current_price, dict) and 'price' in current_price:
                        price = float(current_price['price'])
                elif 'displayPrice' in price_info:
                    display_price = price_info['displayPrice']
                    if isinstance(display_price, (int, float)):
                        price = float(display_price)
                elif 'priceByWeight' in price_info:
                    # Some products are priced by weight
                    price_by_weight = price_info['priceByWeight']
                    if isinstance(price_by_weight, dict) and 'displayPrice' in price_by_weight:
                        price = float(price_by_weight['displayPrice'])
            elif isinstance(price_info, (int, float)):
                price = float(price_info)
            
            # Check for promotional price
            if isinstance(price_info, dict) and 'wasPrice' in price_info:
                was_price = price_info['wasPrice']
                if isinstance(was_price, (int, float)) and was_price > price:
                    was_price = float(was_price)
                else:
                    was_price = None
            else:
                was_price = None
            
            # Extract URL with better URL construction
            product_url = ""
            if 'canonicalUrl' in item:
                product_url = f"https://www.walmart.com{item['canonicalUrl']}"
            elif 'productPageUrl' in item:
                product_url = f"https://www.walmart.com{item['productPageUrl']}"
            elif 'productUrl' in item:
                product_url = f"https://www.walmart.com{item['productUrl']}"
            elif 'seoUrl' in item:
                product_url = f"https://www.walmart.com{item['seoUrl']}"
            
            # Extract image URL with better fallbacks
            image_url = ""
            if 'imageInfo' in item:
                image_info = item['imageInfo']
                if 'thumbnailUrl' in image_info:
                    image_url = image_info['thumbnailUrl']
                elif 'mainImage' in image_info:
                    image_url = image_info['mainImage']
            elif 'images' in item and len(item['images']) > 0:
                images = item['images']
                if isinstance(images[0], dict) and 'url' in images[0]:
                    image_url = images[0]['url']
            elif 'image' in item:
                image_url = item['image']
            
            # Fix Walmart image URLs if needed
            if image_url and not image_url.startswith('http'):
                image_url = f"https://i5.walmartimages.com/asr/{image_url}"
            
            # Extract rating with better fallbacks
            rating = 0.0
            if 'averageRating' in item:
                rating = float(item['averageRating'])
            elif 'rating' in item:
                rating_data = item['rating']
                if isinstance(rating_data, dict) and 'averageRating' in rating_data:
                    rating = float(rating_data['averageRating'])
                elif isinstance(rating_data, (int, float)):
                    rating = float(rating_data)
            
            # Extract number of reviews with better fallbacks
            reviews = 0
            if 'numberOfReviews' in item:
                reviews = int(item['numberOfReviews'])
            elif 'rating' in item and isinstance(item['rating'], dict):
                rating_data = item['rating']
                if 'numberOfReviews' in rating_data:
                    reviews = int(rating_data['numberOfReviews'])
                elif 'reviewCount' in rating_data:
                    reviews = int(rating_data['reviewCount'])
            elif 'reviewCount' in item:
                reviews = int(item['reviewCount'])
            
            # Check if product is sponsored
            is_sponsored = False
            if 'sponsored' in item:
                is_sponsored = bool(item['sponsored'])
            elif 'sponsoredProduct' in item:
                is_sponsored = True
            
            # Check if product is available for pickup
            is_pickup_today = False
            if 'fulfillmentBadge' in item and 'fulfillmentType' in item:
                is_pickup_today = 'PICKUP' in item['fulfillmentType']
            elif 'fulfillment' in item and isinstance(item['fulfillment'], dict):
                fulfillment = item['fulfillment']
                if 'pickup' in fulfillment:
                    is_pickup_today = True
                elif 'pickupToday' in fulfillment:
                    is_pickup_today = bool(fulfillment['pickupToday'])
                
            # Extract description with better fallbacks
            description = ""
            if 'description' in item:
                description = item['description']
            elif 'shortDescription' in item:
                description = item['shortDescription']
            elif 'detailedDescription' in item:
                description = item['detailedDescription']
            
            # Extract availability information
            availability = "In Stock"
            if 'availabilityStatus' in item:
                availability = item['availabilityStatus']
            elif 'inventoryStatus' in item:
                inventory_status = item['inventoryStatus']
                if isinstance(inventory_status, dict) and 'status' in inventory_status:
                    availability = inventory_status['status']
            
            # Extract seller information if available
            seller = "Walmart"
            if 'sellerName' in item:
                seller = item['sellerName']
            elif 'seller' in item and isinstance(item['seller'], dict) and 'name' in item['seller']:
                seller = item['seller']['name']
            
            # Use Gemini fallback if essential fields are missing
            # Use Gemini fallback if essential fields are missing
            if (not title or title == "Unknown Product") or not product_url or price == 0.0:
                try:
                    gemini = GeminiAgent()
                    html_context = json.dumps(item)  # Pass the JSON item as context string
                    gemini_response = gemini.extract_product_details_from_html(html_context)
                    if isinstance(gemini_response, dict):
                        title = gemini_response.get("title", title)
                        price = gemini_response.get("price", price)
                        product_url = gemini_response.get("url", product_url)
                        image_url = gemini_response.get("image_url", image_url)
                except Exception as e:
                    self.logger.error(f"Gemini fallback failed: {str(e)}")

            # Create enhanced product dictionary with all available information
            product = {
                "title": title,
                "price": price,
                "was_price": was_price,
                "currency": "USD",
                "url": product_url,
                "image_url": image_url,
                "rating": rating,
                "reviews": reviews,
                "is_sponsored": is_sponsored,
                "is_pickup_today": is_pickup_today,
                "product_id": product_id,
                "description": description,
                "availability": availability,
                "seller": seller
            }

            # Log successful extraction
            self.logger.info(f"Extracted product from JSON: {title}")
            return product

        except Exception as e:
            self.logger.error(f"Error parsing JSON product: {str(e)}")
            return None
    
    def _extract_from_html(self, soup, max_results: int) -> List[Dict[str, Any]]:
        """
        Extract product data from HTML when JSON extraction fails, with improved selectors.
        
        Args:
            soup: BeautifulSoup object of the page
            max_results: Maximum number of results to return
            
        Returns:
            A list of product dictionaries
        """
        products = []
        
        try:
            # Find all product divs in the search results with multiple selectors
            product_divs = soup.select('div[data-item-id]')
            
            if not product_divs:
                # Try alternate selector for newer Walmart design
                product_divs = soup.select('.product-card')
            
            if not product_divs:
                # Try another alternate selector for older Walmart design
                product_divs = soup.select('.search-result-gridview-item')
            
            if not product_divs:
                # Try yet another selector for 2023+ Walmart design
                product_divs = soup.select('div[data-testid="list-item"]')
            
            self.logger.info(f"Found {len(product_divs)} product divs in HTML")
            
            # Process each product div
            for div in product_divs[:max_results * 2]:  # Get extra products in case some fail extraction
                product = self._extract_product_data(div)
                if product:
                    products.append(product)
                    
                    # If we've collected enough products, stop
                    if len(products) >= max_results:
                        break
            
            self.logger.info(f"Extracted {len(products)} products from HTML")
            return products
            
        except Exception as e:
            self.logger.error(f"Error extracting from HTML: {str(e)}")
            return []
    
    def _extract_product_data(self, product_div) -> Optional[Dict[str, Any]]:
        """
        Extract product data from a product div element with enhanced extraction.
        
        Args:
            product_div: BeautifulSoup element containing product data
            
        Returns:
            A dictionary of product data, or None if extraction fails
        """
        try:
            # Extract product ID with multiple selectors
            product_id = product_div.get('data-item-id', '')
            if not product_id:
                product_id = product_div.get('data-product-id', '')
            if not product_id:
                # Try to find it in data attributes
                for attr in product_div.attrs:
                    if 'item-id' in attr or 'product-id' in attr:
                        product_id = product_div.get(attr, '')
                        break

            # Check if the product is sponsored with multiple selectors
            is_sponsored = bool(product_div.select_one('.sponsored-flag'))
            if not is_sponsored:
                is_sponsored = bool(product_div.select_one('[data-testid="sponsored-badge"]'))
            if not is_sponsored:
                sponsored_text = product_div.text.lower()
                is_sponsored = 'sponsored' in sponsored_text or 'ad' in sponsored_text.split()

            # Extract product title with multiple selectors
            title_element = product_div.select_one('.product-title-link span')
            if not title_element:
                title_element = product_div.select_one('.ProductPlaceholder-title')
            if not title_element:
                title_element = product_div.select_one('span[data-automation="product-title"]')
            if not title_element:
                title_element = product_div.select_one('[data-testid="product-title"]')
            if not title_element:
                # Try to find any heading element
                for heading in product_div.select('h2, h3, h4, .heading'):
                    if heading.text.strip():
                        title_element = heading
                        break

            title = title_element.text.strip() if title_element else "Unknown Product"

            # Extract product URL with multiple selectors
            url_element = product_div.select_one('a.product-title-link')
            if not url_element:
                url_element = product_div.select_one('a[href^="/ip/"]')
            if not url_element:
                url_element = product_div.select_one('a[data-testid="product-title"]')
            if not url_element:
                # Try to find any link
                for link in product_div.select('a'):
                    if 'href' in link.attrs and ('/ip/' in link['href'] or '/product/' in link['href']):
                        url_element = link
                        break

            # Form the complete URL
            url = "https://www.walmart.com" + url_element['href'] if url_element and 'href' in url_element.attrs else "#"

            # Extract product image URL with multiple selectors
            img_element = product_div.select_one('img.product-image-photo')
            if not img_element:
                img_element = product_div.select_one('img.ProductPlaceholder-image')
            if not img_element:
                img_element = product_div.select_one('img[data-testid="product-image"]')
            if not img_element:
                # Try to find any image
                for img in product_div.select('img'):
                    if img.get('src') or img.get('data-src'):
                        img_element = img
                        break

            # Try multiple attributes for image URL
            image_url = ""
            if img_element:
                for attr in ['src', 'data-src', 'data-image-src']:
                    if attr in img_element.attrs and img_element[attr]:
                        image_url = img_element[attr]
                        break

            # Extract product price with multiple selectors
            price_element = product_div.select_one('.price-main')
            if not price_element:
                price_element = product_div.select_one('.product-price')
            if not price_element:
                price_element = product_div.select_one('span[data-automation="product-price"]')
            if not price_element:
                price_element = product_div.select_one('[data-testid="price-per-unit"]')
            if not price_element:
                price_element = product_div.select_one('[data-price]')
                if price_element and 'data-price' in price_element.attrs:
                    price = float(price_element['data-price'])
                    # Skip the text extraction below
                    price_extracted = True
                else:
                    price_extracted = False
            else:
                price_extracted = False

            # Extract price text if not already extracted
            price = 0.0
            if price_element and not price_extracted:
                price_text = price_element.text.strip()
                price = self._parse_price(price_text)

            # Extract "was price" if available
            was_price_element = product_div.select_one('.was-price')
            was_price = None
            if was_price_element:
                was_price_text = was_price_element.text.strip()
                was_price = self._parse_price(was_price_text)

            # Extract product rating with multiple selectors
            rating_element = product_div.select_one('.stars-reviews-count')
            if not rating_element:
                rating_element = product_div.select_one('.ratings')
            if not rating_element:
                rating_element = product_div.select_one('[data-testid="ratings"]')

            # Parse rating text
            rating = 0.0
            if rating_element:
                rating_text = rating_element.text.strip()
                rating_match = re.search(r'(\d+\.\d+)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))

            # Extract number of reviews with multiple selectors
            reviews_element = product_div.select_one('.stars-reviews-count span')
            if not reviews_element:
                reviews_element = product_div.select_one('.review-count')
            if not reviews_element:
                reviews_element = product_div.select_one('[data-testid="review-count"]')

            # Parse reviews text
            reviews = 0
            if reviews_element:
                reviews_text = reviews_element.text.strip()
                reviews_text = reviews_text.replace(',', '')
                reviews_match = re.search(r'(\d+)', reviews_text)
                if reviews_match:
                    reviews = int(reviews_match.group(1))

            # Check if the product has pickup today with multiple selectors
            is_pickup_today = bool(product_div.select_one('.fulfillment-shipping-text'))
            if not is_pickup_today:
                is_pickup_today = bool(product_div.select_one('.pickup-today'))
            if not is_pickup_today:
                is_pickup_today = bool(product_div.select_one('[data-testid="pickup-today-badge"]'))
            if not is_pickup_today:
                pickup_text = product_div.text.lower()
                is_pickup_today = 'pickup today' in pickup_text or 'store pickup' in pickup_text
                
            # Extract description if available
            description_element = product_div.select_one('.product-description-text')
            if not description_element:
                description_element = product_div.select_one('.description')
            if not description_element:
                description_element = product_div.select_one('[data-testid="product-description"]')
                
            description = description_element.text.strip() if description_element else ""
            
            # Extract seller information if available
            seller_element = product_div.select_one('.seller-name')
            if not seller_element:
                seller_element = product_div.select_one('[data-testid="seller-name"]')
                
            seller = seller_element.text.strip() if seller_element else "Walmart"
            
            # Extract availability information
            availability_element = product_div.select_one('.availability')
            if not availability_element:
                availability_element = product_div.select_one('[data-testid="availability"]')
                
            availability = availability_element.text.strip() if availability_element else "In Stock"

            # Use Gemini fallback if essential fields are missing
            if (not title or title == "Unknown Product") or not url or price == 0.0:
                try:
                    gemini = GeminiAgent()
                    html_context = str(product_div)
                    gemini_response = gemini.extract_product_details_from_html(html_context)
                    if isinstance(gemini_response, dict):
                        self.logger.info("Gemini used for product extraction")
                        title = gemini_response.get("title", title)
                        price = gemini_response.get("price", price)
                        url = gemini_response.get("url", url)
                        image_url = gemini_response.get("image_url", image_url)
                except Exception as e:
                    self.logger.error(f"Gemini fallback failed: {str(e)}")

            self.logger.info(f"Extracted product: {title} at {price} USD")

            # Create enhanced product dictionary
            product = {
                "title": title,
                "price": price,
                "was_price": was_price,
                "currency": "USD",
                "url": url,
                "image_url": image_url,
                "rating": rating,
                "reviews": reviews,
                "is_sponsored": is_sponsored,
                "is_pickup_today": is_pickup_today,
                "product_id": product_id,
                "description": description,
                "availability": availability,
                "seller": seller
            }

            return product

        except Exception as e:
            self.logger.error(f"Error extracting product data: {str(e)}")
            return None
    
    def _parse_price(self, price_text: str) -> float:
        """
        Parse price string to float with enhanced detection.
        
        Args:
            price_text: Price text to parse
            
        Returns:
            Parsed price as float
        """
        try:
            # Handle empty or invalid inputs
            if not price_text or price_text.lower() in ('free', 'n/a'):
                return 0.0
                
            # Handle Walmart's "From $X.XX" format
            if price_text.lower().startswith('from '):
                price_text = price_text[5:]
                
            # Handle Walmart's range format "Now $X.XX - $Y.YY"
            if ' - ' in price_text:
                price_text = price_text.split(' - ')[0]  # Take the lower price
                
            # Handle Walmart's "Now $X.XX" format 
            if price_text.lower().startswith('now '):
                price_text = price_text[4:]
                
            # Handle Walmart's cent format "$X¢"
            if '¢' in price_text:
                cent_match = re.search(r'(\d+)¢', price_text)
                if cent_match:
                    return float(cent_match.group(1)) / 100
            
            # Look for currency symbol with regex
            price_match = re.search(r'\$\s*(\d+(?:,\d+)*(?:\.\d+)?)', price_text)
            if price_match:
                return float(price_match.group(1).replace(',', ''))
                
            # Fallback to just extracting any number
            numbers = re.findall(r'(\d+(?:\.\d+)?)', price_text.replace(',', ''))
            if numbers:
                return float(numbers[0])
                
            # If no price found
            return 0.0
            
        except (ValueError, AttributeError, IndexError) as e:
            self.logger.warning(f"Error parsing price '{price_text}': {str(e)}")
            return 0.0
    
    def _gemini_search_query_prompt(self, search_params: Dict[str, Any]) -> str:
        """
        Generate a prompt for Gemini to create an optimized search query.
        
        Useful for complex searches or when trying to find specific products.
        
        Args:
            search_params: Original search parameters
            
        Returns:
            Gemini-generated search query
        """
        try:
            # Extract query components for prompt
            components = []
            
            if "product_type" in search_params:
                components.append(f"Product type: {search_params['product_type']}")
            
            if "keywords" in search_params:
                keywords = search_params["keywords"]
                if isinstance(keywords, list):
                    components.append(f"Keywords: {', '.join(keywords)}")
                else:
                    components.append(f"Keywords: {keywords}")
            
            if "brands" in search_params and search_params["brands"]:
                brands = search_params["brands"]
                if isinstance(brands, list):
                    components.append(f"Brands: {', '.join(brands)}")
                else:
                    components.append(f"Brands: {brands}")
            
            if "features" in search_params and search_params["features"]:
                features = search_params["features"]
                if isinstance(features, list):
                    components.append(f"Features: {', '.join(features)}")
                else:
                    components.append(f"Features: {features}")
                    
            if "price_range" in search_params and search_params["price_range"]:
                price_range = search_params["price_range"]
                if isinstance(price_range, list) and len(price_range) == 2:
                    min_price, max_price = price_range
                    price_range_str = ""
                    if min_price is not None:
                        price_range_str += f"Min: ${min_price}"
                    if max_price is not None:
                        if price_range_str:
                            price_range_str += f", Max: ${max_price}"
                        else:
                            price_range_str = f"Max: ${max_price}"
                    components.append(f"Price range: {price_range_str}")
            
            # Create the prompt for Gemini
            prompt = f"""
            Create the optimal search query for Walmart's search engine based on these parameters:
            
            {' | '.join(components)}
            
            For Walmart's search engine:
            1. Focus on specific model numbers or part identifiers if present
            2. Include the most important brand names
            3. Keep the query concise (3-7 terms maximum)
            4. Focus on unique, specific terms rather than generic ones
            5. Consider Walmart's specific product categories and terminology
            
            Return ONLY the search query text with no explanation or additional text.
            """
            
            # Call Gemini
            message = MCPMessage(
                sender="WalmartScraperAgent",
                receiver="GeminiAgent",
                content=prompt,
                message_type="REQUEST"
            )
            
            response = self.gemini_agent.process_message(message)
            
            # Clean and return the query
            if isinstance(response.content, str):
                # Clean up the response - remove quotes and extraneous text
                query = response.content.strip()
                query = re.sub(r'^["\']+|["\']+$', '', query)  # Remove surrounding quotes
                query = re.sub(r'^Search Query:\s*', '', query, flags=re.IGNORECASE)  # Remove "Search Query:" prefix
                
                self.logger.info(f"Gemini-generated search query: {query}")
                return query
            
            # Fallback to manual query building
            return self._build_search_query(search_params)
            
        except Exception as e:
            self.logger.error(f"Error generating search query with Gemini: {str(e)}")
            # Fallback to standard query building
            return self._build_search_query(search_params)