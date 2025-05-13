"""
Chat Memory Agent for DealFinder AI.

This module implements the ChatMemoryAgent class that stores conversation history
and enables follow-up questions about products.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dealfinder.agents.gemini_agent import GeminiAgent
from dealfinder.agents.base import Agent, MCPMessage
from dealfinder.utils.logging import get_logger

logger = get_logger("ChatMemory")

class ChatMemoryAgent(Agent):
    """Agent for storing conversation history and enabling context-aware responses"""
    
    def __init__(self):
        """Initialize the Chat Memory agent."""
        super().__init__("ChatMemoryAgent")
        
        # Store conversation context by conversation ID
        self.conversation_contexts = {}
        
        # Store product information by conversation ID
        self.product_info = {}
        
        # Track recent queries by conversation ID
        self.recent_queries = {}
        
        # Track currently viewed product
        self.focused_products = {}
    
    def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Process memory-related operations.
        
        Args:
            message: The MCPMessage to process
            
        Returns:
            A new MCPMessage containing the response
        """
        conversation_id = message.conversation_id
        
        if message.message_type == "MEMORY_STORE":
            # Store conversation context and product info
            return self._store_context(message)
        
        elif message.message_type == "MEMORY_RETRIEVE":
            # Retrieve conversation context and product info
            return self._retrieve_context(message)
        
        elif message.message_type == "MEMORY_ANALYZE":
            # Analyze if a query is related to previous products
            return self._analyze_query(message)
        
        elif message.message_type == "MEMORY_UPDATE_FOCUS":
            # Update which product is currently in focus
            return self._update_focus(message)
        
        else:
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Unsupported message type: {message.message_type}"},
                message_type="ERROR",
                conversation_id=conversation_id
            )
    
    def _retrieve_context(self, message: MCPMessage) -> MCPMessage:
        """
        Retrieve conversation context and product information.
        
        Args:
            message: The MCPMessage containing retrieval request
            
        Returns:
            A new MCPMessage containing the context information
        """
        try:
            conversation_id = message.conversation_id
            
            # Gather all context information
            context_data = {
                "recent_queries": self.recent_queries.get(conversation_id, []),
                "product_info": self.product_info.get(conversation_id, []),
                "conversation_context": self.conversation_contexts.get(conversation_id, {}),
                "focused_product": self.focused_products.get(conversation_id, None)
            }
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content=context_data,
                message_type="MEMORY_RETRIEVE_RESPONSE",
                conversation_id=conversation_id
            )
            
        except Exception as e:
            self.logger.error(f"Error retrieving context: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Context retrieval error: {str(e)}"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
    
    """
Fix for the ChatMemoryAgent class to properly analyze follow-up questions.
The issue is that the agent isn't properly detecting follow-up questions or
storing/retrieving conversation context.
"""

    # def _analyze_query(self, message: MCPMessage) -> MCPMessage:
    #     """
    #     Analyze if a query is related to previous products.
        
    #     Args:
    #         message: The MCPMessage containing the query to analyze
            
    #     Returns:
    #         A new MCPMessage containing the analysis results
    #     """
    #     try:
    #         conversation_id = message.conversation_id
    #         query = message.content.get("query", "").lower()
            
    #         # Add detailed logging for debugging
    #         self.logger.info(f"Analyzing query: '{query}' for conversation {conversation_id}")
    #         self.logger.info(f"Current product info: {conversation_id in self.product_info}")
    #         if conversation_id in self.product_info:
    #             self.logger.info(f"Number of products in memory: {len(self.product_info[conversation_id])}")
            
    #         # Check if there are products to reference
    #         if conversation_id not in self.product_info or not self.product_info[conversation_id]:
    #             self.logger.info("No product context available for this conversation")
    #             return MCPMessage(
    #                 sender=self.name,
    #                 receiver=message.sender,
    #                 content={
    #                     "is_follow_up": False,
    #                     "focused_product": None,
    #                     "referenced_products": [],
    #                     "products": []
    #                 },
    #                 message_type="MEMORY_ANALYZE_RESPONSE",
    #                 conversation_id=conversation_id
    #             )
            
    #         # List of products currently stored
    #         products = self.product_info[conversation_id]
    #         self.logger.info(f"Found {len(products)} products in memory")
            
    #         # Current focused product (if any)
    #         focused_product = self.focused_products.get(conversation_id, None)
            
    #         # More extensive list of follow-up phrases
    #         follow_up_phrases = [
    #             "more info", "tell me more", "more details", "specs", "specifications",
    #             "reviews", "ratings", "shipping", "delivery", "warranty", "features",
    #             "cheaper", "better", "price", "discount", "deal", "best deal", "cheapest",
    #             "compare", "difference", "vs", "versus", "which one", "which is", "how is",
    #             "about product", "about item", "about the", "what about", "first one", "second one",
    #             "best one", "top pick", "option"
    #         ]
            
    #         # Check if query contains references to specific products
    #         referenced_products = []
            
    #         # Check for direct product number references like "product 1", "first product", etc.
    #         number_words = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]
    #         product_refs = re.findall(r"(?:product|item|option|deal)\s+#?(\d+)", query)
    #         number_refs = re.findall(r"(\d+)(?:st|nd|rd|th)\s+(?:product|item|option)", query)
    #         word_refs = [word for word in number_words if word in query]
            
    #         # Add special cases for "best deal" or similar phrases
    #         best_deal_ref = re.search(r"best\s+(?:deal|option|choice|product|one)", query) is not None
            
    #         # Convert all references to zero-based indices
    #         indices = []
    #         for ref in product_refs:
    #             try:
    #                 index = int(ref) - 1  # Convert to zero-based
    #                 if 0 <= index < len(products):
    #                     indices.append(index)
    #             except ValueError:
    #                 pass
            
    #         for ref in number_refs:
    #             try:
    #                 index = int(ref) - 1  # Convert to zero-based
    #                 if 0 <= index < len(products):
    #                     indices.append(index)
    #             except ValueError:
    #                 pass
            
    #         for word in word_refs:
    #             try:
    #                 index = number_words.index(word)
    #                 if 0 <= index < len(products):
    #                     indices.append(index)
    #             except ValueError:
    #                 pass
            
    #         # Handle "best deal" references - assume it's the first product if sorted by best deal
    #         if best_deal_ref and len(products) > 0:
    #             indices.append(0)  # First product is likely the best deal
            
    #         # Get referenced products
    #         for index in indices:
    #             if 0 <= index < len(products):
    #                 referenced_products.append(products[index])
            
    #         # If no direct references but there's a focused product,
    #         # consider the query to be about that product
    #         if not referenced_products and focused_product is not None:
    #             if 0 <= focused_product < len(products):
    #                 referenced_products = [products[focused_product]]
    #                 self.logger.info(f"Using focused product: {focused_product}")
            
    #         # If still no referenced products but talking about products in general,
    #         # assume they're talking about the first product
    #         if not referenced_products and len(products) > 0 and (
    #             "product" in query or "item" in query or "it" in query or "this" in query
    #         ):
    #             referenced_products = [products[0]]
    #             self.logger.info("Defaulting to first product based on generic reference")
            
    #         # Determine if this is a follow-up question
    #         is_follow_up = False
            
    #         # Check for follow-up phrases
    #         is_follow_up = any(phrase in query for phrase in follow_up_phrases)
            
    #         # Also check for pronoun references that likely refer to previous products
    #         if not is_follow_up:
    #             pronoun_refs = re.search(r"\b(it|this|that|these|those|they|them)\b", query)
    #             is_follow_up = pronoun_refs is not None
            
    #         # For very short queries, likely follow-ups
    #         if not is_follow_up and len(query.split()) <= 5:
    #             is_follow_up = True
            
    #         # If we have referenced products, it's definitely a follow-up
    #         if referenced_products:
    #             is_follow_up = True
            
    #         self.logger.info(f"Follow-up analysis: {is_follow_up}, Referenced products: {len(referenced_products)}")
            
    #         # If no specific products referenced but it's a follow-up,
    #         # include all products for context
    #         if is_follow_up and not referenced_products and products:
    #             all_products = products
    #         else:
    #             all_products = products if is_follow_up else []
            
    #         return MCPMessage(
    #             sender=self.name,
    #             receiver=message.sender,
    #             content={
    #                 "is_follow_up": is_follow_up,
    #                 "focused_product": focused_product,
    #                 "referenced_products": referenced_products,
    #                 "products": all_products
    #             },
    #             message_type="MEMORY_ANALYZE_RESPONSE",
    #             conversation_id=conversation_id
    #         )
            
    #     except Exception as e:
    #         self.logger.error(f"Error analyzing query: {str(e)}")
    #         return MCPMessage(
    #             sender=self.name,
    #             receiver=message.sender,
    #             content={"error": f"Query analysis error: {str(e)}"},
    #             message_type="ERROR",
    #             conversation_id=message.conversation_id
    #         )
    """
Fix 2: Improve follow-up question handling in chat_memory_agent.py

Enhance the _analyze_query method to better identify follow-up questions and
detect product references.
"""

    # def _analyze_query(self, message: MCPMessage) -> MCPMessage:
    #     """
    #     Analyze if a query is related to previous products.
        
    #     Args:
    #         message: The MCPMessage containing the query to analyze
            
    #     Returns:
    #         A new MCPMessage containing the analysis results
    #     """
    #     try:
    #         conversation_id = message.conversation_id
    #         query = message.content.get("query", "").lower()
            
    #         # Add detailed logging for debugging
    #         self.logger.info(f"Analyzing query: '{query}' for conversation {conversation_id}")
    #         self.logger.info(f"Current product info: {conversation_id in self.product_info}")
    #         if conversation_id in self.product_info:
    #             self.logger.info(f"Number of products in memory: {len(self.product_info[conversation_id])}")
            
    #         # Check if there are products to reference
    #         if conversation_id not in self.product_info or not self.product_info[conversation_id]:
    #             self.logger.info("No product context available for this conversation")
    #             return MCPMessage(
    #                 sender=self.name,
    #                 receiver=message.sender,
    #                 content={
    #                     "is_follow_up": False,
    #                     "focused_product": None,
    #                     "referenced_products": [],
    #                     "products": []
    #                 },
    #                 message_type="MEMORY_ANALYZE_RESPONSE",
    #                 conversation_id=conversation_id
    #             )
            
    #         # List of products currently stored
    #         products = self.product_info[conversation_id]
    #         self.logger.info(f"Found {len(products)} products in memory")
            
    #         # Current focused product (if any)
    #         focused_product = self.focused_products.get(conversation_id, None)
            
    #         # Expanded list of follow-up patterns
    #         follow_up_phrases = [
    #             "more info", "tell me more", "more details", "specifications", "specs",
    #             "reviews", "ratings", "shipping", "delivery", "warranty", "features",
    #             "cheaper", "better", "price", "discount", "deal", "best deal", "cheapest",
    #             "compare", "difference", "vs", "versus", "which one", "which is", "how is",
    #             "about product", "about item", "about the", "what about", "first one", "second one",
    #             "best one", "top pick", "option", "tell me about", "more about"
    #         ]
            
    #         # Check if query contains any product-specific keywords
    #         query_keywords = set(query.split())
            
    #         # Check if direct brand names are mentioned
    #         brand_mentions = []
    #         common_brands = ["sony", "bose", "apple", "samsung", "lg", "beats", "sennheiser", 
    #                         "amazon", "walmart", "ebay", "target", "best buy"]
            
    #         for brand in common_brands:
    #             if brand in query:
    #                 brand_mentions.append(brand)
            
    #         # Check for direct product number references like "product 1", "first product", etc.
    #         number_words = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]
    #         product_refs = re.findall(r"(?:product|item|option|deal)\s+#?(\d+)", query)
    #         number_refs = re.findall(r"(\d+)(?:st|nd|rd|th)\s+(?:product|item|option)", query)
    #         word_refs = [word for word in number_words if word in query]
            
    #         # Add special cases for "best deal" or similar phrases
    #         best_deal_ref = re.search(r"best\s+(?:deal|option|choice|product|one)", query) is not None
            
    #         # Find keyword matches between products and query
    #         referenced_products = []
    #         keyword_matches = {}
            
    #         # When this is a new query with specific brand/product mentioned (NOT a follow up)
    #         if not any(phrase in query for phrase in follow_up_phrases) and brand_mentions:
    #             # This is a NEW search query, NOT a follow-up
    #             self.logger.info(f"This appears to be a new search with brands: {brand_mentions}")
    #             return MCPMessage(
    #                 sender=self.name,
    #                 receiver=message.sender,
    #                 content={
    #                     "is_follow_up": False,
    #                     "focused_product": None,
    #                     "referenced_products": [],
    #                     "products": []
    #                 },
    #                 message_type="MEMORY_ANALYZE_RESPONSE",
    #                 conversation_id=conversation_id
    #             )
            
    #         # Convert all references to zero-based indices
    #         indices = []
    #         for ref in product_refs:
    #             try:
    #                 index = int(ref) - 1  # Convert to zero-based
    #                 if 0 <= index < len(products):
    #                     indices.append(index)
    #             except ValueError:
    #                 pass
            
    #         for ref in number_refs:
    #             try:
    #                 index = int(ref) - 1  # Convert to zero-based
    #                 if 0 <= index < len(products):
    #                     indices.append(index)
    #             except ValueError:
    #                 pass
            
    #         for word in word_refs:
    #             try:
    #                 index = number_words.index(word)
    #                 if 0 <= index < len(products):
    #                     indices.append(index)
    #             except ValueError:
    #                 pass
            
    #         # Handle "best deal" references - assume it's the first product if sorted by best deal
    #         if best_deal_ref and len(products) > 0:
    #             indices.append(0)  # First product is likely the best deal
            
    #         # Get referenced products by index
    #         for index in indices:
    #             if 0 <= index < len(products):
    #                 referenced_products.append(products[index])
            
    #         # If no direct references but there's a focused product,
    #         # consider the query to be about that product
    #         if not referenced_products and focused_product is not None:
    #             if 0 <= focused_product < len(products):
    #                 referenced_products = [products[focused_product]]
    #                 self.logger.info(f"Using focused product: {focused_product}")
            
    #         # If still no referenced products but talking about products in general,
    #         # assume they're talking about the first product
    #         if not referenced_products and len(products) > 0 and (
    #             "product" in query or "item" in query or "it" in query or "this" in query
    #         ):
    #             referenced_products = [products[0]]
    #             self.logger.info("Defaulting to first product based on generic reference")
            
    #         # Determine if this is a follow-up question
    #         is_follow_up = False
            
    #         # Check for follow-up phrases
    #         is_follow_up = any(phrase in query for phrase in follow_up_phrases)
            
    #         # Also check for pronoun references that likely refer to previous products
    #         if not is_follow_up:
    #             pronoun_refs = re.search(r"\b(it|this|that|these|those|they|them)\b", query)
    #             is_follow_up = pronoun_refs is not None
            
    #         # For very short queries, likely follow-ups
    #         if not is_follow_up and len(query.split()) <= 5:
    #             is_follow_up = True
            
    #         # If we have referenced products, it's definitely a follow-up
    #         if referenced_products:
    #             is_follow_up = True
            
    #         self.logger.info(f"Follow-up analysis: {is_follow_up}, Referenced products: {len(referenced_products)}")
            
    #         # If no specific products referenced but it's a follow-up,
    #         # include all products for context
    #         if is_follow_up and not referenced_products and products:
    #             all_products = products
    #         else:
    #             all_products = products if is_follow_up else []
            
    #         return MCPMessage(
    #             sender=self.name,
    #             receiver=message.sender,
    #             content={
    #                 "is_follow_up": is_follow_up,
    #                 "focused_product": focused_product,
    #                 "referenced_products": referenced_products,
    #                 "products": all_products
    #             },
    #             message_type="MEMORY_ANALYZE_RESPONSE",
    #             conversation_id=conversation_id
    #         )
            
    #     except Exception as e:
    #         self.logger.error(f"Error analyzing query: {str(e)}")
    #         return MCPMessage(
    #             sender=self.name,
    #             receiver=message.sender,
    #             content={"error": f"Query analysis error: {str(e)}"},
    #             message_type="ERROR",
    #             conversation_id=message.conversation_id
    #         )

    # def _store_context(self, message: MCPMessage) -> MCPMessage:
    #     """
    #     Store conversation context and product information.
        
    #     Args:
    #         message: The MCPMessage containing context to store
            
    #     Returns:
    #         A new MCPMessage indicating success or failure
    #     """
    #     try:
    #         conversation_id = message.conversation_id
    #         content = message.content
            
    #         self.logger.info(f"Storing context for conversation {conversation_id}")
            
    #         # Store original query
    #         if "query" in content:
    #             if conversation_id not in self.recent_queries:
    #                 self.recent_queries[conversation_id] = []
                
    #             # Add to recent queries (keep last 5)
    #             self.recent_queries[conversation_id].append({
    #                 "query": content["query"],
    #                 "timestamp": datetime.now().isoformat(),
    #                 "search_params": content.get("search_params", {})
    #             })
                
    #             # Trim to last 5 queries
    #             if len(self.recent_queries[conversation_id]) > 5:
    #                 self.recent_queries[conversation_id] = self.recent_queries[conversation_id][-5:]
            
    #         # Store product information
    #         if "products" in content:
    #             products = content["products"]
    #             self.logger.info(f"Storing {len(products)} products for conversation {conversation_id}")
                
    #             # Initialize if not exists
    #             if conversation_id not in self.product_info:
    #                 self.product_info[conversation_id] = []
                
    #             # Add to product info (replace existing products)
    #             self.product_info[conversation_id] = products
    #         else:
    #             self.logger.warning("No products found in the message content")
            
    #         # Store context information
    #         if "context" in content:
    #             self.conversation_contexts[conversation_id] = content["context"]
            
    #         return MCPMessage(
    #             sender=self.name,
    #             receiver=message.sender,
    #             content={"status": "success"},
    #             message_type="MEMORY_STORE_RESPONSE",
    #             conversation_id=conversation_id
    #         )
            
    #     except Exception as e:
    #         self.logger.error(f"Error storing context: {str(e)}")
    #         return MCPMessage(
    #             sender=self.name,
    #             receiver=message.sender,
    #             content={"error": f"Context storage error: {str(e)}"},
    #             message_type="ERROR",
    #             conversation_id=message.conversation_id
    #         )
    """
    Updated ChatMemoryAgent with Enhanced Follow-Up Detection
    """

    def _legacy_analyze_query(self, message: MCPMessage) -> MCPMessage:
        """
        Analyze if a query is related to previous products.
        
        Args:
            message: The MCPMessage containing the query to analyze
            
        Returns:
            A new MCPMessage containing the analysis results
        """
        try:
            conversation_id = message.conversation_id
            query = message.content.get("query", "").lower()
            
            # Add detailed logging for debugging
            self.logger.info(f"Analyzing query: '{query}' for conversation {conversation_id}")
            self.logger.info(f"Current product info: {conversation_id in self.product_info}")
            if conversation_id in self.product_info:
                self.logger.info(f"Number of products in memory: {len(self.product_info[conversation_id])}")
            
            # Check if there are products to reference
            if conversation_id not in self.product_info or not self.product_info[conversation_id]:
                self.logger.info("No product context available for this conversation")
                return MCPMessage(
                    sender=self.name,
                    receiver=message.sender,
                    content={
                        "is_follow_up": False,
                        "focused_product": None,
                        "referenced_products": [],
                        "products": []
                    },
                    message_type="MEMORY_ANALYZE_RESPONSE",
                    conversation_id=conversation_id
                )
            
            # List of products currently stored
            products = self.product_info[conversation_id]
            self.logger.info(f"Found {len(products)} products in memory")
            
            # Current focused product (if any)
            focused_product = self.focused_products.get(conversation_id, None)
            
            # Expanded list of follow-up patterns
            follow_up_phrases = [
                "more info", "tell me more", "more details", "specifications", "specs",
                "reviews", "ratings", "shipping", "delivery", "warranty", "features",
                "cheaper", "better", "price", "discount", "deal", "best deal", "cheapest",
                "compare", "difference", "vs", "versus", "which one", "which is", "how is",
                "about product", "about item", "about the", "what about", "first one", "second one",
                "best one", "top pick", "option", "tell me about", "more about"
            ]
            
            # Check if query contains any product-specific keywords
            query_keywords = set(query.split())
            
            # Check if direct brand names are mentioned
            brand_mentions = []
            common_brands = ["sony", "bose", "apple", "samsung", "lg", "beats", "sennheiser", 
                            "amazon", "walmart", "ebay", "target", "best buy"]
            
            for brand in common_brands:
                if brand in query:
                    brand_mentions.append(brand)
            
            # Keywords that indicate specific types of searches
            specific_search_keywords = ["find", "search", "looking for", "show me", "latest"]
            
            # If this appears to be a specific new search, don't treat as follow-up
            if any(keyword in query for keyword in specific_search_keywords) and len(query.split()) > 3:
                # Check if this might be a new search rather than a follow-up
                if "latest" in query or "new" in query:
                    self.logger.info("Query appears to be a new search with 'latest' or 'new'")
                    return MCPMessage(
                        sender=self.name,
                        receiver=message.sender,
                        content={
                            "is_follow_up": False,
                            "focused_product": None,
                            "referenced_products": [],
                            "products": []
                        },
                        message_type="MEMORY_ANALYZE_RESPONSE",
                        conversation_id=conversation_id
                    )
            
            # Check for direct product number references like "product 1", "first product", etc.
            number_words = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]
            product_refs = re.findall(r"(?:product|item|option|deal)\s+#?(\d+)", query)
            number_refs = re.findall(r"(\d+)(?:st|nd|rd|th)\s+(?:product|item|option)", query)
            word_refs = [word for word in number_words if word in query]
            
            # Add special cases for "best deal" or similar phrases
            best_deal_ref = re.search(r"best\s+(?:deal|option|choice|product|one)", query) is not None
            
            # Find keyword matches between products and query
            referenced_products = []
            keyword_matches = {}
            
            # Convert all references to zero-based indices
            indices = []
            for ref in product_refs:
                try:
                    index = int(ref) - 1  # Convert to zero-based
                    if 0 <= index < len(products):
                        indices.append(index)
                except ValueError:
                    pass
            
            for ref in number_refs:
                try:
                    index = int(ref) - 1  # Convert to zero-based
                    if 0 <= index < len(products):
                        indices.append(index)
                except ValueError:
                    pass
            
            for word in word_refs:
                try:
                    index = number_words.index(word)
                    if 0 <= index < len(products):
                        indices.append(index)
                except ValueError:
                    pass
            
            # Handle "best deal" references - assume it's the first product if sorted by best deal
            if best_deal_ref and len(products) > 0:
                indices.append(0)  # First product is likely the best deal
            
            # Get referenced products by index
            for index in indices:
                if 0 <= index < len(products):
                    referenced_products.append(products[index])
            
            # If no direct references but there's a focused product,
            # consider the query to be about that product
            if not referenced_products and focused_product is not None:
                if 0 <= focused_product < len(products):
                    referenced_products = [products[focused_product]]
                    self.logger.info(f"Using focused product: {focused_product}")
            
            # If still no referenced products but talking about products in general,
            # assume they're talking about the first product
            if not referenced_products and len(products) > 0 and (
                "product" in query or "item" in query or "it" in query or "this" in query
            ):
                referenced_products = [products[0]]
                self.logger.info("Defaulting to first product based on generic reference")
            
            # Determine if this is a follow-up question
            is_follow_up = False
            
            # Check for follow-up phrases
            is_follow_up = any(phrase in query for phrase in follow_up_phrases)
            
            # Also check for pronoun references that likely refer to previous products
            if not is_follow_up:
                pronoun_refs = re.search(r"\b(it|this|that|these|those|they|them)\b", query)
                is_follow_up = pronoun_refs is not None
            
            # For very short queries, likely follow-ups
            if not is_follow_up and len(query.split()) <= 5:
                is_follow_up = True
            
            # If we have referenced products, it's definitely a follow-up
            if referenced_products:
                is_follow_up = True
            
            # Special case: check if this is clearly a new search despite having the patterns above
            # Keywords that indicate a new search for Sony headphones
            sony_headphone_keywords = ["sony", "headphones", "wh1000", "wh-1000", "xm4", "xm5", "wireless"]
            
            # If multiple specific Sony headphone keywords are present, treat as new search
            if len([kw for kw in sony_headphone_keywords if kw in query]) >= 3:
                self.logger.info("Query contains multiple Sony headphone keywords - treating as new search")
                is_follow_up = False
                referenced_products = []
            
            self.logger.info(f"Follow-up analysis: {is_follow_up}, Referenced products: {len(referenced_products)}")
            
            # If no specific products referenced but it's a follow-up,
            # include all products for context
            if is_follow_up and not referenced_products and products:
                all_products = products
            else:
                all_products = products if is_follow_up else []
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={
                    "is_follow_up": is_follow_up,
                    "focused_product": focused_product,
                    "referenced_products": referenced_products,
                    "products": all_products
                },
                message_type="MEMORY_ANALYZE_RESPONSE",
                conversation_id=conversation_id
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing query: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Query analysis error: {str(e)}"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )

    def _analyze_query(self, message: MCPMessage) -> MCPMessage:
        """
        Analyze if a query is related to previous products or represents a new search
        using Gemini's language understanding capabilities.
        
        Args:
            message: The MCPMessage containing the query to analyze
            
        Returns:
            A new MCPMessage containing the analysis results
        """
        try:
            conversation_id = message.conversation_id
            query = message.content.get("query", "")
            
            self.logger.info(f"Analyzing query: '{query}' for conversation {conversation_id}")
            
            # Check if there are products to reference
            if conversation_id not in self.product_info or not self.product_info[conversation_id]:
                self.logger.info("No product context available for this conversation")
                return MCPMessage(
                    sender=self.name,
                    receiver=message.sender,
                    content={
                        "is_follow_up": False,
                        "focused_product": None,
                        "referenced_products": [],
                        "products": []
                    },
                    message_type="MEMORY_ANALYZE_RESPONSE",
                    conversation_id=conversation_id
                )
            
            # Get previous products
            stored_products = self.product_info[conversation_id]
            self.logger.info(f"Found {len(stored_products)} products in memory")
            
            # Create a structured prompt for Gemini to analyze context switch
            context_analysis_prompt = self._create_context_switch_prompt(query, stored_products)
            
            # Create a message to send to the Gemini agent
            gemini_message = MCPMessage(
                sender=self.name,
                receiver="GeminiAgent",
                content=context_analysis_prompt,
                message_type="REQUEST",
                conversation_id=conversation_id
            )
            
            # Get Gemini's analysis - instantiate directly to avoid circular imports
            gemini_agent = GeminiAgent()
            analysis_response = gemini_agent.process_message(gemini_message)
            
            if analysis_response.message_type == "ERROR":
                self.logger.warning(f"Error from Gemini agent: {analysis_response.content}")
                # Fall back to legacy approach on error
                return self._legacy_analyze_query(message)
            
            # Parse Gemini's response to extract the analysis
            analysis_result = self._parse_gemini_analysis(analysis_response.content, stored_products)
            
            # Return the analysis results
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content=analysis_result,
                message_type="MEMORY_ANALYZE_RESPONSE",
                conversation_id=conversation_id
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing query with Gemini: {str(e)}")
            # Fall back to the legacy approach on exception
            return self._legacy_analyze_query(message)
        
    def _update_focus(self, message: MCPMessage) -> MCPMessage:
        """
        Update which product is currently in focus.
        
        Args:
            message: The MCPMessage containing the focus update
            
        Returns:
            A new MCPMessage indicating success or failure
        """
        try:
            conversation_id = message.conversation_id
            product_index = message.content.get("product_index")
            
            if product_index is not None:
                self.focused_products[conversation_id] = product_index
            else:
                # Clear focus if no index provided
                if conversation_id in self.focused_products:
                    del self.focused_products[conversation_id]
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"status": "success"},
                message_type="MEMORY_UPDATE_FOCUS_RESPONSE",
                conversation_id=conversation_id
            )
            
        except Exception as e:
            self.logger.error(f"Error updating focus: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Focus update error: {str(e)}"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
    def _store_context(self, message: MCPMessage) -> MCPMessage:
        """
        Store conversation context and product information.
        
        Args:
            message: The MCPMessage containing context to store
            
        Returns:
            A new MCPMessage indicating success or failure
        """
        try:
            conversation_id = message.conversation_id
            content = message.content
            
            self.logger.info(f"Storing context for conversation {conversation_id}")
            
            # Store original query
            if "query" in content:
                if conversation_id not in self.recent_queries:
                    self.recent_queries[conversation_id] = []
                
                # Add to recent queries (keep last 5)
                self.recent_queries[conversation_id].append({
                    "query": content["query"],
                    "timestamp": datetime.now().isoformat(),
                    "search_params": content.get("search_params", {})
                })
                
                # Trim to last 5 queries
                if len(self.recent_queries[conversation_id]) > 5:
                    self.recent_queries[conversation_id] = self.recent_queries[conversation_id][-5:]
            
            # Store product information
            if "products" in content:
                products = content["products"]
                self.logger.info(f"Storing {len(products)} products for conversation {conversation_id}")
                
                # Initialize if not exists
                if conversation_id not in self.product_info:
                    self.product_info[conversation_id] = []
                
                # Add to product info (replace existing products)
                self.product_info[conversation_id] = products
            else:
                self.logger.warning("No products found in the message content")
            
            # Store context information
            if "context" in content:
                self.conversation_contexts[conversation_id] = content["context"]
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"status": "success"},
                message_type="MEMORY_STORE_RESPONSE",
                conversation_id=conversation_id
            )
            
        except Exception as e:
            self.logger.error(f"Error storing context: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Context storage error: {str(e)}"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
    def _create_context_switch_prompt(self, query, stored_products):
        """Create a structured prompt for Gemini to analyze context switching"""
        
        # Prepare product information in a structured format
        product_info = []
        for i, product in enumerate(stored_products[:5]):  # Limit to first 5 products to keep prompt manageable
            product_info.append(f"Product {i+1}: {product.get('title', 'Unknown Product')}")
        
        products_text = "\n".join(product_info)
        
        # Create the prompt
        prompt = f"""
        You are an AI helping to analyze if a user's query is a follow-up question about previously shown products, or if it's a completely new search.

        Previous products shown to the user:
        {products_text}

        User's new query: "{query}"

        Please analyze if this query is:
        1. A follow-up question about the previously shown products (e.g., asking for more details, comparing them, etc.)
        2. A completely new search (e.g., asking about different products, starting a new topic)

        Return your analysis in JSON format:
        {{
            "is_new_search": true/false,
            "is_follow_up": true/false,
            "reasoning": "brief explanation of your decision",
            "referenced_product_indices": [list of 0-based indices of referenced products, if any]
        }}
        
        Only return the JSON, with no additional text.
        """
        
        return prompt

    def _parse_gemini_analysis(self, gemini_response, stored_products):
        """Parse Gemini's response to extract context switching analysis"""
        
        try:
            # Try to extract JSON from the response
            # First, check if response is already a dict
            if isinstance(gemini_response, dict):
                analysis = gemini_response
            else:
                # Try to parse as JSON
                import json
                import re
                
                # Look for JSON pattern in the response
                json_match = re.search(r'({.*})', gemini_response, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group(1))
                else:
                    # If no JSON found, assume it's not a follow-up
                    self.logger.warning("Could not parse Gemini response as JSON")
                    return {
                        "is_follow_up": False,
                        "focused_product": None,
                        "referenced_products": [],
                        "products": []
                    }
            
            # Extract the analysis results
            is_new_search = analysis.get("is_new_search", True)
            is_follow_up = analysis.get("is_follow_up", False)
            referenced_indices = analysis.get("referenced_product_indices", [])
            
            # If it's a new search, clear context
            if is_new_search:
                return {
                    "is_follow_up": False,
                    "focused_product": None,
                    "referenced_products": [],
                    "products": []
                }
            
            # If it's a follow-up, find referenced products
            referenced_products = []
            if referenced_indices:
                for idx in referenced_indices:
                    if 0 <= idx < len(stored_products):
                        referenced_products.append(stored_products[idx])
            
            # If no specific products referenced but it's a follow-up, use first product
            if not referenced_products and is_follow_up and stored_products:
                referenced_products.append(stored_products[0])
            
            return {
                "is_follow_up": is_follow_up,
                "focused_product": referenced_indices[0] if referenced_indices else None,
                "referenced_products": referenced_products,
                "products": stored_products if is_follow_up and not referenced_products else []
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing Gemini analysis: {str(e)}")
            # Default to not a follow-up on error
            return {
                "is_follow_up": False,
                "focused_product": None,
                "referenced_products": [],
                "products": []
            }