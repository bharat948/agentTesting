import re
import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, status
from fastapi.responses import JSONResponse

from app.core.config import settings

from app.models.schemas import InferenceRequest, InferenceResponse
from app.services.agent import Agent
from app.services.memory import ConversationDB, RAGMemory
from app.services.prompt import ReActAgentPrompt
from app.services.tools import ToolRegistry, Tool,register_built_in_tools
from app.utils.helpers import parse_agent_response
from app.models.tool import ToolCreate, ToolUpdate
import groq 
router = APIRouter()
tool_registry = ToolRegistry()
register_built_in_tools(tool_registry)
# Initialize global instances
try:
    rag_memory = RAGMemory()
    groq_client = groq.Groq(api_key=settings.GROQ_API_KEY)
    conversation_db = ConversationDB()  
except Exception as e:

    rag_memory = None
    groq_client = None

# Dependency: Extract username from header (default to "anonymous")
async def get_username(request: Request) -> str:
    return request.headers.get("X-Username", "anonymous")

@router.post("/infer", response_model=InferenceResponse)
def infer(request_data: InferenceRequest, username: str = Depends(get_username)):
    # Retrieve additional context from RAG memory (if available)
    context = ""
    if rag_memory:
        context = rag_memory.get_context(request_data.query)
    
    history = request_data.history
    if context:
        history += "\n[Additional Context from Knowledge Base]\n" + context

    # List available tools
    tools = tool_registry.list_tools()
    print("Available tools:", tools, type(tools))
    
    # Build tool descriptions and system prompt using ReActAgentPrompt
    tool_descriptions = [f"{tool.name}: {tool.description}" for tool in tools]
    react_prompt = ReActAgentPrompt(query=request_data.query, history=history, tools=tool_descriptions)
    system_prompt = react_prompt.build_prompt()
    if request_data.system_prompt_extra:
        system_prompt += "\n" + request_data.system_prompt_extra
    
    # Initialize the agent with the custom prompt, tools, temperature, and username
    agent_instance = Agent(
        client=groq_client,
        model=settings.DEFAULT_MODEL,
        system=system_prompt,
        tools=tools,
        temperature=request_data.temperature,
    )
    
    # Get the LLM response
    response = agent_instance(request_data.query)
    thought, answer, action = parse_agent_response(response)
    
    # If an action is specified, attempt to perform it
    if action is not None:
        tool_name = action.get("name")
        tool_input = action.get("input")
        for tool in tools:
            if tool.name.lower() == tool_name.lower():
                try:
                    # Execute the tool's action
                    tool_output = tool.__call__(tool_input)
                    # Append the tool's output to the answer
                    answer += f"\n\n[Executed Action: {tool_name}]\nResult: {tool_output}"
                except Exception as e:
                    answer += f"\n\n[Action {tool_name} execution failed: {e}]"
                break
        
        else:
            answer += f"\n\n[No matching tool found for action: {tool_name}]"
    
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
def add_tool(tool_data: ToolCreate):
    if tool_registry.get(tool_data.name):
        raise HTTPException(status_code=400, detail=f"Tool {tool_data.name} already exists.")
    
    try:
        # If code is provided but init_code or call_code are not, use code as call_code
        init_code = tool_data.init_code or ""
        
        # Use call_code if provided, otherwise use code
        call_code = tool_data.call_code or tool_data.code
        
        # Validate that we have a valid call_code
        if not call_code:
            raise HTTPException(status_code=400, detail="Either 'code' or 'call_code' must be provided.")
        
        # Create the tool
        new_tool = tool_registry.create_tool_from_code(
            name=tool_data.name,
            description=tool_data.description,
            init_code=init_code,
            call_code=call_code
        )
        
        # Register the tool
        tool_registry.register(new_tool)
        
        # Save the registry state
        tool_registry.save_state()
        
        return {"message": f"Tool {tool_data.name} added successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating tool: {str(e)}"
        )
@router.delete("/tools/{name}")
def delete_tool(name: str):
    if not tool_registry.remove(name):
        raise HTTPException(status_code=404, detail=f"Tool {name} not found.")
    tool_registry.save_state()  # Save the state after removing a tool
    return {"message": f"Tool {name} deleted successfully."}

@router.put("/tools/{name}")
def update_tool(name: str, tool_data: ToolUpdate):
    tool = tool_registry.get(name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {name} not found.")
    tool.description = tool_data.description
    tool_registry.save_state()  # Save the state after updating a tool
    return {"message": f"Tool {name} updated successfully."}

