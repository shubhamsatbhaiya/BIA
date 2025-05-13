# # """
# # Real eBay Scraper Implementation for DealFinder AI.

# # This module implements the RealEbayScraperAgent class that uses BeautifulSoup
# # and requests to extract actual product data from eBay.
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

# # logger = get_logger("Scrapers.Ebay")

# # class RealEbayScraperAgent(Agent):
# #     """Agent for scraping eBay product listings with actual web scraping"""
    
# #     def __init__(self):
# #         """Initialize the eBay scraper agent."""
# #         super().__init__("EbayScraperAgent")
# #         self.base_url = config.EBAY_BASE_URL
        
# #         # Configure headers with default values
# #         self.headers = {
# #             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
# #             "Accept-Language": "en-US,en;q=0.5",
# #             "Accept-Encoding": "gzip, deflate, br",
# #             "Connection": "keep-alive",
# #             "Upgrade-Insecure-Requests": "1",
# #         }
    
# #     def process_message(self, message: MCPMessage) -> MCPMessage:
# #         """
# #         Process search request for eBay.
        
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
# #         self.logger.info(f"Searching eBay for: {search_params}")
        
# #         try:
# #             # Convert search parameters to eBay search query
# #             query = self._build_search_query(search_params)
            
# #             # Perform the search
# #             products = self._scrape_search_results(query, search_params)
            
# #             return MCPMessage(
# #                 sender=self.name,
# #                 receiver=message.sender,
# #                 content={
# #                     "source": "eBay",
# #                     "query": query,
# #                     "products": products
# #                 },
# #                 message_type="SEARCH_RESPONSE",
# #                 conversation_id=message.conversation_id
# #             )
        
# #         except Exception as e:
# #             self.logger.error(f"Error scraping eBay: {str(e)}")
# #             return MCPMessage(
# #                 sender=self.name,
# #                 receiver=message.sender,
# #                 content={"error": f"eBay scraping error: {str(e)}"},
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
# #         Scrape eBay search results for the given query.
        
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
        
# #         # Set up request parameters
# #         params = {
# #             "_nkw": query,
# #             "_sacat": "0",
# #             "_ipg": "50",  # Items per page
# #         }
        
# #         # Add price range if specified
# #         if "price_range" in search_params and search_params["price_range"]:
# #             price_range = search_params["price_range"]
# #             if isinstance(price_range, list) and len(price_range) == 2:
# #                 min_price, max_price = price_range
# #                 if min_price is not None:
# #                     params["_udlo"] = min_price  # Price Lower than
# #                 if max_price is not None:
# #                     params["_udhi"] = max_price  # Price Higher than
        
# #         # Add sorting parameter if specified
# #         if "sorting_preference" in search_params:
# #             sort_pref = search_params["sorting_preference"]
# #             if sort_pref == "price_low_to_high":
# #                 params["_sop"] = "15"  # Price + Shipping: lowest first
# #             elif sort_pref == "price_high_to_low":
# #                 params["_sop"] = "16"  # Price + Shipping: highest first
# #             elif sort_pref == "rating":
# #                 params["_sop"] = "24"  # Best Match
# #             elif sort_pref == "newest":
# #                 params["_sop"] = "10"  # Newly Listed
        
# #         # Filter to Buy It Now items if preferred
# #         if "buy_it_now" in search_params and search_params["buy_it_now"]:
# #             params["LH_BIN"] = "1"
        
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
# #         products = []
# #         seen_ids = set()
# #         product_divs = soup.select('li.s-item')
# #         # Optional: always_use_gemini
# #         if search_params.get("always_use_gemini"):
# #             self.logger.info("Gemini used for product extraction")
# #             from dealfinder.agents.gemini_agent import GeminiAgent
# #             gemini = GeminiAgent()
# #             return [gemini.extract_product_details_from_html(str(div)) for div in product_divs[:max_results]]

# #         for div in product_divs[:max_results]:
# #             product = self._extract_product_data(div)
# #             if not product:
# #                 continue
# #             if not self._is_relevant_product(product, search_params.get("keywords", [])):
# #                 continue
# #             item_id = product.get("item_id")
# #             if item_id in seen_ids:
# #                 continue
# #             seen_ids.add(item_id)
# #             product["source"] = "eBay"
# #             self.logger.info(f"Extracted product: {product['title']} at {product['price']} USD")
# #             products.append(product)
# #             if len(products) >= max_results:
# #                 break

# #         time.sleep(random.uniform(
# #             config.SCRAPING_DELAY_MIN,
# #             config.SCRAPING_DELAY_MAX
# #         ))
# #         return products
    
# #     def _extract_product_data(self, product_div) -> Optional[Dict[str, Any]]:
# #         """
# #         Extract product data from a product div element.
        
# #         Args:
# #             product_div: BeautifulSoup element containing product data
            
# #         Returns:
# #             A dictionary of product data, or None if extraction fails
# #         """
# #         try:
# #             # Extract product title
# #             title_element = product_div.select_one('.s-item__title')
# #             if not title_element:
# #                 return None
                
# #             title = title_element.text.strip()
# #             # Skip "Shop on eBay" placeholder items
# #             if title == "Shop on eBay" or "Shop on eBay" in title:
# #                 return None
            
