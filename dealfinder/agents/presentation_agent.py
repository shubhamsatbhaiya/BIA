"""
Presentation Agent for DealFinder AI.

This module implements the PresentationAgent class that formats results
for presentation to the user in a conversational format with product
comparison support and memory-aware responses.
"""

import logging
from typing import Dict, Any, List, Optional

from dealfinder.agents.base import Agent, MCPMessage
from dealfinder.utils.logging import get_logger

logger = get_logger("PresentationAgent")

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
            comparison_results = results.get("comparison_results", None)
            
            self.logger.info(f"Preparing presentation for {len(top_products)} products")
            
            # Format results for terminal display
            if comparison_results and comparison_results.get("best_deals", []):
                # Format results with comparison information
                formatted_response = self._format_comparison_response(
                    original_query, 
                    comparison_results.get("best_deals", []), 
                    top_products
                )
            else:
                # Format regular results without comparison
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
    
#     def _format_terminal_response(self, query: str, products: List[Dict[str, Any]]) -> str:
#         """
#         Format products for terminal display.
        
#         Args:
#             query: The original user query
#             products: List of product dictionaries to format
            
#         Returns:
#             Formatted string for terminal output
#         """
#         lines = []
        
#         lines.append(f"🔍 Found {len(products)} great deals for: '{query}'")
#         lines.append("")
        
#         for i, product in enumerate(products, 1):
#             title = product.get("title", "Unknown Product")
#             price = product.get("price", 0)
#             source = product.get("source", "Unknown Source")
#             rating = product.get("rating", 0)
#             url = product.get("url", "#")
            
#             sponsored_label = " [SPONSORED]" if product.get("is_sponsored", False) else ""
            
#             # Format price with additional information based on source
#             price_info = f"${price:.2f}"
            
#             # Add shipping information
#             if "shipping" in product and product["shipping"] > 0:
#                 price_info += f" + ${product['shipping']:.2f} shipping"
#             elif "shipping" in product and product["shipping"] == 0:
#                 price_info += " (Free shipping)"
#             elif "is_free_shipping" in product and product["is_free_shipping"]:
#                 price_info += " (Free shipping)"
            
#             # Add prime/pickup indicators
#             if product.get("is_prime", False):
#                 price_info += " ✓ Prime"
#             if product.get("is_pickup_today", False):
#                 price_info += " ✓ Pickup Today"
            
#             # Format rating
#             rating_display = "★" * int(rating) + "☆" * (5 - int(rating))
#             if "reviews" in product:
#                 rating_display += f" ({product['reviews']} reviews)"
            
#             # Add condition for eBay items
#             condition_info = ""
#             if "condition" in product:
#                 condition_info = f" • {product['condition']}"
            
#             # Add seller rating for eBay
#             seller_info = ""
#             if "seller_rating" in product and product["seller_rating"] > 0:
#                 seller_info = f" • Seller: {product['seller_rating']}% positive"
            
#             lines.append(f"{i}. {title}{sponsored_label}")
#             lines.append(f"   💰 {price_info}{condition_info}")
#             lines.append(f"   ⭐ {rating_display}{seller_info}")
#             lines.append(f"   🏬 {source}: <a href='{url}' target='_blank'>{url}</a>")
#             lines.append("")
        
#         # Add a helpful prompt for the user
#         if products:
#             lines.append("Would you like more information about any of these products?")
#             lines.append("You can ask follow-up questions like 'Tell me more about product 1' or 'Which one has the best reviews?'")
#         else:
#             lines.append("No deals found matching your criteria.")
#             lines.append("Try broadening your search or using different keywords.")
        
#         return "\n".join(lines)
    
#     """
# Fix for Product Price Display Issue in presentation_agent.py

# The issue is in the _format_comparison_response method, which is using placeholder values
# for prices instead of the actual product prices from the data.
# """

#     def _format_comparison_response(self, query: str, best_deals: List[Dict[str, Any]], all_products: List[Dict[str, Any]]) -> str:
#         """
#         Format products with comparison information.
        
#         Args:
#             query: The original user query
#             best_deals: List of best deals with comparison information
#             all_products: List of all products
            
#         Returns:
#             Formatted string for terminal output
#         """
#         lines = []
        
