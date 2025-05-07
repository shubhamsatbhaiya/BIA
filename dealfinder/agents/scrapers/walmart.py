"""
Real Walmart Scraper Implementation for DealFinder AI.

This module implements the RealWalmartScraperAgent class that uses BeautifulSoup
and requests to extract actual product data from Walmart.
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

logger = get_logger("Scrapers.Walmart")

class RealWalmartScraperAgent(Agent):
    """Agent for scraping Walmart product listings with actual web scraping"""
    
    def __init__(self):
        """Initialize the Walmart scraper agent."""
        super().__init__("WalmartScraperAgent")
        self.base_url = config.WALMART_BASE_URL
        
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
            # Convert search parameters to Walmart search query
            query = self._build_search_query(search_params)
            
            # Perform the search
            products = self._scrape_search_results(query, search_params)
            
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
    
    def _build_search_query(self, search_params: Dict[str, Any]) -> str:
        """
        Build search query string from parameters.
        
        Args:
            search_params: Search parameters to use for the query
            
        Returns:
            A search query string
        """
        components = []
        
        if "product_type" in search_params:
            components.append(search_params["product_type"])
        
        if "keywords" in search_params:
            if isinstance(search_params["keywords"], list):
                components.extend(search_params["keywords"])
            else:
                components.append(search_params["keywords"])
        
        if "brands" in search_params and search_params["brands"]:
            brands = search_params["brands"]
            if isinstance(brands, list):
                components.append(" ".join(brands))
            else:
                components.append(brands)
        
        if "features" in search_params and search_params["features"]:
            features = search_params["features"]
            if isinstance(features, list):
                components.extend(features)
            else:
                components.append(features)
        
        return " ".join(components)
    
    def _scrape_search_results(self, query: str, search_params: Dict[str, Any], max_results: int = None) -> List[Dict[str, Any]]:
        """
        Scrape Walmart search results for the given query.
        
        Args:
            query: The search query string
            search_params: Additional search parameters
            max_results: Maximum number of results to return (default: from config)
            
        Returns:
            A list of product dictionaries
        """
        # Use configured max_results if not specified
        if max_results is None:
            max_results = config.MAX_PRODUCTS_PER_SOURCE
        
        # Construct the search URL
        params = {
            "q": query,
        }
        
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
        
        # Use a random user agent for each request
        current_headers = self.headers.copy()
        current_headers["User-Agent"] = random.choice(config.USER_AGENTS)
        
        try:
            # Send the request to Walmart
            response = requests.get(
                self.base_url,
                params=params,
                headers=current_headers,
                timeout=config.SCRAPING_TIMEOUT
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                self.logger.error(f"Failed to retrieve Walmart search results: {response.status_code}")
                return []
            
            # Parse the HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract products from the JSON data first (more reliable)
            products = self._extract_from_json_data(soup)
            
            # If JSON extraction failed, try HTML extraction
            if not products:
                products = self._extract_from_html(soup, max_results)
            
            # Add source information
            for product in products:
                product["source"] = "Walmart"
            
            # Add a small delay to avoid rate limiting
            time.sleep(random.uniform(
                config.SCRAPING_DELAY_MIN,
                config.SCRAPING_DELAY_MAX
            ))
            
            return products[:max_results]  # Limit to max_results
            
        except Exception as e:
            self.logger.error(f"Error during Walmart search scraping: {str(e)}")
            return []
    
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
            
            return products
            
        except Exception as e:
            self.logger.error(f"Error extracting from JSON data: {str(e)}")
            return []
    
    def _parse_json_product(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse product data from a JSON item.
        
        Args:
            item: JSON object containing product data
            
        Returns:
            A dictionary of product data, or None if parsing fails
        """
        try:
            # Extract basic product info
            product_id = item.get('id', item.get('productId', ''))
            title = item.get('title', item.get('name', ''))
            
            # Extract price information
            price = 0.0
            price_info = item.get('price', item.get('priceInfo', {}))
            if isinstance(price_info, dict):
                current_price = price_info.get('currentPrice', price_info.get('displayPrice', 0))
                if isinstance(current_price, (int, float)):
                    price = float(current_price)
                elif isinstance(current_price, dict) and 'price' in current_price:
                    price = float(current_price['price'])
            elif isinstance(price_info, (int, float)):
                price = float(price_info)
            
            # Extract URL
            product_url = ""
            if 'canonicalUrl' in item:
                product_url = f"https://www.walmart.com{item['canonicalUrl']}"
            elif 'productPageUrl' in item:
                product_url = f"https://www.walmart.com{item['productPageUrl']}"
            elif 'productUrl' in item:
                product_url = f"https://www.walmart.com{item['productUrl']}"
            
            # Extract image URL
            image_url = ""
            if 'imageInfo' in item and 'thumbnailUrl' in item['imageInfo']:
                image_url = item['imageInfo']['thumbnailUrl']
            elif 'images' in item and len(item['images']) > 0:
                image_url = item['images'][0].get('url', '')
            elif 'image' in item:
                image_url = item['image']
            
            # Extract rating
            rating = 0.0
            if 'averageRating' in item:
                rating = float(item['averageRating'])
            elif 'rating' in item and 'averageRating' in item['rating']:
                rating = float(item['rating']['averageRating'])
            
            # Extract number of reviews
            reviews = 0
            if 'numberOfReviews' in item:
                reviews = int(item['numberOfReviews'])
            elif 'rating' in item and 'numberOfReviews' in item['rating']:
                reviews = int(item['rating']['numberOfReviews'])
            elif 'reviewCount' in item:
                reviews = int(item['reviewCount'])
            
            # Check if product is sponsored
            is_sponsored = False
            if 'sponsored' in item:
                is_sponsored = bool(item['sponsored'])
            
            # Check if product is available for pickup
            is_pickup_today = False
            if 'fulfillmentBadge' in item and 'fulfillmentType' in item:
                is_pickup_today = 'PICKUP' in item['fulfillmentType']
            elif 'fulfillment' in item and 'pickup' in item['fulfillment']:
                is_pickup_today = True
            
            # Create product dictionary
            product = {
                "title": title,
                "price": price,
                "currency": "USD",
                "url": product_url,
                "image_url": image_url,
                "rating": rating,
                "reviews": reviews,
                "is_sponsored": is_sponsored,
                "is_pickup_today": is_pickup_today,
                "product_id": product_id,
            }
            
            return product
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON product: {str(e)}")
            return None
    
    def _extract_from_html(self, soup, max_results: int) -> List[Dict[str, Any]]:
        """
        Extract product data from HTML when JSON extraction fails.
        
        Args:
            soup: BeautifulSoup object of the page
            max_results: Maximum number of results to return
            
        Returns:
            A list of product dictionaries
        """
        products = []
        
        try:
            # Find all product divs in the search results
            product_divs = soup.select('div[data-item-id]')
            
            if not product_divs:
                # Try alternate selector
                product_divs = soup.select('.product-card')
            
            if not product_divs:
                # Try another alternate selector
                product_divs = soup.select('.search-result-gridview-item')
            
            for div in product_divs[:max_results]:
                product = self._extract_product_data(div)
                if product:
                    products.append(product)
                    
                    # If we've collected enough products, stop
                    if len(products) >= max_results:
                        break
            
            return products
            
        except Exception as e:
            self.logger.error(f"Error extracting from HTML: {str(e)}")
            return []
    
    def _extract_product_data(self, product_div) -> Optional[Dict[str, Any]]:
        """
        Extract product data from a product div element.
        
        Args:
            product_div: BeautifulSoup element containing product data
            
        Returns:
            A dictionary of product data, or None if extraction fails
        """
        try:
            # Extract product ID
            product_id = product_div.get('data-item-id', '')
            if not product_id:
                product_id = product_div.get('data-product-id', '')
            
            # Check if the product is sponsored
            is_sponsored = bool(product_div.select_one('.sponsored-flag'))
            
            # Extract product title
            title_element = product_div.select_one('.product-title-link span')
            if not title_element:
                title_element = product_div.select_one('.ProductPlaceholder-title')
                
            # If we still don't have a title, try other common selectors
            if not title_element:
                title_element = product_div.select_one('span[data-automation="product-title"]')
                
            # If still no title, search for any heading element
            if not title_element:
                for heading in product_div.select('h2, h3'):
                    if heading.text.strip():
                        title_element = heading
                        break

            title = title_element.text.strip() if title_element else "Unknown Product"
            
            # Extract product URL
            url_element = product_div.select_one('a.product-title-link')
            if not url_element:
                url_element = product_div.select_one('a[href^="/ip/"]')
            
            url = "https://www.walmart.com" + url_element['href'] if url_element and 'href' in url_element.attrs else "#"
            
            # Extract product image URL
            img_element = product_div.select_one('img.product-image-photo')
            if not img_element:
                img_element = product_div.select_one('img.ProductPlaceholder-image')
            
            image_url = img_element['src'] if img_element and 'src' in img_element.attrs else ""
            if not image_url and img_element and 'data-src' in img_element.attrs:
                image_url = img_element['data-src']
            
            # Extract product price
            price_element = product_div.select_one('.price-main')
            if not price_element:
                price_element = product_div.select_one('.product-price')
            if not price_element:
                price_element = product_div.select_one('span[data-automation="product-price"]')
            if not price_element:
                price_element = product_div.select_one('[data-price]')
                if price_element and 'data-price' in price_element.attrs:
                    price = float(price_element['data-price'])
                    # Skip the text extraction below
                    price_extracted = True
                else:
                    price_extracted = False

            price = 0.0
            if price_element and not price_extracted:
                price_text = price_element.text.strip()
                price = self._parse_price(price_text)
                        
            # Extract product rating
            rating_element = product_div.select_one('.stars-reviews-count')
            if not rating_element:
                rating_element = product_div.select_one('.ratings')
            
            rating = 0.0
            if rating_element:
                rating_text = rating_element.text.strip()
                rating_match = re.search(r'(\d+\.\d+)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Extract number of reviews
            reviews_element = product_div.select_one('.stars-reviews-count span')
            if not reviews_element:
                reviews_element = product_div.select_one('.review-count')
            
            reviews = 0
            if reviews_element:
                reviews_text = reviews_element.text.strip()
                reviews_text = reviews_text.replace(',', '')
                reviews_match = re.search(r'(\d+)', reviews_text)
                if reviews_match:
                    reviews = int(reviews_match.group(1))
            
            # Check if the product has pickup today
            is_pickup_today = bool(product_div.select_one('.fulfillment-shipping-text'))
            if not is_pickup_today:
                is_pickup_today = bool(product_div.select_one('.pickup-today'))
            
            # Create product dictionary
            product = {
                "title": title,
                "price": price,
                "currency": "USD",
                "url": url,
                "image_url": image_url,
                "rating": rating,
                "reviews": reviews,
                "is_sponsored": is_sponsored,
                "is_pickup_today": is_pickup_today,
                "product_id": product_id,
            }
            
            return product
            
        except Exception as e:
            self.logger.error(f"Error extracting product data: {str(e)}")
            return None
    
    def _parse_price(self, price_text: str) -> float:
        """
        Parse price string to float.
        
        Args:
            price_text: Price text to parse
            
        Returns:
            Parsed price as float
        """
        try:
            # Remove currency symbol and commas, then convert to float
            price_text = price_text.replace('$', '').replace(',', '')
            # Extract numbers using regex
            price_match = re.search(r'(\d+\.\d+)', price_text)
            if price_match:
                return float(price_match.group(1))
            return 0.0
        except (ValueError, AttributeError):
            return 0.0