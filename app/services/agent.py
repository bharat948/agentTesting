import re
import uuid
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_user_logger
from app.services.tools import Tool
from app.services.memory import ConversationDB

# Dummy Groq Client (replace with production client as needed)
try:
    from groq import Groq
except ImportError:
    class Groq:
        def __init__(self, api_key):
            self.api_key = api_key
            self.chat = self
        def completions(self, **kwargs):
            class Choice:
                def __init__(self):
                    self.message = type("Msg", (), {"content": "Thought: I have reasoned through the query.\nAnswer: This is a dummy response from Groq."})
            class Completion:
                def __init__(self):
                    self.choices = [Choice()]
            return Completion()
        def create(self, **kwargs):
            return self.completions(**kwargs)

class Agent:
    def __init__(self, 
                 client: Any, 
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
        self.logger = get_user_logger(username)
        self.logger.info(f"Initializing agent with ID: {self.conversation_id} for user: {username}")
        if self.system:
            self.messages.append({"role": "system", "content": system})
            
    def __call__(self, message: str = "") -> str:
        if message:
            self.logger.info(f"User ({self.username}) message: {message[:50]}{'...' if len(message) > 50 else ''}")
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        # Save conversation to persistent storage
        ConversationDB().save_conversation(self.username, self.conversation_id, self.messages)
        return result
        
    def execute(self) -> str:
        self.logger.info(f"Executing LLM call with {len(self.messages)} messages for user: {self.username}")
        try:
            completion = self.client.chat.completions.create(
                model=self.model, 
                messages=self.messages,
                temperature=self.temperature
            )
            result = completion.choices[0].message.content
            self.logger.info(f"LLM response: {result[:50]}{'...' if len(result) > 50 else ''}")
            return result
        except Exception as e:
            self.logger.error(f"LLM execution error: {e}")
            return f"Error: Failed to get response from LLM: {str(e)}" 