# #             # Remove "New Listing" prefix if present
# #             title = re.sub(r'^New Listing', '', title).strip()
            
# #             # Extract product URL
# #             url_element = product_div.select_one('a.s-item__link')
# #             url = "#"
# #             if url_element and 'href' in url_element.attrs:
# #                 url = url_element['href']
            
# #             # Extract item ID from URL
# #             item_id = ""
# #             id_match = re.search(r'itm/(\d+)', url)
# #             if id_match:
# #                 item_id = id_match.group(1)
            
# #             # Extract product image URL
# #             img_element = product_div.select_one('.s-item__image-img')
# #             image_url = ""
# #             if img_element:
# #                 if 'src' in img_element.attrs:
# #                     image_url = img_element['src']
# #                 elif 'data-src' in img_element.attrs:
# #                     image_url = img_element['data-src']
            
# #             # Extract product price
# #             price_element = product_div.select_one('.s-item__price')
# #             price = 0.0
# #             if price_element:
# #                 price_text = price_element.text.strip()
# #                 if "to" in price_text:  # Handle price ranges like "$10.00 to $15.00"
# #                     price_text = price_text.split("to")[0].strip()
# #                 price = self._parse_price(price_text)
            
# #             # Extract shipping cost
# #             shipping_element = product_div.select_one('.s-item__shipping')
# #             shipping_cost = 0.0
# #             is_free_shipping = False
# #             if shipping_element:
# #                 shipping_text = shipping_element.text.strip()
# #                 if "Free" in shipping_text:
# #                     is_free_shipping = True
# #                 else:
# #                     shipping_cost = self._parse_price(shipping_text)
            
# #             # Calculate total price
# #             total_price = price + shipping_cost
            
# #             # Extract product condition
# #             condition_element = product_div.select_one('.SECONDARY_INFO')
# #             condition = condition_element.text.strip() if condition_element else "Not specified"
            
# #             # Extract listing type (Auction, Buy It Now, etc.)
# #             listing_type = "Buy It Now"  # Default
# #             bids_element = product_div.select_one('.s-item__bids')
# #             if bids_element:
# #                 listing_type = "Auction"
            
# #             # Check if the product is sponsored
# #             is_sponsored = bool(product_div.select_one('.s-item__SPONSORED'))
            
# #             # Extract seller rating if available
# #             seller_element = product_div.select_one('.s-item__seller-info-text')
# #             seller_rating = 0.0
# #             if seller_element:
# #                 rating_match = re.search(r'(\d+(\.\d+)?)%', seller_element.text)
# #                 if rating_match:
# #                     seller_rating = float(rating_match.group(1))
            
# #             # Create product dictionary
# #             product = {
# #                 "title": title,
# #                 "price": price,
# #                 "shipping": shipping_cost,
# #                 "total_price": total_price,
# #                 "is_free_shipping": is_free_shipping,
# #                 "currency": "USD",
# #                 "url": url,
# #                 "image_url": image_url,
# #                 "is_sponsored": is_sponsored,
# #                 "condition": condition,
# #                 "listing_type": listing_type,
# #                 "seller_rating": seller_rating,
# #                 "item_id": item_id,
# #             }
            
# #             if not title or not url or url.strip() == "#" or price == 0.0:
# #                 self.logger.warning(f"Incomplete eBay data for item ID {item_id}, using Gemini fallback.")
# #                 gemini_fallback = self._extract_with_gemini(str(product_div))
# #                 if gemini_fallback:
# #                     self.logger.info("Gemini used for product extraction")
# #                     self.logger.info(f"Extracted product: {gemini_fallback.get('title', '')} at {gemini_fallback.get('price', 0)} USD")
# #                     return gemini_fallback
# #             self.logger.info(f"Extracted product: {product['title']} at {product['price']} USD")
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
# #             # Remove currency symbol, commas, and extra text
# #             price_text = re.sub(r'[^\d\.]', '', price_text.split(' ')[0])
# #             if price_text:
# #                 return float(price_text)
# #             return 0.0
# #         except (ValueError, AttributeError, IndexError):
# #             return 0.0

# #     def _extract_with_gemini(self, html_block: str) -> Optional[Dict[str, Any]]:
# #         try:
# #             from dealfinder.agents.gemini_agent import GeminiAgent
# #             gemini = GeminiAgent()
# #             data = gemini.extract_product_details_from_html(html_block)
# #             if "item_id" not in data or not data["item_id"]:
# #                 return None
# #             data.setdefault("currency", "USD")
# #             data.setdefault("source", "eBay")
# #             self.logger.info("Gemini used for product extraction")
# #             self.logger.info(f"Extracted product: {data.get('title', '')} at {data.get('price', 0)} USD")
# #             return data
# #         except Exception as e:
# #             self.logger.error(f"Gemini fallback failed: {str(e)}")
# #             return None
# """
# Real eBay Scraper Implementation for DealFinder AI.

# This module implements the RealEbayScraperAgent class that uses BeautifulSoup
# and requests to extract actual product data from eBay.
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

# logger = get_logger("Scrapers.Ebay")

# class RealEbayScraperAgent(Agent):
#     """Agent for scraping eBay product listings with actual web scraping"""
    
