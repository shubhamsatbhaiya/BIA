"""
Results Aggregator Agent for DealFinder AI.

This module implements the ResultsAggregatorAgent class that aggregates
and ranks results from multiple sources.
"""

import logging
from typing import Dict, Any, List, Optional

from dealfinder.agents.base import Agent, MCPMessage
from dealfinder import config

logger = logging.getLogger("DealFinderAI.ResultsAggregatorAgent")

class ResultsAggregatorAgent(Agent):
    """Agent for aggregating and ranking results from multiple sources"""
    
    def __init__(self):
        """Initialize a new Results Aggregator agent."""
        super().__init__("ResultsAggregatorAgent")
    
    # def process_message(self, message: MCPMessage) -> MCPMessage:
    #     """
    #     Process and aggregate search results.
        
    #     Args:
    #         message: The MCPMessage containing search results to aggregate
            
    #     Returns:
    #         A new MCPMessage containing the aggregated results
    #     """
    #     if message.message_type != "AGGREGATE_REQUEST":
    #         return MCPMessage(
    #             sender=self.name,
    #             receiver=message.sender,
    #             content={"error": "Only AGGREGATE_REQUEST message type is supported"},
    #             message_type="ERROR",
    #             conversation_id=message.conversation_id
    #         )
        
    #     try:
    #         results_data = message.content
    #         original_query = results_data.get("original_query", "")
    #         search_params = results_data.get("search_params", {})
    #         all_results = results_data.get("results", [])
            
    #         self.logger.info(f"Aggregating results for query: {original_query}")
    #         self.logger.info(f"Found {len(all_results)} results from various sources")
            
    #         # Extract all products from different sources
    #         all_products = []
    #         for result in all_results:
    #             if "products" in result:
    #                 all_products.extend(result["products"])
            
    #         # Sort and rank products based on search parameters
    #         sorted_products = self._rank_products(all_products, search_params)
            
    #         # Take top results (up to DEFAULT_MAX_RESULTS)
    #         max_results = config.DEFAULT_MAX_RESULTS
    #         top_products = sorted_products[:max_results]
            
    #         # Group by source for presentation
    #         grouped_results = self._group_by_source(top_products)
            
    #         return MCPMessage(
    #             sender=self.name,
    #             receiver=message.sender,
    #             content={
    #                 "original_query": original_query,
    #                 "search_params": search_params,
    #                 "top_products": top_products,
    #                 "grouped_results": grouped_results,
    #                 "total_results": len(all_products),
    #                 "selected_results": len(top_products)
    #             },
    #             message_type="AGGREGATE_RESPONSE",
    #             conversation_id=message.conversation_id
    #         )
            
    #     except Exception as e:
    #         self.logger.error(f"Error aggregating results: {str(e)}")
    #         return MCPMessage(
    #             sender=self.name,
    #             receiver=message.sender,
    #             content={"error": f"Results aggregation error: {str(e)}"},
    #             message_type="ERROR",
    #             conversation_id=message.conversation_id
    #         )
    
    # def _rank_products(self, products: List[Dict[str, Any]], search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
    #     """
    #     Rank and sort products based on search parameters.
        
    #     Args:
    #         products: List of product dictionaries to rank
    #         search_params: Search parameters to use for ranking
            
    #     Returns:
    #         Sorted list of products by calculated score
    #     """
    #     # Calculate a score for each product
    #     for product in products:
    #         score = 0
            
    #         # Base score
    #         # Higher ratings increase score
    #         if "rating" in product:
    #             score += product["rating"] * 10
            
    #         # More reviews increase confidence
    #         if "reviews" in product:
    #             reviews = product["reviews"]
    #             if reviews > 1000:
    #                 score += 15
    #             elif reviews > 500:
    #                 score += 10
    #             elif reviews > 100:
    #                 score += 5
            
    #         # Price considerations
    #         if "price" in product:
    #             price = product["price"]
                
    #             # Check if product is within desired price range
    #             if "price_range" in search_params and search_params["price_range"]:
    #                 min_price, max_price = search_params["price_range"]
    #                 if min_price and max_price:
    #                     if min_price <= price <= max_price:
    #                         score += 20
    #                     elif price < min_price:
    #                         score -= 5  # Too cheap might indicate lower quality
    #                     elif price > max_price:
    #                         score -= 15  # Too expensive
    #                 elif max_price and price <= max_price:
    #                     score += 10
    #                 elif min_price and price >= min_price:
    #                     score += 5
                
    #             # Generally, lower prices are better for same product
    #             normalized_price_score = max(0, 30 - (price / 10))
    #             score += normalized_price_score
            
    #         # Shipping considerations (for eBay)
    #         if "shipping" in product and product["shipping"] == 0:
    #             score += 5  # Free shipping bonus
    #         if "is_free_shipping" in product and product["is_free_shipping"]:
    #             score += 5  # Free shipping bonus
            
    #         # Prime benefits (for Amazon)
    #         if "is_prime" in product and product["is_prime"]:
    #             score += 8
            
    #         # Pickup today benefits (for Walmart)
    #         if "is_pickup_today" in product and product["is_pickup_today"]:
    #             score += 6
            
    #         # Condition considerations (for eBay)
    #         if "condition" in product:
    #             condition = product.get("condition", "").lower()
    #             if "new" in condition:
    #                 score += 10
    #             elif "refurbished" in condition or "renewed" in condition:
    #                 score += 5
    #             elif "used" in condition and "like new" in condition:
    #                 score += 3
            
    #         # Listing type considerations (for eBay)
    #         if "listing_type" in product:
    #             listing_type = product.get("listing_type", "").lower()
    #             if "buy it now" in listing_type:
    #                 score += 5  # Buy It Now is generally preferred for immediacy
            
    #         # Seller rating considerations (for eBay)
    #         if "seller_rating" in product:
    #             seller_rating = product.get("seller_rating", 0)
    #             if seller_rating > 95:
    #                 score += 5
    #             elif seller_rating > 90:
    #                 score += 3
            
    #         # Sponsored items are ranked lower
    #         if "is_sponsored" in product and product["is_sponsored"]:
    #             score -= 10
            
    #         # Store the score
    #         product["_score"] = score
        
    #     # Sort by score (highest first)
    #     sorted_products = sorted(products, key=lambda x: x.get("_score", 0), reverse=True)
        
    #     # Ensure diversity by taking products from different sources
    #     if len(sorted_products) > 5:
    #         # Ensure top results have diversity of sources
    #         top_5_sources = set()
    #         final_products = []
            
    #         # Always include the top product
    #         final_products.append(sorted_products[0])
    #         top_5_sources.add(sorted_products[0].get("source"))
            
    #         # Add remaining products ensuring source diversity
    #         remaining = sorted_products[1:]
            
    #         # First pass: add one product from each source not yet represented
    #         for product in remaining:
    #             source = product.get("source")
    #             if source not in top_5_sources and len(final_products) < 5:
    #                 final_products.append(product)
    #                 top_5_sources.add(source)
            
    #         # Second pass: add remaining top products
    #         for product in remaining:
    #             if product not in final_products and len(final_products) < config.DEFAULT_MAX_RESULTS:
    #                 final_products.append(product)
            
    #         return final_products
        
    #     return sorted_products
    
    """
Updated ResultsAggregatorAgent class with enhanced error handling and product filtering
"""

    def _rank_products(self, products: List[Dict[str, Any]], search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank and sort products based on search parameters.
        
        Args:
            products: List of product dictionaries to rank
            search_params: Search parameters to use for ranking
            
        Returns:
            Sorted list of products by calculated score
        """
        # Fix: First check if there are any products to rank
        if not products:
            self.logger.warning("No products to rank")
            return []
            
        # Debug logging for the products before ranking
        self.logger.info(f"Ranking {len(products)} products")
        
        # Fix: Ensure prices are always numeric to avoid comparison issues
        for product in products:
            if "price" in product:
                try:
                    product["price"] = float(product["price"])
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid price format in product: {product.get('title', 'Unknown')}")
                    product["price"] = 0.0
            
            if "shipping" in product and product["shipping"] is not None:
                try:
                    product["shipping"] = float(product["shipping"])
                except (ValueError, TypeError):
                    product["shipping"] = 0.0
        
        # Calculate a score for each product
        for product in products:
            score = 0
            
            # Base score
            # Higher ratings increase score
            if "rating" in product:
                try:
                    rating = float(product["rating"])
                    score += rating * 10
                except (ValueError, TypeError):
                    pass
            
            # More reviews increase confidence
            if "reviews" in product:
                try:
                    reviews = int(product["reviews"])
                    if reviews > 1000:
                        score += 15
                    elif reviews > 500:
                        score += 10
                    elif reviews > 100:
                        score += 5
                except (ValueError, TypeError):
                    pass
            
            # Price considerations
            if "price" in product:
                try:
                    price = float(product["price"])
                    
                    # Check if product is within desired price range
                    if "price_range" in search_params and search_params["price_range"]:
                        min_price, max_price = search_params["price_range"]
                        if min_price and max_price:
                            try:
                                min_price = float(min_price)
                                max_price = float(max_price)
                                if min_price <= price <= max_price:
                                    score += 20
                                elif price < min_price:
                                    score -= 5  # Too cheap might indicate lower quality
                                elif price > max_price:
                                    score -= 15  # Too expensive
                            except (ValueError, TypeError):
                                pass
                        elif max_price:
                            try:
                                max_price = float(max_price)
                                if price <= max_price:
                                    score += 10
                            except (ValueError, TypeError):
                                pass
                        elif min_price:
                            try:
                                min_price = float(min_price)
                                if price >= min_price:
                                    score += 5
                            except (ValueError, TypeError):
                                pass
                    
                    # Generally, lower prices are better for same product
                    normalized_price_score = max(0, 30 - (price / 10))
                    score += normalized_price_score
                except (ValueError, TypeError):
                    pass
            
            # Shipping considerations (for eBay)
            if "shipping" in product:
                try:
                    shipping = float(product["shipping"])
                    if shipping == 0:
                        score += 5  # Free shipping bonus
                except (ValueError, TypeError):
                    pass
                    
            if "is_free_shipping" in product and product["is_free_shipping"]:
                score += 5  # Free shipping bonus
            
            # Prime benefits (for Amazon)
            if "is_prime" in product and product["is_prime"]:
                score += 8
            
            # Pickup today benefits (for Walmart)
            if "is_pickup_today" in product and product["is_pickup_today"]:
                score += 6
            
            # Condition considerations (for eBay)
            if "condition" in product:
                condition = str(product.get("condition", "")).lower()
                if "new" in condition:
                    score += 10
                elif "refurbished" in condition or "renewed" in condition:
                    score += 5
                elif "used" in condition and "like new" in condition:
                    score += 3
            
            # Listing type considerations (for eBay)
            if "listing_type" in product:
                listing_type = str(product.get("listing_type", "")).lower()
                if "buy it now" in listing_type:
                    score += 5  # Buy It Now is generally preferred for immediacy
            
            # Seller rating considerations (for eBay)
            if "seller_rating" in product:
                try:
                    seller_rating = float(product["seller_rating"])
                    if seller_rating > 95:
                        score += 5
                    elif seller_rating > 90:
                        score += 3
                except (ValueError, TypeError):
                    pass
            
            # Sponsored items are ranked lower
            if "is_sponsored" in product and product["is_sponsored"]:
                score -= 10
            
            # Store the score
            product["_score"] = score
        
        # Sort by score (highest first)
        sorted_products = sorted(products, key=lambda x: x.get("_score", 0), reverse=True)
        
        # Debug logging after sorting
        self.logger.info(f"Sorted {len(sorted_products)} products by score")
        
        # Ensure diversity by taking products from different sources
        if len(sorted_products) > 5:
            # Ensure top results have diversity of sources
            top_5_sources = set()
            final_products = []
            
            # Always include the top product
            final_products.append(sorted_products[0])
            top_5_sources.add(sorted_products[0].get("source"))
            
            # Add remaining products ensuring source diversity
            remaining = sorted_products[1:]
            
            # First pass: add one product from each source not yet represented
            for product in remaining:
                source = product.get("source")
                if source not in top_5_sources and len(final_products) < 5:
                    final_products.append(product)
                    top_5_sources.add(source)
            
            # Second pass: add remaining top products
            for product in remaining:
                if product not in final_products and len(final_products) < config.DEFAULT_MAX_RESULTS:
                    final_products.append(product)
            
            # Debug logging for diversified results
            self.logger.info(f"Returning {len(final_products)} diversified products")
            return final_products
        
        # Debug logging for results when <= 5 products
        self.logger.info(f"Returning all {len(sorted_products)} sorted products")
        return sorted_products

    def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Process and aggregate search results.
        
        Args:
            message: The MCPMessage containing search results to aggregate
            
        Returns:
            A new MCPMessage containing the aggregated results
        """
        if message.message_type != "AGGREGATE_REQUEST":
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": "Only AGGREGATE_REQUEST message type is supported"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
        
        try:
            results_data = message.content
            original_query = results_data.get("original_query", "")
            search_params = results_data.get("search_params", {})
            all_results = results_data.get("results", [])
            
            self.logger.info(f"Aggregating results for query: {original_query}")
            self.logger.info(f"Found {len(all_results)} results from various sources")
            
            # Extract all products from different sources
            all_products = []
            for result in all_results:
                if "products" in result:
                    products_from_source = result["products"]
                    self.logger.info(f"Source {result.get('source', 'Unknown')}: {len(products_from_source)} products")
                    all_products.extend(products_from_source)
            
            # Debug logging to verify products were extracted
            self.logger.info(f"Total products extracted: {len(all_products)}")
            
            if not all_products:
                self.logger.warning("No products found in any source")
                return MCPMessage(
                    sender=self.name,
                    receiver=message.sender,
                    content={
                        "original_query": original_query,
                        "search_params": search_params,
                        "top_products": [],
                        "grouped_results": {},
                        "total_results": 0,
                        "selected_results": 0
                    },
                    message_type="AGGREGATE_RESPONSE",
                    conversation_id=message.conversation_id
                )
            
            # Sort and rank products based on search parameters
            sorted_products = self._rank_products(all_products, search_params)
            
            # Debug logging after ranking
            self.logger.info(f"Products after ranking: {len(sorted_products)}")
            
            # Take top results (up to DEFAULT_MAX_RESULTS)
            max_results = config.DEFAULT_MAX_RESULTS
            top_products = sorted_products[:max_results]
            
            # FIX: If no products after ranking, use all products
            if not top_products and all_products:
                self.logger.warning("No products after ranking, using original products")
                top_products = all_products[:max_results]
            
            # Group by source for presentation
            grouped_results = self._group_by_source(top_products)
            
            # Debug logging for final results
            self.logger.info(f"Final products: {len(top_products)}")
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={
                    "original_query": original_query,
                    "search_params": search_params,
                    "top_products": top_products,
                    "grouped_results": grouped_results,
                    "total_results": len(all_products),
                    "selected_results": len(top_products)
                },
                message_type="AGGREGATE_RESPONSE",
                conversation_id=message.conversation_id
            )
            
        except Exception as e:
            self.logger.error(f"Error aggregating results: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Results aggregation error: {str(e)}"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
    def _group_by_source(self, products: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group products by their source.
        
        Args:
            products: List of product dictionaries to group
            
        Returns:
            Dictionary with sources as keys and lists of products as values
        """
        grouped = {}
        
        for product in products:
            source = product.get("source", "Unknown")
            if source not in grouped:
                grouped[source] = []
            
            grouped[source].append(product)
        
        return grouped