from typing import Optional
from pydantic import BaseModel, Field

class ToolCreate(BaseModel):
    name: str
    description: str
    code: str = Field(..., description="Python code for the __call__ method")

class ToolUpdate(BaseModel):
    description: Optional[str] = None
    code: Optional[str] = None