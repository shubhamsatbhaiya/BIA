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
import json
from typing import Optional
from datetime import datetime, timedelta

from dotenv import load_dotenv
from rich.console import Console

from dealfinder.langchain_integration.controller import DealFinderControllerAdapter
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
        # Initialize the controller adapter which can use either implementation
        controller = DealFinderControllerAdapter(
            gemini_api_key=gemini_api_key
        )
        
        # Display welcome message and which implementation is being used
        welcome_message = controller.display_welcome_message()
        if config.ENABLE_LANGCHAIN:
            console.print(welcome_message)
            console.print(f"[bold blue]Using LangChain implementation with Gemini model[/bold blue]")
        else:
            controller.display_welcome_message()  # Display directly (doesn't return a string)
            console.print("[bold blue]Using original implementation[/bold blue]")
        
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
    try:
        from flask import Flask, request, jsonify, render_template, session, make_response, Response
    except ImportError:
        console.print("[bold red]Error:[/bold red] Flask is not installed. Run 'pip install flask'.")
        sys.exit(1)

    app = Flask(__name__)
    
    # Add CORS headers for all responses
    @app.after_request
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Handle OPTIONS requests
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        return Response('', 204)
    
    # Flask session configuration - simplified to avoid Flask-Session dependency
    app.secret_key = os.getenv("SECRET_KEY") or "dealfinder-secret-key"  
    
    # Initialize session store - simple in-memory dict for sessions
    session_store = {}

    # Initialize the controller adapter which can use either implementation
    try:
        controller = DealFinderControllerAdapter(
            gemini_api_key=gemini_api_key
        )
        
        # Log which implementation is being used
        if config.ENABLE_LANGCHAIN:
            logger.info("Web app using LangChain implementation with Gemini model")
        else:
            logger.info("Web app using original implementation")
    except Exception as e:
        logger.error(f"Error initializing controller: {str(e)}")
        # We'll continue and handle errors in the API endpoints
    
    # Serve static HTML
    @app.route('/')
    def home():
        return render_template('index.html')
    
    # Utility function to get or create session ID
    def get_session_id():
        client_id = request.cookies.get('dealfinder_session')
        
        if not client_id or client_id not in session_store:
            # Create new session ID
            client_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"
            # Initialize session data
            session_store[client_id] = {
                "created_at": datetime.now(),
                "last_accessed": datetime.now()
            }
        else:
            # Update last accessed time
            session_store[client_id]["last_accessed"] = datetime.now()
            
        # Clean up old sessions periodically
        clean_old_sessions()
            
        return client_id
    
    # Clean up old sessions to avoid memory leaks
    def clean_old_sessions():
        now = datetime.now()
        expired_time = now - timedelta(hours=1)  # Sessions expire after 1 hour
        
        expired_sessions = [
            session_id for session_id, data in session_store.items() 
            if data["last_accessed"] < expired_time
        ]
        
        for session_id in expired_sessions:
            del session_store[session_id]

    # API endpoint for querying
    @app.route('/api/query', methods=['POST'])
    def query():
        try:
            # Safety check for invalid JSON
            if not request.is_json:
                return jsonify({'error': 'Invalid request format - expected JSON'}), 400
                
            data = request.get_json() or {}
            user_query = data.get('query', '').strip()

            if not user_query:
                return jsonify({'error': 'No query provided'}), 400

            # Get or create a session ID
            client_id = get_session_id()
            
            # Set cookie in response
            response = make_response(jsonify({
                'message': 'Processing query...'
            }))
            response.set_cookie('dealfinder_session', client_id, max_age=3600, httponly=True)

            # Process the query using the controller adapter
            try:
                controller_response = controller.process_user_query(user_query, session_id=client_id)
                
                # Create JSON response
                return jsonify({
                    'response': controller_response,
                    'using_langchain': config.ENABLE_LANGCHAIN,
                    'session_id': client_id
                })
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                return jsonify({'error': f"Error processing query: {str(e)}"}), 500
                
        except Exception as e:
            logger.error(f"Error in query endpoint: {str(e)}")
            return jsonify({'error': f"Server error: {str(e)}"}), 500
            
    # API endpoint for getting welcome message
    @app.route('/api/welcome', methods=['GET', 'HEAD'])
    def welcome():
        # For HEAD requests, just return headers for connection testing
        if request.method == 'HEAD':
            return '', 200
            
        try:
            # Get or create a session ID
            client_id = get_session_id()
            
            # Set cookie in response
            response = make_response(jsonify({
                'welcome_message': controller.display_welcome_message(),
                'using_langchain': config.ENABLE_LANGCHAIN,
                'server_info': {
                    'version': '1.0',
                    'status': 'online'
                }
            }))
            response.set_cookie('dealfinder_session', client_id, max_age=3600, httponly=True)
            return response
            
        except Exception as e:
            logger.error(f"Error getting welcome message: {str(e)}")
            return jsonify({
                'error': f"Error getting welcome message: {str(e)}",
                'server_info': {
                    'version': '1.0',
                    'status': 'error'
                }
            }), 500

    # API endpoint for toggling LangChain
    @app.route('/api/toggle_langchain', methods=['POST'])
    def toggle_langchain():
        try:
            # Toggle the LangChain setting
            config.ENABLE_LANGCHAIN = not config.ENABLE_LANGCHAIN
            logger.info(f"Toggled LangChain integration to: {config.ENABLE_LANGCHAIN}")
            
            return jsonify({
                'using_langchain': config.ENABLE_LANGCHAIN,
                'message': f"Switched to {'LangChain' if config.ENABLE_LANGCHAIN else 'original'} implementation"
            })
        except Exception as e:
            logger.error(f"Error toggling LangChain: {str(e)}")
            return jsonify({'error': f"Error toggling LangChain: {str(e)}"}), 500
    
    # Basic health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'using_langchain': config.ENABLE_LANGCHAIN
        })

    return app

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='DealFinder AI - Find the best deals online')
    parser.add_argument('--api-key', type=str, help='Gemini API Key (optional, can also use GEMINI_API_KEY env var)')
    parser.add_argument('--web', action='store_true', help='Run as a web service instead of terminal')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the web server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the web server on')
    parser.add_argument('--no-langchain', action='store_true', help='Disable LangChain integration')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    # Get API key from args or environment
    gemini_api_key = args.api_key or config.GEMINI_API_KEY
    
    if not gemini_api_key:
        console.print("[bold red]Error:[/bold red] Gemini API key is required. Set it with --api-key or GEMINI_API_KEY environment variable.")
        sys.exit(1)
    
    # Override LangChain setting if specified
    if args.no_langchain:
        config.ENABLE_LANGCHAIN = False
    
    # Override debug mode if specified
    if args.debug:
        config.DEBUG_MODE = True
    
    # Log startup info
    logger.info("Starting DealFinder AI")
    logger.info(f"Using {'LangChain' if config.ENABLE_LANGCHAIN else 'original'} implementation")
    
    # Run appropriate interface
    try:
        if args.web:
            try:
                app = setup_flask_app(
                    gemini_api_key=gemini_api_key
                )
                console.print(f"[bold green]Starting web server on http://{args.host}:{args.port}/[/bold green]")
                console.print("[bold blue]Press Ctrl+C to stop the server[/bold blue]")
                app.run(host=args.host, port=args.port, debug=config.DEBUG_MODE)
            except Exception as e:
                logger.error(f"Error starting web server: {str(e)}")
                console.print(f"[bold red]Error starting web server:[/bold red] {str(e)}")
                sys.exit(1)
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