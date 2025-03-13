from pydantic import BaseModel

class ToolCreate(BaseModel):
    name: str
    description: str

class ToolUpdate(BaseModel):
    description: str 