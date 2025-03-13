from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class PromptSection(str, Enum):
    INTRODUCTION = "introduction"
    CONTEXT = "context"
    BEHAVIOR = "behavior"
    CONSTRAINTS = "constraints"
    ADAPTATION = "adaptation"
    FORMAT = "format"
    ERROR_HANDLING = "error_handling"
    METRICS = "metrics"
    CUSTOM = "custom"

class InferenceRequest(BaseModel):
    query: str = Field(..., description="The query to be answered")
    history: Optional[str] = Field("", description="Previous reasoning steps")
    temperature: Optional[float] = Field(0.7, description="Temperature for LLM")
    system_prompt_extra: Optional[str] = Field("", description="Additional instructions to append to the system prompt")

class InferenceResponse(BaseModel):
    reasoning: str = Field(..., description="The internal reasoning of the agent")
    answer: str = Field(..., description="The final answer provided by the agent")

class ToolAction(BaseModel):
    name: str = Field(..., description="Name of the tool to use")
    reason: str = Field(..., description="Reason for using this tool")
    input: str = Field(..., description="Input for the tool")

class AgentThought(BaseModel):
    thought: str = Field(..., description="Agent's reasoning process")
    action: Optional[ToolAction] = Field(None, description="Tool action to take")
    answer: Optional[str] = Field(None, description="Final answer if available")

class ConversationResponse(BaseModel):
    conversation_id: str
    username: str
    timestamp: str
    messages: List[Dict[str, str]] 