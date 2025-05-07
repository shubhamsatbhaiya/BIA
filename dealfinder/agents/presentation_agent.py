"""
Presentation Agent for DealFinder AI.

This module implements the PresentationAgent class that formats results
for presentation to the user in a conversational format.
"""

import logging
from typing import Dict, Any, List, Optional

from dealfinder.agents.base import Agent, MCPMessage

logger = logging.getLogger("DealFinderAI.PresentationAgent")

class PresentationAgent(Agent):
    """Agent for presenting results to the user in a conversational format"""
    
    def __init__(self):
        """Initialize a new Presentation agent."""
        super().__init__("PresentationAgent")
    
    def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Format results for user presentation.
        
        Args:
            message: The MCPMessage containing results to format
            
        Returns:
            A new MCPMessage containing the formatted response
        """
        if message.message_type != "PRESENT_REQUEST":
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": "Only PRESENT_REQUEST message type is supported"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
        
        try:
            results = message.content
            original_query = results.get("original_query", "")
            top_products = results.get("top_products", [])
            
            self.logger.info(f"Preparing presentation for {len(top_products)} products")
            
            # Format results for terminal display
            formatted_response = self._format_terminal_response(original_query, top_products)
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={
                    "formatted_response": formatted_response,
                    "raw_results": results
                },
                message_type="PRESENT_RESPONSE",
                conversation_id=message.conversation_id
            )
            
        except Exception as e:
            self.logger.error(f"Error formatting results: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Presentation error: {str(e)}"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
    
    def _format_terminal_response(self, query: str, products: List[Dict[str, Any]]) -> str:
        """
        Format products for terminal display.
        
        Args:
            query: The original user query
            products: List of product dictionaries to format
            
        Returns:
            Formatted string for terminal output
        """
        lines = []
        
        lines.append(f"🔍 Found {len(products)} great deals for: '{query}'")
        lines.append("")
        
        for i, product in enumerate(products, 1):
            title = product.get("title", "Unknown Product")
            price = product.get("price", 0)
            source = product.get("source", "Unknown Source")
            rating = product.get("rating", 0)
            url = product.get("url", "#")
            
            sponsored_label = " [SPONSORED]" if product.get("is_sponsored", False) else ""
            
            # Format price with additional information based on source
            price_info = f"${price:.2f}"
            
            # Add shipping information
            if "shipping" in product and product["shipping"] > 0:
                price_info += f" + ${product['shipping']:.2f} shipping"
            elif "shipping" in product and product["shipping"] == 0:
                price_info += " (Free shipping)"
            elif "is_free_shipping" in product and product["is_free_shipping"]:
                price_info += " (Free shipping)"
            
            # Add prime/pickup indicators
            if product.get("is_prime", False):
                price_info += " ✓ Prime"
            if product.get("is_pickup_today", False):
                price_info += " ✓ Pickup Today"
            
            # Format rating
            rating_display = "★" * int(rating) + "☆" * (5 - int(rating))
            if "reviews" in product:
                rating_display += f" ({product['reviews']} reviews)"
            
            # Add condition for eBay items
            condition_info = ""
            if "condition" in product:
                condition_info = f" • {product['condition']}"
            
            # Add seller rating for eBay
            seller_info = ""
            if "seller_rating" in product and product["seller_rating"] > 0:
                seller_info = f" • Seller: {product['seller_rating']}% positive"
            
            lines.append(f"{i}. {title}{sponsored_label}")
            lines.append(f"   💰 {price_info}{condition_info}")
            lines.append(f"   ⭐ {rating_display}{seller_info}")
            lines.append(f"   🏬 {source}: {url}")
            lines.append("")
        
        # Add a helpful prompt for the user
        if products:
            lines.append("Would you like more information about any of these products?")
            lines.append("You can also refine your search with more specific criteria.")
        else:
            lines.append("No deals found matching your criteria.")
            lines.append("Try broadening your search or using different keywords.")
        
        return "\n".join(lines)
    
    def _format_web_response(self, query: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format products for web interface display.
        
        Args:
            query: The original user query
            products: List of product dictionaries to format
            
        Returns:
            Formatted data for web interface
        """
        # This is a more structured format that can be used with the web UI
        formatted_products = []
        
        for product in products:
            # Format each product for web display
            formatted_product = {
                "title": product.get("title", "Unknown Product"),
                "price": product.get("price", 0),
                "formatted_price": f"${product.get('price', 0):.2f}",
                "source": product.get("source", "Unknown Source"),
                "url": product.get("url", "#"),
                "image_url": product.get("image_url", ""),
                "rating": product.get("rating", 0),
                "reviews": product.get("reviews", 0),
                "is_sponsored": product.get("is_sponsored", False),
            }
            
            # Add shipping information
            if "shipping" in product:
                formatted_product["shipping"] = product["shipping"]
                if product["shipping"] > 0:
                    formatted_product["shipping_display"] = f"+ ${product['shipping']:.2f} shipping"
                else:
                    formatted_product["shipping_display"] = "Free shipping"
            elif "is_free_shipping" in product and product["is_free_shipping"]:
                formatted_product["shipping_display"] = "Free shipping"
            
            # Add source-specific information
            if product.get("source") == "Amazon":
                formatted_product["is_prime"] = product.get("is_prime", False)
            elif product.get("source") == "Walmart":
                formatted_product["is_pickup_today"] = product.get("is_pickup_today", False)
            elif product.get("source") == "eBay":
                formatted_product["condition"] = product.get("condition", "Not specified")
                formatted_product["listing_type"] = product.get("listing_type", "")
                formatted_product["seller_rating"] = product.get("seller_rating", 0)
            
            formatted_products.append(formatted_product)
        
        return {
            "query": query,
            "products": formatted_products,
            "count": len(formatted_products)
        }