import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API settings
    APP_TITLE: str = "Agentic Workflow API"
    APP_DESCRIPTION: str = "Production-level API for a modular agent system with per-user conversation history and detailed logging."
    APP_VERSION: str = "1.0"
    
    # Environment settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "dummy_api_key")
    
    # Database settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    
    # Logging settings
    LOGS_DIR: str = os.getenv("LOGS_DIR", "logs")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # LLM settings
    DEFAULT_MODEL: str = "gemma2-9b-it"
    DEFAULT_TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 