# # """
# # Real Amazon Scraper Implementation for DealFinder AI.

# # This module implements the RealAmazonScraperAgent class that uses BeautifulSoup
# # and requests to extract actual product data from Amazon.
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

# # logger = get_logger("Scrapers.Amazon")

# # class RealAmazonScraperAgent(Agent):
# #     """Agent for scraping Amazon product listings with actual web scraping"""
    
# #     def __init__(self):
# #         """Initialize the Amazon scraper agent."""
# #         super().__init__("AmazonScraperAgent")
# #         self.base_url = config.AMAZON_BASE_URL
        
# #         # Configure headers with default values
# #         self.headers = {
# #             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
# #             "Accept-Language": "en-US,en;q=0.5",
# #             "Accept-Encoding": "gzip, deflate, br",
# #             "Connection": "keep-alive",
# #             "Upgrade-Insecure-Requests": "1",
# #             "TE": "Trailers",
# #         }
    
# #     def process_message(self, message: MCPMessage) -> MCPMessage:
# #         """
# #         Process search request for Amazon.
        
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
# #         self.logger.info(f"Searching Amazon for: {search_params}")
        
# #         try:
# #             # Convert search parameters to Amazon search query
# #             query = self._build_search_query(search_params)
            
# #             # Perform the search
# #             products = self._scrape_search_results(query, search_params)
            
# #             return MCPMessage(
# #                 sender=self.name,
# #                 receiver=message.sender,
# #                 content={
# #                     "source": "Amazon",
# #                     "query": query,
# #                     "products": products
# #                 },
# #                 message_type="SEARCH_RESPONSE",
# #                 conversation_id=message.conversation_id
# #             )
        
# #         except Exception as e:
# #             self.logger.error(f"Error scraping Amazon: {str(e)}")
# #             return MCPMessage(
# #                 sender=self.name,
# #                 receiver=message.sender,
# #                 content={"error": f"Amazon scraping error: {str(e)}"},
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
    
# #     # def _is_relevant_product(self, product, keywords):
# #     #     title = product.get("title", "").lower()
# #     #     return all(kw.lower() in title for kw in keywords if kw)
# #     def _is_relevant_product(self, product, search_params):
# #         """
# #         Use Gemini to check if a product is relevant to the search query.
        
# #         Args:
# #             product: The product to check
# #             search_params: The original search parameters
            
# #         Returns:
# #             Boolean indicating if the product is relevant
# #         """
# #         # For quick filtering, do a basic keyword check first
# #         title = product.get("title", "").lower()
# #         keywords = search_params.get("keywords", [])
        
# #         # If no keywords provided, consider it relevant
# #         if not keywords:
# #             return True
        
# #         # Quick check for obvious matches to avoid unnecessary Gemini calls
# #         if isinstance(keywords, list):
# #             # If all keywords are in the title, it's definitely relevant
# #             if all(kw.lower() in title for kw in keywords if kw):
# #                 return True
                
# #             # For Sony XM series, special case
# #             if any(kw.lower() in ['sony', 'xm'] for kw in keywords if kw):
# #                 if 'sony' in title and any(x in title for x in ['wh-1000', 'wf-1000', 'xm']):
# #                     return True
# #         else:
# #             # If keywords is a string and it's in the title, it's relevant
# #             if keywords.lower() in title:
# #                 return True
        
# #         # For more complex cases, use Gemini
# #         try:
# #             # Create query string
# #             query_components = []
            
# #             if "product_type" in search_params:
# #                 query_components.append(search_params["product_type"])
            
# #             if "keywords" in search_params:
# #                 if isinstance(search_params["keywords"], list):
# #                     query_components.extend(search_params["keywords"])
# #                 else:
# #                     query_components.append(search_params["keywords"])
            
# #             if "brands" in search_params and search_params["brands"]:
# #                 brands = search_params["brands"]
# #                 if isinstance(brands, list):
# #                     query_components.append(" ".join(brands))
# #                 else:
# #                     query_components.append(brands)
            
# #             # Create a query string
# #             query = " ".join(query_components)
            
# #             # Use Gemini to check relevance
# #             from dealfinder.agents.gemini_agent import GeminiAgent
# #             gemini = GeminiAgent()
            
# #             prompt = f"""
# #             I need to determine if a product is relevant to a search query.
            
# #             Search query: "{query}"
# #             Product title: "{title}"
            
# #             Is this product relevant to the search query? Consider closely related products as relevant.
# #             For example, for a search query "sony xm 1000 series", products like "Sony WH-1000XM4" or "Sony WF-1000XM5" are relevant.
            
# #             Only answer with either "YES" or "NO".
# #             """
            
# #             response = gemini.run(prompt)
            
# #             # Check if the response indicates relevance
# #             is_relevant = "YES" in response.upper()
            
# #             # Log the result
# #             if is_relevant:
# #                 self.logger.info(f"Gemini determined product is relevant: {title}")
# #             else:
# #                 self.logger.info(f"Gemini determined product is NOT relevant: {title}")
            
# #             return is_relevant
            
# #         except Exception as e:
# #             self.logger.warning(f"Error checking relevance with Gemini: {str(e)}. Defaulting to including product.")
            
# #             # Fall back to basic filtering - require at least one keyword match
# #             if isinstance(keywords, list):
# #                 return any(kw.lower() in title for kw in keywords if kw)
# #             else:
# #                 return keywords.lower() in title

# #     def _scrape_search_results(self, query: str, search_params: Dict[str, Any], max_results: int = None) -> List[Dict[str, Any]]:
# #         """
# #         Scrape Amazon search results for the given query.
        
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
# #             "k": query,
# #             "ref": "nb_sb_noss",
# #         }
        
