"""
State definitions for the DealFinder LangGraph workflow.

This module defines the state structure used by the LangGraph workflow
and provides helper functions for state manipulation.
"""

from typing import Dict, List, Any, TypedDict, Optional, Tuple

class DealFinderState(TypedDict):
    """
    State definition for the DealFinder workflow.
    
    This represents the complete state that flows through the LangGraph nodes.
    """
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

def create_initial_state(query: str, conversation_id: str = None, 
                        chat_history: List[Tuple[str, str]] = None,
                        memory: Dict[str, Any] = None) -> DealFinderState:
    """
    Create an initial state for the workflow with the given query.
    
    Args:
        query: The user's query
        conversation_id: Optional conversation ID
        chat_history: Optional conversation history
        memory: Optional memory dictionary
        
    Returns:
        An initialized state dictionary
    """
    import time
    
    # Use provided values or defaults
    conv_id = conversation_id or f"session_{int(time.time())}"
    history = chat_history or []
    mem = memory or {}
    
    # Create and return the initial state
    return {
        "query": query,
        "parsed_query": {},
        "search_results": [],
        "aggregated_results": {},
        "comparison_results": {},
        "response": "",
        "conversation_id": conv_id,
        "chat_history": history,
        "follow_up_info": {},
        "memory": mem
    }

def update_chat_history(state: DealFinderState) -> DealFinderState:
    """
    Update the chat history in the state with the current query and response.
    
    Args:
        state: The current state
        
    Returns:
        Updated state with the new history entry
    """
    # Create a new state to avoid modifying the original
    new_state = dict(state)
    
    # Add the current query and response to the history
    if "query" in new_state and "response" in new_state:
        history = list(new_state.get("chat_history", []))
        history.append((new_state["query"], new_state["response"]))
        new_state["chat_history"] = history
    
    return new_state