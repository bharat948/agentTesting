import re
import uuid
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.core.config import settings

from app.services.tools import Tool
from app.services.memory import ConversationDB
from groq import Groq
class Agent:
    def __init__(self, 
                 client: Any=None, 
                 model: str = settings.DEFAULT_MODEL, 
                 system: str = "",
                 tools: Optional[List[Tool]] = None,
                 temperature: float = settings.DEFAULT_TEMPERATURE,
                 username: str = "anonymous") -> None:
        self.client = client
        self.model = model
        self.system = system
        self.temperature = temperature
        self.username = username
        self.messages: List[Dict[str, str]] = []
        self.conversation_id = str(uuid.uuid4())
        self.tools = tools or []
        self.tool_map = {tool.name: tool for tool in self.tools}
        if self.system:
            self.messages.append({"role": "system", "content": system})
            
    def __call__(self, message: str = "") -> str:
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        # Save conversation to persistent storage
        ConversationDB().save_conversation(self.username, self.conversation_id, self.messages)
        return result
        
    def execute(self) -> str:
        try:
            print("System messages:", self.messages)
            
            # Import necessary modules
            import groq 
            import asyncio

            # Initialize the Groq client with your API key
            client = groq.Groq(api_key=settings.GROQ_API_KEY)
            print("Initialized Groq client:", client)

            # Run the asynchronous API call inside an event loop
            completion = client.chat.completions.create(
                model=self.model, 
                messages=self.messages,
                temperature=self.temperature
            )
            print("Completion response:", completion)
            
            # Extract the result
            result = completion.choices[0].message.content
            print("LLM response:", result)
            return result

        except Exception as e:
            return f"Error: Failed to get response from LLM: {str(e)}"
