#!/usr/bin/env python3
"""
DealFinder AI - Main Entry Point

This script initializes and runs the DealFinder AI chatbot,
which finds the best deals across multiple shopping sites.
"""

import os
import sys
import argparse
import logging
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console

from dealfinder.controller import DealFinderController
from dealfinder.utils.logging import setup_logging
from dealfinder import config

# Ensure the script runs from the project root directory
if os.path.dirname(__file__):
    os.chdir(os.path.dirname(__file__))

# Load environment variables
load_dotenv()

# Set up logging
setup_logging()
logger = logging.getLogger("DealFinderAI.Main")
console = Console()

def run_terminal_interface(gemini_api_key: Optional[str] = None, use_real_scrapers: bool = False):
    """
    Run the chatbot in terminal mode.
    
    Args:
        gemini_api_key: Optional API key for Gemini
        use_real_scrapers: Whether to use real web scrapers or mock scrapers
    """
    try:
        # Initialize the controller
        controller = DealFinderController(
            gemini_api_key=gemini_api_key,
            use_real_scrapers=use_real_scrapers
        )
        
        # Display welcome message
        controller.display_welcome_message()
        
        # Main interaction loop
        while True:
            try:
                user_input = console.input("\n[bold blue]What are you looking for today?[/bold blue] ")
                
                if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
                    console.print("[bold green]Thank you for using DealFinder AI! Goodbye![/bold green]")
                    break
                
                # Show a spinner while processing
                with console.status("[bold green]Searching for the best deals...[/bold green]", spinner="dots"):
                    response = controller.process_user_query(user_input)
                
                # Print the response
                console.print(response)
                
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Search interrupted.[/bold yellow]")
            except Exception as e:
                logger.error(f"Error in terminal interface: {str(e)}")
                console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    except Exception as e:
        logger.error(f"Fatal error in terminal interface: {str(e)}")
        console.print(f"[bold red]Fatal error:[/bold red] {str(e)}")
        sys.exit(1)

def setup_flask_app(gemini_api_key: Optional[str] = None, use_real_scrapers: bool = False):
    """
    Set up the Flask web app for the chatbot.
    
    Args:
        gemini_api_key: Optional API key for Gemini
        use_real_scrapers: Whether to use real web scrapers or mock scrapers
        
    Returns:
        Flask application instance
    """
    from flask import Flask, request, jsonify, render_template
    
    app = Flask(__name__)
    
    # Initialize the controller
    controller = DealFinderController(
        gemini_api_key=gemini_api_key,
        use_real_scrapers=use_real_scrapers
    )
    
    # Serve static HTML
    @app.route('/')
    def home():
        return render_template('index.html')
    
    # API endpoint for querying
    @app.route('/api/query', methods=['POST'])
    def query():
        data = request.json
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({'error': 'No query provided'}), 400
        
        try:
            response = controller.process_user_query(user_query)
            return jsonify({'response': response})
        except Exception as e:
            logger.error(f"Error processing API query: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return app

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='DealFinder AI - Find the best deals online')
    parser.add_argument('--api-key', type=str, help='Gemini API Key (optional, can also use GEMINI_API_KEY env var)')
    parser.add_argument('--web', action='store_true', help='Run as a web service instead of terminal')
    parser.add_argument('--port', type=int, default=config.WEB_PORT, help=f'Port for web service (default: {config.WEB_PORT})')
    parser.add_argument('--real-scrapers', action='store_true', help='Use real web scrapers instead of mock implementations')
    
    args = parser.parse_args()
    
    # Get API key from args or environment
    gemini_api_key = args.api_key or config.GEMINI_API_KEY
    
    if not gemini_api_key:
        console.print("[bold red]Error:[/bold red] Gemini API key is required. Set it with --api-key or GEMINI_API_KEY environment variable.")
        sys.exit(1)
    
    # Log startup info
    logger.info("Starting DealFinder AI")
    logger.info(f"Using {'real' if args.real_scrapers else 'mock'} scrapers")
    
    try:
        # Run appropriate interface
        if args.web:
            app = setup_flask_app(gemini_api_key, args.real_scrapers)
            console.print(f"[bold green]Starting web interface on http://localhost:{args.port}[/bold green]")
            app.run(host=config.WEB_HOST, port=args.port, debug=config.DEBUG_MODE)
        else:
            run_terminal_interface(gemini_api_key, args.real_scrapers)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        console.print(f"[bold red]Fatal error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()