# #         # Add price range if specified
# #         if "price_range" in search_params and search_params["price_range"]:
# #             price_range = search_params["price_range"]
# #             if isinstance(price_range, list) and len(price_range) == 2:
# #                 min_price, max_price = price_range
# #                 if min_price:
# #                     params["low-price"] = min_price
# #                 if max_price:
# #                     params["high-price"] = max_price
        
# #         # Add sorting parameter if specified
# #         if "sorting_preference" in search_params:
# #             sort_pref = search_params["sorting_preference"]
# #             if sort_pref == "price_low_to_high":
# #                 params["s"] = "price-asc-rank"
# #             elif sort_pref == "price_high_to_low":
# #                 params["s"] = "price-desc-rank"
# #             elif sort_pref == "rating":
# #                 params["s"] = "review-rank"
# #             elif sort_pref == "newest":
# #                 params["s"] = "date-desc-rank"
        
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
# #         product_divs = soup.select('div[data-component-type="s-search-result"]')
# #         # Optional: always_use_gemini
# #         if search_params.get("always_use_gemini"):
# #             self.logger.info("Gemini used for product extraction")
# #             from dealfinder.agents.gemini_agent import GeminiAgent
# #             gemini = GeminiAgent()
# #             return [gemini.extract_product_details_from_html(str(div)) for div in product_divs[:max_results]]

# #         # for div in product_divs[:max_results]:
# #         #     product = self._extract_product_data(div)
# #         #     if not product:
# #         #         continue
# #         #     if not self._is_relevant_product(product, search_params.get("keywords", [])):
# #         #         continue
# #         #     asin = product.get("asin")
# #         #     if asin in seen_ids:
# #         #         continue
# #         #     seen_ids.add(asin)
# #         #     product["source"] = "Amazon"
# #         #     self.logger.info(f"Extracted product: {product['title']} at {product['price']} USD")
# #         #     products.append(product)
# #         #     if len(products) >= max_results:
# #         #         break
# #         for div in product_divs[:max_results * 2]:  # Get extra products for filtering
# #             product = self._extract_product_data(div)
# #             if not product:
# #                 continue
            
# #             # Use new Gemini-powered relevance check
# #             if not self._is_relevant_product(product, search_params):
# #                 continue
            
# #             asin = product.get("asin")
# #             if asin in seen_ids:
# #                 continue
            
# #             seen_ids.add(asin)
# #             product["source"] = "Amazon"
# #             self.logger.info(f"Adding relevant product: {product['title']} at {product['price']} USD")
# #             products.append(product)
            
# #             if len(products) >= max_results:
# #                 break

# #         time.sleep(random.uniform(
# #             config.SCRAPING_DELAY_MIN,
# #             config.SCRAPING_DELAY_MAX
# #         ))
# #         # Log the final list of products to be returned
# #         self.logger.info(f"Returning {len(products)} products after filtering")
# #         for product in products:
# #             self.logger.info(f"Returning product: {product.get('title', 'Unknown')} | Price: ${product.get('price', 0)}")

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
# #             # Extract ASIN (Amazon Standard Identification Number)
# #             asin = product_div.get('data-asin')
# #             if not asin:
# #                 return None
                
# #             # Check if the product is sponsored
# #             is_sponsored = bool(product_div.select_one('.s-sponsored-label-info-icon'))
                
# #             # Extract product title
# #             title_element = product_div.select_one('h2 a.a-link-normal span')
# #             title = title_element.text.strip() if title_element and title_element.text.strip() else f"Amazon Product {asin}"
                
# #             # Extract product URL
# #             url_element = product_div.select_one('h2 a.a-link-normal')
# #             url = f"https://www.amazon.com/dp/{asin}" if asin else "#"
                
# #             # Extract product image URL
# #             img_element = product_div.select_one('img.s-image')
# #             image_url = img_element['src'] if img_element and 'src' in img_element.attrs else ""
                
# #             # Extract product price
# #             price_element = product_div.select_one('.a-price .a-offscreen')
# #             price_text = price_element.text.strip() if price_element else ""
# #             price = self._parse_price(price_text)
                
# #             # Extract product rating
# #             rating_element = product_div.select_one('i.a-icon-star-small .a-icon-alt')
# #             rating = 0.0
# #             if rating_element:
# #                 rating_text = rating_element.text.strip()
# #                 rating_match = rating_text.split(' out of')[0]
# #                 try:
# #                     rating = float(rating_match)
# #                 except ValueError:
# #                     pass
                
# #             # Extract number of reviews
# #             reviews_element = product_div.select_one('span.a-size-base')
# #             reviews = 0
# #             if reviews_element:
# #                 reviews_text = reviews_element.text.strip()
# #                 reviews_text = reviews_text.replace(',', '')
# #                 reviews_match = ''.join(c for c in reviews_text if c.isdigit())
# #                 if reviews_match:
# #                     try:
# #                         reviews = int(reviews_match)
# #                     except ValueError:
# #                         pass
                
# #             # Check if the product has Prime shipping
# #             is_prime = bool(product_div.select_one('.s-prime'))
                
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
# #                 "is_prime": is_prime,
# #                 "asin": asin,
# #             }
            
# #             if not title or not url or not price:
# #                 self.logger.warning(f"Incomplete data for ASIN {asin}, falling back to Gemini extraction.")
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
# #             # Remove currency symbol and commas, then convert to float
# #             price_text = price_text.replace('$', '').replace(',', '')
# #             return float(price_text)
# #         except (ValueError, AttributeError):
# #             return 0.0

