import uvicorn
from app.core.config import settings
from app.core.logging import setup_logging
# from app.services.tools import tool_registry

if __name__ == "__main__":
    setup_logging()
    # tool_registry.load_state()  # Load the state of tools on startup
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config="logging_config.py"  # Use the INI-style logging configuration
    )