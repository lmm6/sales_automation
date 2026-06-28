from typing import TypedDict, Annotated, List, Dict
from langchain_core.messages import BaseMessage
from core.agent.schema import AgentProfile

def add_msgs(a, b):
    return a + b

class SalesState(TypedDict):
    # 两个智能体
    lead_agent: AgentProfile
    proposal_agent: AgentProfile

    # 流程数据
    company_url: str
    lead_info: Dict
    lead_score: int
    proposal_path: str
    followup_email: str
    script: str

    # 对话
    messages: Annotated[List[BaseMessage], add_msgs]