# #     def _extract_with_gemini(self, html_block: str) -> Optional[Dict[str, Any]]:
# #         try:
# #             from dealfinder.agents.gemini_agent import GeminiAgent
# #             gemini = GeminiAgent()
# #             data = gemini.extract_product_details_from_html(html_block)
# #             if "asin" not in data or not data["asin"]:
# #                 return None
# #             data.setdefault("currency", "USD")
# #             data.setdefault("source", "Amazon")
# #             self.logger.info("Gemini used for product extraction")
# #             self.logger.info(f"Extracted product: {data.get('title', '')} at {data.get('price', 0)} USD")
# #             return data
# #         except Exception as e:
# #             self.logger.error(f"Gemini fallback failed: {str(e)}")
# #             return None

# """
# Real Amazon Scraper Implementation for DealFinder AI.

# This module implements the RealAmazonScraperAgent class that uses BeautifulSoup
# and requests to extract actual product data from Amazon.
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

# logger = get_logger("Scrapers.Amazon")

# class RealAmazonScraperAgent(Agent):
#     """Agent for scraping Amazon product listings with actual web scraping"""
    
#     def __init__(self):
#         """Initialize the Amazon scraper agent."""
#         super().__init__("AmazonScraperAgent")
#         self.base_url = config.AMAZON_BASE_URL
        
#         # Configure headers with default values
#         self.headers = {
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#             "Accept-Language": "en-US,en;q=0.5",
#             "Accept-Encoding": "gzip, deflate, br",
#             "Connection": "keep-alive",
#             "Upgrade-Insecure-Requests": "1",
#             "TE": "Trailers",
#         }
    
#     def process_message(self, message: MCPMessage) -> MCPMessage:
#         """
#         Process search request for Amazon.
        
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
#         self.logger.info(f"Searching Amazon for: {search_params}")
        
#         try:
#             # Convert search parameters to Amazon search query
#             query = self._build_search_query(search_params)
            
#             # Perform the search
#             products = self._scrape_search_results(query, search_params)
            
#             return MCPMessage(
#                 sender=self.name,
#                 receiver=message.sender,
#                 content={
#                     "source": "Amazon",
#                     "query": query,
#                     "products": products
#                 },
#                 message_type="SEARCH_RESPONSE",
#                 conversation_id=message.conversation_id
#             )
        
#         except Exception as e:
#             self.logger.error(f"Error scraping Amazon: {str(e)}")
#             return MCPMessage(
#                 sender=self.name,
#                 receiver=message.sender,
#                 content={"error": f"Amazon scraping error: {str(e)}"},
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
#         Scrape Amazon search results for the given query.
        
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
#             "k": query,
#             "ref": "nb_sb_noss",
#         }
        
#         # Add price range if specified
#         if "price_range" in search_params and search_params["price_range"]:
#             price_range = search_params["price_range"]
#             if isinstance(price_range, list) and len(price_range) == 2:
#                 min_price, max_price = price_range
#                 if min_price:
#                     params["low-price"] = min_price
#                 if max_price:
#                     params["high-price"] = max_price
        
#         # Add sorting parameter if specified
#         if "sorting_preference" in search_params:
#             sort_pref = search_params["sorting_preference"]
#             if sort_pref == "price_low_to_high":
#                 params["s"] = "price-asc-rank"
#             elif sort_pref == "price_high_to_low":
#                 params["s"] = "price-desc-rank"
#             elif sort_pref == "rating":
#                 params["s"] = "review-rank"
#             elif sort_pref == "newest":
#                 params["s"] = "date-desc-rank"
        
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
#         product_divs = soup.select('div[data-component-type="s-search-result"]')
        
#         # Optional: Gemini-based extraction if specified
#         if search_params.get("always_use_gemini"):
#             self.logger.info("Gemini used for product extraction")
#             from dealfinder.agents.gemini_agent import GeminiAgent
#             gemini = GeminiAgent()
#             return [gemini.extract_product_details_from_html(str(div)) for div in product_divs[:max_results]]

#         # Process products without relevance filtering
#         for div in product_divs[:max_results * 2]:  
#             product = self._extract_product_data(div)
#             if not product:
#                 continue
            
#             # Only check for duplicate ASINs
#             asin = product.get("asin")
#             if asin in seen_ids:
#                 continue
            
#             seen_ids.add(asin)
#             product["source"] = "Amazon"
#             self.logger.info(f"Adding product: {product['title']} at {product['price']} USD")
#             products.append(product)
            
#             if len(products) >= max_results:
#                 break

#         time.sleep(random.uniform(
#             config.SCRAPING_DELAY_MIN,
#             config.SCRAPING_DELAY_MAX
#         ))
        
#         # Log the final list of products to be returned
#         self.logger.info(f"Returning {len(products)} products")
        
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
#             # Extract ASIN (Amazon Standard Identification Number)
#             asin = product_div.get('data-asin')
#             if not asin:
#                 return None
                
#             # Check if the product is sponsored
#             is_sponsored = bool(product_div.select_one('.s-sponsored-label-info-icon'))
                
#             # Extract product title
#             title_element = product_div.select_one('h2 a.a-link-normal span')
#             title = title_element.text.strip() if title_element and title_element.text.strip() else f"Amazon Product {asin}"
                
#             # Extract product URL
#             url_element = product_div.select_one('h2 a.a-link-normal')
#             url = f"https://www.amazon.com/dp/{asin}" if asin else "#"
                
#             # Extract product image URL
#             img_element = product_div.select_one('img.s-image')
#             image_url = img_element['src'] if img_element and 'src' in img_element.attrs else ""
                
#             # Extract product price
#             price_element = product_div.select_one('.a-price .a-offscreen')
#             price_text = price_element.text.strip() if price_element else ""
#             price = self._parse_price(price_text)
                
