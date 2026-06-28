from pydantic import BaseModel
from typing import List

class AgentProfile(BaseModel):
    name: str # 代理名称
    role: str # 代理角色
    goal: str # 代理目标
    backstory: str # 代理背景故事
    tone: str # 代理 tone
    allow_tools: List[str] # 代理允许的工具
    output_format: str # 代理输出格式