#     def __init__(self):
#         """Initialize the eBay scraper agent."""
#         super().__init__("EbayScraperAgent")
#         self.base_url = config.EBAY_BASE_URL
        
#         # Configure headers with default values
#         self.headers = {
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#             "Accept-Language": "en-US,en;q=0.5",
#             "Accept-Encoding": "gzip, deflate, br",
#             "Connection": "keep-alive",
#             "Upgrade-Insecure-Requests": "1",
#         }
    
#     def process_message(self, message: MCPMessage) -> MCPMessage:
#         """
#         Process search request for eBay.
        
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
#         self.logger.info(f"Searching eBay for: {search_params}")
        
#         try:
#             # Convert search parameters to eBay search query
#             query = self._build_search_query(search_params)
            
#             # Perform the search
#             products = self._scrape_search_results(query, search_params)
            
#             return MCPMessage(
#                 sender=self.name,
#                 receiver=message.sender,
#                 content={
#                     "source": "eBay",
#                     "query": query,
#                     "products": products
#                 },
#                 message_type="SEARCH_RESPONSE",
#                 conversation_id=message.conversation_id
#             )
        
#         except Exception as e:
#             self.logger.error(f"Error scraping eBay: {str(e)}")
#             return MCPMessage(
#                 sender=self.name,
#                 receiver=message.sender,
#                 content={"error": f"eBay scraping error: {str(e)}"},
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
#         Scrape eBay search results for the given query.
        
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
        
#         # Set up request parameters
#         params = {
#             "_nkw": query,
#             "_sacat": "0",
#             "_ipg": "50",  # Items per page
#         }
        
#         # Add price range if specified
#         if "price_range" in search_params and search_params["price_range"]:
#             price_range = search_params["price_range"]
#             if isinstance(price_range, list) and len(price_range) == 2:
#                 min_price, max_price = price_range
#                 if min_price is not None:
#                     params["_udlo"] = min_price  # Price Lower than
#                 if max_price is not None:
#                     params["_udhi"] = max_price  # Price Higher than
        
#         # Add sorting parameter if specified
#         if "sorting_preference" in search_params:
#             sort_pref = search_params["sorting_preference"]
#             if sort_pref == "price_low_to_high":
#                 params["_sop"] = "15"  # Price + Shipping: lowest first
#             elif sort_pref == "price_high_to_low":
#                 params["_sop"] = "16"  # Price + Shipping: highest first
#             elif sort_pref == "rating":
#                 params["_sop"] = "24"  # Best Match
#             elif sort_pref == "newest":
#                 params["_sop"] = "10"  # Newly Listed
        
#         # Filter to Buy It Now items if preferred
#         if "buy_it_now" in search_params and search_params["buy_it_now"]:
#             params["LH_BIN"] = "1"
        
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
#         products = []
#         seen_ids = set()
#         product_divs = soup.select('li.s-item')
        
#         # Optional: always_use_gemini
#         if search_params.get("always_use_gemini"):
#             self.logger.info("Gemini used for product extraction")
#             from dealfinder.agents.gemini_agent import GeminiAgent
#             gemini = GeminiAgent()
#             return [gemini.extract_product_details_from_html(str(div)) for div in product_divs[:max_results]]

#         # Process products without the relevance filter
#         for div in product_divs[:max_results * 2]:  # Get extra products in case some fail extraction
#             product = self._extract_product_data(div)
#             if not product:
#                 continue
                
#             # Removed the relevance check:
#             # if not self._is_relevant_product(product, search_params.get("keywords", [])):
#             #    continue
                
#             item_id = product.get("item_id")
#             if item_id in seen_ids:
#                 continue
                
#             seen_ids.add(item_id)
#             product["source"] = "eBay"
#             self.logger.info(f"Extracted product: {product['title']} at {product['price']} USD")
#             products.append(product)
            
#             if len(products) >= max_results:
#                 break

#         time.sleep(random.uniform(
#             config.SCRAPING_DELAY_MIN,
#             config.SCRAPING_DELAY_MAX
#         ))
        
#         # Log the final count
#         self.logger.info(f"Returning {len(products)} products from eBay")
        
#         return products
    
#     def _extract_product_data(self, product_div) -> Optional[Dict[str, Any]]:
#         """
#         Extract product data from a product div element.
        
#         Args:
#             product_div: BeautifulSoup element containing product data
            
#         Returns:
#             A dictionary of product data, or None if extraction fails
#         """
#         try:
#             # Extract product title
#             title_element = product_div.select_one('.s-item__title')
#             if not title_element:
#                 return None
                
#             title = title_element.text.strip()
#             # Skip "Shop on eBay" placeholder items
#             if title == "Shop on eBay" or "Shop on eBay" in title:
#                 return None
            
#             # Remove "New Listing" prefix if present
#             title = re.sub(r'^New Listing', '', title).strip()
            
#             # Extract product URL
#             url_element = product_div.select_one('a.s-item__link')
#             url = "#"
#             if url_element and 'href' in url_element.attrs:
#                 url = url_element['href']
            
#             # Extract item ID from URL
#             item_id = ""
#             id_match = re.search(r'itm/(\d+)', url)
#             if id_match:
#                 item_id = id_match.group(1)
            
