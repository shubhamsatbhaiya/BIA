"""
LangGraph component implementations for DealFinder AI with Gemini-only LLM.
This file provides all the node functions used in the LangGraph workflow.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
import re
from typing import Dict, Any, List, Optional, Tuple

from dealfinder import config
from dealfinder.agents.base import MCPMessage
from dealfinder.agents.scrapers import get_scraper_agents
from dealfinder.langchain_integration.state import GraphState
from dealfinder.langchain_integration.llm import get_llm
from dealfinder.langchain_integration.response_generator import ResponseGenerator
from dealfinder.langchain_integration.product_comparison import ProductComparisonEngine

def get_gemini_llm():
    """Get a Gemini LLM instance with the configured API key."""
    return ChatGoogleGenerativeAI(
        model=config.DEFAULT_LLM_MODEL,
        temperature=0,
        google_api_key=config.GEMINI_API_KEY
    )

# 1. Enhanced Query Parser with Gemini

def create_enhanced_query_parser(llm=None):
    """
    Creates an improved query parser that extracts detailed shopping parameters.
    Uses Gemini LLM by default.
    """
    if llm is None:
        llm = get_gemini_llm()
    
    system_prompt = """
    You are a shopping intent analyzer specialized in understanding detailed product requirements.
    
    Analyze the following shopping query and extract these parameters:
    
    1. product_type: The main product category (e.g., "laptop", "headphones", "coffee maker")
    2. keywords: List of important words for filtering results
    3. price_range: An array with [min_price, max_price], use null for unbounded
    4. brands: List of mentioned brands or null if none
    5. features: List of required product features/specifications
    6. sorting_preference: How results should be sorted:
       - "price_low_to_high" for cheapest first
       - "price_high_to_low" for most expensive first
       - "rating" for best-rated first
       - "newest" for newest first
    7. buy_it_now: Boolean, true if immediate purchase preferred (not auctions)
    8. condition: Product condition preferences ("new", "used", "refurbished", or null if any)
    9. urgency: Rate from 1-5 how urgent this purchase seems (5 being most urgent)
    10. deal_focus: Boolean, true if the query explicitly asks for deals/discounts/sales
    
    Return a JSON object with these fields. Do not include any fields with null values.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{query}")
    ])
    
    parser = JsonOutputParser()
    
    return prompt | llm | parser

# 2. Advanced Follow-up Question Analyzer with Gemini

class FollowUpAnalyzer:
    """
    Advanced follow-up question analyzer that detects if a query is referring to
    previously mentioned products and identifies which ones. Uses Gemini LLM.
    """
    
    def __init__(self, llm=None):
        self.llm = llm or get_gemini_llm()
        
    def is_follow_up(self, query: str, chat_history: List[Tuple[str, str]]) -> bool:
        """Determines if a query is a follow-up question."""
        if not chat_history:
            return False
            
        # Simple regex patterns for follow-up indicators
        pronoun_pattern = r'\b(it|this|that|these|those|they|them)\b'
        ordinal_pattern = r'\b(first|second|third|fourth|fifth|1st|2nd|3rd|4th|5th)\b'
        product_ref_pattern = r'\b(product|item|deal|option)\s+(\d+|#\d+)\b'
        
        # Check for common follow-up phrases
        follow_up_phrases = [
            "more info", "tell me more", "more details", "specs", "specifications",
            "reviews", "ratings", "shipping", "delivery", "warranty", "features",
            "compare", "difference", "vs", "versus", "which one", "better"
        ]
        
        # Check various patterns
        has_pronoun = bool(re.search(pronoun_pattern, query.lower()))
        has_ordinal = bool(re.search(ordinal_pattern, query.lower()))
        has_product_ref = bool(re.search(product_ref_pattern, query.lower()))
        has_follow_up_phrase = any(phrase in query.lower() for phrase in follow_up_phrases)
        
        # Very short queries are likely follow-ups
        is_short_query = len(query.split()) <= 5
        
        return has_pronoun or has_ordinal or has_product_ref or has_follow_up_phrase or is_short_query
    
    def identify_referenced_products(self, query: str, chat_history: List[Tuple[str, str]], 
                                    available_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifies which products the user is referring to in a follow-up question."""
        # Use Gemini to analyze which products are being referenced
        last_ai_message = chat_history[-1][1] if chat_history else ""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an AI assistant analyzing a follow-up question about products.
            Based on the previous conversation and the user's current question,
            determine which product(s) they are referring to.
            
            The output should be an array of indices (0-based) of the products being referenced.
            If no specific product is referenced, return an empty array.
            If the user is referring to all products, return [-1].
            If the user is referring to "the best deal" or similar, return [-2].
            """),
            ("human", f"""
            Previous response with product information:
            {last_ai_message}
            
            User's follow-up question:
            {query}
            
            Available product indices (0 to {len(available_products)-1}).
            """)
        ])
        
        try:
            result = self.llm.invoke(prompt.format_messages(query=query))
            # Extract the indices from the response
            indices_pattern = r'\[([^\]]*)\]'
            match = re.search(indices_pattern, result.content)
            if match:
                indices_str = match.group(1)
                if not indices_str:
                    return []
                
                try:
                    # Parse the indices
                    indices = [int(idx.strip()) for idx in indices_str.split(',') if idx.strip()]
                    
                    # Handle special cases
                    if -1 in indices:  # All products
                        return available_products
                    if -2 in indices:  # Best deal
                        # Return the highest rated or cheapest product as the "best deal"
                        if available_products:
                            sorted_products = sorted(available_products, 
                                                    key=lambda p: (p.get('rating', 0) * -1, p.get('price', float('inf'))))
                            return [sorted_products[0]]
                    
                    # Return the referenced products
                    return [available_products[idx] for idx in indices 
                           if 0 <= idx < len(available_products)]
                except:
                    # If parsing fails, fall back to the first product
                    if available_products:
                        return [available_products[0]]
            
            # If no match is found, default to an empty list
            return []
            
        except Exception as e:
            print(f"Error identifying referenced products: {e}")
            return []

