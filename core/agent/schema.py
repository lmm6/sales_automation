from pydantic import BaseModel
from typing import List

class AgentProfile(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    tone: str
    allow_tools: List[str]
    output_format: str
    prompt: str = ""
