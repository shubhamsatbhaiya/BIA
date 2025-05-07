"""
Logging configuration for DealFinder AI.

This module provides utilities for configuring logging across the application.
"""

import logging
import logging.config
import os
from typing import Optional, Dict, Any

from dealfinder import config

def setup_logging(log_file: Optional[str] = None, log_level: int = logging.INFO) -> None:
    """
    Set up logging for the application.
    
    Args:
        log_file: Optional path to log file. If not provided, uses the default from config.
        log_level: Log level to use (default: INFO)
    """
    # Create a custom logging configuration based on the config
    logging_config = config.LOGGING_CONFIG.copy()
    
    # Override log file if provided
    if log_file:
        logging_config["handlers"]["file"]["filename"] = log_file
    
    # Override log level if different from default
    if log_level != logging.INFO:
        logging_config["handlers"]["console"]["level"] = log_level
        logging_config["handlers"]["file"]["level"] = log_level
        logging_config["loggers"]["DealFinderAI"]["level"] = log_level
    
    # Create log directory if it doesn't exist
    log_path = os.path.dirname(logging_config["handlers"]["file"]["filename"])
    if log_path and not os.path.exists(log_path):
        os.makedirs(log_path)
    
    # Configure logging with the updated config
    logging.config.dictConfig(logging_config)
    
    # Log that logging has been set up
    logging.getLogger("DealFinderAI").info("Logging initialized")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name, prefixed with 'DealFinderAI'.
    
    Args:
        name: The name of the logger (without the 'DealFinderAI' prefix)
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(f"DealFinderAI.{name}")