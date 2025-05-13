"""
Test script to validate the LangChain integration with Gemini-only LLM.
This script tests basic functionality and follow-up question handling.
"""

import os
import time
from rich.console import Console
from rich.table import Table

from dealfinder import config
from dealfinder.controller import DealFinderController
from dealfinder.langchain_integration.controller import DealFinderControllerAdapter

def test_basic_queries():
    """Test basic queries with both implementations."""
    console = Console()
    console.print("[bold]Testing basic queries...[/bold]")
    
    # Test queries
    test_queries = [
        "Find me wireless headphones under $100",
        "What are the best coffee makers with built-in grinders?",
        "Show me gaming laptops under $1200",
    ]
    
    # Initialize both controllers
    original = DealFinderController()
    langchain = DealFinderControllerAdapter()
    
    # Create results table
    table = Table(title="Basic Query Test Results")
    table.add_column("Query", style="cyan")
    table.add_column("Original Response Length", style="green")
    table.add_column("LangChain Response Length", style="blue")
    table.add_column("Processing Time (Original)", style="green")
    table.add_column("Processing Time (LangChain)", style="blue")
    
    for query in test_queries:
        console.print(f"Testing query: [italic]{query}[/italic]")
        
        # Test original implementation
        start_time = time.time()
        original_response = original.process_user_query(query)
        original_time = time.time() - start_time
        
        # Test LangChain implementation
        start_time = time.time()
        langchain_response = langchain.process_user_query(query)
        langchain_time = time.time() - start_time
        
        # Add to results table
        table.add_row(
            query,
            str(len(original_response)),
            str(len(langchain_response)),
            f"{original_time:.2f}s",
            f"{langchain_time:.2f}s"
        )
        
        # Save responses to files for comparison (optional)
        with open(f"test_original_{time.time()}.txt", "w") as f:
            f.write(original_response)
        
        with open(f"test_langchain_{time.time()}.txt", "w") as f:
            f.write(langchain_response)
    
    # Display results table
    console.print(table)

def test_followup_questions():
    """Test follow-up question handling in both implementations."""
    console = Console()
    console.print("\n[bold]Testing follow-up question handling...[/bold]")
    
    # Initial query
    initial_query = "Find me wireless headphones under $100"
    
    # Follow-up queries to test
    followup_queries = [
        "Which one has the best battery life?",
        "Tell me more about the first product",
        "Is the second one waterproof?",
        "Which one is the best deal?",
        "Does product 3 have noise cancellation?"
    ]
    
    # Test with original controller
    console.print("[bold green]Testing original controller follow-up handling...[/bold green]")
    original = DealFinderController()
    
    # Create a session ID
    session_id_original = f"test_original_{int(time.time())}"
    
    # Process initial query
    console.print(f"Initial query: {initial_query}")
    response = original.process_user_query(initial_query, session_id_original)
    console.print(f"Initial response received, length: {len(response)}")
    
    # Process follow-up queries
    for i, followup in enumerate(followup_queries, 1):
        console.print(f"\nFollow-up {i}: {followup}")
        followup_response = original.process_user_query(followup, session_id_original)
        # Print first 150 characters of the response
        console.print(f"Response preview: {followup_response[:150]}...")
    
    # Test with LangChain controller
    console.print("\n[bold blue]Testing LangChain controller follow-up handling...[/bold blue]")
    langchain = DealFinderControllerAdapter()
    
    # Create a session ID
    session_id_langchain = f"test_langchain_{int(time.time())}"
    
    # Process initial query
    console.print(f"Initial query: {initial_query}")
    response = langchain.process_user_query(initial_query, session_id_langchain)
    console.print(f"Initial response received, length: {len(response)}")
    
    # Process follow-up queries
    for i, followup in enumerate(followup_queries, 1):
        console.print(f"\nFollow-up {i}: {followup}")
        followup_response = langchain.process_user_query(followup, session_id_langchain)
        # Print first 150 characters of the response
        console.print(f"Response preview: {followup_response[:150]}...")

def test_adapter():
    """Test the controller adapter."""
    console = Console()
    console.print("\n[bold]Testing controller adapter...[/bold]")
    
    # Initialize the adapter
    adapter = DealFinderControllerAdapter()
    
    # Test with LangChain enabled
    config.ENABLE_LANGCHAIN = True
    console.print("[bold blue]Testing with LangChain enabled...[/bold blue]")
    
    # Display welcome message
    welcome = adapter.display_welcome_message()
    console.print(f"Welcome message received, length: {len(welcome)}")
    
    # Process a query
    query = "Find me a budget gaming mouse"
    session_id = f"test_adapter_langchain_{int(time.time())}"
    
    console.print(f"Query: {query}")
    response = adapter.process_user_query(query, session_id)
    console.print(f"Response received, length: {len(response)}")
    
    # Test with LangChain disabled
    config.ENABLE_LANGCHAIN = False
    console.print("\n[bold green]Testing with LangChain disabled...[/bold green]")
    
    # Display welcome message
    welcome = adapter.display_welcome_message()
    console.print(f"Welcome message: {welcome}")  # Should be "Welcome message displayed"
    
    # Process a query
    query = "Find me a budget gaming keyboard"
    session_id = f"test_adapter_original_{int(time.time())}"
    
    console.print(f"Query: {query}")
    response = adapter.process_user_query(query, session_id)
    console.print(f"Response received, length: {len(response)}")
    
    # Reset to default
    config.ENABLE_LANGCHAIN = True

if __name__ == "__main__":
    # Make sure Gemini API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set")
        exit(1)
    
    # Run the tests
    try:
        test_basic_queries()
        test_followup_questions()
        test_adapter()
        print("\nAll tests completed!")
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()