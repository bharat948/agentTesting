from datetime import datetime
from typing import Any, Dict, List

from app.core.config import settings

class RAGMemory:
    def __init__(self, mongo_uri: str = settings.MONGODB_URI, db_name: str = "rag_system", collection_name: str = "knowledge"):
        try:
            from pymongo import MongoClient
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
        except ImportError:
            self.collection = None
        except Exception:
            self.collection = None
            
    def get_context(self, query: str, limit: int = 3) -> str:
        if self.collection is None:
            return ""
        try:
            results = self.collection.find({"$text": {"$search": query}}).limit(limit)
            docs = [doc.get("content", "") for doc in results]
            return "\n".join(docs)
        except Exception:
            return ""

class ConversationDB:
    def __init__(self, mongo_uri: str = settings.MONGODB_URI, db_name: str = "rag_system", collection_name: str = "knowledge"):
        try:
            import pymongo 
            self.client = pymongo.MongoClient(mongo_uri)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
        except ImportError:
            self.collection = None
        except Exception:
            self.collection = None
            
    def save_conversation(self, username: str, conversation_id: str, messages: List[Dict[str, str]]) -> None:
        if self.collection is None:
            return
        try:
            doc = {
                "username": username,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
                "messages": messages
            }
            result = self.collection.insert_one(doc)
            print(result)
        except Exception:
            pass
            
    def get_conversations(self, username: str) -> List[Dict[str, Any]]:
        if self.collection is None:
            return []
        try:
            return list(self.collection.find({"username": username}, {"_id": 0}))
        except Exception:
            return []
