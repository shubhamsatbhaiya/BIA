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

def run_terminal_interface(gemini_api_key: Optional[str] = None):
    """
    Run the chatbot in terminal mode.
    
    Args:
        gemini_api_key: Optional API key for Gemini
    """
    try:
        # Initialize the controller
        controller = DealFinderController(
            gemini_api_key=gemini_api_key
        )
        
        # Display welcome message
        controller.display_welcome_message()
        from datetime import datetime
        session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Main interaction loop
        while True:
            try:
                user_input = console.input("\n[bold blue]What are you looking for today?[/bold blue] ")
                
                if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
                    console.print("[bold green]Thank you for using DealFinder AI! Goodbye![/bold green]")
                    break
                
                # Show a spinner while processing
                with console.status("[bold green]Searching for the best deals...[/bold green]", spinner="dots"):
                    response = controller.process_user_query(user_input, session_id=session_id)
                
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

def setup_flask_app(gemini_api_key: Optional[str] = None):
    """
    Set up the Flask web app for the chatbot.
    
    Args:
        gemini_api_key: Optional API key for Gemini
        
    Returns:
        Flask application instance
    """
    from flask import Flask, request, jsonify, render_template, session

    app = Flask(__name__)

    # Flask session configuration
    app.secret_key = os.getenv("SECRET_KEY")  # Replace with a secure key
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_TYPE'] = 'filesystem'

    # Initialize the controller
    controller = DealFinderController(
        gemini_api_key=gemini_api_key
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

        # Reuse or create a session-level conversation ID
        if 'session_id' not in session:
            from datetime import datetime
            session['session_id'] = datetime.now().strftime("%Y%m%d%H%M%S")

        try:
            response = controller.process_user_query(user_query, session_id=session['session_id'])
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
    
    args = parser.parse_args()
    
    # Get API key from args or environment
    gemini_api_key = args.api_key or config.GEMINI_API_KEY
    
    if not gemini_api_key:
        console.print("[bold red]Error:[/bold red] Gemini API key is required. Set it with --api-key or GEMINI_API_KEY environment variable.")
        sys.exit(1)
    
    # Log startup info
    logger.info("Starting DealFinder AI")
    logger.info(f"Using real scrapers")
    
    # Run appropriate interface
    try:
        if args.web:
            app = setup_flask_app(
                gemini_api_key=gemini_api_key
            )
            app.run(debug=True)
        else:
            run_terminal_interface(
                gemini_api_key=gemini_api_key
            )
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        console.print(f"[bold red]Fatal error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()