#             # Extract product image URL
#             img_element = product_div.select_one('.s-item__image-img')
#             image_url = ""
#             if img_element:
#                 if 'src' in img_element.attrs:
#                     image_url = img_element['src']
#                 elif 'data-src' in img_element.attrs:
#                     image_url = img_element['data-src']
            
#             # Extract product price
#             price_element = product_div.select_one('.s-item__price')
#             price = 0.0
#             if price_element:
#                 price_text = price_element.text.strip()
#                 if "to" in price_text:  # Handle price ranges like "$10.00 to $15.00"
#                     price_text = price_text.split("to")[0].strip()
#                 price = self._parse_price(price_text)
            
#             # Extract shipping cost
#             shipping_element = product_div.select_one('.s-item__shipping')
#             shipping_cost = 0.0
#             is_free_shipping = False
#             if shipping_element:
#                 shipping_text = shipping_element.text.strip()
#                 if "Free" in shipping_text:
#                     is_free_shipping = True
#                 else:
#                     shipping_cost = self._parse_price(shipping_text)
            
#             # Calculate total price
#             total_price = price + shipping_cost
            
#             # Extract product condition
#             condition_element = product_div.select_one('.SECONDARY_INFO')
#             condition = condition_element.text.strip() if condition_element else "Not specified"
            
#             # Extract listing type (Auction, Buy It Now, etc.)
#             listing_type = "Buy It Now"  # Default
#             bids_element = product_div.select_one('.s-item__bids')
#             if bids_element:
#                 listing_type = "Auction"
            
#             # Check if the product is sponsored
#             is_sponsored = bool(product_div.select_one('.s-item__SPONSORED'))
            
#             # Extract seller rating if available
#             seller_element = product_div.select_one('.s-item__seller-info-text')
#             seller_rating = 0.0
#             if seller_element:
#                 rating_match = re.search(r'(\d+(\.\d+)?)%', seller_element.text)
#                 if rating_match:
#                     seller_rating = float(rating_match.group(1))
            
#             # Extract item description if available
#             description_element = product_div.select_one('.s-item__subtitle')
#             description = description_element.text.strip() if description_element else ""
            
#             # Create product dictionary
#             product = {
#                 "title": title,
#                 "price": price,
#                 "shipping": shipping_cost,
#                 "total_price": total_price,
#                 "is_free_shipping": is_free_shipping,
#                 "currency": "USD",
#                 "url": url,
#                 "image_url": image_url,
#                 "is_sponsored": is_sponsored,
#                 "condition": condition,
#                 "listing_type": listing_type,
#                 "seller_rating": seller_rating,
#                 "item_id": item_id,
#                 "description": description
#             }
            
#             if not title or not url or url.strip() == "#" or price == 0.0:
#                 self.logger.warning(f"Incomplete eBay data for item ID {item_id}, using Gemini fallback.")
#                 gemini_fallback = self._extract_with_gemini(str(product_div))
#                 if gemini_fallback:
#                     self.logger.info("Gemini used for product extraction")
#                     self.logger.info(f"Extracted product: {gemini_fallback.get('title', '')} at {gemini_fallback.get('price', 0)} USD")
#                     return gemini_fallback
                    
#             self.logger.info(f"Extracted product: {product['title']} at {product['price']} USD")
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
#             # Remove currency symbol, commas, and extra text
#             price_text = re.sub(r'[^\d\.]', '', price_text.split(' ')[0])
#             if price_text:
#                 return float(price_text)
#             return 0.0
#         except (ValueError, AttributeError, IndexError):
#             return 0.0