#         # Start with a header
#         lines.append(f"🔍 Found {len(all_products)} products for: '{query}'")
        
#         # Add comparison information if available
#         if best_deals:
#             lines.append("")
#             lines.append("💡 BEST DEAL COMPARISON 💡")
            
#             # Show the top 3 best deals (or fewer if there are fewer deals)
#             for i, deal in enumerate(best_deals[:3], 1):
#                 product = deal.get("product", {})
#                 similar_count = len(deal.get("similar_products", []))
#                 savings = deal.get("savings", 0)
#                 savings_percent = deal.get("savings_percent", 0)
#                 source_count = deal.get("source_count", 0)
                
#                 if not product:
#                     continue
                    
#                 title = product.get("title", "Unknown Product")
#                 price = product.get("price", 0)  # Get the actual price
#                 source = product.get("source", "Unknown Source")
                
#                 lines.append("")
#                 lines.append(f"🏆 DEAL #{i}: {title}")
                
#                 # Format price with the ACTUAL price value
#                 price_info = f"${price:.2f}"  # Make sure to use the correct price
#                 if "shipping" in product and product["shipping"] > 0:
#                     price_info += f" + ${product['shipping']:.2f} shipping"
#                 elif "shipping" in product and product["shipping"] == 0 or product.get("is_free_shipping", False):
#                     price_info += " (Free shipping)"
                
#                 # Add source-specific benefits
#                 if product.get("is_prime", False):
#                     price_info += " ✓ Prime"
#                 if product.get("is_pickup_today", False):
#                     price_info += " ✓ Pickup Today"
                
#                 # Add condition if available
#                 if "condition" in product:
#                     price_info += f" • {product['condition']}"
                
#                 lines.append(f"   💰 PRICE: {price_info}")
                
#                 # Add savings information
#                 if savings > 0 and savings_percent > 5:  # Only show significant savings
#                     lines.append(f"   💵 SAVINGS: ${savings:.2f} ({savings_percent:.1f}% below average price)")
                
#                 # Add comparison information
#                 if similar_count > 0:
#                     lines.append(f"   🔄 COMPARED WITH: {similar_count} similar product{'' if similar_count == 1 else 's'} across {source_count} site{'' if source_count == 1 else 's'}")
                
#                 # Add source and URL with proper HTML link formatting
#                 lines.append(f"   🏬 AVAILABLE AT: {source} - <a href='{product.get('url', '#')}' target='_blank'>{product.get('url', '#')}</a>")
            
#             lines.append("")
        
#         # Add all products
#         lines.append("")
#         lines.append("ALL PRODUCTS:")
#         lines.append("")
        
#         for i, product in enumerate(all_products, 1):
#             title = product.get("title", "Unknown Product")
#             price = product.get("price", 0)  # Get the actual price
#             source = product.get("source", "Unknown Source")
#             rating = product.get("rating", 0)
#             url = product.get("url", "#")
            
#             sponsored_label = " [SPONSORED]" if product.get("is_sponsored", False) else ""
            
#             # Format price with ACTUAL price value
#             price_info = f"${price:.2f}"  # Use the correct price
            
#             # Add shipping information
#             if "shipping" in product and product["shipping"] > 0:
#                 price_info += f" + ${product['shipping']:.2f} shipping"
#             elif "shipping" in product and product["shipping"] == 0:
#                 price_info += " (Free shipping)"
#             elif "is_free_shipping" in product and product["is_free_shipping"]:
#                 price_info += " (Free shipping)"
            
#             # Add prime/pickup indicators
#             if product.get("is_prime", False):
#                 price_info += " ✓ Prime"
#             if product.get("is_pickup_today", False):
#                 price_info += " ✓ Pickup Today"
            
#             # Format rating
#             rating_display = "★" * int(rating) + "☆" * (5 - int(rating))
#             if "reviews" in product:
#                 rating_display += f" ({product['reviews']} reviews)"
            
#             # Check if this product is one of the best deals
#             is_best_deal = False
#             deal_rank = 0
#             for j, deal in enumerate(best_deals[:3], 1):
#                 if product.get("title") == deal.get("product", {}).get("title") and product.get("source") == deal.get("product", {}).get("source"):
#                     is_best_deal = True
#                     deal_rank = j
#                     break
            
