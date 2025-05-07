"""
Real Amazon Scraper Implementation for DealFinder AI.

This module implements the RealAmazonScraperAgent class that uses BeautifulSoup
and requests to extract actual product data from Amazon.
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

logger = get_logger("Scrapers.Amazon")

class RealAmazonScraperAgent(Agent):
    """Agent for scraping Amazon product listings with actual web scraping"""
    
    def __init__(self):
        """Initialize the Amazon scraper agent."""
        super().__init__("AmazonScraperAgent")
        self.base_url = config.AMAZON_BASE_URL
        
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
            # Convert search parameters to Amazon search query
            query = self._build_search_query(search_params)
            
            # Perform the search
            products = self._scrape_search_results(query, search_params)
            
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
        Scrape Amazon search results for the given query.
        
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
            "k": query,
            "ref": "nb_sb_noss",
        }
        
        # Add price range if specified
        if "price_range" in search_params and search_params["price_range"]:
            price_range = search_params["price_range"]
            if isinstance(price_range, list) and len(price_range) == 2:
                min_price, max_price = price_range
                if min_price:
                    params["low-price"] = min_price
                if max_price:
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
        
        # Use a random user agent for each request
        current_headers = self.headers.copy()
        current_headers["User-Agent"] = random.choice(config.USER_AGENTS)
        
        try:
            # Send the request to Amazon
            response = requests.get(
                self.base_url,
                params=params,
                headers=current_headers,
                timeout=config.SCRAPING_TIMEOUT
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                self.logger.error(f"Failed to retrieve Amazon search results: {response.status_code}")
                return []
            
            # Parse the HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract product data
            products = []
            
            # Find all product divs in the search results
            product_divs = soup.select('div[data-component-type="s-search-result"]')
            
            for div in product_divs[:max_results]:  # Limit to max_results
                product = self._extract_product_data(div)
                if product:
                    product["source"] = "Amazon"
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
            self.logger.error(f"Error during Amazon search scraping: {str(e)}")
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
            # Extract ASIN (Amazon Standard Identification Number)
            asin = product_div.get('data-asin')
            if not asin:
                return None
                
            # Check if the product is sponsored
            is_sponsored = bool(product_div.select_one('.s-sponsored-label-info-icon'))
                
            # Extract product title
            title_element = product_div.select_one('h2 a.a-link-normal span')
            title = title_element.text.strip() if title_element else "Unknown Product"
                
            # Extract product URL
            url_element = product_div.select_one('h2 a.a-link-normal')
            url = "https://www.amazon.com" + url_element['href'] if url_element and 'href' in url_element.attrs else "#"
                
            # Extract product image URL
            img_element = product_div.select_one('img.s-image')
            image_url = img_element['src'] if img_element and 'src' in img_element.attrs else ""
                
            # Extract product price
            price_element = product_div.select_one('.a-price .a-offscreen')
            price_text = price_element.text.strip() if price_element else ""
            price = self._parse_price(price_text)
                
            # Extract product rating
            rating_element = product_div.select_one('i.a-icon-star-small .a-icon-alt')
            rating = 0.0
            if rating_element:
                rating_text = rating_element.text.strip()
                rating_match = rating_text.split(' out of')[0]
                try:
                    rating = float(rating_match)
                except ValueError:
                    pass
                
            # Extract number of reviews
            reviews_element = product_div.select_one('span.a-size-base')
            reviews = 0
            if reviews_element:
                reviews_text = reviews_element.text.strip()
                reviews_text = reviews_text.replace(',', '')
                reviews_match = ''.join(c for c in reviews_text if c.isdigit())
                if reviews_match:
                    try:
                        reviews = int(reviews_match)
                    except ValueError:
                        pass
                
            # Check if the product has Prime shipping
            is_prime = bool(product_div.select_one('.s-prime'))
                
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
                "is_prime": is_prime,
                "asin": asin,
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
            return float(price_text)
        except (ValueError, AttributeError):
            return 0.0