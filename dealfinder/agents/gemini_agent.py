"""
Gemini API Agent for DealFinder AI.

This module implements the GeminiAgent class that interfaces with
Google's Gemini API for natural language understanding.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

import google.generativeai as genai

from dealfinder.agents.base import Agent, MCPMessage

logger = logging.getLogger("DealFinderAI.GeminiAgent")

class GeminiAgent(Agent):
    """Agent that interfaces with Google's Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize a new Gemini API agent.
        
        Args:
            api_key: Optional Gemini API key. If not provided, will try to get it from
                     the GEMINI_API_KEY environment variable.
        """
        super().__init__("GeminiAgent")
        
        # Initialize the Gemini API with the provided key or from environment
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass it to the constructor.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Process requests using Gemini API.
        
        Handles various message types:
        - REQUEST: Generate a response to the user query
        - PARSE_QUERY: Parse the user query into structured search parameters
        
        Args:
            message: The incoming MCPMessage to process
            
        Returns:
            A new MCPMessage containing the response
        """
        self.logger.info(f"Processing query with Gemini: {message.content}")
        
        try:
            if message.message_type == "REQUEST":
                # Generate response from Gemini
                response = self.model.generate_content(message.content)
                
                return MCPMessage(
                    sender=self.name,
                    receiver=message.sender,
                    content=response.text,
                    message_type="RESPONSE",
                    conversation_id=message.conversation_id
                )
            elif message.message_type == "PARSE_QUERY":
                # Parse user query to extract search parameters
                return self._parse_user_query(message)
            else:
                return MCPMessage(
                    sender=self.name,
                    receiver=message.sender,
                    content={"error": f"Unsupported message type: {message.message_type}"},
                    message_type="ERROR",
                    conversation_id=message.conversation_id
                )
                
        except Exception as e:
            self.logger.error(f"Error processing Gemini request: {str(e)}")
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": f"Gemini API error: {str(e)}"},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
    
    def _parse_user_query(self, message: MCPMessage) -> MCPMessage:
        """
        Parse a user query into structured search parameters.
        
        Args:
            message: The incoming MCPMessage with the query to parse
            
        Returns:
            A new MCPMessage containing the parsed parameters
        """
        prompt = f"""
        Parse the following shopping query into structured data:
        "{message.content}"
        
        Return a JSON object with these fields:
        - product_type: The main product category
        - keywords: Important keywords for filtering results
        - price_range: Optional price range (min, max) as two numbers
        - brands: Optional specific brands mentioned
        - features: Important features or specifications
        - sorting_preference: How results should be sorted (price_low_to_high, price_high_to_low, rating, newest)
        - buy_it_now: Boolean, true if the user prefers immediate purchase (not auctions)
        
        Format as valid JSON without explanations.
        """
        
        response = self.model.generate_content(prompt)
        
        try:
            # Attempt to parse the JSON response
            parsed_json = json.loads(response.text)
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content=parsed_json,
                message_type="RESPONSE",
                conversation_id=message.conversation_id
            )
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the response
            self.logger.warning(f"Failed to parse Gemini response as JSON: {response.text}")
            
            # Try to extract JSON block if it's wrapped in code markers
            try:
                if "```json" in response.text:
                    json_content = response.text.split("```json")[1].split("```")[0].strip()
                    parsed_json = json.loads(json_content)
                    return MCPMessage(
                        sender=self.name,
                        receiver=message.sender,
                        content=parsed_json,
                        message_type="RESPONSE",
                        conversation_id=message.conversation_id
                    )
            except (IndexError, json.JSONDecodeError):
                pass
            
            # Return error message if all parsing attempts fail
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                content={"error": "Failed to parse query", "raw_response": response.text},
                message_type="ERROR",
                conversation_id=message.conversation_id
            )
    
    def extract_product_details_from_html(self, html_content: str) -> Dict[str, Any]:
        """
        Extract product details from HTML content using Gemini.
        
        Args:
            html_content: HTML content to extract details from
            
        Returns:
            Dictionary containing extracted product details
        """
        try:
            prompt = f"""
            Extract product details from the following HTML content:

            Content:
            ```html
            {html_content}
            ```

            Extract the following fields:
            - title: Product title
            - price: Product price as a float
            - url: Product URL
            - image_url: Product image URL
            - rating: Product rating (0-5)
            - reviews: Number of reviews
            - 
            Return the results in JSON format:
            ```json
            {{
                "title": "",
                "price": 0.0,
                "url": "",
                "image_url": "",
                "rating": 0.0,
                "reviews": 0
            }}
            ```
            """
            response = self.model.generate_content(prompt)
            content = response.text
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'```json\s*([^`]+)\s*```', content)
            data = None
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    data = None
            if data is None:
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    return {
                        "error": "Could not extract product details from HTML"
                    }
            # Type correction
            try:
                data["price"] = float(data.get("price", 0.0))
            except Exception:
                data["price"] = 0.0
            try:
                data["rating"] = float(data.get("rating", 0.0))
            except Exception:
                data["rating"] = 0.0
            try:
                data["reviews"] = int(data.get("reviews", 0))
            except Exception:
                data["reviews"] = 0
            return data
        except Exception as e:
            self.logger.error(f"Error extracting product details: {str(e)}")
            return {
                "error": f"Error extracting product details: {str(e)}"
            }
    def run(self, prompt: str) -> str:
        """
        Run a free-form prompt using the Gemini model and return the response text.
        
        Args:
            prompt: A text prompt to be sent to the Gemini model.
            
        Returns:
            The text content of Gemini's response.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Error in run(): {str(e)}")
            return f"Error: {str(e)}"