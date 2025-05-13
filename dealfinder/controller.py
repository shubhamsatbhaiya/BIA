"""
Updated controller implementation for DealFinder AI with product comparison and chat memory.
"""

import json
import logging
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel

from dealfinder.agents.base import Agent, MCPMessage
from dealfinder.agents.gemini_agent import GeminiAgent
from dealfinder.agents.aggregator_agent import ResultsAggregatorAgent
from dealfinder.agents.presentation_agent import PresentationAgent
from dealfinder.agents.product_comparison import ProductComparisonAgent
from dealfinder.agents.chat_memory import ChatMemoryAgent

# Import scraper agents
from dealfinder.agents.scrapers import get_scraper_agents

from dealfinder import config
from dealfinder.utils.logging import setup_logging, get_logger

# Set up logging
logger = get_logger("Controller")

class DealFinderController:
    """Main controller that orchestrates the agents and handles user interaction"""
    
    def __init__(self, 
                 gemini_api_key: Optional[str] = None,
                 max_results: int = config.DEFAULT_MAX_RESULTS):
        """
        Initialize the DealFinder controller.
        
        Args:
            gemini_api_key: Optional API key for Gemini. If not provided, will try to get from config.
            max_results: Maximum number of results to return per source
            max_results: Maximum number of results to return per source
        """
        self.logger = get_logger("Controller")
        self.console = Console()
        self.max_results = max_results
        
        # Use API key from constructor or config
        api_key = gemini_api_key or config.GEMINI_API_KEY
        
        # Initialize agents
        self.gemini_agent = GeminiAgent(api_key)
        self.aggregator_agent = ResultsAggregatorAgent()
        self.presentation_agent = PresentationAgent()
        self.comparison_agent = ProductComparisonAgent()
        self.chat_memory_agent = ChatMemoryAgent()
        
        # Initialize scraper agents
        self.scraper_agents = get_scraper_agents()
        self.logger.info(f"Initialized scraper agents: {list(self.scraper_agents.keys())}")
        
        # Agent registry
        self.agents = {
            "GeminiAgent": self.gemini_agent,
            "AmazonScraperAgent": self.scraper_agents["amazon"],
            "WalmartScraperAgent": self.scraper_agents["walmart"],
            "EbayScraperAgent": self.scraper_agents["ebay"],
            "ResultsAggregatorAgent": self.aggregator_agent,
            "PresentationAgent": self.presentation_agent,
            "ProductComparisonAgent": self.comparison_agent,
            "ChatMemoryAgent": self.chat_memory_agent
        }
        
        # Conversation history
        self.conversation_history = {}
    
    """
Fix for the Controller class to properly handle follow-up questions.
The issue is that the controller is trying to parse follow-up queries as new search queries
instead of properly handling them through the chat memory system.
"""

    # # Update the process_user_query method in the DealFinderController class
    # def process_user_query(self, query: str, session_id: str = None) -> str:
    #     """
    #     Process a user query and return the formatted response.
        
    #     Args:
    #         query: The user query string
    #         session_id: Optional session ID for conversation tracking
            
    #     Returns:
    #         A formatted response string with the search results
    #     """
    #     try:
    #         # Create a conversation ID for this interaction if not provided
    #         conversation_id = session_id or datetime.now().strftime("%Y%m%d%H%M%S")
            
    #         # If this is a new session, initialize conversation history
    #         if conversation_id not in self.conversation_history:
    #             self.conversation_history[conversation_id] = []
                
    #         self.logger.info(f"Processing user query: {query}")
            
    #         # Check if this is a follow-up question by analyzing the query
    #         analyze_message = MCPMessage(
    #             sender="Controller",
    #             receiver="ChatMemoryAgent",
    #             content={"query": query},
    #             message_type="MEMORY_ANALYZE",
    #             conversation_id=conversation_id
    #         )
    #         analyze_response = self.chat_memory_agent.process_message(analyze_message)
    #         self.conversation_history[conversation_id].append((analyze_message, analyze_response))
            
    #         # Extract results from the analysis
    #         is_follow_up = False
    #         referenced_products = []
            
    #         if analyze_response.message_type != "ERROR":
    #             self.logger.info(f"Analyze response: {analyze_response.content}")
    #             is_follow_up = analyze_response.content.get("is_follow_up", False)
    #             referenced_products = analyze_response.content.get("referenced_products", [])
                
    #             # Log the decision for debugging
    #             self.logger.info(f"Is follow-up? {is_follow_up}")
    #             self.logger.info(f"Referenced products: {len(referenced_products)}")
            
    #         # Handle follow-up questions
    #         if is_follow_up and referenced_products:
    #             self.logger.info(f"Handling as follow-up question about {len(referenced_products)} products")
    #             return self._handle_follow_up(query, referenced_products, conversation_id)
            
    #         # If not a follow-up or no products found, proceed with a new search
    #         self.logger.info("Processing as new search query")
            
    #         # 1. Parse the user query with Gemini
    #         parse_message = MCPMessage(
    #             sender="Controller",
    #             receiver="GeminiAgent",
    #             content=query,
    #             message_type="PARSE_QUERY",
    #             conversation_id=conversation_id
    #         )
            
    #         parse_response = self.gemini_agent.process_message(parse_message)
    #         self.conversation_history[conversation_id].append((parse_message, parse_response))
            
    #         if parse_response.message_type == "ERROR":
    #             return f"Error parsing your query: {parse_response.content.get('error', 'Unknown error')}"
            
    #         # Extract search parameters from the response
    #         if isinstance(parse_response.content, str):
    #             # Try to extract JSON from a string response (happens when Gemini returns JSON in a code block)
    #             import re
    #             import json
    #             json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', parse_response.content)
    #             if json_match:
    #                 try:
    #                     search_params = json.loads(json_match.group(1))
    #                 except:
    #                     # If parsing fails, create a basic search parameter
    #                     search_params = {"keywords": [query.strip()]}
    #             else:
    #                 # If no JSON found, use the raw query
    #                 search_params = {"keywords": [query.strip()]}
    #         else:
    #             search_params = parse_response.content
                
    #         # Make sure we have valid search parameters
    #         if not search_params or not any(search_params.values()):
    #             search_params = {"keywords": [query.strip()]}
                
    #         self.logger.info(f"Parsed search parameters: {search_params}")
            
    #         # 2. Send search requests to each scraper agent
    #         search_results = []
            
    #         # Amazon search
    #         amazon_message = MCPMessage(
    #             sender="Controller",
    #             receiver="AmazonScraperAgent",
    #             content=search_params,
    #             message_type="SEARCH_REQUEST",
    #             conversation_id=conversation_id
    #         )
    #         amazon_response = self.scraper_agents["amazon"].process_message(amazon_message)
    #         self.conversation_history[conversation_id].append((amazon_message, amazon_response))
            
    #         if amazon_response.message_type != "ERROR":
    #             search_results.append(amazon_response.content)
    #         else:
    #             self.logger.warning(f"Amazon search error: {amazon_response.content}")
            
    #         # Walmart search
    #         walmart_message = MCPMessage(
    #             sender="Controller",
    #             receiver="WalmartScraperAgent",
    #             content=search_params,
    #             message_type="SEARCH_REQUEST",
    #             conversation_id=conversation_id
    #         )
    #         walmart_response = self.scraper_agents["walmart"].process_message(walmart_message)
    #         self.conversation_history[conversation_id].append((walmart_message, walmart_response))
            
    #         if walmart_response.message_type != "ERROR":
    #             search_results.append(walmart_response.content)
    #         else:
    #             self.logger.warning(f"Walmart search error: {walmart_response.content}")
            
    #         # eBay search
    #         ebay_message = MCPMessage(
    #             sender="Controller",
    #             receiver="EbayScraperAgent",
    #             content=search_params,
    #             message_type="SEARCH_REQUEST",
    #             conversation_id=conversation_id
    #         )
    #         ebay_response = self.scraper_agents["ebay"].process_message(ebay_message)
    #         self.conversation_history[conversation_id].append((ebay_message, ebay_response))
            
    #         if ebay_response.message_type != "ERROR":
    #             search_results.append(ebay_response.content)
    #         else:
    #             self.logger.warning(f"eBay search error: {ebay_response.content}")
            
    #         # 3. Aggregate and rank results
    #         aggregate_message = MCPMessage(
    #             sender="Controller",
    #             receiver="ResultsAggregatorAgent",
    #             content={
    #                 "original_query": query,
    #                 "search_params": search_params,
    #                 "results": search_results
    #             },
    #             message_type="AGGREGATE_REQUEST",
    #             conversation_id=conversation_id
    #         )
    #         aggregate_response = self.aggregator_agent.process_message(aggregate_message)
    #         self.conversation_history[conversation_id].append((aggregate_message, aggregate_response))
            
    #         if aggregate_response.message_type == "ERROR":
    #             return f"Error aggregating results: {aggregate_response.content.get('error', 'Unknown error')}"
            
    #         # 4. Compare similar products across sites
    #         # Extract all products from the aggregated results
    #         all_products = aggregate_response.content.get("top_products", [])
            
    #         if not all_products:
    #             return "I couldn't find any products matching your search. Could you try a different query?"
            
    #         compare_message = MCPMessage(
    #             sender="Controller",
    #             receiver="ProductComparisonAgent",
    #             content={
    #                 "original_query": query,
    #                 "search_params": search_params,
    #                 "all_products": all_products
    #             },
    #             message_type="COMPARE_REQUEST",
    #             conversation_id=conversation_id
    #         )
    #         compare_response = self.comparison_agent.process_message(compare_message)
    #         self.conversation_history[conversation_id].append((compare_message, compare_response))
            
    #         if compare_response.message_type == "ERROR":
    #             self.logger.warning(f"Error comparing products: {compare_response.content}")
    #             # Continue without comparison results
    #             comparison_results = None
    #         else:
    #             comparison_results = compare_response.content

    #         # Store product memory for follow-up queries
    #         store_message = MCPMessage(
    #             sender="Controller",
    #             receiver="ChatMemoryAgent",
    #             message_type="MEMORY_STORE",
    #             content={
    #                 "query": query,
    #                 "products": all_products,
    #             },
    #             conversation_id=conversation_id
    #         )
    #         self.chat_memory_agent.process_message(store_message)
    #         print("[DEBUG] Stored products in memory:", len(all_products))
            
    #         # 5. Format and present results with comparison highlights
    #         present_message = MCPMessage(
    #             sender="Controller",
    #             receiver="PresentationAgent",
    #             content={
    #                 "original_query": query,
    #                 "search_params": search_params,
    #                 "top_products": all_products,
    #                 "grouped_results": aggregate_response.content.get("grouped_results", {}),
    #                 "comparison_results": comparison_results,
    #                 "total_results": aggregate_response.content.get("total_results", 0),
    #                 "selected_results": aggregate_response.content.get("selected_results", 0)
    #             },
    #             message_type="PRESENT_REQUEST",
    #             conversation_id=conversation_id
    #         )
    #         present_response = self.presentation_agent.process_message(present_message)
    #         self.conversation_history[conversation_id].append((present_message, present_response))
            
    #         if present_response.message_type == "ERROR":
    #             return f"Error presenting results: {present_response.content.get('error', 'Unknown error')}"
            
    #         # 6. Store the product data in chat memory for future reference
    #         memory_store_message = MCPMessage(
    #             sender="Controller",
    #             receiver="ChatMemoryAgent",
    #             message_type="MEMORY_STORE",
    #             content={
    #                 "query": query,
    #                 "search_params": search_params,
    #                 "products": all_products,
    #                 "context": {
    #                     "comparison_results": comparison_results
    #                 }
    #             },
    #             conversation_id=conversation_id
    #         )
    #         memory_store_response = self.chat_memory_agent.process_message(memory_store_message)
    #         self.conversation_history[conversation_id].append((memory_store_message, memory_store_response))
            
    #         if memory_store_response.message_type == "ERROR":
    #             self.logger.warning(f"Error storing memory: {memory_store_response.content}")
    #         else:
    #             self.logger.info("Successfully stored search results in memory")
            
    #         # 7. Log the complete interaction for future analytics
    #         self._log_interaction(query, search_params, aggregate_response.content)
            
    #         # Return the formatted response
    #         return present_response.content["formatted_response"]
            
    #     except Exception as e:
    #         self.logger.error(f"Error processing query: {str(e)}")
    #         return f"Sorry, there was an error processing your request: {str(e)}"
    
    # def _handle_follow_up(self, query: str, referenced_products: List[Dict[str, Any]], conversation_id: str) -> str:
    #     """
    #     Handle follow-up questions about specific products.
        
    #     Args:
    #         query: The follow-up query
    #         referenced_products: List of products being referenced
    #         conversation_id: Conversation ID for this interaction
            
    #     Returns:
    #         A formatted response to the follow-up question
    #     """
    #     try:
    #         self.logger.info(f"Handling follow-up question: {query}")
    #         self.logger.info(f"Referenced products: {len(referenced_products)}")
            
    #         # Update focus to this product
    #         product = referenced_products[0] if referenced_products else None
    #         if not product:
    #             return "I'm sorry, I couldn't find any products to tell you about. Could you try a new search?"
            
    #         # Extract product index if available (for better reference)
    #         product_index = 0
            
    #         # Update focus to this product
    #         update_focus_message = MCPMessage(
    #             sender="Controller",
    #             receiver="ChatMemoryAgent",
    #             content={"product_index": product_index},
    #             message_type="MEMORY_UPDATE_FOCUS",
    #             conversation_id=conversation_id
    #         )
    #         self.chat_memory_agent.process_message(update_focus_message)
            
    #         # Generate a detailed response using Gemini
    #         # Create a prompt with the product details and the follow-up query
    #         product_details = json.dumps(product, indent=2)
            
    #         prompt = f"""
    #         I'm a shopping assistant helping a customer with product information.
            
    #         The customer previously searched for products and is now asking a follow-up question: "{query}"
            
    #         They're referring to this product:
    #         {product_details}
            
    #         Please provide a helpful, conversational response addressing their question
    #         about this product. Include relevant details from the product information.
            
    #         If the product is a "best deal", emphasize why it's a good value compared to alternatives.
    #         If they're asking about comparisons to other products, highlight the key differences.
    #         If they're asking about specific features, focus on those details.
    #         """
            
    #         response_message = MCPMessage(
    #             sender="Controller",
    #             receiver="GeminiAgent",
    #             content=prompt,
    #             message_type="REQUEST",
    #             conversation_id=conversation_id
    #         )
            
    #         response = self.gemini_agent.process_message(response_message)
    #         self.conversation_history[conversation_id].append((response_message, response))
            
    #         if response.message_type == "ERROR":
    #             return f"I'm sorry, I couldn't process your follow-up question. {response.content.get('error', '')}"
            
    #         # Return the formatted response
    #         return response.content
            
    #     except Exception as e:
    #         self.logger.error(f"Error handling follow-up: {str(e)}")
    #         return f"I'm sorry, I had trouble understanding your follow-up question. Could you try asking in a different way?"
    """
Updated Controller with enhanced debugging and fallback options
"""

    def process_user_query(self, query: str, session_id: str = None) -> str:
        """
        Process a user query and return the formatted response.
        
        Args:
            query: The user query string
            session_id: Optional session ID for conversation tracking
            
        Returns:
            A formatted response string with the search results
        """
        try:
            # Create a conversation ID for this interaction if not provided
            conversation_id = session_id or datetime.now().strftime("%Y%m%d%H%M%S")
            
            # If this is a new session, initialize conversation history
            if conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []
                
            self.logger.info(f"Processing user query: {query}")
            
            # Check if this is a follow-up question by analyzing the query
            analyze_message = MCPMessage(
                sender="Controller",
                receiver="ChatMemoryAgent",
                content={"query": query},
                message_type="MEMORY_ANALYZE",
                conversation_id=conversation_id
            )
            analyze_response = self.chat_memory_agent.process_message(analyze_message)
            self.conversation_history[conversation_id].append((analyze_message, analyze_response))
            
            # Extract results from the analysis
            is_follow_up = False
            referenced_products = []
            
            if analyze_response.message_type != "ERROR":
                self.logger.info(f"Analyze response: {analyze_response.content}")
                is_follow_up = analyze_response.content.get("is_follow_up", False)
                referenced_products = analyze_response.content.get("referenced_products", [])
                
                # Log the decision for debugging
                self.logger.info(f"Is follow-up? {is_follow_up}")
                self.logger.info(f"Referenced products: {len(referenced_products)}")
            
            # Enhanced follow-up detection based on query content
            # Keywords that indicate a search for specific products
            sony_keywords = ["sony", "headphones", "wh1000", "wh-1000", "xm4", "xm5"]
            
            # Check if query contains explicit Sony headphone references
            contains_sony_keywords = sum(1 for kw in sony_keywords if kw.lower() in query.lower()) >= 2
            
            # If this looks like a new product search rather than a follow-up, reset follow-up status
            if contains_sony_keywords and "latest" in query.lower():
                self.logger.info(f"Query contains explicit Sony headphone keywords with 'latest'. Treating as new search.")
                is_follow_up = False
                referenced_products = []
            
            # Handle follow-up questions
            if is_follow_up and referenced_products:
                self.logger.info(f"Handling as follow-up question about {len(referenced_products)} products")
                return self._handle_follow_up(query, referenced_products, conversation_id)
            
            # If not a follow-up or no products found, proceed with a new search
            self.logger.info("Processing as new search query")
            
            # 1. Parse the user query with Gemini
            parse_message = MCPMessage(
                sender="Controller",
                receiver="GeminiAgent",
                content=query,
                message_type="PARSE_QUERY",
                conversation_id=conversation_id
            )
            
            parse_response = self.gemini_agent.process_message(parse_message)
            self.conversation_history[conversation_id].append((parse_message, parse_response))
            
            if parse_response.message_type == "ERROR":
                return f"Error parsing your query: {parse_response.content.get('error', 'Unknown error')}"
            
            # Extract search parameters from the response
            if isinstance(parse_response.content, str):
                # Try to extract JSON from a string response (happens when Gemini returns JSON in a code block)
                import re
                import json
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', parse_response.content)
                if json_match:
                    try:
                        search_params = json.loads(json_match.group(1))
                    except:
                        # If parsing fails, create a basic search parameter
                        search_params = {"keywords": [query.strip()]}
                else:
                    # If no JSON found, use the raw query
                    search_params = {"keywords": [query.strip()]}
            else:
                search_params = parse_response.content
                
            # Make sure we have valid search parameters
            if not search_params or not any(search_params.values()):
                search_params = {"keywords": [query.strip()]}
                
            self.logger.info(f"Parsed search parameters: {search_params}")
            
            # 2. Send search requests to each scraper agent
            search_results = []
            
            # Amazon search
            amazon_message = MCPMessage(
                sender="Controller",
                receiver="AmazonScraperAgent",
                content=search_params,
                message_type="SEARCH_REQUEST",
                conversation_id=conversation_id
            )
            amazon_response = self.scraper_agents["amazon"].process_message(amazon_message)
            self.conversation_history[conversation_id].append((amazon_message, amazon_response))
            
            # if amazon_response.message_type != "ERROR":
            #     search_results.append(amazon_response.content)
            #     # Debug: Log the number of Amazon products
            #     if "products" in amazon_response.content:
            #         self.logger.info(f"Amazon returned {len(amazon_response.content['products'])} products")
            # else:
            #     self.logger.warning(f"Amazon search error: {amazon_response.content}")
            if amazon_response.message_type != "ERROR":
                # Add this debug print
                self.logger.info(f"Amazon response content: {amazon_response.content}")
                
                if "products" in amazon_response.content:
                    products_list = amazon_response.content["products"]
                    self.logger.info(f"Amazon returned {len(products_list)} products")
                    search_results.append(amazon_response.content)
                else:
                    self.logger.warning("No 'products' field in Amazon response")
            else:
                self.logger.warning(f"Amazon search error: {amazon_response.content}")
            # Walmart search
            walmart_message = MCPMessage(
                sender="Controller",
                receiver="WalmartScraperAgent",
                content=search_params,
                message_type="SEARCH_REQUEST",
                conversation_id=conversation_id
            )
            walmart_response = self.scraper_agents["walmart"].process_message(walmart_message)
            self.conversation_history[conversation_id].append((walmart_message, walmart_response))
            
            if walmart_response.message_type != "ERROR":
                search_results.append(walmart_response.content)
                # Debug: Log the number of Walmart products
                if "products" in walmart_response.content:
                    self.logger.info(f"Walmart returned {len(walmart_response.content['products'])} products")
            else:
                self.logger.warning(f"Walmart search error: {walmart_response.content}")
            
            # eBay search
            ebay_message = MCPMessage(
                sender="Controller",
                receiver="EbayScraperAgent",
                content=search_params,
                message_type="SEARCH_REQUEST",
                conversation_id=conversation_id
            )
            ebay_response = self.scraper_agents["ebay"].process_message(ebay_message)
            self.conversation_history[conversation_id].append((ebay_message, ebay_response))
            
            if ebay_response.message_type != "ERROR":
                search_results.append(ebay_response.content)
                # Debug: Log the number of eBay products
                if "products" in ebay_response.content:
                    self.logger.info(f"eBay returned {len(ebay_response.content['products'])} products")
            else:
                self.logger.warning(f"eBay search error: {ebay_response.content}")
            
            # Count total number of products before aggregation
            total_products_before = sum(
                len(result.get("products", [])) for result in search_results
            )
            self.logger.info(f"Total products before aggregation: {total_products_before}")
            
            # 3. Aggregate and rank results
            aggregate_message = MCPMessage(
                sender="Controller",
                receiver="ResultsAggregatorAgent",
                content={
                    "original_query": query,
                    "search_params": search_params,
                    "results": search_results
                },
                message_type="AGGREGATE_REQUEST",
                conversation_id=conversation_id
            )
            aggregate_response = self.aggregator_agent.process_message(aggregate_message)
            self.conversation_history[conversation_id].append((aggregate_message, aggregate_response))
            
            if aggregate_response.message_type == "ERROR":
                return f"Error aggregating results: {aggregate_response.content.get('error', 'Unknown error')}"
            
            # 4. Compare similar products across sites
            # Extract all products from the aggregated results
            all_products = aggregate_response.content.get("top_products", [])
            
            # FIX: If aggregation filtered out all products but we had products before,
            # use the raw search results instead
            if not all_products and total_products_before > 0:
                self.logger.warning("Aggregation returned no products despite having search results. Using raw search results.")
                all_products = []
                for result in search_results:
                    if "products" in result:
                        all_products.extend(result["products"][:5])  # Take top 5 from each source
            
            if not all_products:
                return "I couldn't find any products matching your search. Could you try a different query?"
            
            # Log the number of products after aggregation
            self.logger.info(f"Products after aggregation: {len(all_products)}")
            
            compare_message = MCPMessage(
                sender="Controller",
                receiver="ProductComparisonAgent",
                content={
                    "original_query": query,
                    "search_params": search_params,
                    "all_products": all_products
                },
                message_type="COMPARE_REQUEST",
                conversation_id=conversation_id
            )
            compare_response = self.comparison_agent.process_message(compare_message)
            self.conversation_history[conversation_id].append((compare_message, compare_response))
            
            if compare_response.message_type == "ERROR":
                self.logger.warning(f"Error comparing products: {compare_response.content}")
                # Continue without comparison results
                comparison_results = None
            else:
                comparison_results = compare_response.content

            # Store product memory for follow-up queries
            store_message = MCPMessage(
                sender="Controller",
                receiver="ChatMemoryAgent",
                message_type="MEMORY_STORE",
                content={
                    "query": query,
                    "products": all_products,
                },
                conversation_id=conversation_id
            )
            self.chat_memory_agent.process_message(store_message)
            print("[DEBUG] Stored products in memory:", len(all_products))
            
            # 5. Format and present results with comparison highlights
            present_message = MCPMessage(
                sender="Controller",
                receiver="PresentationAgent",
                content={
                    "original_query": query,
                    "search_params": search_params,
                    "top_products": all_products,
                    "grouped_results": aggregate_response.content.get("grouped_results", {}),
                    "comparison_results": comparison_results,
                    "total_results": aggregate_response.content.get("total_results", 0),
                    "selected_results": aggregate_response.content.get("selected_results", 0)
                },
                message_type="PRESENT_REQUEST",
                conversation_id=conversation_id
            )
            present_response = self.presentation_agent.process_message(present_message)
            self.conversation_history[conversation_id].append((present_message, present_response))
            
            if present_response.message_type == "ERROR":
                return f"Error presenting results: {present_response.content.get('error', 'Unknown error')}"
            
            # 6. Store the product data in chat memory for future reference
            memory_store_message = MCPMessage(
                sender="Controller",
                receiver="ChatMemoryAgent",
                message_type="MEMORY_STORE",
                content={
                    "query": query,
                    "search_params": search_params,
                    "products": all_products,
                    "context": {
                        "comparison_results": comparison_results
                    }
                },
                conversation_id=conversation_id
            )
            memory_store_response = self.chat_memory_agent.process_message(memory_store_message)
            self.conversation_history[conversation_id].append((memory_store_message, memory_store_response))
            
            if memory_store_response.message_type == "ERROR":
                self.logger.warning(f"Error storing memory: {memory_store_response.content}")
            else:
                self.logger.info("Successfully stored search results in memory")
            
            # 7. Log the complete interaction for future analytics
            self._log_interaction(query, search_params, aggregate_response.content)
            
            # Return the formatted response
            return present_response.content["formatted_response"]
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return f"Sorry, there was an error processing your request: {str(e)}"
        
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
            
            # Debug log the product we're focusing on
            self.logger.info(f"Follow-up for product: {product.get('title', 'Unknown')}")
            
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
            
            # Ensure product price is a float for proper formatting
            if "price" in product:
                try:
                    product["price"] = float(product["price"])
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid price format: {product.get('price')}")
                    product["price"] = 0.0
            
            # Generate a detailed response using Gemini
            # Create a prompt with the product details and the follow-up query
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
            1. Always format prices as exact dollar amounts (e.g., "${price:.2f}" not "$1")
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
            
    def _log_interaction(self, query: str, search_params: Dict[str, Any], results: Dict[str, Any]) -> None:
        """
        Log the interaction for future analysis.
        
        Args:
            query: The original user query
            search_params: The parsed search parameters
            results: The aggregated results
        """
        try:
            if not config.ENABLE_ANALYTICS:
                return
                
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "search_params": search_params,
                "results_summary": {
                    "total_results": results.get("total_results", 0),
                    "selected_results": results.get("selected_results", 0),
                    "sources": list(results.get("grouped_results", {}).keys())
                }
            }
            
            with open(config.ANALYTICS_FILE, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            self.logger.error(f"Error logging interaction: {str(e)}")
    
    def display_welcome_message(self) -> None:
        """Display welcome message in the terminal"""
        panel_content = """
[bold green]Welcome to DealFinder AI![/bold green]

I can help you find the best deals across multiple shopping sites.
Just tell me what you're looking for in natural language.

For example:
- "Find me the best deals on wireless headphones"
- "I need a budget laptop for college under $500"
- "What are the top-rated coffee makers on sale right now?"

[italic]You can also ask follow-up questions about any product![/italic]
[italic]Type 'exit' or 'quit' to end the session.[/italic]
        """
        self.console.print(Panel(panel_content, title="DealFinder AI", border_style="blue"))