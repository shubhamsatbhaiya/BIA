"""
Product Comparison Agent for DealFinder AI.

This module implements the ProductComparisonAgent class that identifies
the same products across different e-commerce sites and compares prices.
"""

import re
import logging
import difflib
from typing import Dict, Any, List, Optional, Tuple

from dealfinder.agents.base import Agent, MCPMessage
from dealfinder.utils.logging import get_logger

logger = get_logger("ProductComparison")

class ProductComparisonAgent(Agent):
    """Agent for comparing the same products across different e-commerce sites"""
    
    def __init__(self):
        """Initialize the Product Comparison agent."""
        super().__init__("ProductComparisonAgent")
    
    def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Process aggregated search results to identify and compare the same products.
        
        Args:
            message: The MCPMessage containing aggregated results to process
            
        Returns:
            A new MCPMessage containing the comparison results
        """
        if message.message_type != "COMPARE_REQUEST":
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": "Only COMPARE_REQUEST message type is supported"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
        
        try:
            results_data = message.content
            original_query = results_data.get("original_query", "")
            search_params = results_data.get("search_params", {})
            all_products = results_data.get("all_products", [])
            
            self.logger.info(f"Comparing products for query: {original_query}")
            self.logger.info(f"Found {len(all_products)} products to compare")
            
            # Group similar products together
            product_groups = self._group_similar_products(all_products)
            
            # Find best deals for each product group
            best_deals = self._find_best_deals(product_groups)
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={
                    "original_query": original_query,
                    "search_params": search_params,
                    "product_groups": product_groups,
                    "best_deals": best_deals,
                    "all_products": all_products
                },
                message_type="COMPARE_RESPONSE",
                conversation_id=message.conversation_id
            )
            
        except Exception as e:
            self.logger.error(f"Error comparing products: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Product comparison error: {str(e)}"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
    
    # def _group_similar_products(self, products: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    #     """
    #     Group similar products together based on title similarity.
        
    #     Args:
    #         products: List of product dictionaries to group
            
    #     Returns:
    #         List of product groups, where each group is a list of similar products
    #     """
    #     # Create groups of similar products
    #     product_groups = []
        
    #     # Products already assigned to a group
    #     assigned_products = set()
        
    #     # Extract model numbers and significant terms from titles
    #     product_info = []
    #     for i, product in enumerate(products):
    #         title = product.get("title", "").lower()
    #         # Try to extract model numbers (like WH-1000XM4)
    #         model_numbers = re.findall(r'[a-zA-Z]+[-]?\d+[a-zA-Z0-9]*', title)
    #         # Extract significant terms (words with 4+ characters)
    #         significant_terms = [word for word in title.split() if len(word) >= 4]
    #         product_info.append({
    #             "index": i,
    #             "model_numbers": model_numbers,
    #             "significant_terms": significant_terms,
    #             "title": title
    #         })
        
    #     # First pass: group by model number
    #     for i, info in enumerate(product_info):
    #         if i in assigned_products:
    #             continue
                
    #         group = [products[i]]
    #         assigned_products.add(i)
            
    #         for j, other_info in enumerate(product_info):
    #             if j in assigned_products or i == j:
    #                 continue
                
    #             # Check for matching model numbers
    #             if info["model_numbers"] and other_info["model_numbers"]:
    #                 for model in info["model_numbers"]:
    #                     if any(model.lower() in other_model.lower() or other_model.lower() in model.lower() 
    #                            for other_model in other_info["model_numbers"]):
    #                         group.append(products[j])
    #                         assigned_products.add(j)
    #                         break
            
    #         if len(group) > 1:
    #             product_groups.append(group)
        
    #     # Second pass: group by title similarity
    #     for i, info in enumerate(product_info):
    #         if i in assigned_products:
    #             continue
                
    #         group = [products[i]]
    #         assigned_products.add(i)
            
    #         for j, other_info in enumerate(product_info):
    #             if j in assigned_products or i == j:
    #                 continue
                
    #             # Calculate title similarity
    #             similarity = difflib.SequenceMatcher(None, info["title"], other_info["title"]).ratio()
                
    #             # Check for shared significant terms
    #             shared_terms = set(info["significant_terms"]) & set(other_info["significant_terms"])
    #             term_ratio = len(shared_terms) / max(len(info["significant_terms"]), len(other_info["significant_terms"]), 1)
                
    #             # If titles are similar or share many significant terms
    #             if similarity > 0.6 or term_ratio > 0.5:
    #                 group.append(products[j])
    #                 assigned_products.add(j)
            
    #         if len(group) > 1:
    #             product_groups.append(group)
        
    #     # Add remaining ungrouped products as single-item groups
    #     for i, product in enumerate(products):
    #         if i not in assigned_products:
    #             product_groups.append([product])
        
    #     return product_groups
    
    # def _find_best_deals(self, product_groups: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    #     """
    #     Find the best deal for each group of similar products.
        
    #     Args:
    #         product_groups: List of product groups to analyze
            
    #     Returns:
    #         List of best deals, one for each product group
    #     """
    #     best_deals = []
        
    #     for group in product_groups:
    #         if not group:
    #             continue
                
    #         # Calculate "effective price" considering shipping, Prime benefits, etc.
    #         for product in group:
    #             effective_price = product.get("price", 0)
                
    #             # Add shipping cost if not free
    #             if "shipping" in product and product["shipping"] > 0:
    #                 effective_price += product["shipping"]
                
    #             # Apply small discount for Prime/pickup benefits
    #             if product.get("is_prime", False) or product.get("is_pickup_today", False):
    #                 effective_price *= 0.98  # 2% discount for convenience
                
    #             # Penalize slightly for lower ratings or fewer reviews
    #             if "rating" in product and product["rating"] > 0:
    #                 rating_factor = min(1.0, product["rating"] / 5.0)
    #                 reviews = product.get("reviews", 0)
    #                 review_factor = min(1.0, reviews / 1000) if reviews > 0 else 0.5
                    
    #                 # Small adjustment based on rating and reviews (max 5%)
    #                 rating_adjustment = 1.0 - ((rating_factor * review_factor) * 0.05)
    #                 effective_price *= rating_adjustment
                
    #             product["effective_price"] = effective_price
            
    #         # Sort by effective price
    #         sorted_group = sorted(group, key=lambda x: x.get("effective_price", float("inf")))
            
    #         # Get best deal
    #         best_deal = sorted_group[0] if sorted_group else None
            
    #         if best_deal:
    #             # Calculate price difference from average
    #             total_price = sum(p.get("effective_price", 0) for p in group)
    #             avg_price = total_price / len(group) if group else 0
                
    #             savings = avg_price - best_deal["effective_price"] if avg_price > 0 else 0
    #             savings_percent = (savings / avg_price) * 100 if avg_price > 0 else 0
                
    #             best_deals.append({
    #                 "product": best_deal,
    #                 "similar_products": sorted_group[1:],
    #                 "average_price": avg_price,
    #                 "savings": savings,
    #                 "savings_percent": savings_percent,
    #                 "source_count": len(set(p.get("source", "") for p in group))
    #             })
        
    #     # Sort best deals by savings percentage
    #     best_deals = sorted(best_deals, key=lambda x: x.get("savings_percent", 0), reverse=True)
        
    #     return best_deals
        """
    Updated ProductComparisonAgent to fix price data type issues and comparison
    """

    def _find_best_deals(self, product_groups: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Find the best deal for each group of similar products.
        
        Args:
            product_groups: List of product groups to analyze
            
        Returns:
            List of best deals, one for each product group
        """
        best_deals = []
        
        for group in product_groups:
            if not group:
                continue
            
            # Debug log the group
            self.logger.info(f"Analyzing product group with {len(group)} items")
                
            # Calculate "effective price" considering shipping, Prime benefits, etc.
            for product in group:
                # Ensure price is a float
                try:
                    price = float(product.get("price", 0))
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid price format in product: {product.get('title', 'Unknown')}")
                    price = 0.0
                    
                effective_price = price
                
                # Add shipping cost if not free
                if "shipping" in product and product["shipping"] is not None:
                    try:
                        shipping = float(product["shipping"])
                        effective_price += shipping
                    except (ValueError, TypeError):
                        self.logger.warning(f"Invalid shipping format: {product['shipping']}")
                
                # Apply small discount for Prime/pickup benefits
                if product.get("is_prime", False) or product.get("is_pickup_today", False):
                    effective_price *= 0.98  # 2% discount for convenience
                
                # Penalize slightly for lower ratings or fewer reviews
                if "rating" in product and product["rating"] is not None:
                    try:
                        rating = float(product["rating"])
                        rating_factor = min(1.0, rating / 5.0)
                        
                        reviews = 0
                        if "reviews" in product and product["reviews"] is not None:
                            try:
                                reviews = int(product["reviews"])
                            except (ValueError, TypeError):
                                reviews = 0
                                
                        review_factor = min(1.0, reviews / 1000) if reviews > 0 else 0.5
                        
                        # Small adjustment based on rating and reviews (max 5%)
                        rating_adjustment = 1.0 - ((rating_factor * review_factor) * 0.05)
                        effective_price *= rating_adjustment
                    except (ValueError, TypeError):
                        self.logger.warning(f"Invalid rating format: {product['rating']}")
                
                # Store the effective price in the product
                product["effective_price"] = effective_price
                
                # Also ensure the actual price is stored as a float 
                product["price"] = price
            
            # Sort by effective price
            sorted_group = sorted(group, key=lambda x: x.get("effective_price", float("inf")))
            
            # Get best deal
            best_deal = sorted_group[0] if sorted_group else None
            
            if best_deal:
                # Calculate price difference from average
                total_price = sum(p.get("effective_price", 0) for p in group)
                avg_price = total_price / len(group) if group else 0
                
                savings = avg_price - best_deal["effective_price"] if avg_price > 0 else 0
                savings_percent = (savings / avg_price) * 100 if avg_price > 0 else 0
                
                # Debug log the best deal
                self.logger.info(f"Best deal: {best_deal.get('title', 'Unknown')} at ${best_deal.get('price', 0):.2f}")
                self.logger.info(f"Savings: ${savings:.2f} ({savings_percent:.1f}%)")
                
                best_deals.append({
                    "product": best_deal,
                    "similar_products": sorted_group[1:],
                    "average_price": avg_price,
                    "savings": savings,
                    "savings_percent": savings_percent,
                    "source_count": len(set(p.get("source", "") for p in group))
                })
            
            # Sort best deals by savings percentage
            best_deals = sorted(best_deals, key=lambda x: x.get("savings_percent", 0), reverse=True)
            
            return best_deals
        
    def _group_similar_products(self, products: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Group similar products together based on title similarity.
        
        Args:
            products: List of product dictionaries to group
            
        Returns:
            List of product groups, where each group is a list of similar products
        """
        # Create groups of similar products
        product_groups = []
        
        # Products already assigned to a group
        assigned_products = set()
        
        # Log the number of products to group
        self.logger.info(f"Grouping {len(products)} products")
        
        # Fix: Ensure all prices are numeric
        for product in products:
            if "price" in product:
                try:
                    product["price"] = float(product["price"])
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid price in product {product.get('title', 'Unknown')}: {product.get('price')}")
                    product["price"] = 0.0
        
        # Extract model numbers and significant terms from titles
        product_info = []
        for i, product in enumerate(products):
            title = product.get("title", "").lower()
            # Try to extract model numbers (like WH-1000XM4)
            model_numbers = re.findall(r'[a-zA-Z]+[-]?\d+[a-zA-Z0-9]*', title)
            # Extract significant terms (words with 4+ characters)
            significant_terms = [word for word in title.split() if len(word) >= 4]
            product_info.append({
                "index": i,
                "model_numbers": model_numbers,
                "significant_terms": significant_terms,
                "title": title
            })
        
        # First pass: group by model number
        for i, info in enumerate(product_info):
            if i in assigned_products:
                continue
                
            group = [products[i]]
            assigned_products.add(i)
            
            for j, other_info in enumerate(product_info):
                if j in assigned_products or i == j:
                    continue
                
                # Check for matching model numbers
                if info["model_numbers"] and other_info["model_numbers"]:
                    for model in info["model_numbers"]:
                        if any(model.lower() in other_model.lower() or other_model.lower() in model.lower() 
                            for other_model in other_info["model_numbers"]):
                            group.append(products[j])
                            assigned_products.add(j)
                            break
            
            if len(group) > 1:
                product_groups.append(group)
        
        # Second pass: group by title similarity
        for i, info in enumerate(product_info):
            if i in assigned_products:
                continue
                
            group = [products[i]]
            assigned_products.add(i)
            
            for j, other_info in enumerate(product_info):
                if j in assigned_products or i == j:
                    continue
                
                # Calculate title similarity
                similarity = difflib.SequenceMatcher(None, info["title"], other_info["title"]).ratio()
                
                # Check for shared significant terms
                shared_terms = set(info["significant_terms"]) & set(other_info["significant_terms"])
                term_ratio = len(shared_terms) / max(len(info["significant_terms"]), len(other_info["significant_terms"]), 1)
                
                # If titles are similar or share many significant terms
                if similarity > 0.6 or term_ratio > 0.5:
                    group.append(products[j])
                    assigned_products.add(j)
            
            if len(group) > 1:
                product_groups.append(group)
        
        # Add remaining ungrouped products as single-item groups
        for i, product in enumerate(products):
            if i not in assigned_products:
                product_groups.append([product])
        
        # Log the results
        self.logger.info(f"Created {len(product_groups)} product groups")
        
        return product_groups