"""
Mock scrapers module for DealFinder AI.

This module contains mock implementations of scraper agents for testing and development.
"""

from dealfinder.agents.scrapers.mock.amazon import MockAmazonScraperAgent
from dealfinder.agents.scrapers.mock.walmart import MockWalmartScraperAgent
from dealfinder.agents.scrapers.mock.ebay import MockEbayScraperAgent

__all__ = [
    'MockAmazonScraperAgent',
    'MockWalmartScraperAgent',
    'MockEbayScraperAgent',
]