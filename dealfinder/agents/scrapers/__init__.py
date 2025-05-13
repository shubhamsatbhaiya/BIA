"""
Scraper Agents Module for DealFinder AI.

This module provides factory functions to create scraper agents for different shopping sites.
"""

import logging
from typing import Dict, Any

# Import real scraper implementations
from dealfinder.agents.scrapers.amazon import RealAmazonScraperAgent
from dealfinder.agents.scrapers.walmart import RealWalmartScraperAgent
from dealfinder.agents.scrapers.ebay import RealEbayScraperAgent

logger = logging.getLogger("DealFinderAI.Scrapers")

def get_scraper_agents() -> Dict[str, Any]:
    """
    Get scraper agents for real web scraping.
    
    Returns:
        Dictionary of scraper agents with their names as keys
    """
    logger.info("Initializing real web scraper agents")
    return {
        'amazon': RealAmazonScraperAgent(),
        'walmart': RealWalmartScraperAgent(),
        'ebay': RealEbayScraperAgent()
    }

# Export the classes directly as well
__all__ = [
    'RealAmazonScraperAgent',
    'RealWalmartScraperAgent',
    'RealEbayScraperAgent',
    'get_scraper_agents',
]