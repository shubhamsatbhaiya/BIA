"""
Main application entry point for DealFinder AI.
"""

import os
import sys
import time
from rich.console import Console
from rich.panel import Panel

from dealfinder import config
from dealfinder.utils.logging import setup_logging
from dealfinder.controller import DealFinderController  # Import the adapter

def main():
    """Main entry point for the application."""
    # Set up logging
    setup_logging()
    
    # Create the console for rich text output
    console = Console()
    
    console.print(Panel("[bold green]DealFinder AI[/bold green]", subtitle="Shopping Assistant"))
    
    # Get API key for Gemini
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        console.print("[bold red]Error: GEMINI_API_KEY environment variable not set[/bold red]")
        sys.exit(1)
    
    # Create the controller adapter
    controller = DealFinderController(gemini_api_key=gemini_api_key)
    
    # Display which implementation is being used
    if config.ENABLE_LANGCHAIN:
        console.print(f"[bold blue]Using LangChain implementation with Gemini Pro model[/bold blue]")
    else:
        console.print("[bold blue]Using original implementation with Gemini[/bold blue]")
    
    # Display welcome message
    welcome_message = controller.display_welcome_message()
    if config.ENABLE_LANGCHAIN:  # Only print if we have a return value
        console.print(welcome_message)
    
    # Generate a session ID for this conversation
    session_id = f"session_{int(time.time())}"
    
    # Interactive session loop
    while True:
        try:
            # Get user input
            user_input = input("\nWhat would you like to search for? (type 'exit' to quit): ")
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[bold green]Thank you for using DealFinder AI. Goodbye![/bold green]")
                break
            
            # Process the query
            console.print("[bold blue]Searching...[/bold blue]")
            response = controller.process_user_query(user_input, session_id)
            
            # Display the response
            print("\n" + response)
            
        except KeyboardInterrupt:
            console.print("\n[bold green]Search cancelled. Goodbye![/bold green]")
            break
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            import traceback
            traceback.print_exc()  # Print the stack trace for debugging

if __name__ == "__main__":
    main()