#             # Add best deal tag
#             best_deal_tag = f" 🏆 BEST DEAL #{deal_rank}" if is_best_deal else ""
            
#             lines.append(f"{i}. {title}{sponsored_label}{best_deal_tag}")
#             lines.append(f"   💰 {price_info}")
#             lines.append(f"   ⭐ {rating_display}")
#             lines.append(f"   🏬 {source}: <a href='{url}' target='_blank'>{url}</a>")
#             lines.append("")
        
#         # Add helpful prompts
#         lines.append("Would you like more information about any of these products?")
#         lines.append("You can ask follow-up questions like 'Tell me more about the best deal' or 'Which one has the best reviews?'")
        
#         return "\n".join(lines)
    """
    Updated PresentationAgent formatting methods to fix price display and URLs
    """

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
        
        # Debug log products to see what we're working with
        self.logger.info(f"Formatting {len(products)} products for display")
        
        # Add a search header with result count
        lines.append(f"🔍 Found {len(products)} products for: '{query}'")
        lines.append("")
        
        for i, product in enumerate(products, 1):
            title = product.get("title", "Unknown Product")
            source = product.get("source", "Unknown Source")
            url = product.get("url", "#")
            
            # Fix: Ensure price is a float for proper formatting
            try:
                price = float(product.get("price", 0))
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid price format in product: {title}")
                price = 0.0
                
            # Fix: Ensure rating is numeric
            try:
                rating = float(product.get("rating", 0))
            except (ValueError, TypeError):
                rating = 0
            
            # Debug log individual product info
            self.logger.info(f"Product {i}: {title} - Price: ${price:.2f} - Source: {source}")
            
            sponsored_label = " [SPONSORED]" if product.get("is_sponsored", False) else ""
            
            # Format price with additional information based on source
            price_info = f"${price:.2f}"
            
            # Add shipping information - ensure shipping is a float
            if "shipping" in product and product["shipping"] is not None:
                try:
                    shipping = float(product["shipping"])
                    if shipping > 0:
                        price_info += f" + ${shipping:.2f} shipping"
                    else:
                        price_info += " (Free shipping)"
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid shipping format for product: {title}")
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
                try:
                    reviews = int(product["reviews"])
                    rating_display += f" ({reviews} reviews)"
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid reviews format for product: {title}")
            
            # Add condition for eBay items
            condition_info = ""
            if "condition" in product:
                condition_info = f" • {product['condition']}"
            
            # Add seller rating for eBay
            seller_info = ""
            if "seller_rating" in product and product["seller_rating"] > 0:
                try:
                    seller_rating = float(product["seller_rating"])
                    seller_info = f" • Seller: {seller_rating}% positive"
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid seller rating format for product: {title}")
            
            lines.append(f"{i}. {title}{sponsored_label}")
            lines.append(f"   💰 {price_info}{condition_info}")
            lines.append(f"   ⭐ {rating_display}{seller_info}")
            lines.append(f"   🏬 {source}: <a href='{url}' target='_blank'>{url}</a>")
            lines.append("")
        
        # Add a helpful prompt for the user
        if products:
            lines.append("Would you like more information about any of these products?")
            lines.append("You can ask follow-up questions like 'Tell me more about product 1' or 'Which one has the best reviews?'")
        else:
            lines.append("No deals found matching your criteria.")
            lines.append("Try broadening your search or using different keywords.")
        
        return "\n".join(lines)

    def _format_comparison_response(self, query: str, best_deals: List[Dict[str, Any]], all_products: List[Dict[str, Any]]) -> str:
        """
        Format products with comparison information.
        
        Args:
            query: The original user query
            best_deals: List of best deals with comparison information
            all_products: List of all products
            
        Returns:
            Formatted string for terminal output
        """
        lines = []
        
        # Start with a header
        lines.append(f"🔍 Found {len(all_products)} products for: '{query}'")
        
        # Add comparison information if available
        if best_deals:
            lines.append("")
            lines.append("💡 BEST DEAL COMPARISON 💡")
            
            # Show the top 3 best deals (or fewer if there are fewer deals)
            for i, deal in enumerate(best_deals[:3], 1):
                product = deal.get("product", {})
                similar_count = len(deal.get("similar_products", []))
                savings = deal.get("savings", 0)
                savings_percent = deal.get("savings_percent", 0)
                source_count = deal.get("source_count", 0)
                
                if not product:
                    continue
                    
                title = product.get("title", "Unknown Product")
                source = product.get("source", "Unknown Source")
                url = product.get("url", "#")
                
                # Fix: Ensure price is a float for proper formatting
                try:
                    price = float(product.get("price", 0))
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid price format in best deal: {title}")
                    price = 0.0
                
                lines.append("")
                lines.append(f"🏆 DEAL #{i}: {title}")
                
                # Format price with the ACTUAL price value
                price_info = f"${price:.2f}"  # Make sure to use the correct price
                
                # Add shipping information - ensure shipping is a float
                if "shipping" in product and product["shipping"] is not None:
                    try:
                        shipping = float(product["shipping"])
                        if shipping > 0:
                            price_info += f" + ${shipping:.2f} shipping"
                        else:
                            price_info += " (Free shipping)"
                    except (ValueError, TypeError):
                        self.logger.warning(f"Invalid shipping format in best deal: {title}")
                elif "is_free_shipping" in product and product["is_free_shipping"]:
                    price_info += " (Free shipping)"
                
                # Add source-specific benefits
                if product.get("is_prime", False):
                    price_info += " ✓ Prime"
                if product.get("is_pickup_today", False):
                    price_info += " ✓ Pickup Today"
                
                # Add condition if available
                if "condition" in product:
                    price_info += f" • {product['condition']}"
                
                lines.append(f"   💰 PRICE: {price_info}")
                
                # Add savings information
                if savings > 0 and savings_percent > 5:  # Only show significant savings
                    lines.append(f"   💵 SAVINGS: ${savings:.2f} ({savings_percent:.1f}% below average price)")
                
                # Add comparison information
                if similar_count > 0:
                    lines.append(f"   🔄 COMPARED WITH: {similar_count} similar product{'' if similar_count == 1 else 's'} across {source_count} site{'' if source_count == 1 else 's'}")
                
                # Add source and URL with proper HTML link formatting
                lines.append(f"   🏬 AVAILABLE AT: {source} - <a href='{url}' target='_blank'>{url}</a>")
            
            lines.append("")
        
        # Add all products
        lines.append("")
        lines.append("ALL PRODUCTS:")
        lines.append("")
        
        for i, product in enumerate(all_products, 1):
            title = product.get("title", "Unknown Product")
            source = product.get("source", "Unknown Source")
            url = product.get("url", "#")
            
            # Fix: Ensure price is a float for proper formatting
            try:
                price = float(product.get("price", 0))
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid price format in product: {title}")
                price = 0.0
                
            # Fix: Ensure rating is numeric
            try:
                rating = float(product.get("rating", 0))
            except (ValueError, TypeError):
                rating = 0
            
            sponsored_label = " [SPONSORED]" if product.get("is_sponsored", False) else ""
            
            # Format price with ACTUAL price value
            price_info = f"${price:.2f}"  # Use the correct price
            
            # Add shipping information - ensure shipping is a float
            if "shipping" in product and product["shipping"] is not None:
                try:
                    shipping = float(product["shipping"])
                    if shipping > 0:
                        price_info += f" + ${shipping:.2f} shipping"
                    else:
                        price_info += " (Free shipping)"
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid shipping format in product: {title}")
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
                try:
                    reviews = int(product["reviews"])
                    rating_display += f" ({reviews} reviews)"
                except (ValueError, TypeError):
                    pass
            
            # Check if this product is one of the best deals
            is_best_deal = False
            deal_rank = 0
            for j, deal in enumerate(best_deals[:3], 1):
                deal_product = deal.get("product", {})
                if product.get("title") == deal_product.get("title") and product.get("source") == deal_product.get("source"):
                    is_best_deal = True
                    deal_rank = j
                    break
            
            # Add best deal tag
            best_deal_tag = f" 🏆 BEST DEAL #{deal_rank}" if is_best_deal else ""
            
            lines.append(f"{i}. {title}{sponsored_label}{best_deal_tag}")
            lines.append(f"   💰 {price_info}")
            lines.append(f"   ⭐ {rating_display}")
            lines.append(f"   🏬 {source}: <a href='{url}' target='_blank'>{url}</a>")
            lines.append("")
        
        # Add helpful prompts
        lines.append("Would you like more information about any of these products?")
        lines.append("You can ask follow-up questions like 'Tell me more about the best deal' or 'Which one has the best reviews?'")
        
        return "\n".join(lines)

    def _format_web_response(self, query: str, products: List[Dict[str, Any]], best_deals: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Format products for web interface display.
        
        Args:
            query: The original user query
            products: List of product dictionaries to format
            best_deals: Optional list of best deals with comparison information
            
        Returns:
            Formatted data for web interface
        """
        # This is a more structured format that can be used with the web UI
        formatted_products = []
        
        for product in products:
            # Format each product for web display
            # Fix: Ensure price is a float
            try:
                price = float(product.get("price", 0))
                formatted_price = f"${price:.2f}"
            except (ValueError, TypeError):
                price = 0.0
                formatted_price = "$0.00"
                
            formatted_product = {
                "title": product.get("title", "Unknown Product"),
                "price": price,
                "formatted_price": formatted_price,
                "source": product.get("source", "Unknown Source"),
                "url": product.get("url", "#"),
                "image_url": product.get("image_url", ""),
                "rating": product.get("rating", 0),
                "reviews": product.get("reviews", 0),
                "is_sponsored": product.get("is_sponsored", False),
            }
            
            # Add shipping information
            if "shipping" in product:
                try:
                    shipping = float(product["shipping"])
                    formatted_product["shipping"] = shipping
                    if shipping > 0:
                        formatted_product["shipping_display"] = f"+ ${shipping:.2f} shipping"
                    else:
                        formatted_product["shipping_display"] = "Free shipping"
                except (ValueError, TypeError):
                    formatted_product["shipping_display"] = ""
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
            
            # Check if this product is one of the best deals
            if best_deals:
                for i, deal in enumerate(best_deals, 1):
                    deal_product = deal.get("product", {})
                    if product.get("title") == deal_product.get("title") and product.get("source") == deal_product.get("source"):
                        formatted_product["is_best_deal"] = True
                        formatted_product["deal_rank"] = i
                        
                        # Ensure savings are floats
                        try:
                            savings = float(deal.get("savings", 0))
                            savings_percent = float(deal.get("savings_percent", 0))
                        except (ValueError, TypeError):
                            savings = 0.0
                            savings_percent = 0.0
                            
                        formatted_product["savings"] = savings
                        formatted_product["savings_percent"] = savings_percent
                        break
            
            formatted_products.append(formatted_product)
        
        # Create the response
        response = {
            "query": query,
            "products": formatted_products,
            "count": len(formatted_products),
            "has_best_deals": best_deals is not None and len(best_deals) > 0
        }
        
        # Add best deals information if available
        if best_deals and len(best_deals) > 0:
            response["best_deals"] = []
            for i, deal in enumerate(best_deals[:3], 1):
                product = deal.get("product", {})
                if not product:
                    continue
                
                # Ensure price is a float
                try:
                    price = float(product.get("price", 0))
                    formatted_price = f"${price:.2f}"
                except (ValueError, TypeError):
                    price = 0.0
                    formatted_price = "$0.00"
                    
                # Ensure savings are floats
                try:
                    savings = float(deal.get("savings", 0))
                    savings_percent = float(deal.get("savings_percent", 0))
                except (ValueError, TypeError):
                    savings = 0.0
                    savings_percent = 0.0
                
                response["best_deals"].append({
                    "title": product.get("title", "Unknown Product"),
                    "price": price,
                    "formatted_price": formatted_price,
                    "source": product.get("source", "Unknown Source"),
                    "url": product.get("url", "#"),
                    "savings": savings,
                    "savings_percent": savings_percent,
                    "similar_count": len(deal.get("similar_products", [])),
                    "source_count": deal.get("source_count", 0),
                    "rank": i
                })
        
        return response

    """
    Fix for Product Price Display in the _handle_follow_up method in controller.py

    We need to ensure follow-up questions properly display actual prices.
    """

    def _handle_follow_up(self, query: str, referenced_products: List[Dict[str, Any]], conversation_id: str) -> str:
        """
        Handle follow-up questions about specific products.
        
        Args:
            query: The follow-up query
            referenced_products: List of products being referenced
            conversation_id: Conversation ID for this interaction
            
        Returns:
            A formatted response to the follow-up question
        """
        try:
            self.logger.info(f"Handling follow-up question: {query}")
            self.logger.info(f"Referenced products: {len(referenced_products)}")
            
            # Update focus to this product
            product = referenced_products[0] if referenced_products else None
            if not product:
                return "I'm sorry, I couldn't find any products to tell you about. Could you try a new search?"
            
            # Extract product index if available (for better reference)
            product_index = 0
            
            # Update focus to this product
            update_focus_message = MCPMessage(
                sender="Controller",
                receiver="ChatMemoryAgent",
                content={"product_index": product_index},
                message_type="MEMORY_UPDATE_FOCUS",
                conversation_id=conversation_id
            )
            self.chat_memory_agent.process_message(update_focus_message)
            
            # Generate a detailed response using Gemini
            # Create a prompt with the product details and the follow-up query
            # Ensure all fields are properly formatted in the product details
            
            # Make sure the product has the correct price format
            price = product.get("price", 0)
            if isinstance(price, (int, float)):
                formatted_price = f"${price:.2f}"
                # Update the product object to include the formatted price
                product_with_formatted_price = product.copy()
                product_with_formatted_price["formatted_price"] = formatted_price
                product_details = json.dumps(product_with_formatted_price, indent=2)
            else:
                product_details = json.dumps(product, indent=2)
            
            prompt = f"""
            I'm a shopping assistant helping a customer with product information.
            
            The customer previously searched for products and is now asking a follow-up question: "{query}"
            
            They're referring to this product:
            {product_details}
            
            Please provide a helpful, conversational response addressing their question
            about this specific product. Include relevant details from the product information.
            
            Important guidelines:
            1. Always format prices as exact dollar amounts (e.g., "$7.25" not "$1")
            2. Format URLs as clickable HTML links <a href="url">url</a>
            3. If the product has a price field, be sure to mention the exact price as shown in the data
            4. Be accurate about the product details - don't make up information not in the data
            5. If the product is a "best deal", explain why it's a good value
            
            Your response should be conversational but accurate, highlighting the actual price 
            and key product features. Don't create fake discounts or savings.
            """
            
            response_message = MCPMessage(
                sender="Controller",
                receiver="GeminiAgent",
                content=prompt,
                message_type="REQUEST",
                conversation_id=conversation_id
            )
            
            response = self.gemini_agent.process_message(response_message)
            self.conversation_history[conversation_id].append((response_message, response))
            
            if response.message_type == "ERROR":
                return f"I'm sorry, I couldn't process your follow-up question. {response.content.get('error', '')}"
            
            # Return the formatted response
            return response.content
            
        except Exception as e:
            self.logger.error(f"Error handling follow-up: {str(e)}")
            return f"I'm sorry, I had trouble understanding your follow-up question. Could you try asking in a different way?"

    """
    Fix for the ProductComparisonAgent to ensure it correctly calculates savings
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
                
            # Calculate "effective price" considering shipping, Prime benefits, etc.
            for product in group:
                # Ensure price is a float
                price = float(product.get("price", 0))
                effective_price = price
                
                # Add shipping cost if not free
                if "shipping" in product and product["shipping"] > 0:
                    effective_price += product["shipping"]
                
                # Apply small discount for Prime/pickup benefits
                if product.get("is_prime", False) or product.get("is_pickup_today", False):
                    effective_price *= 0.98  # 2% discount for convenience
                
                # Penalize slightly for lower ratings or fewer reviews
                if "rating" in product and product["rating"] > 0:
                    rating_factor = min(1.0, product["rating"] / 5.0)
                    reviews = product.get("reviews", 0)
                    review_factor = min(1.0, reviews / 1000) if reviews > 0 else 0.5
                    
                    # Small adjustment based on rating and reviews (max 5%)
                    rating_adjustment = 1.0 - ((rating_factor * review_factor) * 0.05)
                    effective_price *= rating_adjustment
                
                product["effective_price"] = effective_price
            
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
                
                # Ensure the best deal has the correct price type
                if "price" in best_deal:
                    best_deal["price"] = float(best_deal["price"])
                
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