#     def _extract_with_gemini(self, html_block: str) -> Optional[Dict[str, Any]]:
#         try:
#             from dealfinder.agents.gemini_agent import GeminiAgent
#             gemini = GeminiAgent()
#             data = gemini.extract_product_details_from_html(html_block)
#             if "item_id" not in data or not data["item_id"]:
#                 return None
#             data.setdefault("currency", "USD")
#             data.setdefault("source", "eBay")
#             self.logger.info("Gemini used for product extraction")
#             self.logger.info(f"Extracted product: {data.get('title', '')} at {data.get('price', 0)} USD")
#             return data
#         except Exception as e:
#             self.logger.error(f"Gemini fallback failed: {str(e)}")
#             return None
"""
Real eBay Scraper Implementation for DealFinder AI with Gemini-enhanced search.

This module implements the RealEbayScraperAgent class that uses BeautifulSoup,
requests, and Gemini AI to extract and optimize product data from eBay.
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

logger = get_logger("Scrapers.Ebay")

class RealEbayScraperAgent(Agent):
    """Agent for scraping eBay product listings with Gemini-enhanced search optimization"""
    
    def __init__(self):
        """Initialize the eBay scraper agent."""
        super().__init__("EbayScraperAgent")
        self.base_url = config.EBAY_BASE_URL
        self.gemini_agent = GeminiAgent()
        
        # Configure headers with default values
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Process search request for eBay.
        
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
        self.logger.info(f"Searching eBay for: {search_params}")
        
        try:
            # Use Gemini to optimize the search query for eBay's search engine
            optimized_params = self._optimize_search_params(search_params)
            self.logger.info(f"Optimized search parameters: {optimized_params}")
            
            # Convert optimized parameters to eBay search query
            query = self._build_search_query(optimized_params)
            self.logger.info(f"Built eBay query: {query}")
            
            # Perform the search
            products = self._scrape_search_results(query, optimized_params)
            
            # Apply Gemini-based relevance filtering
            if not search_params.get("skip_relevance_filter", False):
                products = self._apply_relevance_filter(products, search_params)
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={
                    "source": "eBay",
                    "query": query,
                    "products": products
                },
                message_type="SEARCH_RESPONSE",
                conversation_id=message.conversation_id
            )
        
        except Exception as e:
            self.logger.error(f"Error scraping eBay: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"eBay scraping error: {str(e)}"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
    
    def _optimize_search_params(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Gemini to optimize search parameters for eBay's search engine.
        
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
            Optimize this search query for eBay's search engine:
            
            "{original_query}"
            
            For eBay searches, please:
            1. Focus on exact model numbers and specific part identifiers if present
            2. Include key brand names
            3. Remove generic words that may dilute results
            4. Add eBay-specific terms that might improve results
            5. Optimize for finding the most relevant listings
            
            Return a JSON object with:
            - optimized_keywords: List of 3-5 optimized search terms (most important first)
            - category_hints: Any eBay category suggestions
            - must_include_terms: Terms that MUST be in results
            - exclude_terms: Terms that should NOT be in results
            
            Format as JSON only with no explanation.
            """
            
            # Call Gemini
            message = MCPMessage(
                sender="EbayScraperAgent",
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
            
            # Add category hints if provided
            if "category_hints" in optimization_data and optimization_data["category_hints"]:
                optimized_params["category_hints"] = optimization_data["category_hints"]
            
            # Add must-include terms
            if "must_include_terms" in optimization_data and optimization_data["must_include_terms"]:
                optimized_params["must_include_terms"] = optimization_data["must_include_terms"]
            
            # Add exclude terms
            if "exclude_terms" in optimization_data and optimization_data["exclude_terms"]:
                optimized_params["exclude_terms"] = optimization_data["exclude_terms"]
            
            return optimized_params
            
        except Exception as e:
            self.logger.error(f"Error optimizing search parameters: {str(e)}")
            # Fall back to original parameters
            return search_params
    
    def _build_search_query(self, search_params: Dict[str, Any]) -> str:
        """
        Build optimized search query string from parameters for eBay's search engine.
        
        Args:
            search_params: Optimized search parameters
            
        Returns:
            A search query string
        """
        components = []
        
        # Primary components: product type and exact model numbers
        if "product_type" in search_params and search_params["product_type"]:
            components.append(search_params["product_type"])
        
        # Add keywords with priority
        if "keywords" in search_params:
            if isinstance(search_params["keywords"], list):
                # For eBay, limit to most important keywords to avoid too-specific searches
                priority_keywords = search_params["keywords"]
                if len(priority_keywords) > 5:
                    priority_keywords = priority_keywords[:5]
                components.extend(priority_keywords)
            else:
                components.append(search_params["keywords"])
        
        # Add brand information (important for eBay)
        if "brands" in search_params and search_params["brands"]:
            brands = search_params["brands"]
            if isinstance(brands, list):
                # For eBay, include each brand separately for better matching
                components.extend(brands)
            else:
                components.append(brands)
        
        # Add must_include_terms if specified
        if "must_include_terms" in search_params and search_params["must_include_terms"]:
            terms = search_params["must_include_terms"]
            if isinstance(terms, list):
                components.extend(terms)
            else:
                components.append(terms)
        
        # For eBay, we want to be selective with features to avoid over-filtering
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
        
        # eBay works best with reasonable length queries
        query = " ".join(components)
        
        # If query is too long, prioritize the most important components
        if len(query.split()) > 10:
            # For eBay, keep it more focused on specific identifiers
            short_components = []
            
            # Product type is important
            if "product_type" in search_params and search_params["product_type"]:
                short_components.append(search_params["product_type"])
            
            # Brands are very important on eBay
            if "brands" in search_params and search_params["brands"]:
                if isinstance(search_params["brands"], list) and search_params["brands"]:
                    # Include all brands as they're critical for eBay
                    short_components.extend(search_params["brands"])
                else:
                    short_components.append(search_params["brands"])
            
            # Add a few critical keywords
            if "keywords" in search_params and search_params["keywords"]:
                if isinstance(search_params["keywords"], list) and search_params["keywords"]:
                    # Take top 3 keywords only
                    short_components.extend(search_params["keywords"][:3])
                else:
                    short_components.append(search_params["keywords"])
            
            query = " ".join(short_components)
        
        self.logger.info(f"Built optimized eBay search query: {query}")
        return query

    def _scrape_search_results(self, query: str, search_params: Dict[str, Any], max_results: int = None) -> List[Dict[str, Any]]:
        """
        Scrape eBay search results for the given query with enhanced parameters.
        
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
        
        # Set up eBay-specific request parameters
        params = {
            "_nkw": query,
            "_sacat": "0",
            "_ipg": "96",  # Increased items per page for better dataset
        }
        
        # Add category if available from Gemini optimization
        if "category_hints" in search_params and search_params["category_hints"]:
            category_hint = search_params["category_hints"]
            if isinstance(category_hint, list) and category_hint:
                category_hint = category_hint[0]
            # eBay requires numeric category IDs, but we'll use text hints for fallback search
            params["_nkw"] = f"{params['_nkw']} {category_hint}"
        
        # Add price range if specified
        if "price_range" in search_params and search_params["price_range"]:
            price_range = search_params["price_range"]
            if isinstance(price_range, list) and len(price_range) == 2:
                min_price, max_price = price_range
                if min_price is not None:
                    params["_udlo"] = min_price  # Price Lower than
                if max_price is not None:
                    params["_udhi"] = max_price  # Price Higher than
        
        # Add sorting parameter if specified
        if "sorting_preference" in search_params:
            sort_pref = search_params["sorting_preference"]
            if sort_pref == "price_low_to_high":
                params["_sop"] = "15"  # Price + Shipping: lowest first
            elif sort_pref == "price_high_to_low":
                params["_sop"] = "16"  # Price + Shipping: highest first
            elif sort_pref == "rating":
                params["_sop"] = "24"  # Best Match
            elif sort_pref == "newest":
                params["_sop"] = "10"  # Newly Listed
        
        # Filter to Buy It Now items if preferred
        if "buy_it_now" in search_params and search_params["buy_it_now"]:
            params["LH_BIN"] = "1"
        else:
            # Otherwise, favor "Buy It Now" but don't exclude auctions
            # Buy It Now tends to have more reliable information
            params["LH_BIN"] = "1"
        
        # Include specific eBay filters based on optimization
        if "condition" in search_params:
            condition = search_params["condition"]
            if condition == "new":
                params["LH_ItemCondition"] = "1000"  # New
            elif condition == "used":
                params["LH_ItemCondition"] = "3000"  # Used
            elif condition == "refurbished":
                params["LH_ItemCondition"] = "2500"  # Manufacturer refurbished
        
        # Use a random user agent for each request to avoid blocking
        current_headers = self.headers.copy()
        current_headers["User-Agent"] = random.choice(config.USER_AGENTS)

        # Make the request with retry logic
        for attempt in range(3):
            try:
                self.logger.info(f"Making eBay search request with params: {params}")
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=current_headers,
                    timeout=config.SCRAPING_TIMEOUT
                )
                
                if response.status_code == 200:
                    break
                else:
                    self.logger.warning(f"eBay search request failed with status {response.status_code}, retrying")
                    time.sleep(2 ** attempt)
            except Exception as e:
                self.logger.warning(f"Request error: {str(e)}, retrying")
                time.sleep(2 ** attempt)
        else:
            self.logger.error("Max retries exceeded")
            return []

        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get product listings
        products = []
        seen_ids = set()
        product_divs = soup.select('li.s-item')
        
        self.logger.info(f"Found {len(product_divs)} product listings")
        
        # Optional: Use Gemini for all product extraction
        if search_params.get("always_use_gemini"):
            self.logger.info("Using Gemini for all product extraction")
            extracted_products = []
            
            for div in product_divs[:scrape_count]:
                product = self.gemini_agent.extract_product_details_from_html(str(div))
                if product and isinstance(product, dict):
                    product["source"] = "eBay"
                    extracted_products.append(product)
                    
            # Return the requested number of products
            return extracted_products[:max_results]

        # Process products with standard extraction
        for div in product_divs[:scrape_count]:
            product = self._extract_product_data(div)
            if not product:
                continue
                
            item_id = product.get("item_id")
            if item_id in seen_ids:
                continue
                
            seen_ids.add(item_id)
            product["source"] = "eBay"
            self.logger.info(f"Extracted product: {product['title']} at {product['price']} USD")
            products.append(product)
            
            if len(products) >= scrape_count:
                break

        # Add a short delay to avoid rate limiting
        time.sleep(random.uniform(
            config.SCRAPING_DELAY_MIN, 
            config.SCRAPING_DELAY_MAX
        ))
        
        self.logger.info(f"Extracted {len(products)} products from eBay")
        
        # Return the requested number of products (will be filtered for relevance later)
        return products
    
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
                
                # Calculate a relevance score
                relevance_score = 0
                
                # Keywords in title are very important
                keyword_matches = sum(1 for kw in keywords if kw in title)
                relevance_score += keyword_matches * 10
                
                # Keywords in description are less important
                description_matches = sum(1 for kw in keywords if kw in description)
                relevance_score += description_matches * 2
                
                # Prefer Buy It Now listings
                if product.get("listing_type") == "Buy It Now":
                    relevance_score += 5
                
                # Prefer listings with better condition
                condition = product.get("condition", "").lower()
                if "new" in condition:
                    relevance_score += 8
                elif "refurbished" in condition or "renewed" in condition:
                    relevance_score += 4
                elif "used" in condition and ("like new" in condition or "excellent" in condition):
                    relevance_score += 3
                
                # Prefer listings with better seller ratings
                seller_rating = product.get("seller_rating", 0)
                if seller_rating > 95:
                    relevance_score += 5
                elif seller_rating > 90:
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
    
    def _extract_product_data(self, product_div) -> Optional[Dict[str, Any]]:
        """
        Extract product data from a product div element with enhanced extraction.
        
        Args:
            product_div: BeautifulSoup element containing product data
            
        Returns:
            A dictionary of product data, or None if extraction fails
        """
        try:
            # Extract product title
            title_element = product_div.select_one('.s-item__title')
            if not title_element:
                return None
                
            title = title_element.text.strip()
            
            # Skip "Shop on eBay" placeholder items
            if title == "Shop on eBay" or "Shop on eBay" in title:
                return None
            
            # Remove "New Listing" prefix if present
            title = re.sub(r'^New Listing', '', title).strip()
            
            # Extract product URL
            url_element = product_div.select_one('a.s-item__link')
            url = "#"
            if url_element and 'href' in url_element.attrs:
                url = url_element['href']
            
            # Extract item ID from URL
            item_id = ""
            id_match = re.search(r'itm/(\d+)', url)
            if id_match:
                item_id = id_match.group(1)
            
            # Extract product image URL
            img_element = product_div.select_one('.s-item__image-img')
            image_url = ""
            if img_element:
                if 'src' in img_element.attrs:
                    image_url = img_element['src']
                elif 'data-src' in img_element.attrs:
                    image_url = img_element['data-src']
            
            # Extract product price
            price_element = product_div.select_one('.s-item__price')
            price = 0.0
            if price_element:
                price_text = price_element.text.strip()
                if "to" in price_text:  # Handle price ranges like "$10.00 to $15.00"
                    price_text = price_text.split("to")[0].strip()
                price = self._parse_price(price_text)
            
            # Extract shipping cost
            shipping_element = product_div.select_one('.s-item__shipping')
            shipping_cost = 0.0
            is_free_shipping = False
            if shipping_element:
                shipping_text = shipping_element.text.strip()
                if "Free" in shipping_text:
                    is_free_shipping = True
                else:
                    shipping_cost = self._parse_price(shipping_text)
            
            # Calculate total price
            total_price = price + shipping_cost
            
            # Extract product condition
            condition_element = product_div.select_one('.SECONDARY_INFO')
            condition = condition_element.text.strip() if condition_element else "Not specified"
            
            # Extract listing type (Auction, Buy It Now, etc.)
            listing_type = "Buy It Now"  # Default
            bids_element = product_div.select_one('.s-item__bids')
            if bids_element:
                listing_type = "Auction"
            
            # Check if the product is sponsored
            is_sponsored = bool(product_div.select_one('.s-item__SPONSORED'))
            
            # Extract seller rating if available
            seller_element = product_div.select_one('.s-item__seller-info-text')
            seller_rating = 0.0
            if seller_element:
                rating_match = re.search(r'(\d+(\.\d+)?)%', seller_element.text)
                if rating_match:
                    seller_rating = float(rating_match.group(1))
            
            # Extract item description if available
            description_element = product_div.select_one('.s-item__subtitle')
            description = description_element.text.strip() if description_element else ""
            
            # Try to extract quantity sold if available (indicates popularity)
            quantity_sold = 0
            sold_element = product_div.select_one('.s-item__quantitySold')
            if sold_element:
                sold_text = sold_element.text.strip()
                sold_match = re.search(r'(\d+)', sold_text)
                if sold_match:
                    quantity_sold = int(sold_match.group(1))
            
            # Try to extract watch count (another popularity indicator)
            watch_count = 0
            watches_element = product_div.select_one('.s-item__watchCountTotal')
            if watches_element:
                watches_text = watches_element.text.strip()
                watches_match = re.search(r'(\d+)', watches_text)
                if watches_match:
                    watch_count = int(watches_match.group(1))
            
            # Create product dictionary with enhanced data
            product = {
                "title": title,
                "price": price,
                "shipping": shipping_cost,
                "total_price": total_price,
                "is_free_shipping": is_free_shipping,
                "currency": "USD",
                "url": url,
                "image_url": image_url,
                "is_sponsored": is_sponsored,
                "condition": condition,
                "listing_type": listing_type,
                "seller_rating": seller_rating,
                "item_id": item_id,
                "description": description,
                "quantity_sold": quantity_sold,
                "watch_count": watch_count
            }
            
            # Use Gemini fallback if essential fields are missing
            if not title or not url or url.strip() == "#" or price == 0.0:
                self.logger.warning(f"Incomplete eBay data for item ID {item_id}, using Gemini fallback.")
                gemini_fallback = self._extract_with_gemini(str(product_div))
                if gemini_fallback:
                    self.logger.info("Gemini used for product extraction")
                    self.logger.info(f"Extracted product: {gemini_fallback.get('title', '')} at {gemini_fallback.get('price', 0)} USD")
                    return gemini_fallback
                    
            self.logger.info(f"Extracted product: {product['title']} at {product['price']} USD")
            return product
            
        except Exception as e:
            self.logger.error(f"Error extracting product data: {str(e)}")
            return None
    
    def _parse_price(self, price_text: str) -> float:
        """
        Parse price string to float with improved accuracy.
        
        Args:
            price_text: Price text to parse
            
        Returns:
            Parsed price as float
        """
        try:
            # First check for common patterns
            if not price_text or price_text.lower() in ('free', 'n/a', 'unknown'):
                return 0.0
                
            # Handle 'to' ranges by taking first value
            if ' to ' in price_text:
                price_text = price_text.split(' to ')[0]
                
            # Look for currency symbols with regex
            price_match = re.search(r'(?:US\s*)?\$\s*(\d+(?:,\d+)*(?:\.\d+)?)', price_text)
            if price_match:
                # Remove commas and convert to float
                return float(price_match.group(1).replace(',', ''))
                
            # Fallback: extract any numeric value
            numeric_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', price_text)
            if numeric_match:
                return float(numeric_match.group(1).replace(',', ''))
                
            # If no numeric value found
            return 0.0
            
        except (ValueError, AttributeError, IndexError) as e:
            self.logger.warning(f"Error parsing price '{price_text}': {str(e)}")
            return 0.0

    def _extract_with_gemini(self, html_block: str) -> Optional[Dict[str, Any]]:
        """
        Use Gemini to extract product details from HTML.
        
        Args:
            html_block: HTML string containing product data
            
        Returns:
            Dictionary of product details, or None if extraction fails
        """
        try:
            # Create a detailed prompt for Gemini
            prompt = f"""
            Extract detailed product information from this eBay listing HTML:
            
            ```html
            {html_block}
            ```
            
                Extract:
            - title: Full product title
            - price: Numeric price value only (no currency symbol)
            - shipping: Shipping cost (0 if free)
            - currency: Currency code (e.g., USD)
            - url: Product URL
            - image_url: Main product image URL
            - condition: Item condition (New, Used, etc.)
            - listing_type: "Auction" or "Buy It Now"
            - seller_rating: Seller feedback percentage
            - item_id: eBay item ID
            - description: Any additional description text
            - is_free_shipping: Boolean for free shipping
            - is_sponsored: Boolean for sponsored listing
            - quantity_sold: Number of items sold if shown
            - watch_count: Number of people watching if shown
            
            Return a clean JSON object with these fields. Use null for missing values.
            ```
            """
            
            # Call Gemini
            data = self.gemini_agent.extract_product_details_from_html(html_block)
            
            # Validate the response
            if not isinstance(data, dict) or not data:
                return None
                
            # Set default source
            data.setdefault("currency", "USD")
            data.setdefault("source", "eBay")
            
            # Convert price to float if it's not already
            if "price" in data and data["price"] is not None:
                try:
                    data["price"] = float(data["price"])
                except (ValueError, TypeError):
                    # If conversion fails, default to 0
                    data["price"] = 0.0
            
            # Convert shipping to float
            if "shipping" in data and data["shipping"] is not None:
                try:
                    data["shipping"] = float(data["shipping"])
                except (ValueError, TypeError):
                    data["shipping"] = 0.0
            
            # Calculate total_price
            if "price" in data and "shipping" in data:
                data["total_price"] = data["price"] + data["shipping"]
            
            self.logger.info(f"Gemini extracted: {data.get('title', 'Unknown')} at {data.get('price', 0)} USD")
            return data
            
        except Exception as e:
            self.logger.error(f"Gemini extraction failed: {str(e)}")
            return None
            
    def _gemini_relevance_check(self, product: Dict[str, Any], search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Gemini to evaluate if a product is relevant to the search query.
        
        Args:
            product: Product data dictionary
            search_params: Original search parameters
            
        Returns:
            Dictionary with relevance score and reasoning
        """
        try:
            # Extract original query components
            query_components = []
            if "product_type" in search_params:
                query_components.append(search_params["product_type"])
                
            if "keywords" in search_params:
                if isinstance(search_params["keywords"], list):
                    query_components.extend(search_params["keywords"])
                else:
                    query_components.append(search_params["keywords"])
                    
            original_query = " ".join(query_components)
            
            # Create product summary
            product_summary = {
                "title": product.get("title", ""),
                "price": product.get("price", 0),
                "description": product.get("description", ""),
                "condition": product.get("condition", "Not specified"),
                "listing_type": product.get("listing_type", "Unknown")
            }
            
            # Create prompt for Gemini
            prompt = f"""
            Evaluate if this eBay product is relevant to the search query.
            
            Search query: "{original_query}"
            
            Product:
            {json.dumps(product_summary, indent=2)}
            
            Return a JSON with:
            - relevance_score: 0-100 (higher means more relevant)
            - reasoning: Brief explanation of the score
            
            Format as JSON only.
            """
            
            # Call Gemini
            message = MCPMessage(
                sender="EbayScraperAgent",
                receiver="GeminiAgent",
                content=prompt,
                message_type="REQUEST"
            )
            
            response = self.gemini_agent.process_message(message)
            
            # Parse response
            relevance_data = {"relevance_score": 50, "reasoning": "Default score"}
            
            if isinstance(response.content, str):
                # Try to extract JSON from the response
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response.content)
                if json_match:
                    relevance_data = json.loads(json_match.group(1))
                else:
                    # Try direct parsing
                    try:
                        relevance_data = json.loads(response.content)
                    except json.JSONDecodeError:
                        pass
            else:
                # Response is already parsed
                relevance_data = response.content
            
            return relevance_data
            
        except Exception as e:
            self.logger.error(f"Error in Gemini relevance check: {str(e)}")
            return {"relevance_score": 50, "reasoning": f"Error: {str(e)}"}