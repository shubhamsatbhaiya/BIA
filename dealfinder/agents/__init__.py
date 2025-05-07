"""
Agents module for DealFinder AI.

This module contains all the agent implementations for the system.
"""

from dealfinder.agents.base import Agent, MCPMessage
from dealfinder.agents.gemini_agent import GeminiAgent
from dealfinder.agents.aggregator_agent import ResultsAggregatorAgent
from dealfinder.agents.presentation_agent import PresentationAgent

# Import scraper agents
from dealfinder.agents.scrapers import get_scraper_agents

__all__ = [
    'Agent',
    'MCPMessage',
    'GeminiAgent',
    'ResultsAggregatorAgent',
    'PresentationAgent',
    'get_scraper_agents',
]