#             # Extract product rating
#             rating_element = product_div.select_one('i.a-icon-star-small .a-icon-alt')
#             rating = 0.0
#             if rating_element:
#                 rating_text = rating_element.text.strip()
#                 rating_match = rating_text.split(' out of')[0]
#                 try:
#                     rating = float(rating_match)
#                 except ValueError:
#                     pass
                
#             # Extract number of reviews
#             reviews_element = product_div.select_one('span.a-size-base')
#             reviews = 0
#             if reviews_element:
#                 reviews_text = reviews_element.text.strip()
#                 reviews_text = reviews_text.replace(',', '')
#                 reviews_match = ''.join(c for c in reviews_text if c.isdigit())
#                 if reviews_match:
#                     try:
#                         reviews = int(reviews_match)
#                     except ValueError:
#                         pass
                
#             # Check if the product has Prime shipping
#             is_prime = bool(product_div.select_one('.s-prime'))
            
#             # Extract any visible product features (new)
#             features_element = product_div.select_one('.a-section.a-spacing-small')
#             description = ""
#             if features_element:
#                 description = features_element.text.strip()
                
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
#                 "is_prime": is_prime,
#                 "asin": asin,
#                 "description": description
#             }
            
#             if not title or not url or not price:
#                 self.logger.warning(f"Incomplete data for ASIN {asin}, falling back to Gemini extraction.")
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
#             # Remove currency symbol and commas, then convert to float
#             price_text = price_text.replace('$', '').replace(',', '')
#             return float(price_text)
#         except (ValueError, AttributeError):
#             return 0.0

