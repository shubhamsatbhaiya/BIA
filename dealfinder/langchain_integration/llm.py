"""
LLM provider management for DealFinder AI - Gemini only version.
"""

from typing import Dict, Any, Optional
from langchain_core.language_models import LLM
from langchain_google_genai import ChatGoogleGenerativeAI

from dealfinder import config

def get_llm(model_name: Optional[str] = None) -> LLM:
    """
    Get a Gemini LLM instance.
    
    Args:
        model_name: Optional model name to override config (always uses Gemini)
        
    Returns:
        An initialized Gemini LLM instance
    """
    # Use specified model or default from config (always a Gemini model)
    model = model_name or config.DEFAULT_LLM_MODEL
    
    # Ensure we're using a Gemini model
    if not model.startswith("gemini-"):
        model = "gemini-pro"  # Default to gemini-pro if not a Gemini model
        
    # Initialize Gemini model
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=0,
        google_api_key=config.GEMINI_API_KEY
    )