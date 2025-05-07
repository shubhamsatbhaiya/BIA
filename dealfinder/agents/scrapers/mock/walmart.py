"""
Mock Walmart Scraper Implementation for DealFinder AI.

This module implements the MockWalmartScraperAgent class that provides
simulated product data for testing and development.
"""

import random
import logging
from typing import Dict, Any, List, Optional

from dealfinder.agents.base import Agent, MCPMessage
from dealfinder.utils.logging import get_logger

logger = get_logger("Scrapers.Mock.Walmart")

class MockWalmartScraperAgent(Agent):
    """Agent for simulating Walmart product listings"""
    
    def __init__(self):
        """Initialize the mock Walmart scraper agent."""
        super().__init__("WalmartScraperAgent")
    
    def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Process search request for Walmart.
        
        Args:
            message: The incoming MCPMessage to process
            
        Returns:
            A new MCPMessage containing the simulated search results
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
        self.logger.info(f"Mock Walmart search for: {search_params}")
        
        try:
            # Convert search parameters to Walmart search query
            query = self._build_search_query(search_params)
            
            # Generate mock products
            products = self._generate_mock_products(query, search_params)
            
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
            self.logger.error(f"Error in mock Walmart search: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Mock Walmart search error: {str(e)}"},
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
    
    def _generate_mock_products(self, query: str, search_params: Dict[str, Any], count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate mock product data.
        
        Args:
            query: The search query string
            search_params: Additional search parameters
            count: Number of mock products to generate
            
        Returns:
            A list of mock product dictionaries
        """
        products = []
        brands = ["Sony", "Bose", "JBL", "Anker", "Sennheiser", "onn.", "Philips"]
        adjectives = ["Value", "Wireless", "Noise-Cancelling", "Bluetooth", "Basic", "Premium", "Sport"]
        
        # Words from the query to incorporate into product names
        query_words = [word for word in query.split() if len(word) > 3]
        
        # Get product type from search params or fallback to generic type
        product_type = (
            search_params.get("product_type", "Headphones") 
            if "product_type" in search_params and search_params["product_type"] 
            else "Headphones"
        )
        
        # Get brand from search params or use random brands
        if "brands" in search_params and search_params["brands"]:
            if isinstance(search_params["brands"], list):
                use_brands = search_params["brands"]
            else:
                use_brands = [search_params["brands"]]
        else:
            use_brands = brands
        
        # Check for price range in search params
        min_price = 29.99
        max_price = 299.99
        if "price_range" in search_params and search_params["price_range"]:
            price_range = search_params["price_range"]
            if isinstance(price_range, list) and len(price_range) == 2:
                if price_range[0] is not None:
                    min_price = price_range[0]
                if price_range[1] is not None:
                    max_price = price_range[1]
        
        for i in range(count):
            brand = random.choice(use_brands)
            adjective = random.choice(adjectives)
            
            # Create a product name that relates to the search query
            if query_words:
                product_type_word = random.choice(query_words).capitalize()
            else:
                product_type_word = product_type.capitalize()
            
            model_number = f"{random.choice('WXYZ')}{random.randint(100, 999)}"
            
            # Generate prices that respect the price range
            price = round(random.uniform(min_price, max_price), 2)
            
            # Generate high ratings because these are top products
            rating = round(random.uniform(3.0, 5.0), 1)
            reviews = random.randint(20, 3000)
            is_sponsored = random.random() < 0.3  # 30% chance of being sponsored
            
            product = {
                "title": f"{brand} {adjective} {product_type_word} {model_number}",
                "price": price,
                "currency": "USD",
                "rating": rating,
                "reviews": reviews,
                "url": f"https://www.walmart.com/ip/{brand.lower()}-{product_type_word.lower()}-{model_number.lower()}",
                "image_url": f"https://example.com/images/walmart-{brand.lower()}-{model_number.lower()}.jpg",
                "is_sponsored": is_sponsored,
                "is_pickup_today": random.random() < 0.5,  # 50% chance of being available for pickup
                "source": "Walmart",
                "product_id": f"WM{random.randint(10000000, 99999999)}",
            }
            
            products.append(product)
        
        # Sort products based on search preferences
        if "sorting_preference" in search_params:
            sort_pref = search_params["sorting_preference"]
            if sort_pref == "price_low_to_high":
                products.sort(key=lambda x: x["price"])
            elif sort_pref == "price_high_to_low":
                products.sort(key=lambda x: x["price"], reverse=True)
            elif sort_pref == "rating":
                products.sort(key=lambda x: (x["rating"], x["reviews"]), reverse=True)
        
        return products