#     def _extract_with_gemini(self, html_block: str) -> Optional[Dict[str, Any]]:
#         try:
#             from dealfinder.agents.gemini_agent import GeminiAgent
#             gemini = GeminiAgent()
#             data = gemini.extract_product_details_from_html(html_block)
#             if "asin" not in data or not data["asin"]:
#                 return None
#             data.setdefault("currency", "USD")
#             data.setdefault("source", "Amazon")
#             self.logger.info("Gemini used for product extraction")
#             self.logger.info(f"Extracted product: {data.get('title', '')} at {data.get('price', 0)} USD")
#             return data
#         except Exception as e:
#             self.logger.error(f"Gemini fallback failed: {str(e)}")
#             return None
"""
Real Amazon Scraper Implementation for DealFinder AI with Gemini optimization.

This module implements the RealAmazonScraperAgent class that uses BeautifulSoup,
requests, and Gemini AI to extract and optimize product data from Amazon.
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

logger = get_logger("Scrapers.Amazon")

class RealAmazonScraperAgent(Agent):
    """Agent for scraping Amazon product listings with Gemini-enhanced search optimization"""
    
    def __init__(self):
        """Initialize the Amazon scraper agent."""
        super().__init__("AmazonScraperAgent")
        self.base_url = config.AMAZON_BASE_URL
        self.gemini_agent = GeminiAgent()
        
        # Configure headers with default values
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "TE": "Trailers",
        }
    
    def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Process search request for Amazon.
        
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
        self.logger.info(f"Searching Amazon for: {search_params}")
        
        try:
            # Use Gemini to optimize the search query for Amazon's search engine
            optimized_params = self._optimize_search_params(search_params)
            self.logger.info(f"Optimized search parameters: {optimized_params}")
            
            # Convert optimized parameters to Amazon search query
            query = self._build_search_query(optimized_params)
            self.logger.info(f"Built Amazon query: {query}")
            
            # Perform the search
            products = self._scrape_search_results(query, optimized_params)
            
            # Apply Gemini-based relevance filtering
            if not search_params.get("skip_relevance_filter", False):
                products = self._apply_relevance_filter(products, search_params)
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={
                    "source": "Amazon",
                    "query": query,
                    "products": products
                },
                message_type="SEARCH_RESPONSE",
                conversation_id=message.conversation_id
            )
        
        except Exception as e:
            self.logger.error(f"Error scraping Amazon: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Amazon scraping error: {str(e)}"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
    
    def _optimize_search_params(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Gemini to optimize search parameters for Amazon's search engine.
        
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
            Optimize this search query for Amazon's search engine:
            
            "{original_query}"
            
            For Amazon searches, please:
            1. Focus on product-specific model numbers and identifiers if present
            2. Include key brand names (Amazon's A9 algorithm prioritizes brand matches)
            3. Remove generic words that may dilute results
            4. Add Amazon-specific terms that might improve results (like "Amazon's Choice" if looking for quality products)
            5. Optimize for Amazon's search algorithm which prioritizes exact matches and recent sales volume
            
            Return a JSON object with:
            - optimized_keywords: List of 3-5 optimized search terms (most important first)
            - amazon_category: Any Amazon department/category suggestion (Electronics, Books, etc.)
            - must_include_terms: Terms that MUST be in results
            - exclude_terms: Terms that should NOT be in results
            - amazon_search_filters: Any Amazon-specific filters to apply (Prime eligible, etc.)
            
            Format as JSON only with no explanation.
            """
            
            # Call Gemini
            message = MCPMessage(
                sender="AmazonScraperAgent",
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
            
            # Add Amazon category if provided
            if "amazon_category" in optimization_data and optimization_data["amazon_category"]:
                optimized_params["category"] = optimization_data["amazon_category"]
            
            # Add must-include terms
            if "must_include_terms" in optimization_data and optimization_data["must_include_terms"]:
                optimized_params["must_include_terms"] = optimization_data["must_include_terms"]
            
            # Add exclude terms
            if "exclude_terms" in optimization_data and optimization_data["exclude_terms"]:
                optimized_params["exclude_terms"] = optimization_data["exclude_terms"]
            
            # Add Amazon-specific filters
            if "amazon_search_filters" in optimization_data and optimization_data["amazon_search_filters"]:
                optimized_params["amazon_filters"] = optimization_data["amazon_search_filters"]
            
            return optimized_params
            
        except Exception as e:
            self.logger.error(f"Error optimizing search parameters: {str(e)}")
            # Fall back to original parameters
            return search_params
    
    def _build_search_query(self, search_params: Dict[str, Any]) -> str:
        """
        Build optimized search query string from parameters for Amazon's search engine.
        
        Args:
            search_params: Optimized search parameters
            
        Returns:
            A search query string
        """
        components = []
        
        # Build Amazon-specific query, prioritizing brand and model numbers
        # Brand is important for Amazon searches
        if "brands" in search_params and search_params["brands"]:
            brands = search_params["brands"]
            if isinstance(brands, list):
                # For Amazon, include brands as a high-priority component
                components.extend(brands)
            else:
                components.append(brands)
        
        # Product type is important for Amazon's categorization
        if "product_type" in search_params and search_params["product_type"]:
            components.append(search_params["product_type"])
        
        # Add optimized keywords with priority
        if "keywords" in search_params:
            if isinstance(search_params["keywords"], list):
                # For Amazon, use all optimized keywords as they help with targeting
                components.extend(search_params["keywords"])
            else:
                components.append(search_params["keywords"])
        
        # Add Amazon-specific category/department if specified
        if "category" in search_params and search_params["category"]:
            category = search_params["category"]
            # For Amazon, we'll handle categories via search parameters rather than in the query string
            # But we can add category-specific terms to improve targeting
            if isinstance(category, str):
                # Add as a component only if it's not already in the components
                if not any(category.lower() in c.lower() for c in components):
                    components.append(category)
            elif isinstance(category, list) and category:
                # Add the first category if it's a list
                if not any(category[0].lower() in c.lower() for c in components):
                    components.append(category[0])
        
        # Add must_include_terms if specified
        if "must_include_terms" in search_params and search_params["must_include_terms"]:
            terms = search_params["must_include_terms"]
            if isinstance(terms, list):
                components.extend(terms)
            else:
                components.append(terms)
        
        # Add features with more selective inclusion
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
        
        # Join with spaces for the final query
        query = " ".join(components)
        
        # If query is too long, prioritize the most important components
        if len(query.split()) > 8:
            # For Amazon, prioritize brands and specific model numbers
            short_components = []
            
            # Brands are very important for Amazon
            if "brands" in search_params and search_params["brands"]:
                if isinstance(search_params["brands"], list) and search_params["brands"]:
                    short_components.append(search_params["brands"][0])  # Use first brand
                else:
                    short_components.append(search_params["brands"])
            
            # Product type is important for targeting the right category
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
        
        self.logger.info(f"Built optimized Amazon search query: {query}")
        return query

    def _scrape_search_results(self, query: str, search_params: Dict[str, Any], max_results: int = None) -> List[Dict[str, Any]]:
        """
        Scrape Amazon search results for the given query with enhanced parameters.
        
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
        
        # Set up Amazon-specific request parameters
        params = {
            "k": query,           # Main search query
            "ref": "nb_sb_noss",  # Standard Amazon reference
            "crid": int(time.time()),  # Add a cache-busting reference ID
        }
        
        # Add Amazon category if specified (via the search-alias parameter)
        if "category" in search_params and search_params["category"]:
            category = search_params["category"]
            # Convert category name to Amazon's search-alias format
            category_map = {
                "electronics": "electronics",
                "computers": "computers",
                "home": "garden",
                "kitchen": "kitchen",
                "books": "stripbooks",
                "toys": "toys-and-games",
                "clothing": "fashion",
                "beauty": "beauty",
                "sports": "sporting",
                "tools": "tools",
                "grocery": "grocery",
                "health": "hpc",
                "music": "popular",
            }
            
            # Try to map the category or use as-is if not in our map
            if isinstance(category, str):
                category_lower = category.lower()
                search_alias = None
                
                # Look for partial matches in the category map
                for key, value in category_map.items():
                    if key in category_lower:
                        search_alias = value
                        break
                
                if search_alias:
                    params["i"] = "aps"  # This is required for search-alias to work
                    params["search-alias"] = search_alias
            elif isinstance(category, list) and category:
                # Use the first category if it's a list
                category_lower = category[0].lower()
                
                for key, value in category_map.items():
                    if key in category_lower:
                        params["i"] = "aps"
                        params["search-alias"] = value
                        break
        
        # Add price range if specified
        if "price_range" in search_params and search_params["price_range"]:
            price_range = search_params["price_range"]
            if isinstance(price_range, list) and len(price_range) == 2:
                min_price, max_price = price_range
                if min_price is not None:
                    params["low-price"] = min_price
                if max_price is not None:
                    params["high-price"] = max_price
        
        # Add sorting parameter if specified
        if "sorting_preference" in search_params:
            sort_pref = search_params["sorting_preference"]
            if sort_pref == "price_low_to_high":
                params["s"] = "price-asc-rank"
            elif sort_pref == "price_high_to_low":
                params["s"] = "price-desc-rank"
            elif sort_pref == "rating":
                params["s"] = "review-rank"
            elif sort_pref == "newest":
                params["s"] = "date-desc-rank"
                
        # Add Amazon-specific filters
        if "amazon_filters" in search_params:
            amazon_filters = search_params["amazon_filters"]
            if isinstance(amazon_filters, dict):
                # Apply common Amazon filters
                if amazon_filters.get("prime_eligible", False):
                    params["rh"] = "p_85:2470955011"  # Prime eligible
                
                if amazon_filters.get("free_shipping", False):
                    if "rh" in params:
                        params["rh"] += ",p_76:2661625011"  # Free shipping
                    else:
                        params["rh"] = "p_76:2661625011"
                
                if amazon_filters.get("new_condition", False):
                    if "rh" in params:
                        params["rh"] += ",p_n_condition-type:6461716011"  # New condition
                    else:
                        params["rh"] = "p_n_condition-type:6461716011"
                
                if amazon_filters.get("amazon_choice", False):
                    # Unfortunately, Amazon's Choice can't be directly filtered via URL parameters
                    # We'll handle this in post-processing
                    pass
        
        # Use a random user agent for each request
        current_headers = self.headers.copy()
        current_headers["User-Agent"] = random.choice(config.USER_AGENTS)

        # Make the request with retry logic
        for attempt in range(3):
            try:
                self.logger.info(f"Making Amazon search request with params: {params}")
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=current_headers,
                    timeout=config.SCRAPING_TIMEOUT
                )
                
                if response.status_code == 200:
                    break
                else:
                    self.logger.warning(f"Amazon search request failed with status {response.status_code}, retrying")
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
        product_divs = soup.select('div[data-component-type="s-search-result"]')
        self.logger.info(f"Found {len(product_divs)} product divs in search results")
        
        # Gemini-based extraction for all products if specified
        if search_params.get("always_use_gemini"):
            self.logger.info("Using Gemini for all product extraction")
            extracted_products = []
            
            for div in product_divs[:scrape_count]:
                product = self.gemini_agent.extract_product_details_from_html(str(div))
                if product and isinstance(product, dict):
                    product["source"] = "Amazon"
                    extracted_products.append(product)
                    
            # Return the requested number of products
            return extracted_products[:max_results]

        # Process products with standard extraction
        products = []
        seen_ids = set()
        
        for div in product_divs[:scrape_count]:
            product = self._extract_product_data(div)
            if not product:
                continue
            
            # Skip duplicates
            asin = product.get("asin")
            if asin in seen_ids:
                continue
            
            seen_ids.add(asin)
            product["source"] = "Amazon"
            self.logger.info(f"Extracted product: {product['title']} at {product['price']} USD")
            products.append(product)
            
            if len(products) >= scrape_count:
                break

        # Add a short delay to avoid rate limiting
        time.sleep(random.uniform(
            config.SCRAPING_DELAY_MIN,
            config.SCRAPING_DELAY_MAX
        ))
        
        self.logger.info(f"Extracted {len(products)} products from Amazon")
        
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
                
                # Calculate a relevance score for Amazon-specific ranking
                relevance_score = 0
                
                # Keywords in title are very important
                keyword_matches = sum(1 for kw in keywords if kw in title)
                relevance_score += keyword_matches * 10
                
                # Keywords in description are less important
                description_matches = sum(1 for kw in keywords if kw in description)
                relevance_score += description_matches * 2
                
                # Amazon-specific bonuses:
                
                # Prefer items with Prime shipping
                if product.get("is_prime", False):
                    relevance_score += 5
                
                # Prefer items with better ratings
                rating = product.get("rating", 0)
                if rating > 4.5:
                    relevance_score += 8
                elif rating > 4.0:
                    relevance_score += 5
                elif rating > 3.0:
                    relevance_score += 2
                
                # Prefer items with more reviews (Amazon's algorithm also does this)
                reviews = product.get("reviews", 0)
                if reviews > 1000:
                    relevance_score += 6
                elif reviews > 500:
                    relevance_score += 4
                elif reviews > 100:
                    relevance_score += 2
                
                # Prefer Amazon's Choice items
                if product.get("is_amazon_choice", False):
                    relevance_score += 7
                
                # Prefer Best Seller items
                if product.get("is_best_seller", False):
                    relevance_score += 7
                
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
            # Extract ASIN (Amazon Standard Identification Number)
            asin = product_div.get('data-asin')
            if not asin:
                return None
                
            # Check if the product is sponsored with multiple selectors
            is_sponsored = bool(product_div.select_one('.s-sponsored-label-info-icon'))
            if not is_sponsored:
                is_sponsored = bool(product_div.select_one('.s-sponsored-label'))
            if not is_sponsored:
                # Look for "Sponsored" text
                sponsored_text = product_div.text.lower()
                is_sponsored = 'sponsored' in sponsored_text
                
            # Check if the product is "Amazon's Choice"
            is_amazon_choice = bool(product_div.select_one('.a-badge-label:contains("Amazon\'s Choice")'))
            if not is_amazon_choice:
                choice_text = product_div.text.lower()
                is_amazon_choice = "amazon's choice" in choice_text or "amazons choice" in choice_text
                
            # Check if the product is a "Best Seller"
            is_best_seller = bool(product_div.select_one('.a-badge-label:contains("Best Seller")'))
            if not is_best_seller:
                seller_text = product_div.text.lower()
                is_best_seller = "best seller" in seller_text or "bestseller" in seller_text
                
            # Extract product title with multiple selectors
            title_element = product_div.select_one('h2 a.a-link-normal span')
            if not title_element:
                title_element = product_div.select_one('h2 span.a-text-normal')
            if not title_element:
                title_element = product_div.select_one('.a-size-medium.a-color-base.a-text-normal')
            if not title_element:
                # Find any heading element
                heading_elements = product_div.select('h2, h3, h4')
                for heading in heading_elements:
                    if heading.text.strip():
                        title_element = heading
                        break
                
            title = title_element.text.strip() if title_element and title_element.text.strip() else f"Amazon Product {asin}"
                
            # Extract product URL with multiple strategies
            url_element = product_div.select_one('h2 a.a-link-normal')
            if not url_element:
                url_element = product_div.select_one('a.a-link-normal[href*="/dp/"]')
            if not url_element:
                # Look for any link containing the ASIN
                for link in product_div.select('a'):
                    href = link.get('href', '')
                    if f"/dp/{asin}" in href or f"/gp/product/{asin}" in href:
                        url_element = link
                        break
            
            # Form complete URL, either from element or from ASIN
            if url_element and 'href' in url_element.attrs:
                url = url_element['href']
                # Check if it's a relative URL
                if url.startswith('/'):
                    url = f"https://www.amazon.com{url}"
            else:
                url = f"https://www.amazon.com/dp/{asin}"
                
            # Extract product image URL with better handling
            img_element = product_div.select_one('img.s-image')
            if not img_element:
                img_element = product_div.select_one('.a-section.aok-relative img')
            if not img_element:
                # Try any image in the product div
                img_elements = product_div.select('img')
                for img in img_elements:
                    if 'src' in img.attrs and img['src'] and 'sprite' not in img['src'].lower():
                        img_element = img
                        break
                        
            image_url = img_element['src'] if img_element and 'src' in img_element.attrs else ""
            
            # Extract product price with multiple selectors
            price_element = product_div.select_one('.a-price .a-offscreen')
            if not price_element:
                price_element = product_div.select_one('.a-color-base .a-price .a-offscreen')
            if not price_element:
                price_element = product_div.select_one('.a-price')
                
            # Parse price text
            price_text = price_element.text.strip() if price_element else ""
            price = self._parse_price(price_text)
            
            # Extract "was price" / original price if available
            was_price_element = product_div.select_one('.a-price.a-text-price .a-offscreen')
            was_price = None
            if was_price_element:
                was_price_text = was_price_element.text.strip()
                was_price = self._parse_price(was_price_text)
                
            # Extract product rating with enhanced handling
            rating_element = product_div.select_one('i.a-icon-star-small .a-icon-alt')
            if not rating_element:
                rating_element = product_div.select_one('.a-icon-star .a-icon-alt')
            if not rating_element:
                rating_element = product_div.select_one('.a-star-medium-4-5 .a-icon-alt')
                
            rating = 0.0
            if rating_element:
                rating_text = rating_element.text.strip()
                rating_match = re.search(r'(\d+(\.\d+)?)', rating_text)
                if rating_match:
                    try:
                        rating = float(rating_match.group(1))
                    except ValueError:
                        pass
                elif "out of" in rating_text.lower():
                    # Handle "X out of 5 stars" format
                    rating_parts = rating_text.lower().split("out of")
                    if len(rating_parts) == 2:
                        try:
                            rating = float(rating_parts[0].strip())
                        except ValueError:
                            pass
            
            # Try to extract rating from star class name if text extraction fails
            if rating == 0.0:
                star_element = product_div.select_one('i[class*="a-star-"]')
                if star_element:
                    class_name = star_element.get('class', '')
                    if isinstance(class_name, list):
                        class_name = ' '.join(class_name)
                    
                    # Look for patterns like "a-star-4" or "a-star-4-5"
                    star_match = re.search(r'a-star-(\d+)(?:-(\d+))?', class_name)
                    if star_match:
                        whole_stars = int(star_match.group(1))
                        half_star = 0
                        if star_match.group(2):
                            half_star = int(star_match.group(2)) / 10
                        rating = whole_stars + half_star
                
            # Extract number of reviews with enhanced handling
            reviews_element = product_div.select_one('span.a-size-base')
            if not reviews_element:
                reviews_element = product_div.select_one('.a-link-normal .a-size-base')
            if not reviews_element:
                # Look for any element containing reviews info
                for element in product_div.select('.a-row span'):
                    if element.text and any(x in element.text.lower() for x in ['review', 'rating']):
                        reviews_element = element
                        break
                        
            reviews = 0
            if reviews_element:
                reviews_text = reviews_element.text.strip()
                reviews_text = reviews_text.replace(',', '')
                reviews_match = re.search(r'(\d+)', reviews_text)
                if reviews_match:
                    try:
                        reviews = int(reviews_match.group(1))
                    except ValueError:
                        pass
                
            # Check if the product has Prime shipping with multiple selectors
            is_prime = bool(product_div.select_one('.s-prime'))
            if not is_prime:
                is_prime = bool(product_div.select_one('.a-icon-prime'))
            if not is_prime:
                prime_text = product_div.text.lower()
                is_prime = "prime" in prime_text and not any(x in prime_text for x in ["prime video", "prime music"])
            
            # Extract delivery information
            delivery_element = product_div.select_one('.a-row.a-size-base .a-color-secondary')
            delivery_info = ""
            if delivery_element:
                delivery_info = delivery_element.text.strip()
                # Clean up delivery text
                delivery_info = re.sub(r'\s+', ' ', delivery_info)
            
            # Extract any visible product features/description
            features_element = product_div.select_one('.a-section.a-spacing-small')
            description = ""
            if features_element:
                description = features_element.text.strip()
                # Remove any duplicate whitespace
                description = re.sub(r'\s+', ' ', description)
            
            # Check for stock information
            stock_element = product_div.select_one('.a-spacing-top-mini .a-color-price')
            out_of_stock = False
            if stock_element and "out of stock" in stock_element.text.lower():
                out_of_stock = True
            
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
                "is_prime": is_prime,
                "is_amazon_choice": is_amazon_choice,
                "is_best_seller": is_best_seller,
                "asin": asin,
                "description": description,
                "delivery_info": delivery_info,
                "out_of_stock": out_of_stock
            }
            
            # Use Gemini fallback if essential fields are missing or incomplete
            if not title or title == f"Amazon Product {asin}" or not url or price == 0.0:
                self.logger.warning(f"Incomplete data for ASIN {asin}, falling back to Gemini extraction.")
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
        Parse price string to float with enhanced detection.
        
        Args:
            price_text: Price text to parse
            
        Returns:
            Parsed price as float
        """
        try:
            # Handle empty or invalid inputs
            if not price_text:
                return 0.0
                
            # Handle Amazon's various price formats
            
            # Handle range format, take the lower price: "$10.99 - $24.99"
            if " - " in price_text:
                price_text = price_text.split(" - ")[0]
                
            # Look for currency symbol with regex
            price_match = re.search(r'\$\s*(\d+(?:,\d+)*(?:\.\d+)?)', price_text)
            if price_match:
                return float(price_match.group(1).replace(',', ''))
                
            # Try another pattern without currency symbol
            price_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', price_text.replace('$', ''))
            if price_match:
                return float(price_match.group(1).replace(',', ''))
                
            # If no price found
            return 0.0
            
        except (ValueError, AttributeError) as e:
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
            Extract detailed product information from this Amazon listing HTML:
            
            ```html
            {html_block}
            ```
            
            Extract:
            - title: Full product title
            - price: Numeric price value only (no currency symbol)
            - was_price: Original price before discount (if present)
            - currency: Currency code (e.g., USD)
            - url: Product URL
            - image_url: Main product image URL
            - rating: Star rating (0-5)
            - reviews: Number of reviews
            - asin: Amazon ASIN
            - is_prime: Boolean for Prime eligible
            - is_sponsored: Boolean for sponsored listing
            - is_amazon_choice: Boolean for Amazon's Choice
            - is_best_seller: Boolean for Best Seller
            - description: Any additional description text
            - delivery_info: Delivery/shipping information
            - out_of_stock: Boolean for out of stock status
            
            Return a clean JSON object with these fields. Use null for missing values.
            """
            
            # Call Gemini
            message = MCPMessage(
                sender="AmazonScraperAgent",
                receiver="GeminiAgent",
                content=prompt,
                message_type="REQUEST"
            )
            
            response = self.gemini_agent.process_message(message)
            
            # Parse the response
            data = None
            if isinstance(response.content, str):
                # Try to extract JSON from the response
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response.content)
                if json_match:
                    data = json.loads(json_match.group(1))
                else:
                    # Try direct parsing
                    try:
                        data = json.loads(response.content)
                    except json.JSONDecodeError:
                        pass
            else:
                data = response.content
                
            # Validate the extracted data
            if not isinstance(data, dict) or not data:
                self.logger.warning("Gemini extraction returned invalid data")
                return None
                
            # Check if we have the minimal required fields
            if not data.get("asin"):
                self.logger.warning("Gemini extraction missing ASIN field")
                data["asin"] = re.search(r'data-asin="([^"]+)"', html_block)
                if not data["asin"]:
                    return None
                    
            # Set default values
            data.setdefault("currency", "USD")
            data.setdefault("source", "Amazon")
            
            # Convert price to float if it's not already
            if "price" in data and data["price"] is not None:
                try:
                    data["price"] = float(data["price"])
                except (ValueError, TypeError):
                    data["price"] = 0.0
            
            # Convert was_price to float if present
            if "was_price" in data and data["was_price"] is not None:
                try:
                    data["was_price"] = float(data["was_price"])
                except (ValueError, TypeError):
                    data["was_price"] = None
            
            # Normalize rating to float
            if "rating" in data and data["rating"] is not None:
                try:
                    data["rating"] = float(data["rating"])
                except (ValueError, TypeError):
                    data["rating"] = 0.0
            
            # Normalize reviews to int
            if "reviews" in data and data["reviews"] is not None:
                try:
                    data["reviews"] = int(data["reviews"])
                except (ValueError, TypeError):
                    data["reviews"] = 0
            
            # Ensure booleans are actually booleans
            for bool_field in ["is_prime", "is_sponsored", "is_amazon_choice", "is_best_seller", "out_of_stock"]:
                if bool_field in data:
                    data[bool_field] = bool(data[bool_field])
            
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
                    
            if "brands" in search_params and search_params["brands"]:
                brands = search_params["brands"]
                if isinstance(brands, list):
                    query_components.extend(brands)
                else:
                    query_components.append(brands)
                    
            original_query = " ".join(query_components)
            
            # Create product summary
            product_summary = {
                "title": product.get("title", ""),
                "price": product.get("price", 0),
                "description": product.get("description", ""),
                "rating": product.get("rating", 0),
                "is_prime": product.get("is_prime", False),
                "is_amazon_choice": product.get("is_amazon_choice", False)
            }
            
            # Create prompt for Gemini
            prompt = f"""
            Evaluate if this Amazon product is relevant to the search query.
            
            Search query: "{original_query}"
            
            Product:
            {json.dumps(product_summary, indent=2)}
            
            Consider these factors:
            1. Does the product title match key terms in the query?
            2. For electronics, are model numbers matching or compatible?
            3. Is the product from a brand mentioned in the query?
            4. Does the product have the features implied by the query?

            Return a JSON with:
            - relevance_score: 0-100 (higher means more relevant)
            - reasoning: Brief explanation of the score (1-2 sentences)
            
            Format as JSON only.
            """
            
            # Call Gemini
            message = MCPMessage(
                sender="AmazonScraperAgent",
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
            Create the optimal search query for Amazon's search engine based on these parameters:
            
            {' | '.join(components)}
            
            For Amazon's search engine:
            1. Include exact model numbers or part identifiers if available
            2. Include the most important brand names
            3. Keep the query concise (3-7 terms maximum)
            4. Focus on unique, specific terms rather than generic ones
            5. Consider Amazon's search algorithm which prioritizes exact matches
            
            Return ONLY the search query text with no explanation or additional text.
            """
            
            # Call Gemini
            message = MCPMessage(
                sender="AmazonScraperAgent",
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