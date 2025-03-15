import uvicorn
from app.core.config import settings
from app.services.tools import tool_registry

if __name__ == "__main__":
    # Load the state of tools on startup
    tool_registry.load_state()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
