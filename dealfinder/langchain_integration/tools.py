"""
LangChain tool implementations for DealFinder scrapers.
"""

from langchain.tools import BaseTool
from typing import Dict, Any, List

from dealfinder.agents.base import MCPMessage
from dealfinder.agents.scrapers import get_scraper_agents

class AmazonScraperTool(BaseTool):
    """LangChain tool wrapper for the Amazon scraper."""
    
    name = "amazon_scraper"
    description = "Search for products on Amazon with specified parameters"
    
    def __init__(self):
        """Initialize the Amazon scraper tool."""
        super().__init__()
        self.scraper = get_scraper_agents()["amazon"]
    
    def _run(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run the Amazon scraper with the provided search parameters."""
        try:
            # Convert to MCP message format
            message = MCPMessage(
                sender="LangChainController",
                receiver="AmazonScraperAgent",
                content=search_params,
                message_type="SEARCH_REQUEST",
                conversation_id=search_params.get("conversation_id", "default")
            )
            
            # Process using the existing scraper
            response = self.scraper.process_message(message)
            
            # Check for errors
            if response.message_type == "ERROR":
                return {"error": response.content.get("error", "Unknown error")}
            
            # Return the products
            return response.content.get("products", [])
            
        except Exception as e:
            print(f"Error in Amazon scraper tool: {str(e)}")
            return []

# Similar wrappers for Walmart and eBay
class WalmartScraperTool(BaseTool):
    """LangChain tool wrapper for the Walmart scraper."""
    
    name = "walmart_scraper"
    description = "Search for products on Walmart with specified parameters"
    
    def __init__(self):
        """Initialize the Walmart scraper tool."""
        super().__init__()
        self.scraper = get_scraper_agents()["walmart"]
    
    def _run(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run the Walmart scraper with the provided search parameters."""
        # Implementation similar to AmazonScraperTool
        # ...

class EbayScraperTool(BaseTool):
    """LangChain tool wrapper for the eBay scraper."""
    
    name = "ebay_scraper"
    description = "Search for products on eBay with specified parameters"
    
    def __init__(self):
        """Initialize the eBay scraper tool."""
        super().__init__()
        self.scraper = get_scraper_agents()["ebay"]
    
    def _run(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run the eBay scraper with the provided search parameters."""
        # Implementation similar to AmazonScraperTool
        # ...