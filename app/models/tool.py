from typing import Optional
from pydantic import BaseModel, Field

class ToolCreate(BaseModel):
    name: str
    description: str
    code: Optional[str] = None
    init_code: Optional[str] = ""
    call_code: Optional[str] = ""
class ToolUpdate(BaseModel):
    description: Optional[str] = None
    code: Optional[str] = None