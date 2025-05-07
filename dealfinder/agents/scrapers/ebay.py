"""
Real eBay Scraper Implementation for DealFinder AI.

This module implements the RealEbayScraperAgent class that uses BeautifulSoup
and requests to extract actual product data from eBay.
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

logger = get_logger("Scrapers.Ebay")

class RealEbayScraperAgent(Agent):
    """Agent for scraping eBay product listings with actual web scraping"""
    
    def __init__(self):
        """Initialize the eBay scraper agent."""
        super().__init__("EbayScraperAgent")
        self.base_url = config.EBAY_BASE_URL
        
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
            # Convert search parameters to eBay search query
            query = self._build_search_query(search_params)
            
            # Perform the search
            products = self._scrape_search_results(query, search_params)
            
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
        Scrape eBay search results for the given query.
        
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
        
        # Set up request parameters
        params = {
            "_nkw": query,
            "_sacat": "0",
            "_ipg": "50",  # Items per page
        }
        
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
        
        # Use a random user agent for each request
        current_headers = self.headers.copy()
        current_headers["User-Agent"] = random.choice(config.USER_AGENTS)
        
        try:
            # Send the request to eBay
            response = requests.get(
                self.base_url,
                params=params,
                headers=current_headers,
                timeout=config.SCRAPING_TIMEOUT
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                self.logger.error(f"Failed to retrieve eBay search results: {response.status_code}")
                return []
            
            # Parse the HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract product data
            products = []
            
            # Find all product divs in the search results
            product_divs = soup.select('li.s-item')
            
            for div in product_divs[:max_results]:  # Limit to max_results
                product = self._extract_product_data(div)
                if product:
                    product["source"] = "eBay"
                    products.append(product)
                    
                    # If we've collected enough products, stop
                    if len(products) >= max_results:
                        break
            
            # Add a small delay to avoid rate limiting
            time.sleep(random.uniform(
                config.SCRAPING_DELAY_MIN,
                config.SCRAPING_DELAY_MAX
            ))
            
            return products
            
        except Exception as e:
            self.logger.error(f"Error during eBay search scraping: {str(e)}")
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
            
            # Create product dictionary
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
            # Remove currency symbol, commas, and extra text
            price_text = re.sub(r'[^\d\.]', '', price_text.split(' ')[0])
            if price_text:
                return float(price_text)
            return 0.0
        except (ValueError, AttributeError, IndexError):
            return 0.0