"""
Scraper Agents Module for DealFinder AI.

This module provides factory functions to create scraper agents for different shopping sites.
"""

import logging
from typing import Dict, Any

# Import both real and mock implementations
# Real scrapers
from dealfinder.agents.scrapers.amazon import RealAmazonScraperAgent
from dealfinder.agents.scrapers.walmart import RealWalmartScraperAgent
from dealfinder.agents.scrapers.ebay import RealEbayScraperAgent

# Mock scrapers
from dealfinder.agents.scrapers.mock.amazon import MockAmazonScraperAgent
from dealfinder.agents.scrapers.mock.walmart import MockWalmartScraperAgent
from dealfinder.agents.scrapers.mock.ebay import MockEbayScraperAgent

logger = logging.getLogger("DealFinderAI.Scrapers")

def get_scraper_agents(use_real_scrapers: bool = False) -> Dict[str, Any]:
    """
    Get scraper agents based on the specified mode.
    
    Args:
        use_real_scrapers: If True, returns real web scraper agents.
                          If False, returns mock scraper agents.
                          
    Returns:
        A dictionary with keys 'amazon', 'walmart', 'ebay' mapping to
        the corresponding scraper agent instances.
    """
    if use_real_scrapers:
        logger.info("Initializing real web scraper agents")
        return {
            "amazon": RealAmazonScraperAgent(),
            "walmart": RealWalmartScraperAgent(),
            "ebay": RealEbayScraperAgent()
        }
    else:
        logger.info("Initializing mock scraper agents")
        return {
            "amazon": MockAmazonScraperAgent(),
            "walmart": MockWalmartScraperAgent(),
            "ebay": MockEbayScraperAgent()
        }

# Export the classes directly as well
__all__ = [
    'RealAmazonScraperAgent',
    'RealWalmartScraperAgent',
    'RealEbayScraperAgent',
    'MockAmazonScraperAgent',
    'MockWalmartScraperAgent',
    'MockEbayScraperAgent',
    'get_scraper_agents',
]