"""
Base Agent and MCP Protocol implementation for DealFinder AI.

This module defines the base Agent class and MCPMessage protocol
that all agents in the system will use to communicate.
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class MCPMessage:
    """Implementation of Multi-Agent Communication Protocol (MCP) messages"""
    
    def __init__(self, 
                 sender: str, 
                 receiver: str, 
                 content: Any,
                 message_type: str = "REQUEST",
                 conversation_id: Optional[str] = None):
        """
        Initialize a new MCP message.
        
        Args:
            sender: The name of the sending agent
            receiver: The name of the receiving agent
            content: The message content (can be any serializable object)
            message_type: The type of message (REQUEST, RESPONSE, INFO, ERROR)
            conversation_id: Optional conversation ID for grouping related messages
        """
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.message_type = message_type  # REQUEST, RESPONSE, INFO, ERROR
        self.timestamp = datetime.now().isoformat()
        self.conversation_id = conversation_id or datetime.now().strftime("%Y%m%d%H%M%S")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format"""
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp,
            "conversation_id": self.conversation_id
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPMessage':
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls(
            sender=data["sender"],
            receiver=data["receiver"],
            content=data["content"],
            message_type=data["message_type"],
            conversation_id=data["conversation_id"]
        )


class Agent:
    """Base agent class for MCP protocol"""
    
    def __init__(self, name: str):
        """
        Initialize a new agent.
        
        Args:
            name: The name of the agent
        """
        self.name = name
        self.logger = logging.getLogger(f"DealFinderAI.{name}")
    
    def process_message(self, message: MCPMessage) -> MCPMessage:
        """
        Process incoming message and return response.
        
        This is the main method that should be overridden by subclasses
        to implement agent-specific logic.
        
        Args:
            message: The incoming MCPMessage to process
            
        Returns:
            A new MCPMessage containing the response
        """
        self.logger.info(f"Processing message: {message.message_type} from {message.sender}")
        # Default implementation just echoes the message
        return MCPMessage(
            sender=self.name,
            receiver=message.sender,
            content=f"Received your message: {message.content}",
            message_type="RESPONSE",
            conversation_id=message.conversation_id
        )
    
    def send_message(self, receiver: str, content: Any, message_type: str = "REQUEST") -> MCPMessage:
        """
        Create a new message to send to another agent.
        
        Args:
            receiver: The name of the receiving agent
            content: The message content (can be any serializable object)
            message_type: The type of message (REQUEST, RESPONSE, INFO, ERROR)
            
        Returns:
            A new MCPMessage ready to be sent
        """
        return MCPMessage(
            sender=self.name,
            receiver=receiver,
            content=content,
            message_type=message_type
        )