# 3. LangGraph Node Implementation for Query Parsing

def parse_query_node(state):
    """
    LangGraph node that parses the user query using Gemini LLM.
    """
    llm = get_gemini_llm()
    parser = create_enhanced_query_parser(llm)
    
    # Check if this is a follow-up question
    follow_up_analyzer = FollowUpAnalyzer(llm)
    is_follow_up = follow_up_analyzer.is_follow_up(state["query"], state["chat_history"])
    
    if is_follow_up:
        # For follow-up questions, we might have context from previous searches
        state["follow_up_info"] = {"is_follow_up": True}
        
        # Try to identify which products the user is referring to
        if "memory" in state and "products" in state["memory"]:
            referenced_products = follow_up_analyzer.identify_referenced_products(
                state["query"], 
                state["chat_history"],
                state["memory"]["products"]
            )
            state["follow_up_info"]["referenced_products"] = referenced_products
        
        return state
    
    # For new queries, parse the search parameters
    try:
        parsed_query = parser.invoke({"query": state["query"]})
        state["parsed_query"] = parsed_query
        state["follow_up_info"] = {"is_follow_up": False}
    except Exception as e:
        print(f"Error parsing query: {str(e)}")
        # Fallback to simple keyword extraction
        state["parsed_query"] = {"keywords": [state["query"]]}
        state["follow_up_info"] = {"is_follow_up": False}
    
    return state

# Other node implementations would follow a similar pattern, 
# using Gemini LLM where needed instead of other models.
def compare_products_node(state):
    """
    LangGraph node that compares similar products across sources.
    """
    # Skip for follow-up questions
    if state["follow_up_info"].get("is_follow_up", False):
        return state
    
    # Use the product comparison engine
    engine = ProductComparisonEngine()
    
    # Get all products from aggregated results
    all_products = state["aggregated_results"].get("top_products", [])
    
    if not all_products:
        state["comparison_results"] = {"best_deals": [], "product_groups": []}
        return state
    
    # Group similar products
    product_groups = engine.group_similar_products(all_products)
    
    # Find best deals
    best_deals = engine.find_best_deals(product_groups)
    
    state["comparison_results"] = {
        "best_deals": best_deals,
        "product_groups": product_groups
    }
    
    return state

def generate_response_node(state):
    """
    LangGraph node that generates the final response using Gemini LLM.
    """
    llm = get_gemini_llm()
    response_generator = ResponseGenerator(llm)
    
    # For follow-up questions with referenced products
    if (state["follow_up_info"].get("is_follow_up", False) and 
        state["follow_up_info"].get("referenced_products", [])):
        
        referenced_products = state["follow_up_info"]["referenced_products"]
        response = response_generator.generate_follow_up_response(state["query"], referenced_products)
        
    # For regular searches
    else:
        # Get products and best deals
        top_products = state["aggregated_results"].get("top_products", [])
        best_deals = state["comparison_results"].get("best_deals", [])
        
        if not top_products:
            response = "I couldn't find any products matching your search. Could you try a different query?"
        else:
            response = response_generator.generate_search_response(state["query"], top_products, best_deals)
    
    state["response"] = response
    return state

# Helper function to handle follow-up questions about products
def handle_follow_up(state):
    """
    Helper function to handle follow-up questions without executing a new search.
    This is used when we can resolve the follow-up from memory.
    """
    llm = get_gemini_llm()
    response_generator = ResponseGenerator(llm)
    
    # Get referenced products
    referenced_products = state["follow_up_info"].get("referenced_products", [])
    
    # Generate response
    if referenced_products:
        response = response_generator.generate_follow_up_response(state["query"], referenced_products)
        state["response"] = response
    else:
        # If no products are referenced, ask for clarification
        state["response"] = "I'm not sure which product you're asking about. Could you clarify which item you're interested in?"
    
    return state