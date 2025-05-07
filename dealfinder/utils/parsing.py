"""
Text parsing utilities for DealFinder AI.

This module provides utilities for parsing text and search parameters.
"""

import re
import json
from typing import Dict, Any, List, Tuple, Optional, Union

def parse_price_range(text: str) -> Optional[Tuple[Optional[float], Optional[float]]]:
    """
    Parse price range from text.
    
    Examples:
        "under $100" -> (None, 100.0)
        "$50-$100" -> (50.0, 100.0)
        "between $50 and $100" -> (50.0, 100.0)
        "$50 to $100" -> (50.0, 100.0)
        "$50+" -> (50.0, None)
        "less than $100" -> (None, 100.0)
        "more than $50" -> (50.0, None)
    
    Args:
        text: The text to parse
        
    Returns:
        A tuple of (min_price, max_price), or None if no price range is found
    """
    # Clean the text
    text = text.lower().strip()
    
    # Pattern for extracting numbers
    number_pattern = r'\d+(?:\.\d+)?'
    
    # Pattern for "under X" or "less than X"
    under_pattern = r'(?:under|less than|below)\s+\$?(\d+(?:\.\d+)?)'
    under_match = re.search(under_pattern, text)
    if under_match:
        max_price = float(under_match.group(1))
        return (None, max_price)
    
    # Pattern for "over X" or "more than X"
    over_pattern = r'(?:over|more than|above|at least)\s+\$?(\d+(?:\.\d+)?)'
    over_match = re.search(over_pattern, text)
    if over_match:
        min_price = float(over_match.group(1))
        return (min_price, None)
    
    # Pattern for "X+"
    plus_pattern = r'\$?(\d+(?:\.\d+)?)\+\s*'
    plus_match = re.search(plus_pattern, text)
    if plus_match:
        min_price = float(plus_match.group(1))
        return (min_price, None)
    
    # Pattern for "X-Y" or "X to Y" or "between X and Y"
    range_pattern = r'\$?(\d+(?:\.\d+)?)\s*(?:-|to|and)\s*\$?(\d+(?:\.\d+)?)'
    range_match = re.search(range_pattern, text)
    if range_match:
        min_price = float(range_match.group(1))
        max_price = float(range_match.group(2))
        return (min_price, max_price)
    
    # Pattern for "between X and Y"
    between_pattern = r'between\s+\$?(\d+(?:\.\d+)?)\s+and\s+\$?(\d+(?:\.\d+)?)'
    between_match = re.search(between_pattern, text)
    if between_match:
        min_price = float(between_match.group(1))
        max_price = float(between_match.group(2))
        return (min_price, max_price)
    
    # No price range found
    return None

def extract_brands(text: str) -> List[str]:
    """
    Extract potential brand names from text.
    
    Args:
        text: The text to parse
        
    Returns:
        A list of potential brand names
    """
    # This is a simplified implementation
    # In a real system, you would use a database of known brands
    # or use named entity recognition
    
    # Common brand prefixes/suffixes to help identify brands
    brand_indicators = [
        "by", "from", "brand"
    ]
    
    brands = []
    
    # Split the text into words
    words = text.split()
    
    # Look for words after brand indicators
    for i, word in enumerate(words):
        if word.lower() in brand_indicators and i < len(words) - 1:
            # Add the next word as a potential brand
            brand = words[i + 1].strip(',.;:"\'')
            # Only add if it starts with a capital letter (likely a brand)
            if brand and brand[0].isupper():
                brands.append(brand)
    
    # Look for capitalized words that might be brands
    # This is a very simple heuristic and will have many false positives
    for i, word in enumerate(words):
        if word and word[0].isupper() and word.lower() not in ["i", "a", "the", "my", "your"]:
            # Check if this isn't already captured by the previous rule
            if word.strip(',.;:"\'') not in brands:
                brands.append(word.strip(',.;:"\''))
    
    return brands

