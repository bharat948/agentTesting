from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API settings
    APP_TITLE: str = "Agentic Workflow API"
    APP_DESCRIPTION: str = "Production-level API for a modular agent system with per-user conversation history and detailed logging."
    APP_VERSION: str = "1.0"
    
    # Environment settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # API keys
    GROQ_API_KEY: str = "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"
    
    # Database settings
    MONGODB_URI: str = "mongodb+srv://bharat:Bharat948@cluster-1.xtbst.mongodb.net/"
    
    # Logging settings
    LOGS_DIR: str = "logs"
    LOG_LEVEL: str = "INFO"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # LLM settings
    DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    DEFAULT_TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
