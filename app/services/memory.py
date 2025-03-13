import logging
from datetime import datetime
from typing import Any, Dict, List

from app.core.config import settings

# Get a proper logger instance
logger = logging.getLogger(__name__)

class RAGMemory:
    def __init__(self, mongo_uri: str = settings.MONGODB_URI, db_name: str = "rag_system", collection_name: str = "knowledge"):
        try:
            from pymongo import MongoClient
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
        except ImportError:
            logger.warning("pymongo not installed. RAGMemory will return empty results.")
            self.collection = None
        except Exception as e:
            logger.error(f"Error initializing MongoDB connection: {e}")
            self.collection = None
            
    def get_context(self, query: str, limit: int = 3) -> str:
        if not self.collection:
            return ""
        try:
            results = self.collection.find({"$text": {"$search": query}}).limit(limit)
            docs = [doc.get("content", "") for doc in results]
            return "\n".join(docs)
        except Exception as e:
            logger.error(f"Error retrieving context from MongoDB: {e}")
            return ""

class ConversationDB:
    def __init__(self, mongo_uri: str = settings.MONGODB_URI, db_name: str = "agent_db", collection_name: str = "conversations"):
        try:
            from pymongo import MongoClient
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
        except ImportError:
            logger.warning("pymongo not installed. ConversationDB will not persist data.")
            self.collection = None
        except Exception as e:
            logger.error(f"Error initializing MongoDB connection: {e}")
            self.collection = None
            
    def save_conversation(self, username: str, conversation_id: str, messages: List[Dict[str, str]]) -> None:
        if not self.collection:
            logger.warning(f"Cannot save conversation {conversation_id} for user {username}: MongoDB not available")
            return
        try:
            doc = {
                "username": username,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
                "messages": messages
            }
            self.collection.insert_one(doc)
            logger.info(f"Saved conversation {conversation_id} for user {username}")
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            
    def get_conversations(self, username: str) -> List[Dict[str, Any]]:
        if not self.collection:
            logger.warning(f"Cannot retrieve conversations for user {username}: MongoDB not available")
            return []
        try:
            return list(self.collection.find({"username": username}, {"_id": 0}))
        except Exception as e:
            logger.error(f"Error retrieving conversations for user {username}: {e}")
            return []