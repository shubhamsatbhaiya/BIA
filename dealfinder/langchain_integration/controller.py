"""
Controller adapter for DealFinder AI that can dispatch requests to either
the original controller or the new LangChain controller based on configuration.
"""

from dealfinder import config
from dealfinder.controller import DealFinderController

class DealFinderControllerAdapter:
    """
    Adapter that wraps both controller implementations and routes requests
    based on configuration.
    """
    
    def __init__(self, gemini_api_key=None, max_results=None):
        """
        Initialize the controller adapter.
        
        Args:
            gemini_api_key: Optional API key for Gemini
            max_results: Maximum number of results to return per source
        """
        # Initialize both controllers
        self.original_controller = DealFinderController(
            gemini_api_key=gemini_api_key,
            max_results=max_results or config.DEFAULT_MAX_RESULTS
        )
        
        self.langchain_controller = DealFinderController()
        
        # Track which controller is used for each session
        self.session_controllers = {}
    
    def process_user_query(self, query: str, session_id: str = None) -> str:
        """
        Process a user query using the appropriate controller.
        
        Args:
            query: The user query string
            session_id: Optional session ID for conversation tracking
            
        Returns:
            A formatted response string with the search results
        """
        # Determine which controller to use
        use_langchain = config.ENABLE_LANGCHAIN
        
        # If this session already has a controller assigned, use it for consistency
        if session_id in self.session_controllers:
            use_langchain = self.session_controllers[session_id] == "langchain"
        else:
            # Record which controller is used for this session
            self.session_controllers[session_id] = "langchain" if use_langchain else "original"
        
        # Route to the appropriate controller
        if use_langchain:
            return self.langchain_controller.process_user_query(query, session_id)
        else:
            return self.original_controller.process_user_query(query, session_id)
    
    def display_welcome_message(self) -> str:
        """Display welcome message using the appropriate controller."""
        if config.ENABLE_LANGCHAIN:
            return self.langchain_controller.display_welcome_message()
        else:
            self.original_controller.display_welcome_message()
            return "Welcome message displayed"  # Original controller doesn't return the message