def parse_sort_preference(text: str) -> Optional[str]:
    """
    Parse sort preference from text.
    
    Args:
        text: The text to parse
        
    Returns:
        A sort preference string, or None if no preference is found
    """
    # Clean the text
    text = text.lower().strip()
    
    # Check for price sorting indicators
    if re.search(r'(?:sort|order)\s+by\s+(?:price|cost)\s+(?:low|cheap)', text) or \
       re.search(r'(?:cheapest|lowest\s+price|best\s+price)', text):
        return "price_low_to_high"
    
    if re.search(r'(?:sort|order)\s+by\s+(?:price|cost)\s+(?:high|expensive)', text) or \
       re.search(r'(?:most\s+expensive|highest\s+price)', text):
        return "price_high_to_low"
    
    # Check for rating sorting indicators
    if re.search(r'(?:sort|order)\s+by\s+(?:rating|ratings|review|reviews|best|top)', text) or \
       re.search(r'(?:best\s+rated|top\s+rated|highest\s+rated)', text):
        return "rating"
    
    # Check for newness sorting indicators
    if re.search(r'(?:sort|order)\s+by\s+(?:new|newest|recent|latest)', text) or \
       re.search(r'(?:newest|most\s+recent|just\s+released)', text):
        return "newest"
    
    # No sort preference found
    return None

def extract_features(text: str) -> List[str]:
    """
    Extract product features from text.
    
    Args:
        text: The text to parse
        
    Returns:
        A list of potential product features
    """
    # This is a simplified implementation
    # In a real system, you might use more sophisticated NLP techniques
    
    # Common feature indicators
    feature_indicators = [
        "with", "has", "having", "include", "includes", "including",
        "featuring", "feature", "features", "that has", "that have"
    ]
    
    features = []
    
    # Look for phrases after feature indicators
    for indicator in feature_indicators:
        pattern = rf'{indicator}\s+([\w\s]+?)(?:,|\.|and|or|$)'
        matches = re.finditer(pattern, text.lower())
        for match in matches:
            feature = match.group(1).strip()
            if feature and feature not in features:
                features.append(feature)
    
    return features

def normalize_search_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and validate search parameters.
    
    Args:
        params: The search parameters to normalize
        
    Returns:
        Normalized search parameters
    """
    normalized = {}
    
    # Normalize product_type
    if "product_type" in params:
        normalized["product_type"] = str(params["product_type"]).strip()
    
    # Normalize keywords
    if "keywords" in params:
        if isinstance(params["keywords"], list):
            normalized["keywords"] = [str(k).strip() for k in params["keywords"] if k]
        elif params["keywords"]:
            normalized["keywords"] = [str(params["keywords"]).strip()]
    
    # Normalize price_range
    if "price_range" in params:
        price_range = params["price_range"]
        if isinstance(price_range, list) and len(price_range) == 2:
            # Convert to proper numeric values
            min_price = float(price_range[0]) if price_range[0] not in (None, "", "null") else None
            max_price = float(price_range[1]) if price_range[1] not in (None, "", "null") else None
            normalized["price_range"] = [min_price, max_price]
    
    # Normalize brands
    if "brands" in params:
        if isinstance(params["brands"], list):
            normalized["brands"] = [str(b).strip() for b in params["brands"] if b]
        elif params["brands"]:
            normalized["brands"] = [str(params["brands"]).strip()]
    
    # Normalize features
    if "features" in params:
        if isinstance(params["features"], list):
            normalized["features"] = [str(f).strip() for f in params["features"] if f]
        elif params["features"]:
            normalized["features"] = [str(params["features"]).strip()]
    
    # Normalize sorting_preference
    if "sorting_preference" in params and params["sorting_preference"]:
        pref = str(params["sorting_preference"]).strip().lower()
        valid_prefs = ["price_low_to_high", "price_high_to_low", "rating", "newest"]
        if pref in valid_prefs:
            normalized["sorting_preference"] = pref
        else:
            # Default to price low to high
            normalized["sorting_preference"] = "price_low_to_high"
    
    # Normalize buy_it_now
    if "buy_it_now" in params:
        normalized["buy_it_now"] = bool(params["buy_it_now"])
    
    return normalized