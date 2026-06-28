from typing import TypedDict, Annotated, List, Dict
from langchain_core.messages import BaseMessage
from core.agent.schema import AgentProfile

def add_msgs(a, b):
    return a + b

class SalesState(TypedDict):
    # Agents
    lead_agent: AgentProfile
    proposal_agent: AgentProfile

    # Flow data
    company_url: str
    lead_info: Dict
    lead_score: int
    proposal_path: str
    followup_email: str
    script: str

    # Dialogue
    messages: Annotated[List[BaseMessage], add_msgs]

    # Feedback loop
    info_gaps: List[str]
    feedback_request: str
    research_round: int
    max_rounds: int

    # Joint decision & audit
    joint_decision: str
    agent_log: List[Dict]

    # Client feedback (optional)
    client_feedback: str
