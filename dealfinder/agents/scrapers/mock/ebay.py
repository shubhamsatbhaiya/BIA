"""
Mock eBay Scraper Implementation for DealFinder AI.

This module implements the MockEbayScraperAgent class that provides
simulated product data for testing and development.
"""

import random
import logging
from typing import Dict, Any, List, Optional

from dealfinder.agents.base import Agent, MCPMessage
from dealfinder.utils.logging import get_logger

logger = get_logger("Scrapers.Mock.Ebay")

class MockEbayScraperAgent(Agent):
    """Agent for simulating eBay product listings"""
    
    def __init__(self):
        """Initialize the mock eBay scraper agent."""
        super().__init__("EbayScraperAgent")
    
    def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Process search request for eBay.
        
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
        self.logger.info(f"Mock eBay search for: {search_params}")
        
        try:
            # Convert search parameters to eBay search query
            query = self._build_search_query(search_params)
            
            # Generate mock products
            products = self._generate_mock_products(query, search_params)
            
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
            self.logger.error(f"Error in mock eBay search: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Mock eBay search error: {str(e)}"},
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
        conditions = ["New", "Used", "Refurbished", "Open Box"]
        listing_types = ["Buy It Now", "Auction", "Best Offer"]
        
        # Get brand from search params or use generic
        if "brands" in search_params and search_params["brands"]:
            if isinstance(search_params["brands"], list):
                use_brands = search_params["brands"]
            else:
                use_brands = [search_params["brands"]]
        else:
            use_brands = ["Sony", "Bose", "JBL", "Anker", "Sennheiser", "Beats", "Skullcandy"]
        
        # Words from the query to incorporate into product names
        query_words = [word for word in query.split() if len(word) > 3]
        
        # Get product type from search params or fallback to generic type
        product_type = (
            search_params.get("product_type", "Headphones") 
            if "product_type" in search_params and search_params["product_type"] 
            else "Headphones"
        )
        
        # Check for price range in search params
        min_price = 19.99
        max_price = 299.99
        if "price_range" in search_params and search_params["price_range"]:
            price_range = search_params["price_range"]
            if isinstance(price_range, list) and len(price_range) == 2:
                if price_range[0] is not None:
                    min_price = price_range[0]
                if price_range[1] is not None:
                    max_price = price_range[1]
        
        # Check for buy it now preference
        preferred_listing_type = None
        if "buy_it_now" in search_params and search_params["buy_it_now"]:
            preferred_listing_type = "Buy It Now"
        
        for i in range(count):
            brand = random.choice(use_brands)
            
            # Create a product name that relates to the search query
            if query_words:
                product_type_word = random.choice(query_words).capitalize()
            else:
                product_type_word = product_type.capitalize()
            
            model = f"{random.choice('ABCDEFG')}{random.randint(100, 999)}"
            condition = random.choice(conditions)
            
            # Use preferred listing type or random
            if preferred_listing_type:
                listing_type = preferred_listing_type
            else:
                listing_type = random.choice(listing_types)
            
            # Generate a price within the range
            price = round(random.uniform(min_price, max_price), 2)
            
            # Generate shipping cost (sometimes free)
            is_free_shipping = random.random() < 0.4  # 40% chance of free shipping
            shipping_cost = 0.0 if is_free_shipping else round(random.uniform(3.99, 15.99), 2)
            
            # Calculate total price
            total_price = price + shipping_cost
            
            # Sponsored status
            is_sponsored = random.random() < 0.15  # 15% chance of being sponsored
            
            # Generate seller rating (usually high)
            seller_rating = round(random.uniform(92.0, 100.0), 1)
            
            product = {
                "title": f"{brand} {product_type_word} {model} {condition}",
                "price": price,
                "shipping": shipping_cost,
                "total_price": total_price,
                "is_free_shipping": is_free_shipping,
                "currency": "USD",
                "condition": condition,
                "listing_type": listing_type,
                "url": f"https://www.ebay.com/itm/{random.randint(100000000, 999999999)}",
                "image_url": f"https://example.com/images/ebay-{brand.lower()}-{model.lower()}.jpg",
                "is_sponsored": is_sponsored,
                "seller_rating": seller_rating,
                "source": "eBay",
                "item_id": f"{random.randint(100000000, 999999999)}",
            }
            
            products.append(product)
        
        # Sort products based on search preferences
        if "sorting_preference" in search_params:
            sort_pref = search_params["sorting_preference"]
            if sort_pref == "price_low_to_high":
                products.sort(key=lambda x: x["total_price"])
            elif sort_pref == "price_high_to_low":
                products.sort(key=lambda x: x["total_price"], reverse=True)
            elif sort_pref == "newest" and random.random() < 0.3:  # Add some listings as "new" randomly
                for product in random.sample(products, min(2, len(products))):
                    product["title"] = "New Listing " + product["title"]
        
        return products