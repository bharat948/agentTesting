import re
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import get_user_logger, setup_logging
from app.models.schemas import InferenceRequest, InferenceResponse
from app.services.agent import Agent, Groq
from app.services.memory import ConversationDB, RAGMemory
from app.services.prompt import ReActAgentPrompt
from app.services.tools import tool_registry, Tool, some_tool_function
from app.utils.helpers import parse_agent_response
from app.models.tool import ToolCreate, ToolUpdate

global_logger = setup_logging()
router = APIRouter()

# Initialize global instances
rag_memory = RAGMemory()
groq_client = Groq(api_key=settings.GROQ_API_KEY)

# Dependency: Extract username from header (default to "anonymous")
async def get_username(request: Request) -> str:
    return request.headers.get("X-Username", "anonymous")

@router.post("/infer", response_model=InferenceResponse)
def infer(request_data: InferenceRequest, username: str = Depends(get_username)):
    user_logger = get_user_logger(username)
    user_logger.info(f"Received inference request from user: {username}")
    
    # Retrieve additional context from RAG memory (if available)
    context = rag_memory.get_context(request_data.query)
    history = request_data.history
    if context:
        history += "\n[Additional Context from Knowledge Base]\n" + context
    
    # Build the system prompt using ReActAgentPrompt
    tool_descriptions = [f"{tool.name}: {tool.description}" for tool in tool_registry.list_tools()]
    react_prompt = ReActAgentPrompt(query=request_data.query, history=history, tools=tool_descriptions)
    system_prompt = react_prompt.build_prompt()
    if request_data.system_prompt_extra:
        system_prompt += "\n" + request_data.system_prompt_extra
    
    # Initialize agent with the custom prompt, tools, temperature, and username
    agent_instance = Agent(
        client=groq_client,
        model=settings.DEFAULT_MODEL,
        system=system_prompt,
        tools=tool_registry.list_tools(),
        temperature=request_data.temperature,
        username=username
    )
    
    response = agent_instance(request_data.query)
    thought, answer = parse_agent_response(response)
    
    user_logger.info(f"Inference completed for user: {username} with answer: {answer[:50]}{'...' if len(answer) > 50 else ''}")
    return InferenceResponse(reasoning=thought, answer=answer)

@router.get("/conversations/{username}", response_model=List[Dict[str, Any]])
def get_conversations(username: str):
    convos = ConversationDB().get_conversations(username)
    if not convos:
        raise HTTPException(status_code=404, detail=f"No conversations found for user {username}")
    return convos

@router.get("/health")
def health_check():
    return {"status": "OK", "version": settings.APP_VERSION}

@router.get("/tools")
def list_tools():
    tools = tool_registry.list_tools()
    return {
        "tools": [
            {"name": tool.name, "description": tool.description}
            for tool in tools
        ]
    }

@router.post("/tools")
def add_tool(name: str, description: str):
    if tool_registry.get(name):
        raise HTTPException(status_code=400, detail=f"Tool {name} already exists.")
    new_tool = Tool(name=name, description=description)
    tool_registry.register(new_tool)
    tool_registry.save_state()  # Save the state after adding a new tool
    return {"message": f"Tool {name} added successfully."}

@router.delete("/tools/{name}")
def delete_tool(name: str):
    if not tool_registry.remove(name):
        raise HTTPException(status_code=404, detail=f"Tool {name} not found.")
    return {"message": f"Tool {name} deleted successfully."}

@router.put("/tools/{name}")
def update_tool(name: str, tool_data: ToolUpdate):
    tool = tool_registry.get(name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {name} not found.")
    tool.description = tool_data.description
    return {"message": f"Tool {name} updated successfully."}

@router.get("/tools/")
async def read_tools():
    return some_tool_function() 