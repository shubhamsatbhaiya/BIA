"""
Configuration settings for DealFinder AI.

This module contains configuration settings and constants for the DealFinder AI application.
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Scraping configuration
MAX_PRODUCTS_PER_SOURCE = 5  # Maximum number of products to get from each source
SCRAPING_TIMEOUT = 10  # Timeout in seconds for scraping requests
SCRAPING_DELAY_MIN = 0.5  # Minimum delay between requests in seconds
SCRAPING_DELAY_MAX = 1.5  # Maximum delay between requests in seconds

# User agent list for rotating headers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
]

# Base URLs for shopping sites
AMAZON_BASE_URL = "https://www.amazon.com/s"
WALMART_BASE_URL = "https://www.walmart.com/search"
EBAY_BASE_URL = "https://www.ebay.com/sch/i.html"

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": "dealfinder.log",
            "mode": "a",
        }
    },
    "loggers": {
        "DealFinderAI": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        }
    }
}

# Analytics configuration
ANALYTICS_FILE = "dealfinder_analytics.log"
ENABLE_ANALYTICS = True

# Web server configuration
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
DEBUG_MODE = True

# Default settings
DEFAULT_MAX_RESULTS = 10
DEFAULT_SORT_PREFERENCE = "price_low_to_high"

# LangChain Integration Configuration (NEW)
ENABLE_LANGCHAIN = True  # Feature flag to enable/disable LangChain integration
DEFAULT_LLM_MODEL = "gemini-pro"  # Using Gemini model only
LANGCHAIN_MEMORY_TTL = 3600  # Time to live for conversation memory (in seconds)