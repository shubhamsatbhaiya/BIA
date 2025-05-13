"""
LangGraph workflow definition for DealFinder AI.

This module creates the LangGraph workflow for the DealFinder system,
connecting the different components together.
"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any, List, TypedDict, Optional, Tuple
import time

# Import our components
from dealfinder.langchain_integration.components import (
    parse_query_node,
    execute_search_node,
    aggregate_results_node,
    compare_products_node,
    generate_response_node
)

# Define the state structure with type hints
class DealFinderState(TypedDict):
    query: str                           # The user's original query
    parsed_query: Dict[str, Any]         # Structured search parameters
    search_results: List[Dict[str, Any]] # Raw search results from all sources
    aggregated_results: Dict[str, Any]   # Combined and ranked results  
    comparison_results: Dict[str, Any]   # Product comparison results
    response: str                        # Formatted response for the user
    conversation_id: str                 # Session identifier
    chat_history: List[Tuple[str, str]]  # Conversation history
    follow_up_info: Dict[str, Any]       # Information for follow-up handling
    memory: Dict[str, Any]               # Memory for persistent data

# Define the main LangGraph workflow
def create_dealfinder_graph():
    """
    Create and return the LangGraph workflow for DealFinder.
    
    Returns:
        A compiled LangGraph workflow
    """
    # Create a new graph with our state structure
    workflow = StateGraph(DealFinderState)
    
    # Add all nodes to the graph
    workflow.add_node("parse_query", parse_query_node)
    workflow.add_node("execute_search", execute_search_node)
    workflow.add_node("aggregate_results", aggregate_results_node)
    workflow.add_node("compare_products", compare_products_node)
    workflow.add_node("generate_response", generate_response_node)
    
    # Define conditional edges for follow-up handling
    def route_after_parsing(state: DealFinderState):
        """
        Determine the next node after parsing based on whether it's a follow-up.
        
        If it's a follow-up with referenced products, skip to response generation.
        Otherwise, proceed with the search.
        """
        if (state["follow_up_info"].get("is_follow_up", False) and 
            state["follow_up_info"].get("referenced_products", [])):
            return "generate_response"
        else:
            return "execute_search"
    
    # Add edges with conditional routing
    workflow.add_edge("parse_query", route_after_parsing)
    workflow.add_edge("execute_search", "aggregate_results")
    workflow.add_edge("aggregate_results", "compare_products")
    workflow.add_edge("compare_products", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Compile the graph
    return workflow.compile()