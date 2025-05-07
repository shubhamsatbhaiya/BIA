"""
Main Controller for DealFinder AI.

This module implements the DealFinderController class that orchestrates
all the agents and handles user interaction.
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

# Import scraper agents
from dealfinder.agents.scrapers import get_scraper_agents

from dealfinder import config
from dealfinder.utils.logging import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger("DealFinderAI.Controller")

class DealFinderController:
    """Main controller that orchestrates the agents and handles user interaction"""
    
    def __init__(self, 
                 gemini_api_key: Optional[str] = None, 
                 use_real_scrapers: bool = False,
                 max_results: int = config.DEFAULT_MAX_RESULTS):
        """
        Initialize the DealFinder controller.
        
        Args:
            gemini_api_key: Optional API key for Gemini. If not provided, will try to get from config.
            use_real_scrapers: Whether to use real web scrapers or mock scrapers
            max_results: Maximum number of results to return per source
        """
        self.logger = logging.getLogger("DealFinderAI.Controller")
        self.console = Console()
        self.max_results = max_results
        
        # Use API key from constructor or config
        api_key = gemini_api_key or config.GEMINI_API_KEY
        
        # Initialize agents
        self.gemini_agent = GeminiAgent(api_key)
        self.aggregator_agent = ResultsAggregatorAgent()
        self.presentation_agent = PresentationAgent()
        
        # Get scraper agents (real or mock based on use_real_scrapers flag)
        scrapers = get_scraper_agents(use_real_scrapers)
        self.amazon_agent = scrapers["amazon"]
        self.walmart_agent = scrapers["walmart"]
        self.ebay_agent = scrapers["ebay"]
        
        # Agent registry
        self.agents = {
            "GeminiAgent": self.gemini_agent,
            "AmazonScraperAgent": self.amazon_agent,
            "WalmartScraperAgent": self.walmart_agent,
            "EbayScraperAgent": self.ebay_agent,
            "ResultsAggregatorAgent": self.aggregator_agent,
            "PresentationAgent": self.presentation_agent
        }
        
        # Conversation history
        self.conversation_history = []
    
    def process_user_query(self, query: str) -> str:
        """
        Process a user query and return the formatted response.
        
        Args:
            query: The user query string
            
        Returns:
            A formatted response string with the search results
        """
        self.logger.info(f"Processing user query: {query}")
        
        try:
            # Create a conversation ID for this interaction
            conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # 1. Parse the user query with Gemini
            parse_message = MCPMessage(
                sender="Controller",
                receiver="GeminiAgent",
                content=query,
                message_type="PARSE_QUERY",
                conversation_id=conversation_id
            )
            
            parse_response = self.gemini_agent.process_message(parse_message)
            self.conversation_history.append((parse_message, parse_response))
            
            if parse_response.message_type == "ERROR":
                return f"Error parsing your query: {parse_response.content.get('error', 'Unknown error')}"
            
            search_params = parse_response.content
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
            amazon_response = self.amazon_agent.process_message(amazon_message)
            self.conversation_history.append((amazon_message, amazon_response))
            
            if amazon_response.message_type != "ERROR":
                search_results.append(amazon_response.content)
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
            walmart_response = self.walmart_agent.process_message(walmart_message)
            self.conversation_history.append((walmart_message, walmart_response))
            
            if walmart_response.message_type != "ERROR":
                search_results.append(walmart_response.content)
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
            ebay_response = self.ebay_agent.process_message(ebay_message)
            self.conversation_history.append((ebay_message, ebay_response))
            
            if ebay_response.message_type != "ERROR":
                search_results.append(ebay_response.content)
            else:
                self.logger.warning(f"eBay search error: {ebay_response.content}")
            
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
            self.conversation_history.append((aggregate_message, aggregate_response))
            
            if aggregate_response.message_type == "ERROR":
                return f"Error aggregating results: {aggregate_response.content.get('error', 'Unknown error')}"
            
            # 4. Format and present results
            present_message = MCPMessage(
                sender="Controller",
                receiver="PresentationAgent",
                content=aggregate_response.content,
                message_type="PRESENT_REQUEST",
                conversation_id=conversation_id
            )
            present_response = self.presentation_agent.process_message(present_message)
            self.conversation_history.append((present_message, present_response))
            
            if present_response.message_type == "ERROR":
                return f"Error presenting results: {present_response.content.get('error', 'Unknown error')}"
            
            # 5. Log the complete interaction for future analytics
            self._log_interaction(query, search_params, aggregate_response.content)
            
            # Return the formatted response
            return present_response.content["formatted_response"]
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return f"I encountered an error while searching for deals: {str(e)}"
    
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

[italic]Type 'exit' or 'quit' to end the session.[/italic]
        """
        self.console.print(Panel(panel_content, title="DealFinder AI", border_style="blue"))